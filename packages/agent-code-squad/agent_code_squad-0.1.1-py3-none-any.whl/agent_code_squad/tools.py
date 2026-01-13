from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import SquadConfig
from .context import RipgrepNotFound, build_context_pack
from .dispatch import CodexDispatch, DispatchConfig
from .ops_log import log as ops_log
from .paths import ensure_dir, ensure_repo_subpath, find_repo_root, safe_relpath, slugify
from .runner import BackgroundWorker, RunStore
from .utils import truncate_text, utc_now_iso

NOISE_EVENT_TYPES = {
    "thread.started",
    "thread.created",
    "turn.started",
    "turn.created",
    "turn.delta",
    "turn.completed",
    "turn.finished",
    "run.started",
    "run.finished",
    "response.started",
    "response.completed",
    "response.finished",
    "thread_started",
    "thread_created",
    "turn_started",
    "turn_created",
    "turn_delta",
    "turn_completed",
    "turn_finished",
    "run_started",
    "run_finished",
    "response_started",
    "response_completed",
    "response_finished",
    "heartbeat",
    "ping",
    "pong",
    "item.started",
    "item.updated",
    "item.completed",
}

NOISY_ITEM_TYPES = {"command_execution", "mcp_tool_call", "todo_list"}


def _extract_readable_stdout(stdout_tail: str | None, last_message: str | None, *, max_chars: int = 700) -> str | None:
    """
    Lightweight port of agent-supervisor-memory's readable stdout extraction.
    """
    if not stdout_tail:
        return truncate_text(last_message or "", max_chars) if last_message else None

    def _flatten(content: Any) -> str | None:
        if content is None:
            return None
        if isinstance(content, list):
            for item in reversed(content):
                flattened = _flatten(item)
                if flattened:
                    return flattened
            return None
        if isinstance(content, dict):
            ctype = content.get("type")
            if isinstance(ctype, str) and (ctype in NOISE_EVENT_TYPES or ctype in NOISY_ITEM_TYPES):
                return None
            for key in ("message", "content", "text"):
                if key in content:
                    val = _flatten(content.get(key))
                    if val:
                        return val
            if "item" in content:
                return _flatten(content.get("item"))
            return None
        return str(content)

    noise_types = NOISE_EVENT_TYPES
    fallback_event_type: str | None = None
    raw_fallback: str | None = None
    reasoning_fallback: str | None = None

    for line in reversed(stdout_tail.splitlines()):
        candidate = line.strip()
        if not candidate:
            continue
        try:
            obj = json.loads(candidate)
        except json.JSONDecodeError:
            if raw_fallback is None:
                raw_fallback = candidate
            continue

        if isinstance(obj, dict):
            event_type = obj.get("type")
            if isinstance(event_type, str) and event_type in noise_types:
                continue

        text_val = _flatten(obj)
        if text_val:
            return truncate_text(text_val, max_chars)

        if raw_fallback is None:
            raw_fallback = candidate
        if not fallback_event_type and isinstance(obj, dict):
            event_type = obj.get("type")
            if isinstance(event_type, str) and event_type and event_type not in noise_types:
                fallback_event_type = event_type
        if reasoning_fallback is None:
            reasoning_fallback = truncate_text(str(obj), max_chars)

    if reasoning_fallback:
        return reasoning_fallback
    if raw_fallback:
        return truncate_text(raw_fallback, max_chars)
    if last_message:
        return truncate_text(last_message, max_chars)
    return None


def _compact_event(obj: dict[str, Any], *, max_chars: int = 800) -> dict[str, Any]:
    if not isinstance(obj, dict):
        return {"text": truncate_text(str(obj), max_chars)}
    result: dict[str, Any] = {}
    for key in ("type", "message", "text", "content", "item"):
        if key not in obj:
            continue
        val = obj.get(key)
        if isinstance(val, (dict, list)):
            result[key] = truncate_text(json.dumps(val, ensure_ascii=False), max_chars)
        else:
            result[key] = truncate_text(str(val), max_chars)
    if not result:
        return {"text": truncate_text(json.dumps(obj, ensure_ascii=False), max_chars)}
    return result


def _format_context(context_pack: dict[str, Any] | None) -> str | None:
    if not context_pack:
        return None
    snippets = context_pack.get("snippets") or []
    if not snippets:
        return None
    parts: list[str] = ["Context pack (read-only)"]
    for snip in snippets:
        header = f"{snip.get('path')}:{snip.get('start_line')}-{snip.get('end_line')}"
        parts.append(header)
        text_val = snip.get("text") or ""
        parts.append(text_val)
        parts.append("---")
    return "\n".join(parts)


def _compose_prompt(task_prompt: str, context_pack: dict[str, Any] | None) -> str:
    segments = [
        "You are a focused code-writing subagent. Produce git-style patches only, avoid speculation, and keep output minimal.",
        f"Subtask: {task_prompt.strip()}",
    ]
    ctx_text = _format_context(context_pack)
    if ctx_text:
        segments.append(ctx_text)
    segments.append("Return concise diffs or commands. Prefer patches over prose.")
    return "\n\n".join(seg for seg in segments if seg)


def register_tools(mcp: FastMCP, *, config: SquadConfig) -> None:
    app_id = "agent-code-squad"
    store = RunStore(config.dispatch_dir)
    worker = BackgroundWorker(store, verbosity=config.verbosity)

    def _dispatch_for_run(run_id: str) -> CodexDispatch:
        run_dir = store.run_dir(run_id)
        jobs_dir = ensure_dir(run_dir / "jobs")
        return CodexDispatch(DispatchConfig(jobs_dir=jobs_dir, verbosity=config.verbosity))

    def _update_run(run_id: str, updater) -> dict[str, Any] | None:
        return store.update(run_id, updater)

    def _load_run(run_id: str) -> dict[str, Any] | None:
        return store.load(run_id)

    def _save_run(run_id: str, meta: dict[str, Any]) -> None:
        store.save(run_id, meta)

    def _debug_enabled(options: dict[str, Any] | None) -> bool:
        return bool(options and options.get("debug"))

    @mcp.tool(name="code_squad_capabilities_get")
    def code_squad_capabilities_get(options: dict[str, Any] | None = None) -> dict[str, Any]:
        debug = _debug_enabled(options)
        result: dict[str, Any] = {
            "server": {"name": app_id, "defaults": {"model": config.default_model, "sandbox": config.default_sandbox, "approval_policy": config.default_approval_policy}},
            "tools": [
                "code_squad_capabilities_get",
                "code_squad_context_pack",
                "code_squad_run",
                "code_squad_tick",
                "code_squad_status",
                "code_squad_events",
                "code_squad_collect",
                "code_squad_verify",
                "code_squad_cancel",
                "code_squad_cleanup",
            ],
        }
        if debug:
            result["debug"] = {"paths": {"dispatch_dir": str(config.dispatch_dir)}}
        return result

    @mcp.tool(name="code_squad_context_pack")
    def code_squad_context_pack(
        cwd: str,
        query: str,
        hints: list[str] | None = None,
        glob: str = "*.py",
        max_files: int = 12,
        max_snippets: int = 24,
        max_total_chars: int = 20_000,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_context_pack", "start", trace_id, cwd=cwd)
        try:
            try:
                result = build_context_pack(
                    cwd=cwd,
                    query=query,
                    hints=hints or [],
                    glob=glob,
                    max_files=max_files,
                    max_snippets=max_snippets,
                    max_total_chars=max_total_chars,
                )
            except RipgrepNotFound as exc:
                result = {"error": str(exc), "cwd": cwd, "query": query}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                result = {**result, "debug": {"trace_id": trace_id, "elapsed_ms": elapsed_ms}}
            return result
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_context_pack", "end", trace_id, cwd=cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_run")
    def code_squad_run(
        cwd: str,
        tasks: list[dict[str, Any]],
        run_id: str | None = None,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_run", "start", trace_id, cwd=cwd)
        try:
            if not tasks:
                return {"error": "No tasks provided"}
            repo_root = find_repo_root(Path(cwd))
            resolved_run_id = slugify(run_id or uuid.uuid4().hex, fallback="run")
            run_dir = store.run_dir(resolved_run_id)
            worktree_base = ensure_repo_subpath(repo_root, repo_root / ".codex" / "code-squad" / "worktrees" / resolved_run_id)
            ensure_dir(worktree_base)

            defaults = {
                "model": options.get("model") if options else None,
                "sandbox": options.get("sandbox") if options else None,
                "approval_policy": options.get("approval_policy") if options else None,
                "extra_config": options.get("extra_config") if options else None,
            } if options else {}

            existing = _load_run(resolved_run_id)
            run_meta = existing or {
                "id": resolved_run_id,
                "created_at": utc_now_iso(),
                "repo_root": str(repo_root),
                "dispatch_base": str(config.dispatch_dir),
                "run_dir": str(run_dir),
                "worktree_base": str(worktree_base),
                "defaults": {
                    "model": defaults.get("model") or config.default_model,
                    "sandbox": defaults.get("sandbox") or config.default_sandbox,
                    "approval_policy": defaults.get("approval_policy") or config.default_approval_policy,
                    "extra_config": defaults.get("extra_config") if defaults.get("extra_config") else [],
                },
                "tasks": [],
                "queue": [],
            }

            task_results: list[dict[str, Any]] = []
            debug_tasks: list[dict[str, Any]] = []
            for idx, task in enumerate(tasks):
                name = str(task.get("name") or f"task-{idx+1}")
                prompt = str(task.get("prompt") or "")
                if not prompt.strip():
                    task_results.append({"name": name, "slug": None, "job_id": None, "state": "error", "error": "Empty prompt"})
                    continue
                slug = slugify(name, fallback=f"task-{idx+1}")
                existing_slugs = {t.get("slug") for t in run_meta.get("tasks", [])}
                suffix = 2
                base_slug = slug
                while slug in existing_slugs:
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1

                worktree_path = ensure_repo_subpath(repo_root, worktree_base / slug)
                task_context = task.get("context_pack")
                composed_prompt = _compose_prompt(prompt, task_context)
                task_model = task.get("model") or defaults.get("model") or config.default_model
                task_sandbox = task.get("sandbox") or defaults.get("sandbox") or config.default_sandbox
                task_approval = task.get("approval_policy") or defaults.get("approval_policy") or config.default_approval_policy
                extra_config = task.get("extra_config") or defaults.get("extra_config") or []
                job_id = f"{resolved_run_id}--{slug}-{uuid.uuid4().hex[:8]}"

                task_entry = {
                    "name": name,
                    "slug": slug,
                    "job_id": job_id,
                    "worktree": str(worktree_path),
                    "state": "queued",
                    "queued_at": utc_now_iso(),
                    "model": task_model,
                    "sandbox": task_sandbox,
                    "approval_policy": task_approval,
                    "extra_config": extra_config if isinstance(extra_config, list) else [],
                    "prompt": composed_prompt,
                    "context_paths": [snip.get("path") for snip in (task_context.get("snippets") if task_context else [])],
                }
                run_meta["tasks"].append(task_entry)
                run_meta.setdefault("queue", []).append(slug)
                task_results.append({"name": name, "slug": slug, "job_id": job_id, "state": "queued"})
                if debug:
                    debug_tasks.append(
                        {
                            "name": name,
                            "slug": slug,
                            "job_id": job_id,
                            "state": "queued",
                            "worktree": str(worktree_path),
                            "model": task_model,
                            "sandbox": task_sandbox,
                            "approval_policy": task_approval,
                            "context_paths": task_entry.get("context_paths"),
                        }
                    )

            _save_run(resolved_run_id, run_meta)
            response: dict[str, Any] = {"run_id": resolved_run_id, "tasks": task_results, "existing": bool(existing)}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {
                    "trace_id": trace_id,
                    "elapsed_ms": elapsed_ms,
                    "run_dir": str(run_dir),
                    "worktree_base": str(worktree_base),
                    "dispatch_base": str(config.dispatch_dir),
                    "repo_root": str(repo_root),
                    "defaults": run_meta.get("defaults"),
                    "queue": list(run_meta.get("queue", [])),
                    "tasks": debug_tasks,
                }
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_run", "end", trace_id, cwd=cwd, elapsed_ms=elapsed_ms)

    def _refresh_task_states(run_id: str, run_meta: dict[str, Any], *, limit: int | None = None) -> tuple[dict[str, Any], int]:
        dispatch = _dispatch_for_run(run_id)
        updated = 0
        for task in run_meta.get("tasks", []):
            if limit is not None and updated >= limit:
                break
            if task.get("state") not in ("starting", "running"):
                continue
            job_id = task.get("job_id")
            status_res = dispatch.status(job_id=job_id, include_last_message=True)
            if not status_res.get("found"):
                continue
            meta = status_res.get("meta") or {}
            meta_status = str(meta.get("status") or "").lower()
            if meta_status in ("completed", "failed", "cancelled"):
                task["state"] = meta_status
                task["finished_at"] = task.get("finished_at") or utc_now_iso()
                task["exit_code"] = meta.get("exit_code")
            elif meta_status:
                task["state"] = meta_status
            if meta.get("pid") is not None:
                task["pid"] = meta.get("pid")
            readable = _extract_readable_stdout(status_res.get("stdout_tail"), status_res.get("last_message"))
            if readable:
                task["last_message"] = readable
            updated += 1
        return run_meta, updated

    @mcp.tool(name="code_squad_status")
    def code_squad_status(run_id: str, include_last_message: bool = True, options: dict[str, Any] | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_status", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            run_meta, _ = _refresh_task_states(run_id, run_meta, limit=None)
            _save_run(run_id, run_meta)

            dispatch = _dispatch_for_run(run_id)
            task_statuses: list[dict[str, Any]] = []
            debug_tasks: list[dict[str, Any]] = []
            counts: dict[str, int] = {}
            for task in run_meta.get("tasks", []):
                state = str(task.get("state") or "unknown")
                counts[state] = counts.get(state, 0) + 1
                readable = task.get("last_message")
                if include_last_message and not readable and task.get("job_id"):
                    status_res = dispatch.status(job_id=task.get("job_id"), include_last_message=True, stdout_max_bytes=1500, stderr_max_bytes=500)
                    readable = _extract_readable_stdout(status_res.get("stdout_tail"), status_res.get("last_message"))
                task_statuses.append(
                    {
                        "name": task.get("name"),
                        "slug": task.get("slug"),
                        "job_id": task.get("job_id"),
                        "status": state,
                        "last_message": readable if include_last_message else None,
                    }
                )
                if debug:
                    debug_tasks.append(
                        {
                            "name": task.get("name"),
                            "slug": task.get("slug"),
                            "job_id": task.get("job_id"),
                            "state": state,
                            "worktree": task.get("worktree"),
                            "pid": task.get("pid"),
                            "model": task.get("model") or run_meta.get("defaults", {}).get("model"),
                            "sandbox": task.get("sandbox") or run_meta.get("defaults", {}).get("sandbox"),
                            "approval_policy": task.get("approval_policy") or run_meta.get("defaults", {}).get("approval_policy"),
                            "last_message": readable if include_last_message else None,
                        }
                    )
            response: dict[str, Any] = {
                "run_id": run_id,
                "counts": counts,
                "tasks": task_statuses,
            }
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {
                    "trace_id": trace_id,
                    "elapsed_ms": elapsed_ms,
                    "tasks": debug_tasks,
                    "defaults": run_meta.get("defaults"),
                }
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_status", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_events")
    def code_squad_events(
        run_id: str,
        cursor: dict[str, int] | None = None,
        max_items: int = 100,
        max_bytes: int = 4000,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_events", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            dispatch = _dispatch_for_run(run_id)
            cursor_map = cursor or {}
            events_out: list[dict[str, Any]] = []
            next_cursor: dict[str, int] = {}
            has_more = False

            for task in run_meta.get("tasks", []):
                job_id = task.get("job_id")
                if not job_id:
                    continue
                start_offset = int(cursor_map.get(job_id, 0))
                ev_res = dispatch.events(job_id=job_id, cursor=start_offset, max_items=max_items - len(events_out), max_bytes=max_bytes)
                next_cursor[job_id] = ev_res.get("cursor", start_offset)
                for ev in ev_res.get("events", []):
                    events_out.append({"job_id": job_id, "event": _compact_event(ev)})
                    if len(events_out) >= max_items:
                        break
                if ev_res.get("has_more"):
                    has_more = True
                if len(events_out) >= max_items:
                    break

            response: dict[str, Any] = {
                "run_id": run_id,
                "events": events_out,
                "cursor": next_cursor,
                "has_more": has_more,
            }
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "cursor_in": cursor_map}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_events", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_collect")
    def code_squad_collect(run_id: str, options: dict[str, Any] | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_collect", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            results: list[dict[str, Any]] = []
            debug_results: list[dict[str, Any]] = []
            for task in run_meta.get("tasks", []):
                worktree = task.get("worktree")
                job_id = task.get("job_id")
                if not worktree:
                    entry = {"job_id": job_id, "name": task.get("name"), "slug": task.get("slug"), "status": "error", "error": "worktree missing", "touched_files": [], "patch": ""}
                    results.append(entry)
                    if debug:
                        debug_results.append({"job_id": job_id, "slug": task.get("slug"), "worktree": worktree, "state": task.get("state")})
                    continue
                worktree_path = Path(worktree)
                subprocess.run(["git", "add", "-N", "."], cwd=worktree_path, check=False, capture_output=True)
                diff_proc = subprocess.run(["git", "diff"], cwd=worktree_path, capture_output=True, text=True)
                files_proc = subprocess.run(
                    ["git", "diff", "--name-only"],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True,
                )
                results.append(
                    {
                        "job_id": job_id,
                        "name": task.get("name"),
                        "slug": task.get("slug"),
                        "patch": diff_proc.stdout,
                        "touched_files": [line for line in files_proc.stdout.splitlines() if line.strip()],
                        "status": "empty" if not diff_proc.stdout.strip() else "ok",
                        "state": task.get("state"),
                    }
                )
                if debug:
                    debug_results.append(
                        {
                            "job_id": job_id,
                            "slug": task.get("slug"),
                            "worktree": worktree,
                            "state": task.get("state"),
                            "finished_at": task.get("finished_at"),
                        }
                    )
            response: dict[str, Any] = {"run_id": run_id, "results": results}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "tasks": debug_results}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_collect", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_verify")
    def code_squad_verify(run_id: str, job_id: str | None = None, options: dict[str, Any] | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_verify", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            targets = [t for t in run_meta.get("tasks", []) if (job_id is None or t.get("job_id") == job_id)]
            results: list[dict[str, Any]] = []
            debug_results: list[dict[str, Any]] = []
            for task in targets:
                worktree = task.get("worktree")
                if not worktree:
                    entry = {"job_id": task.get("job_id"), "name": task.get("name"), "slug": task.get("slug"), "state": task.get("state"), "compileall": {"exit_code": None}, "pytest": None, "message": "worktree missing"}
                    results.append(entry)
                    continue
                worktree_path = Path(worktree)
                compile_proc = subprocess.run(
                    [sys.executable, "-m", "compileall", "-q", "."],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True,
                )
                pytest_result: dict[str, Any] | None = None
                tests_dir = worktree_path / "tests"
                if tests_dir.exists():
                    pytest_proc = subprocess.run(
                        [sys.executable, "-m", "pytest", "-q"],
                        cwd=worktree_path,
                        capture_output=True,
                        text=True,
                    )
                    pytest_result = {"exit_code": pytest_proc.returncode, "stdout": pytest_proc.stdout, "stderr": pytest_proc.stderr}
                compile_exit = compile_proc.returncode
                pytest_exit = pytest_result.get("exit_code") if pytest_result is not None else None
                summary_parts = [f"compileall={'ok' if compile_exit == 0 else 'failed'}"]
                if pytest_result is not None:
                    summary_parts.append(f"pytest={'ok' if pytest_exit == 0 else 'failed'}")
                results.append(
                    {
                        "job_id": task.get("job_id"),
                        "name": task.get("name"),
                        "slug": task.get("slug"),
                        "state": task.get("state"),
                        "compileall": {"exit_code": compile_exit},
                        "pytest": {"exit_code": pytest_exit} if pytest_result is not None else None,
                        "message": "; ".join(summary_parts),
                    }
                )
                if debug:
                    debug_results.append(
                        {
                            "job_id": task.get("job_id"),
                            "slug": task.get("slug"),
                            "worktree": worktree,
                            "compileall": {"stdout": compile_proc.stdout, "stderr": compile_proc.stderr},
                            "pytest": pytest_result,
                        }
                    )
            response: dict[str, Any] = {"run_id": run_id, "results": results}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "tasks": debug_results}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_verify", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_tick")
    def code_squad_tick(run_id: str, max_starts: int = 2, max_updates: int = 5, options: dict[str, Any] | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_tick", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            enqueued = 0
            now = utc_now_iso()
            for task in run_meta.get("tasks", []):
                if enqueued >= max_starts:
                    break
                if task.get("state") == "queued" and not task.get("worker_enqueued_at"):
                    worker.enqueue(run_id, task.get("slug"))
                    task["worker_enqueued_at"] = now
                    enqueued += 1
            run_meta, refreshed = _refresh_task_states(run_id, run_meta, limit=max_updates)
            _save_run(run_id, run_meta)

            counts: dict[str, int] = {}
            for task in run_meta.get("tasks", []):
                state = str(task.get("state") or "unknown")
                counts[state] = counts.get(state, 0) + 1
            response: dict[str, Any] = {"run_id": run_id, "enqueued": enqueued, "refreshed": refreshed, "counts": counts}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "queue": list(run_meta.get("queue", []))}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_tick", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_cancel")
    def code_squad_cancel(run_id: str, job_id: str | None = None, task_slug: str | None = None, options: dict[str, Any] | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_cancel", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            targets: list[dict[str, Any]] = []
            for task in run_meta.get("tasks", []):
                if job_id and task.get("job_id") == job_id:
                    targets.append(task)
                elif task_slug and task.get("slug") == task_slug:
                    targets.append(task)
                elif job_id is None and task_slug is None:
                    targets.append(task)
            dispatch = _dispatch_for_run(run_id)
            cancelled = 0
            for task in targets:
                state = task.get("state")
                if state in ("completed", "failed", "cancelled"):
                    continue
                if task.get("job_id") and state in ("running", "starting"):
                    dispatch.cancel(job_id=task.get("job_id"), reason="user_cancelled")
                task["state"] = "cancelled"
                task["finished_at"] = utc_now_iso()
                cancelled += 1
            _save_run(run_id, run_meta)
            response: dict[str, Any] = {"run_id": run_id, "cancelled": cancelled}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {
                    "trace_id": trace_id,
                    "elapsed_ms": elapsed_ms,
                    "targets": [{"slug": t.get("slug"), "job_id": t.get("job_id"), "state": t.get("state")} for t in targets],
                }
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_cancel", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_cleanup")
    def code_squad_cleanup(run_id: str, delete_run_artifacts: bool = False, options: dict[str, Any] | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        debug = _debug_enabled(options)
        elapsed_ms: int | None = None
        ops_log("code_squad_cleanup", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            repo_root = Path(run_meta.get("repo_root") or find_repo_root(Path("."))).resolve()
            _ = ensure_repo_subpath(repo_root, Path(run_meta.get("worktree_base") or repo_root / ".codex" / "code-squad" / "worktrees" / run_id))
            removed_worktrees = 0
            removed_paths: list[str] = []
            for task in run_meta.get("tasks", []):
                worktree = task.get("worktree")
                if not worktree:
                    continue
                try:
                    worktree_path = ensure_repo_subpath(repo_root, Path(worktree))
                except ValueError:
                    continue
                if worktree_path.exists():
                    subprocess.run(["git", "worktree", "remove", "-f", str(worktree_path)], cwd=repo_root, check=False, capture_output=True)
                    removed_worktrees += 1
                    if debug:
                        removed_paths.append(str(worktree_path))
            if delete_run_artifacts:
                run_dir = store.run_dir(run_id)
                try:
                    ensure_repo_subpath(repo_root, run_dir)
                except ValueError:
                    pass
                else:
                    if run_dir.exists():
                        for child in run_dir.glob("*"):
                            if child.is_file():
                                child.unlink(missing_ok=True)
                                if debug:
                                    removed_paths.append(str(child))
                            elif child.is_dir():
                                shutil.rmtree(child, ignore_errors=True)
                                if debug:
                                    removed_paths.append(str(child))
                            else:
                                child.unlink(missing_ok=True)
                                if debug:
                                    removed_paths.append(str(child))
                        run_dir.rmdir()
                        if debug:
                            removed_paths.append(str(run_dir))
            response: dict[str, Any] = {"run_id": run_id, "removed_worktrees": removed_worktrees, "deleted_run_artifacts": delete_run_artifacts}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "removed_paths": removed_paths}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_cleanup", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)
