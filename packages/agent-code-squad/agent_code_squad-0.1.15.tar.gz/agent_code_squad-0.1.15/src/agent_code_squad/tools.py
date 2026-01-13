from __future__ import annotations

import hashlib
import json
import queue
import re
import threading
import shutil
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from mcp.server.fastmcp import FastMCP

from .config import SquadConfig, resolve_config
from .context import RipgrepNotFound, build_context_pack
from .dispatch import CodexDispatch, DispatchConfig
from .event_utils import (
    EVENT_NOISE_TYPES,
    NOISE_EVENT_TYPES,
    NOISY_ITEM_TYPES,
    extract_patch_from_stdout as _extract_patch_from_stdout,
    iter_event_text as _iter_event_text,
)
from .ops_log import log as ops_log
from .paths import ensure_dir, ensure_repo_subpath, find_repo_root, safe_relpath, slugify
from .runner import BackgroundWorker, RunStore, DEFAULT_DEP_PATCH_MAX_BYTES
from .utils import truncate_text, utc_now_iso


def _extract_readable_stdout(stdout_tail: str | None, last_message: str | None, *, max_chars: int = 240) -> str | None:
    """
    Extract a short, human-readable "last message" from Codex JSONL stdout.

    Goal: reduce noise and avoid returning raw JSON blobs; prefer the last human sentence/line.
    """
    if not stdout_tail:
        if not last_message:
            return None
        text = str(last_message or "").strip()
        if not text:
            return None
        last_line = next((ln.strip() for ln in reversed(text.splitlines()) if ln.strip()), "")
        return truncate_text(last_line, max_chars) if last_line else None

    def _looks_like_diff_line(line: str) -> bool:
        s = str(line or "").lstrip()
        if not s:
            return True
        return s.startswith(("diff --git ", "index ", "--- ", "+++ ", "@@ ", "new file mode"))

    def _last_human_line(text: str) -> str | None:
        for ln in reversed(str(text or "").splitlines()):
            s = ln.strip()
            if not s:
                continue
            if s == "```" or s.startswith("```"):
                continue
            if _looks_like_diff_line(s):
                continue
            return s
        return None

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
            if "usage" in content and len(content.keys()) <= 2:
                return None
            if "item" in content and isinstance(content.get("item"), dict):
                item = content.get("item") or {}
                item_type = item.get("type")
                if isinstance(item_type, str) and item_type in NOISY_ITEM_TYPES:
                    return None
                if isinstance(item_type, str) and item_type in ("agent_message", "assistant_message"):
                    if "text" in item and isinstance(item.get("text"), str):
                        return item.get("text")
                    return _flatten(item)
            for key in ("message", "content", "text"):
                if key in content:
                    val = _flatten(content.get(key))
                    if val:
                        return val
            return None
        return str(content)

    raw_fallback: str | None = None
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
            if isinstance(event_type, str) and event_type in NOISE_EVENT_TYPES:
                continue

        text_val = _flatten(obj)
        if isinstance(text_val, str) and text_val.strip():
            # Avoid showing a raw diff as "message"; prefer the last human sentence/line.
            if "diff --git " in text_val:
                continue
            last_line = _last_human_line(text_val)
            if last_line:
                return truncate_text(last_line, max_chars)
        if raw_fallback is None:
            raw_fallback = candidate

    if raw_fallback:
        last_line = _last_human_line(raw_fallback) or raw_fallback.strip()
        return truncate_text(last_line, max_chars) if last_line else None

    if last_message:
        text = str(last_message or "").strip()
        last_line = _last_human_line(text) or (text.splitlines()[-1].strip() if text else "")
        return truncate_text(last_line, max_chars) if last_line else None
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
    return _compose_prompt_with_scope(task_prompt, context_pack, role=None, allow_globs=None, deny_globs=None, limits=None)


def _compose_prompt_with_scope(
    task_prompt: str,
    context_pack: dict[str, Any] | None,
    *,
    role: str | None,
    allow_globs: list[str] | None,
    deny_globs: list[str] | None,
    limits: dict[str, Any] | None,
) -> str:
    segments = [
        "You are a focused code-writing subagent. Produce git-style patches only, avoid speculation, and keep output minimal.",
        f"Role: {role.strip()}" if isinstance(role, str) and role.strip() else None,
        f"Subtask: {task_prompt.strip()}",
    ]
    scope_lines: list[str] = [
        "Rules:",
        "- Output MUST be a git-style patch (diff) only.",
        "- Keep changes minimal and directly related to the subtask.",
        "- Do NOT assume files exist; only touch/refer to files that you can see in the repo and include in the patch.",
    ]
    if allow_globs:
        scope_lines.append(f"- Allowed paths (allow_globs): {allow_globs}")
        scope_lines.append("- Do NOT modify files outside allow_globs.")
    if deny_globs:
        scope_lines.append(f"- Denied paths (deny_globs): {deny_globs}")
        scope_lines.append("- NEVER modify deny_globs paths.")
    if limits:
        scope_lines.append(f"- Limits: {limits}")
        if limits.get("max_touched_files") is not None:
            scope_lines.append("- Do NOT touch more than max_touched_files files.")
        if limits.get("max_patch_bytes") is not None:
            scope_lines.append("- Keep the patch under max_patch_bytes bytes.")
    segments.append("\n".join(scope_lines))
    ctx_text = _format_context(context_pack)
    if ctx_text:
        segments.append(ctx_text)
    segments.append("Return a git-style patch only. No prose, no Markdown fences.")
    return "\n\n".join(seg for seg in segments if seg)


def register_tools(mcp: FastMCP, *, config: SquadConfig) -> None:
    app_id = "agent-code-squad"
    store = RunStore(config.dispatch_dir)
    worker = BackgroundWorker(store, verbosity=config.verbosity, concurrency=config.worker_concurrency)

    context_pack_cache_dir = ensure_dir(Path(config.dispatch_dir) / "context_packs")
    finalize_queue: queue.Queue[str] = queue.Queue()
    finalize_lock = threading.Lock()
    finalize_enqueued: set[str] = set()

    def _timeline_path(run_id: str) -> Path:
        return ensure_dir(store.run_dir(run_id) / "artifacts") / "timeline.jsonl"

    def _timeline_append(run_id: str, event: str, **fields: Any) -> None:
        payload = {"ts": utc_now_iso(), "event": event, **{k: v for k, v in fields.items() if v is not None}}
        try:
            with _timeline_path(run_id).open("a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except OSError:
            return

    def _timeline_tail(run_id: str, *, max_items: int = 8) -> list[dict[str, Any]]:
        path = _timeline_path(run_id)
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except FileNotFoundError:
            return []
        out: list[dict[str, Any]] = []
        for line in lines[-max(1, int(max_items or 0)) :]:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict):
                out.append(obj)
        return out

    def _enqueue_finalize(run_id: str) -> None:
        with finalize_lock:
            if run_id in finalize_enqueued:
                return
            finalize_enqueued.add(run_id)
        finalize_queue.put(run_id)
        _timeline_append(run_id, "finalize.enqueued")

    def _dispatch_for_run(run_id: str) -> CodexDispatch:
        run_dir = store.run_dir(run_id)
        jobs_dir = ensure_dir(run_dir / "jobs")
        return CodexDispatch(DispatchConfig(jobs_dir=jobs_dir, verbosity=config.verbosity))

    def _effective_config_for_cwd(cwd: str) -> SquadConfig:
        """
        Resolve per-repo configuration using the caller-provided cwd, while keeping
        the server's dispatch_dir/verbosity/worker_concurrency stable.
        """
        repo_root = find_repo_root(Path(cwd))
        return resolve_config(
            dispatch_dir=str(config.dispatch_dir),
            verbosity=config.verbosity,
            worker_concurrency=config.worker_concurrency,
            cwd=str(repo_root),
        )

    def _update_run(run_id: str, updater) -> dict[str, Any] | None:
        return store.update(run_id, updater)

    def _load_run(run_id: str) -> dict[str, Any] | None:
        return store.load(run_id)

    def _save_run(run_id: str, meta: dict[str, Any]) -> None:
        store.save(run_id, meta)

    def _coerce_options(options: Any | None) -> dict[str, Any]:
        return options if isinstance(options, dict) else {}

    def _debug_enabled(options: Any | None) -> bool:
        return bool(_coerce_options(options).get("debug"))

    def _resolve_auto_context_pack(opts: dict[str, Any], effective_config: SquadConfig) -> dict[str, Any] | None:
        """
        Resolve auto context pack configuration using the same rules as code_squad_run
        so preflight and execution stay in sync.
        """
        base_auto = getattr(effective_config, "default_auto_context_pack", None)
        auto_context_pack: dict[str, Any] | None = None
        if "auto_context_pack" in opts:
            raw_auto = opts.get("auto_context_pack")
            if raw_auto is False or raw_auto is None:
                auto_context_pack = None
            elif isinstance(raw_auto, dict):
                merged: dict[str, Any] = dict(base_auto) if isinstance(base_auto, dict) else {}
                merged.update(raw_auto)
                auto_context_pack = merged if _coerce_bool(merged.get("enabled")) is not False else None
        else:
            if isinstance(base_auto, dict) and _coerce_bool(base_auto.get("enabled")) is not False:
                auto_context_pack = dict(base_auto)
        return auto_context_pack

    def _sha256_json(payload: dict[str, Any]) -> str:
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def _extract_glob_prefixes(globs: list[str] | None) -> list[str]:
        if not globs:
            return []
        prefixes: list[str] = []
        for raw in globs:
            if not isinstance(raw, str):
                continue
            s = _normalize_relpath(raw.strip())
            if not s:
                continue
            wild_idx = min([i for i in (s.find("*"), s.find("?"), s.find("[")) if i != -1] or [len(s)])
            prefix = s[:wild_idx].rstrip("/")
            if not prefix:
                continue
            if "/" in prefix:
                prefix = prefix.rsplit("/", 1)[0]
            prefix = prefix.strip("/")
            if not prefix or prefix.startswith(".."):
                continue
            if prefix not in prefixes:
                prefixes.append(prefix)
        return prefixes

    def _cached_context_pack(
        *,
        cwd: str,
        query: str,
        hints: list[str],
        glob: str,
        allow_globs: list[str] | None,
        deny_globs: list[str] | None,
        max_files: int,
        max_snippets: int,
        max_total_chars: int,
    ) -> dict[str, Any]:
        cache_key = {
            "cwd_root": str(find_repo_root(Path(cwd))),
            "query": query,
            "hints": [h for h in hints if isinstance(h, str) and h.strip()],
            "glob": glob,
            "allow_globs": allow_globs or [],
            "deny_globs": deny_globs or [],
            "max_files": int(max_files),
            "max_snippets": int(max_snippets),
            "max_total_chars": int(max_total_chars),
        }
        key_hash = _sha256_json(cache_key)
        cache_path = context_pack_cache_dir / f"{key_hash}.json"
        if cache_path.exists():
            try:
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                if isinstance(cached, dict) and isinstance(cached.get("snippets"), list):
                    return cached
            except (OSError, json.JSONDecodeError):
                pass

        pack = build_context_pack(
            cwd=cwd,
            query=query,
            hints=hints,
            glob=glob,
            allow_globs=allow_globs,
            deny_globs=deny_globs,
            max_files=max_files,
            max_snippets=max_snippets,
            max_total_chars=max_total_chars,
        )
        try:
            cache_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
        except OSError:
            pass
        return pack

    def _utc_now() -> datetime:
        return datetime.now(timezone.utc)

    def _parse_utc_datetime(value: Any) -> datetime | None:
        if not isinstance(value, str) or not value.strip():
            return None
        raw = value.strip()
        try:
            dt = datetime.fromisoformat(raw)
        except ValueError:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _is_failed_like(state: str | None) -> bool:
        return str(state or "").lower() in ("failed", "timeout", "blocked", "cancelled")

    def _is_terminal_state(state: str | None) -> bool:
        return str(state or "").lower() in ("completed", "failed", "cancelled", "timeout", "blocked")

    def _compute_progress(run_meta: dict[str, Any]) -> dict[str, Any]:
        tasks = run_meta.get("tasks") or []
        counts: dict[str, int] = {}
        terminal = 0
        failed_like = 0
        for task in tasks:
            state = str((task or {}).get("state") or "unknown")
            counts[state] = counts.get(state, 0) + 1
            if _is_terminal_state(state):
                terminal += 1
            if _is_failed_like(state):
                failed_like += 1
        total = len(tasks)
        active = total - terminal
        return {
            "total": total,
            "terminal": terminal,
            "active": active,
            "failed_like": failed_like,
            "counts": counts,
        }

    def _dependency_status(task: dict[str, Any], task_map: dict[str, dict[str, Any]]) -> str:
        depends_on = task.get("depends_on") if isinstance(task.get("depends_on"), list) else []
        if not depends_on:
            return "ready"
        for dep in depends_on:
            dep_task = task_map.get(dep)
            if not isinstance(dep_task, dict):
                return "blocked"
            dep_state = str(dep_task.get("state") or "").lower()
            if dep_state in ("failed", "cancelled", "timeout", "blocked"):
                return "blocked"
            if dep_state != "completed":
                return "waiting"
        return "ready"

    def _dependency_block_details(task: dict[str, Any], task_map: dict[str, dict[str, Any]]) -> list[dict[str, str]]:
        depends_on = task.get("depends_on") if isinstance(task.get("depends_on"), list) else []
        details: list[dict[str, str]] = []
        for dep in depends_on:
            dep_task = task_map.get(dep)
            if not isinstance(dep_task, dict):
                details.append({"slug": str(dep), "state": "missing"})
                continue
            dep_state = str(dep_task.get("state") or "unknown")
            if dep_state.lower() in ("failed", "cancelled", "timeout", "blocked"):
                details.append({"slug": str(dep), "state": dep_state})
        return details

    def _dependency_cycle_nodes(tasks: list[dict[str, Any]]) -> set[str]:
        """
        Return slugs involved in dependency cycles (within known tasks only).
        """
        task_map = {str(t.get("slug") or ""): t for t in tasks if isinstance(t, dict) and t.get("slug")}
        visiting: set[str] = set()
        visited: set[str] = set()
        stack: list[str] = []
        in_cycle: set[str] = set()

        def dfs(node: str) -> None:
            visiting.add(node)
            stack.append(node)
            depends_on = task_map.get(node, {}).get("depends_on")
            deps = depends_on if isinstance(depends_on, list) else []
            for dep in deps:
                dep_slug = str(dep or "").strip()
                if not dep_slug or dep_slug not in task_map:
                    continue
                if dep_slug in visiting:
                    try:
                        idx = stack.index(dep_slug)
                    except ValueError:
                        idx = 0
                    in_cycle.update(stack[idx:])
                    in_cycle.add(dep_slug)
                    continue
                if dep_slug not in visited:
                    dfs(dep_slug)
            stack.pop()
            visiting.discard(node)
            visited.add(node)

        for slug in task_map.keys():
            if slug in visited:
                continue
            dfs(slug)
        return in_cycle

    def _enqueue_ready_tasks(run_id: str, run_meta: dict[str, Any], *, max_starts: int | None = None) -> int:
        """
        Enqueue queued tasks whose dependencies are satisfied. Tasks with failed deps become blocked.
        """
        task_map = {str(t.get("slug") or ""): t for t in run_meta.get("tasks", []) if t.get("slug")}
        enqueued = 0
        now = utc_now_iso()
        for task in run_meta.get("tasks", []):
            if max_starts is not None and enqueued >= max(0, int(max_starts)):
                break
            if task.get("state") != "queued" or task.get("worker_enqueued_at"):
                continue
            status = _dependency_status(task, task_map)
            if status == "blocked":
                task["state"] = "blocked"
                details = _dependency_block_details(task, task_map)
                task["error"] = "dependencies blocked" if not details else f"dependencies blocked: {details}"
                task["finished_at"] = utc_now_iso()
                continue
            if status == "waiting":
                continue
            worker.enqueue(run_id, task.get("slug"))
            task["worker_enqueued_at"] = now
            enqueued += 1
        return enqueued

    def _artifact_paths_for_slug(run_dir: Path, slug: str) -> dict[str, str]:
        return {
            "collect_patch": str(run_dir / "artifacts" / "collect" / f"{slug}.patch"),
            "collect_files": str(run_dir / "artifacts" / "collect" / f"{slug}.files.json"),
            "verify": str(run_dir / "artifacts" / "verify" / f"{slug}.json"),
            "scope": str(run_dir / "artifacts" / "scope" / f"{slug}.json"),
        }

    def _write_run_index(run_meta: dict[str, Any], *, extra: dict[str, Any] | None = None) -> Path:
        run_id = str(run_meta.get("id") or "")
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
        ensure_dir(run_dir / "artifacts")
        index_path = run_dir / "artifacts" / "index.json"
        tasks_out: list[dict[str, Any]] = []
        for task in run_meta.get("tasks", []):
            slug = str(task.get("slug") or task.get("job_id") or "task")
            tasks_out.append(
                {
                    "name": task.get("name"),
                    "slug": task.get("slug"),
                    "role": task.get("role"),
                    "depends_on": task.get("depends_on"),
                    "job_id": task.get("job_id"),
                    "state": task.get("state"),
                    "error": task.get("error"),
                    "scope_name": task.get("scope_name"),
                    "allow_globs": task.get("allow_globs"),
                    "deny_globs": task.get("deny_globs"),
                    "artifacts": _artifact_paths_for_slug(run_dir, slug),
                }
            )
        payload: dict[str, Any] = {
            "run_id": run_id,
            "created_at": run_meta.get("created_at"),
            "repo_root": run_meta.get("repo_root"),
            "dispatch_base": run_meta.get("dispatch_base"),
            "progress": _compute_progress(run_meta),
            "artifacts": {
                "run_dir": str(run_dir),
                "index": str(index_path),
                "report_json": str(run_dir / "artifacts" / "report.json"),
                "report_md": str(run_dir / "artifacts" / "report.md"),
                "cleanup_json": str(run_dir / "artifacts" / "cleanup.json"),
            },
            "tasks": tasks_out,
        }
        extra_artifacts = run_meta.get("artifacts")
        if isinstance(extra_artifacts, dict):
            payload["artifacts"].update({k: str(v) for k, v in extra_artifacts.items()})
        if run_meta.get("preflight"):
            payload["preflight"] = run_meta.get("preflight")
        if extra:
            payload.update(extra)
        index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return index_path

    def _write_preflight_doc(run_id: str, run_meta: dict[str, Any], preflight: dict[str, Any] | None) -> Path | None:
        if not preflight:
            return None
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
        docs_dir = ensure_dir(run_dir / "artifacts" / "docs")
        doc_path = docs_dir / "preflight.md"
        lines: list[str] = [
            f"# Preflight for run {run_id}",
            f"Decision: {preflight.get('decision')}",
            f"Generated: {utc_now_iso()}",
            "",
        ]
        for task in preflight.get("tasks", []):
            lines.append(f"## Task: {task.get('name') or 'task'}")
            slug_hint = task.get("slug")
            if slug_hint:
                lines.append(f"- Slug: {slug_hint}")
            scope = task.get("scope") or {}
            lines.append(f"- Scope allow_globs: {scope.get('allow_globs') or []}")
            lines.append(f"- Scope deny_globs: {scope.get('deny_globs') or []}")
            sample_paths = scope.get("sample_paths") or []
            lines.append(f"- Scope samples ({scope.get('sample_count', 0)}): {sample_paths[:8]}")
            context_detail = task.get("context") or {}
            lines.append(f"- Context mode: {context_detail.get('mode')}")
            if context_detail.get("hints") is not None:
                lines.append(f"- Context hints: {context_detail.get('hints')}")
            if context_detail.get("max_total_chars") is not None:
                lines.append(f"- Context budget: max_total_chars={context_detail.get('max_total_chars')}, max_files={context_detail.get('max_files')}, max_snippets={context_detail.get('max_snippets')}")
            prompt_rules = task.get("prompt_rules") or {}
            lines.append(f"- Prompt rules: patch_only={prompt_rules.get('patch_only')}, acceptance={prompt_rules.get('acceptance')}, info_request={prompt_rules.get('info_request')}")
            if task.get("questions"):
                lines.append(f"- Questions: {task.get('questions')}")
            lines.append("")
        try:
            doc_path.write_text("\n".join(lines), encoding="utf-8")
        except OSError:
            return None
        return doc_path

    def _normalize_relpath(path: str) -> str:
        normalized = str(path or "").replace("\\", "/")
        while normalized.startswith("./"):
            normalized = normalized[2:]
        return normalized.lstrip("/")

    def _parse_globs(value: Any) -> list[str] | None:
        if not isinstance(value, list):
            return None
        globs: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                globs.append(_normalize_relpath(item.strip()))
        return globs or None

    def _matches_any(path: str, globs: list[str] | None) -> bool:
        if not globs:
            return False
        rel = _normalize_relpath(path)
        rel_path = PurePosixPath(rel)
        return any(rel_path.match(pat) for pat in globs)

    def _coerce_bool(value: Any) -> bool | None:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            v = value.strip().lower()
            if v in ("true", "1", "yes", "y", "on"):
                return True
            if v in ("false", "0", "no", "n", "off"):
                return False
        return None

    def _sanitize_context_pack(
        context_pack: dict[str, Any] | None,
        *,
        allow_globs: list[str] | None,
        deny_globs: list[str] | None,
    ) -> tuple[dict[str, Any] | None, list[str]]:
        if not context_pack:
            return None, []
        snippets = context_pack.get("snippets")
        if not isinstance(snippets, list) or not snippets:
            return context_pack, []
        kept: list[dict[str, Any]] = []
        removed: list[str] = []
        for snip in snippets:
            if not isinstance(snip, dict):
                continue
            path = str(snip.get("path") or "").strip()
            if not path:
                continue
            rel = _normalize_relpath(path)
            if allow_globs and not _matches_any(rel, allow_globs):
                removed.append(rel)
                continue
            if deny_globs and _matches_any(rel, deny_globs):
                removed.append(rel)
                continue
            kept.append(snip)
        out = dict(context_pack)
        out["snippets"] = kept
        out["allow_globs"] = allow_globs or []
        out["deny_globs"] = deny_globs or []
        if removed:
            out["scope_filtered_paths"] = removed
        return out, removed

    def _check_prompt_rules(prompt: str) -> dict[str, Any]:
        text = (prompt or "").strip()
        lower = text.lower()
        patch_only = any(key in lower for key in ("patch only", "patch-only", "patches only", "diff --git", "apply_patch", "git diff"))
        acceptance = "验收" in text or "acceptance" in lower or "acceptance criteria" in lower or "done when" in lower or "tests" in lower
        info_request = any(key in lower for key in ("缺信息", "缺少信息", "ask", "提问", "clarify", "if missing", "if any detail is missing"))
        missing: list[str] = []
        if not patch_only:
            missing.append("add an explicit patch-only/diff instruction")
        if not acceptance:
            missing.append("list acceptance or expected verification")
        if not info_request:
            missing.append("state that missing details should be asked before coding")
        return {
            "patch_only": patch_only,
            "acceptance": acceptance,
            "info_request": info_request,
            "missing": missing,
            "ok": not missing,
            "length": len(text),
        }

    def _preflight_tasks(cwd: str, tasks: list[dict[str, Any]], opts: dict[str, Any]) -> dict[str, Any]:
        repo_root = find_repo_root(Path(cwd))
        effective_config = _effective_config_for_cwd(cwd)
        auto_context_pack = _resolve_auto_context_pack(opts, effective_config)
        scope_sample_limit = max(5, int(opts.get("preflight_scope_sample") or 32))
        questions: list[str] = []
        warnings: list[str] = []
        task_reports: list[dict[str, Any]] = []

        for idx, task in enumerate(tasks):
            name = str(task.get("name") or f"task-{idx+1}")
            prompt = str(task.get("prompt") or "")
            allow_globs = _parse_globs(task.get("allow_globs"))
            deny_globs = _parse_globs(task.get("deny_globs"))
            scope_samples: list[str] = []
            scope_warning: str | None = None
            try:
                scope_samples = _rg_list_files(repo_root, allow_globs=allow_globs, deny_globs=deny_globs, limit=scope_sample_limit)
            except RipgrepNotFound as exc:
                scope_warning = str(exc)

            scope_issues: list[str] = []
            if allow_globs is None:
                scope_issues.append("allow_globs missing; scope is wide open")
            elif allow_globs and scope_samples == [] and scope_warning is None:
                scope_issues.append("allow_globs/deny_globs produced no sample files; confirm the scope")
            if allow_globs and any(pat in ("**/*", "*", "/**") for pat in allow_globs):
                scope_issues.append("allow_globs contains catch-all patterns; narrow the scope")
            if scope_warning:
                warnings.append(f"Task {name}: {scope_warning}")
                scope_issues.append("scope preview unavailable; ripgrep is required to validate allow/deny globs")

            context_pack = task.get("context_pack") if isinstance(task.get("context_pack"), dict) else None
            context_mode = "provided" if context_pack else ("auto" if auto_context_pack else "disabled")
            context_detail: dict[str, Any] = {"mode": context_mode}
            context_issues: list[str] = []
            if context_pack:
                snippets = context_pack.get("snippets") if isinstance(context_pack.get("snippets"), list) else []
                total_chars = sum(len(str(snip.get("text") or "")) for snip in snippets)
                context_detail.update({"snippets": len(snippets), "total_chars": total_chars})
                if total_chars > 60000:
                    context_issues.append(f"context pack text ({total_chars} chars) is very large; trim or rely on auto context")
            elif auto_context_pack:
                scope_name = str(task.get("scope_name") or "").strip()
                hints: list[str] = []
                auto_hints = auto_context_pack.get("hints")
                if isinstance(auto_hints, list):
                    hints.extend([str(h).strip() for h in auto_hints if str(h).strip()])
                if scope_name:
                    hints.append(scope_name)
                hints.extend(_extract_glob_prefixes(allow_globs))
                max_total_chars_val = int(auto_context_pack.get("max_total_chars", 20_000))
                context_detail.update(
                    {
                        "glob": auto_context_pack.get("glob") or "**/*",
                        "max_files": auto_context_pack.get("max_files", 12),
                        "max_snippets": auto_context_pack.get("max_snippets", 24),
                        "max_total_chars": max_total_chars_val,
                        "hints": hints,
                    }
                )
                if max_total_chars_val > 60000:
                    context_issues.append("auto_context_pack.max_total_chars is very high; reduce to keep context focused")
                if len(hints) > 12:
                    context_issues.append("auto_context_pack.hints is broad; trim to the smallest helpful set")
                if not hints and allow_globs is None:
                    context_issues.append("no hints or scope provided; context pack may pull unrelated files")
            else:
                context_issues.append("context pack disabled; confirm this is intentional for the task")

            prompt_rules = _check_prompt_rules(prompt)
            prompt_issues = [f"Prompt missing: {', '.join(prompt_rules['missing'])}"] if prompt_rules["missing"] else []

            task_questions = [f"Task {name}: {item}" for item in scope_issues + context_issues + prompt_issues]
            questions.extend(task_questions)

            task_reports.append(
                {
                    "name": name,
                    "scope": {
                        "allow_globs": allow_globs or [],
                        "deny_globs": deny_globs or [],
                        "sample_paths": scope_samples,
                        "sample_count": len(scope_samples),
                        "warning": scope_warning,
                        "issues": scope_issues,
                    },
                    "context": context_detail,
                    "prompt_rules": prompt_rules,
                    "questions": task_questions,
                }
            )

        needs_confirm = bool(questions)
        return {
            "ok": not needs_confirm,
            "needs_user_confirm": needs_confirm,
            "questions": questions,
            "tasks": task_reports,
            "warnings": warnings,
            "decision": "needs-confirmation" if needs_confirm else "auto-run",
            "timestamp": utc_now_iso(),
        }

    def _touched_files_from_patch(patch_text: str) -> list[str]:
        touched: list[str] = []
        for line in (patch_text or "").splitlines():
            if not line.startswith("diff --git "):
                continue
            parts = line.split(" ")
            if len(parts) < 4:
                continue
            b_path = parts[3]
            if b_path.startswith("b/"):
                rel = _normalize_relpath(b_path[2:])
                if rel and rel not in touched:
                    touched.append(rel)
        return touched

    def _normalize_effort(value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        effort = value.strip().lower()
        return effort if effort in ("low", "medium", "high") else None

    def _effort_rank(effort: str) -> int:
        return {"low": 1, "medium": 2, "high": 3}.get(str(effort or "").lower(), 2)

    def _rank_to_effort(rank: int) -> str:
        return "low" if rank <= 1 else ("medium" if rank == 2 else "high")

    def _apply_reasoning_effort_cap(
        extra_config: Any, *, options: dict[str, Any], task: dict[str, Any], effective_config: SquadConfig
    ) -> list[str]:
        """
        Enforce model_reasoning_effort <= configured max.
        - Default effort comes from server config.
        - Any existing model_reasoning_effort configs are removed and replaced.
        """
        requested = _normalize_effort(options.get("model_reasoning_effort") or options.get("reasoning_effort"))
        if requested is None:
            requested = _normalize_effort(task.get("model_reasoning_effort") or task.get("reasoning_effort"))
        if requested is None:
            requested = _normalize_effort(getattr(effective_config, "default_reasoning_effort", None)) or "medium"
        max_effort = _normalize_effort(getattr(effective_config, "max_reasoning_effort", None)) or "medium"
        effective_rank = min(_effort_rank(requested), _effort_rank(max_effort))
        effective = _rank_to_effort(effective_rank)

        base: list[str] = []
        if isinstance(extra_config, list):
            for item in extra_config:
                if not isinstance(item, str):
                    continue
                if "model_reasoning_effort" in item:
                    continue
                base.append(item)
        base.append(f'model_reasoning_effort="{effective}"')
        return base

    def _evaluate_scope(
        *,
        patch_text: str,
        scope_name: str | None,
        allow_globs: list[str] | None,
        deny_globs: list[str] | None,
        max_touched_files: int | None,
        max_patch_bytes: int | None,
        require_patch: bool,
    ) -> tuple[bool, dict[str, Any], list[str], int]:
        normalized_touched = _touched_files_from_patch(patch_text)
        patch_bytes = len((patch_text or "").encode("utf-8", errors="replace"))
        not_allowed = [p for p in normalized_touched if allow_globs and not _matches_any(p, allow_globs)]
        denied = [p for p in normalized_touched if deny_globs and _matches_any(p, deny_globs)]
        limits_violation: dict[str, Any] = {}
        if require_patch and not (patch_text or "").strip():
            limits_violation["require_patch"] = {"required": True, "actual": "empty"}
        if isinstance(max_touched_files, int) and max_touched_files > 0 and len(normalized_touched) > max_touched_files:
            limits_violation["max_touched_files"] = {"limit": max_touched_files, "actual": len(normalized_touched)}
        if isinstance(max_patch_bytes, int) and max_patch_bytes > 0 and patch_bytes > max_patch_bytes:
            limits_violation["max_patch_bytes"] = {"limit": max_patch_bytes, "actual": patch_bytes}
        scope_ok = not not_allowed and not denied and not limits_violation
        scope_payload = {
            "scope_name": scope_name,
            "allow_globs": allow_globs,
            "deny_globs": deny_globs,
            "touched_files": normalized_touched,
            "limits": {"require_patch": require_patch, "max_touched_files": max_touched_files, "max_patch_bytes": max_patch_bytes, "patch_bytes": patch_bytes},
            "violations": {"not_allowed": not_allowed, "denied": denied, "limits": limits_violation},
            "ok": scope_ok,
        }
        return scope_ok, scope_payload, normalized_touched, patch_bytes

    def _persist_collect_artifacts(
        *,
        run_dir: Path,
        slug: str,
        patch_text: str,
        touched_files: list[str],
        scope_payload: dict[str, Any] | None,
    ) -> tuple[Path, Path, Path]:
        artifacts_dir = ensure_dir(run_dir / "artifacts" / "collect")
        scope_dir = ensure_dir(run_dir / "artifacts" / "scope")
        patch_path = artifacts_dir / f"{slug}.patch"
        touched_path = artifacts_dir / f"{slug}.files.json"
        scope_path = scope_dir / f"{slug}.json"
        patch_path.write_text(patch_text or "", encoding="utf-8")
        touched_path.write_text(json.dumps(touched_files or [], ensure_ascii=False), encoding="utf-8")
        if scope_payload is not None:
            payload = dict(scope_payload)
            payload["path"] = str(scope_path)
            scope_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return patch_path, touched_path, scope_path

    def _collect_run(run_id: str, run_meta: dict[str, Any], *, include_patch: bool, debug: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
        results: list[dict[str, Any]] = []
        debug_results: list[dict[str, Any]] = []
        for task in run_meta.get("tasks", []):
            job_id = task.get("job_id")
            slug = task.get("slug") or job_id or "task"
            allow_globs = _parse_globs(task.get("allow_globs"))
            deny_globs = _parse_globs(task.get("deny_globs"))
            patch_text = ""
            patch_path = run_dir / "artifacts" / "collect" / f"{slug}.patch"
            touched_path = run_dir / "artifacts" / "collect" / f"{slug}.files.json"
            if patch_path.exists():
                try:
                    cached = patch_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    cached = ""
                if "diff --git " in cached or cached.strip():
                    patch_text = cached
            if not patch_text:
                if job_id:
                    stdout_jsonl = run_dir / "jobs" / str(job_id) / "stdout.jsonl"
                    patch_text = _extract_patch_from_stdout(stdout_jsonl)
            normalized_touched: list[str] = []
            if touched_path.exists():
                try:
                    cached_files = json.loads(touched_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    cached_files = None
                if isinstance(cached_files, list) and cached_files:
                    normalized_touched = [_normalize_relpath(str(p)) for p in cached_files if str(p).strip()]
            if not normalized_touched:
                normalized_touched = _touched_files_from_patch(patch_text)
            max_touched_files = task.get("max_touched_files")
            max_patch_bytes = task.get("max_patch_bytes")
            require_patch = bool(task.get("require_patch", False))
            scope_ok, scope_payload, normalized_touched, patch_bytes = _evaluate_scope(
                patch_text=patch_text,
                scope_name=task.get("scope_name"),
                allow_globs=allow_globs,
                deny_globs=deny_globs,
                max_touched_files=max_touched_files if isinstance(max_touched_files, int) else None,
                max_patch_bytes=max_patch_bytes if isinstance(max_patch_bytes, int) else None,
                require_patch=require_patch,
            )
            scope_artifact: dict[str, Any] | None = None
            if allow_globs or deny_globs or not scope_ok or (scope_payload.get("violations") or {}).get("limits"):
                scope_artifact = dict(scope_payload)
            _persist_collect_artifacts(run_dir=run_dir, slug=str(slug), patch_text=patch_text, touched_files=normalized_touched, scope_payload=scope_artifact)
            if scope_artifact is not None:
                scope_artifact["path"] = str(run_dir / "artifacts" / "scope" / f"{slug}.json")
            _timeline_append(run_id, "collect.task", slug=task.get("slug"), ok=scope_ok, touched_files=len(normalized_touched), patch_bytes=patch_bytes)
            entry: dict[str, Any] = {
                "job_id": job_id,
                "name": task.get("name"),
                "slug": task.get("slug"),
                "patch_path": str(run_dir / "artifacts" / "collect" / f"{slug}.patch"),
                "touched_files_path": str(run_dir / "artifacts" / "collect" / f"{slug}.files.json"),
                "touched_files": normalized_touched,
                "status": "empty" if not patch_text.strip() else "ok",
                "state": task.get("state"),
                "scope": scope_artifact if (allow_globs or deny_globs or not scope_ok) else None,
            }
            if include_patch:
                entry["patch"] = patch_text
            results.append(entry)
            if debug:
                debug_results.append(
                    {
                        "job_id": job_id,
                        "slug": task.get("slug"),
                        "worktree": task.get("worktree"),
                        "state": task.get("state"),
                        "finished_at": task.get("finished_at"),
                    }
                )
        return results, debug_results

    def _cleanup_worktrees_for_run(
        run_meta: dict[str, Any],
        *,
        keep_failed: bool,
    ) -> dict[str, Any]:
        repo_root = Path(run_meta.get("repo_root") or find_repo_root(Path("."))).resolve()
        removed: list[dict[str, Any]] = []
        kept: list[dict[str, Any]] = []
        for task in run_meta.get("tasks", []):
            state = str(task.get("state") or "unknown")
            worktree = task.get("worktree")
            slug = task.get("slug") or task.get("job_id") or "task"
            if keep_failed and _is_failed_like(state):
                kept.append({"slug": slug, "state": state, "path": worktree, "reason": "keep_failed"})
                continue
            if not worktree:
                kept.append({"slug": slug, "state": state, "path": None, "reason": "no_worktree"})
                continue
            try:
                worktree_path = ensure_repo_subpath(repo_root, Path(worktree))
            except ValueError:
                kept.append({"slug": slug, "state": state, "path": worktree, "reason": "worktree_outside_repo_root"})
                continue
            if not worktree_path.exists():
                kept.append({"slug": slug, "state": state, "path": str(worktree_path), "reason": "worktree_missing_on_disk"})
                continue
            subprocess.run(["git", "worktree", "remove", "-f", str(worktree_path)], cwd=repo_root, check=False, capture_output=True)
            removed.append({"slug": slug, "state": state, "path": str(worktree_path)})
        return {"removed": removed, "kept": kept}

    def _parse_verify_commands(options: dict[str, Any] | None) -> list[list[str]] | None:
        if not options:
            return None
        raw = options.get("commands")
        if not isinstance(raw, list):
            return None
        parsed: list[list[str]] = []
        for cmd in raw:
            if isinstance(cmd, list) and cmd:
                parsed.append([str(part) for part in cmd])
        return parsed if parsed else None

    def _verify_run(run_id: str, run_meta: dict[str, Any], *, job_id: str | None, options: dict[str, Any] | None, debug: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
        artifacts_dir = ensure_dir(run_dir / "artifacts" / "verify")
        commands = _parse_verify_commands(options)
        max_output_chars = int(options.get("max_output_chars", 4000)) if options else 4000
        targets = [t for t in run_meta.get("tasks", []) if (job_id is None or t.get("job_id") == job_id)]
        results: list[dict[str, Any]] = []
        debug_results: list[dict[str, Any]] = []

        for task in targets:
            worktree = task.get("worktree")
            slug = task.get("slug") or task.get("job_id") or "task"
            verify_path = artifacts_dir / f"{slug}.json"
            result_entry: dict[str, Any] = {
                "job_id": task.get("job_id"),
                "name": task.get("name"),
                "slug": task.get("slug"),
                "state": task.get("state"),
            }
            scope = task.get("scope") if isinstance(task.get("scope"), dict) else None
            if scope and scope.get("ok") is False:
                result_entry.update({"compileall": None, "pytest": None, "commands": None, "message": "skipped due to scope violations", "scope": scope})
                results.append(result_entry)
                verify_path.write_text(json.dumps(result_entry, ensure_ascii=False, indent=2), encoding="utf-8")
                continue
            if not worktree:
                result_entry.update({"compileall": {"exit_code": None}, "pytest": None, "commands": commands, "message": "worktree missing"})
                results.append(result_entry)
                verify_path.write_text(json.dumps(result_entry, ensure_ascii=False, indent=2), encoding="utf-8")
                continue

            worktree_path = Path(worktree)
            debug_entry: dict[str, Any] = {"job_id": task.get("job_id"), "slug": task.get("slug"), "worktree": worktree}

            if commands is not None:
                cmd_results: list[dict[str, Any]] = []
                debug_cmd_results: list[dict[str, Any]] = []
                for cmd in commands:
                    proc = subprocess.run(cmd, cwd=worktree_path, capture_output=True, text=True)
                    cmd_results.append(
                        {
                            "command": cmd,
                            "exit_code": proc.returncode,
                            "stdout_tail": truncate_text(proc.stdout or "", max_output_chars),
                            "stderr_tail": truncate_text(proc.stderr or "", max_output_chars),
                        }
                    )
                    if debug:
                        debug_cmd_results.append(
                            {
                                "command": cmd,
                                "exit_code": proc.returncode,
                                "stdout": proc.stdout,
                                "stderr": proc.stderr,
                            }
                        )
                message = "commands=" + ("ok" if all(cr.get("exit_code") == 0 for cr in cmd_results) else "failed")
                result_entry.update({"commands": cmd_results, "compileall": None, "pytest": None, "message": message})
                if debug:
                    debug_entry.update({"commands": debug_cmd_results})
            else:
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
                result_entry.update(
                    {
                        "compileall": {"exit_code": compile_exit},
                        "pytest": {"exit_code": pytest_exit} if pytest_result is not None else None,
                        "commands": None,
                        "message": "; ".join(summary_parts),
                    }
                )
                debug_entry.update({"compileall": {"stdout": compile_proc.stdout, "stderr": compile_proc.stderr}, "pytest": pytest_result})

            verify_path.write_text(json.dumps(result_entry, ensure_ascii=False, indent=2), encoding="utf-8")
            results.append(result_entry)
            if debug:
                debug_results.append(debug_entry)

        return results, debug_results

    def _finalize_run(run_id: str) -> None:
        """
        Background finalizer: waits for all tasks to reach terminal states, then runs collect/verify/cleanup and writes index.
        This is deliberately asynchronous to avoid client tool-call timeouts (often ~60s).
        """
        run_meta = _load_run(run_id)
        if not run_meta:
            return

        finalize_cfg = run_meta.get("finalize") if isinstance(run_meta.get("finalize"), dict) else {}
        enabled = bool(finalize_cfg.get("enabled", True))
        if not enabled:
            return
        state = str(finalize_cfg.get("state") or "").lower()
        if state in ("completed", "failed", "cancelled"):
            return

        def _mark(state_val: str, **extra_fields: Any) -> None:
            def updater(meta: dict[str, Any]) -> dict[str, Any]:
                finalize = meta.get("finalize") if isinstance(meta.get("finalize"), dict) else {}
                finalize.update({"state": state_val, **extra_fields})
                meta["finalize"] = finalize
                return meta

            _update_run(run_id, updater)

        _mark("running", started_at=utc_now_iso())
        _timeline_append(run_id, "finalize.start")

        poll_interval = float(finalize_cfg.get("poll_interval") or 1.0)
        max_wait_seconds = int(finalize_cfg.get("max_wait_seconds") or 3600)
        verify_enabled = bool(finalize_cfg.get("verify", False))
        cleanup_enabled = bool(finalize_cfg.get("cleanup", True))
        keep_failed = bool(finalize_cfg.get("keep_failed", True))
        deadline = time.monotonic() + max(1, max_wait_seconds)

        last_progress: dict[str, Any] | None = None
        while True:
            run_meta = _load_run(run_id)
            if not run_meta:
                _mark("failed", finished_at=utc_now_iso(), error="run not found")
                _timeline_append(run_id, "finalize.error", message="run not found")
                return
            run_meta, _ = _refresh_task_states(run_id, run_meta, limit=None)
            _enqueue_ready_tasks(run_id, run_meta, max_starts=None)
            _save_run(run_id, run_meta)
            progress = _compute_progress(run_meta)
            last_progress = progress
            states = [t.get("state") for t in run_meta.get("tasks", [])]
            if states and all(_is_terminal_state(s) for s in states):
                break
            if time.monotonic() >= deadline:
                _mark("failed", finished_at=utc_now_iso(), error="finalize timeout")
                _timeline_append(run_id, "finalize.timeout", progress=progress)
                return
            time.sleep(max(0.2, poll_interval))

        final_meta = _load_run(run_id) or {"tasks": []}
        collect_results, _ = _collect_run(run_id, final_meta, debug=False)
        _timeline_append(run_id, "finalize.collect", tasks=len(collect_results))

        scope_violations: list[dict[str, Any]] = []
        for task in final_meta.get("tasks", []):
            slug = task.get("slug")
            task_collect = next((r for r in collect_results if r.get("slug") == slug), None)
            scope = task_collect.get("scope") if isinstance(task_collect, dict) else None
            if isinstance(scope, dict):
                task["scope"] = scope
                if scope.get("ok") is False:
                    scope_violations.append({"slug": slug, "job_id": task.get("job_id"), "violations": scope.get("violations"), "path": scope.get("path")})
                    task["state"] = "failed"
                    task["error"] = f"scope violation: {scope.get('violations')}"
        _save_run(run_id, final_meta)

        verify_results: list[dict[str, Any]] | None = None
        if verify_enabled:
            verify_results, _ = _verify_run(run_id, final_meta, job_id=None, options=finalize_cfg if isinstance(finalize_cfg, dict) else None, debug=False)
            _timeline_append(run_id, "finalize.verify", tasks=len(verify_results))

        cleanup_summary: dict[str, Any] | None = None
        if cleanup_enabled:
            cleanup = _cleanup_worktrees_for_run(final_meta, keep_failed=keep_failed)
            cleanup_summary = {"keep_failed": keep_failed, "removed": cleanup.get("removed", []), "kept": cleanup.get("kept", [])}
            run_dir = Path(final_meta.get("run_dir") or store.run_dir(run_id))
            cleanup_path = ensure_dir(run_dir / "artifacts") / "cleanup.json"
            cleanup_path.write_text(json.dumps(cleanup_summary, ensure_ascii=False, indent=2), encoding="utf-8")
            _timeline_append(run_id, "finalize.cleanup", removed=len(cleanup_summary["removed"]), kept=len(cleanup_summary["kept"]))

        counts: dict[str, int] = {}
        for task in final_meta.get("tasks", []):
            state_val = str(task.get("state") or "unknown")
            counts[state_val] = counts.get(state_val, 0) + 1

        status = "failed" if scope_violations else ("completed" if all(_is_terminal_state(t.get("state")) for t in final_meta.get("tasks", [])) else "timeout")
        index_path = _write_run_index(
            final_meta,
            extra={
                "finalize": {
                    "status": status,
                    "counts": counts,
                    "progress": last_progress,
                    "scope_violations": scope_violations,
                    "verify_enabled": verify_enabled,
                    "cleanup_enabled": cleanup_enabled,
                }
            },
        )
        _timeline_append(run_id, "finalize.done", status=status, index_path=str(index_path))
        _mark("completed", finished_at=utc_now_iso(), status=status, index_path=str(index_path))

    def _finalizer_loop() -> None:
        while True:
            run_id = finalize_queue.get()
            try:
                _finalize_run(run_id)
            finally:
                with finalize_lock:
                    finalize_enqueued.discard(run_id)

    threading.Thread(target=_finalizer_loop, name="code-squad-finalizer", daemon=True).start()

    @mcp.tool(name="code_squad_capabilities_get")
    def code_squad_capabilities_get(cwd: str | None = None, options: Any | None = None) -> dict[str, Any]:
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        effective = _effective_config_for_cwd(cwd) if cwd else config
        result: dict[str, Any] = {
            "server": {
                "name": app_id,
                "defaults": {
                    "model": effective.default_model,
                    "sandbox": effective.default_sandbox,
                    "approval_policy": effective.default_approval_policy,
                },
            },
            "tools": [
                "code_squad_capabilities_get",
                "code_squad_scope_preview",
                "code_squad_context_pack",
                "code_squad_run",
                "code_squad_execute",
                "code_squad_tick",
                "code_squad_status",
                "code_squad_events",
                "code_squad_collect",
                "code_squad_apply",
                "code_squad_apply_many",
                "code_squad_verify",
                "code_squad_report",
                "code_squad_prune",
                "code_squad_cancel",
                "code_squad_cleanup",
            ],
        }
        if debug:
            result["debug"] = {
                "paths": {"dispatch_dir": str(config.dispatch_dir)},
                "effective": {"cwd": cwd, "repo_dispatch_dir": str(effective.dispatch_dir) if cwd else None},
            }
        return result

    def _matches_any(path: str, globs: list[str] | None) -> bool:
        if not globs:
            return False
        rel_path = PurePosixPath(_normalize_relpath(path))
        return any(rel_path.match(_normalize_relpath(pat)) for pat in globs if isinstance(pat, str) and pat.strip())

    def _scoped(path: str, *, allow_globs: list[str] | None, deny_globs: list[str] | None) -> bool:
        if allow_globs and not _matches_any(path, allow_globs):
            return False
        if deny_globs and _matches_any(path, deny_globs):
            return False
        return True

    def _rg_list_files(repo_root: Path, *, allow_globs: list[str] | None, deny_globs: list[str] | None, limit: int) -> list[str]:
        globs: list[str] = []
        for item in allow_globs or []:
            if isinstance(item, str) and item.strip():
                globs.append(_normalize_relpath(item.strip()))
        for item in deny_globs or []:
            if isinstance(item, str) and item.strip():
                globs.append("!" + _normalize_relpath(item.strip()))
        cmd: list[str] = ["rg", "--files"]
        for g in globs:
            cmd += ["-g", g]
        cmd.append(str(repo_root))
        try:
            res = subprocess.run(cmd, check=False, capture_output=True, text=True)
        except FileNotFoundError as exc:  # pragma: no cover - environment specific
            raise RipgrepNotFound("ripgrep (rg) is required to preview scopes") from exc
        if res.returncode not in (0, 1):
            return []
        out: list[str] = []
        for line in (res.stdout or "").splitlines():
            p = line.strip()
            if not p:
                continue
            try:
                rel = safe_relpath(Path(p), repo_root)
            except ValueError:
                continue
            rel = _normalize_relpath(rel)
            if not rel or rel.startswith(".."):
                continue
            if _scoped(rel, allow_globs=allow_globs, deny_globs=deny_globs):
                out.append(rel)
            if len(out) >= max(1, int(limit or 0)):
                break
        return out

    @mcp.tool(name="code_squad_scope_preview")
    def code_squad_scope_preview(
        cwd: str,
        allow_globs: list[str] | None = None,
        deny_globs: list[str] | None = None,
        max_items: int = 50,
        options: Any | None = None,
    ) -> dict[str, Any]:
        """
        Preview scope globs before running tasks to reduce scope mistakes and rework.

        Returns repo-relative paths only (no absolute paths unless options.debug=true).
        """
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_scope_preview", "start", trace_id, cwd=cwd)
        try:
            repo_root = find_repo_root(Path(cwd))
            allow = _parse_globs(allow_globs)
            deny = _parse_globs(deny_globs)
            items: list[str] = []
            warning: str | None = None
            try:
                items = _rg_list_files(repo_root, allow_globs=allow, deny_globs=deny, limit=max_items)
            except RipgrepNotFound as exc:
                warning = str(exc)
            elapsed_ms = int((time.monotonic() - start) * 1000)
            result: dict[str, Any] = {
                "ok": warning is None,
                "allow_globs": allow or [],
                "deny_globs": deny or [],
                "sample_paths": items,
                "sample_count": len(items),
                "warning": warning,
            }
            if debug:
                result["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "repo_root": str(repo_root)}
            return result
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_scope_preview", "end", trace_id, cwd=cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_context_pack")
    def code_squad_context_pack(
        cwd: str,
        query: str,
        hints: list[str] | None = None,
        glob: str = "*.py",
        max_files: int = 12,
        max_snippets: int = 24,
        max_total_chars: int = 20_000,
        options: Any | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
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

    def _find_task(run_meta: dict[str, Any], slug: str | None) -> dict[str, Any] | None:
        if not slug:
            return None
        slug_val = str(slug).strip()
        if not slug_val:
            return None
        for task in run_meta.get("tasks", []):
            if str(task.get("slug") or "").strip() == slug_val:
                return task
        return None

    def _apply_patch_for_slug(
        run_meta: dict[str, Any],
        repo_root: Path,
        slug: str,
        *,
        dry_run: bool,
        stage_index: bool,
        three_way: bool,
        force: bool,
    ) -> dict[str, Any]:
        task = _find_task(run_meta, slug)
        if not task:
            return {"ok": False, "error": f"Task not found in run: {slug}", "slug": slug}

        scope = task.get("scope") if isinstance(task.get("scope"), dict) else None
        if scope and scope.get("ok") is False and not force:
            return {"ok": False, "error": "scope violations present; re-run with force=true to override", "slug": slug, "scope": scope}

        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_meta.get("id") or ""))
        patch_path = run_dir / "artifacts" / "collect" / f"{slug}.patch"
        if not patch_path.exists():
            return {"ok": False, "error": "patch not found; run code_squad_collect first", "slug": slug}
        patch_text = patch_path.read_text(encoding="utf-8", errors="replace")
        if "diff --git " not in patch_text and patch_text.strip() == "":
            return {"ok": False, "error": "empty patch", "slug": slug}

        cmd: list[str] = ["git", "apply"]
        if three_way:
            cmd.append("--3way")
        if stage_index and not dry_run:
            cmd.append("--index")
        cmd.append("--whitespace=nowarn")
        if dry_run:
            cmd.append("--check")
        cmd.append(str(patch_path))

        proc = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True)
        return {
            "ok": proc.returncode == 0,
            "slug": slug,
            "dry_run": bool(dry_run),
            "applied": bool(proc.returncode == 0 and not dry_run),
            "exit_code": proc.returncode,
            "stdout_tail": truncate_text(proc.stdout or "", 2000),
            "stderr_tail": truncate_text(proc.stderr or "", 2000),
            "scope": scope,
            "command": cmd,
            "patch_path": str(patch_path),
        }

    def _load_touched_files(run_meta: dict[str, Any], slug: str) -> list[str]:
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_meta.get("id") or ""))
        files_path = run_dir / "artifacts" / "collect" / f"{slug}.files.json"
        try:
            payload = json.loads(files_path.read_text(encoding="utf-8", errors="replace"))
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
        if isinstance(payload, dict) and isinstance(payload.get("files"), list):
            return [str(p).replace("\\", "/") for p in payload.get("files") if str(p or "").strip()]
        if isinstance(payload, list):
            return [str(p).replace("\\", "/") for p in payload if str(p or "").strip()]
        return []

    def _topo_order_slugs(run_meta: dict[str, Any], slugs: list[str]) -> tuple[list[str], list[str]]:
        """
        Topologically order provided slugs using in-run depends_on edges.
        Returns (ordered, problems). If a cycle exists within the induced subgraph, returns the original order with a problem.
        """
        wanted: list[str] = [s for s in (str(x or "").strip() for x in slugs) if s]
        if not wanted:
            return [], []
        task_map = {str(t.get("slug") or ""): t for t in run_meta.get("tasks", []) if t.get("slug")}
        in_wanted = set(wanted)
        deps_map: dict[str, set[str]] = {}
        for s in wanted:
            raw = task_map.get(s, {}).get("depends_on")
            deps = raw if isinstance(raw, list) else []
            deps_map[s] = {str(d or "").strip() for d in deps if str(d or "").strip() in in_wanted}

        incoming: dict[str, int] = {s: 0 for s in wanted}
        outgoing: dict[str, list[str]] = {s: [] for s in wanted}
        for node, deps in deps_map.items():
            incoming[node] = len(deps)
            for dep in deps:
                outgoing.setdefault(dep, []).append(node)

        q: list[str] = [s for s in wanted if incoming.get(s, 0) == 0]
        ordered: list[str] = []
        while q:
            n = q.pop(0)
            ordered.append(n)
            for child in outgoing.get(n, []):
                incoming[child] = max(0, int(incoming.get(child, 0)) - 1)
                if incoming[child] == 0:
                    q.append(child)

        if len(ordered) != len(wanted):
            return wanted, ["dependency cycle detected among selected slugs"]
        return ordered, []

    def _detect_patch_conflicts(run_meta: dict[str, Any], slugs: list[str]) -> list[dict[str, Any]]:
        """
        Detect overlapping touched files between slugs (based on collect artifacts).
        """
        file_to_slugs: dict[str, list[str]] = {}
        for slug in slugs:
            for path in _load_touched_files(run_meta, slug):
                file_to_slugs.setdefault(path, [])
                if slug not in file_to_slugs[path]:
                    file_to_slugs[path].append(slug)
        conflicts: list[dict[str, Any]] = []
        for path, owners in file_to_slugs.items():
            if len(owners) > 1:
                conflicts.append({"path": path, "slugs": owners})
        conflicts.sort(key=lambda x: (str(x.get("path") or ""), ",".join(x.get("slugs") or [])))
        return conflicts

    @mcp.tool(name="code_squad_apply")
    def code_squad_apply(
        cwd: str,
        run_id: str,
        slug: str,
        options: Any | None = None,
    ) -> dict[str, Any]:
        """
        Apply a collected patch to the repo worktree.

        Default is dry-run only. Set options.dry_run=false to apply.
        """
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_apply", "start", trace_id, cwd=cwd, run_id=run_id, slug=slug)
        try:
            dry_run = _coerce_bool(opts.get("dry_run"))
            if dry_run is None:
                dry_run = True
            stage_index = _coerce_bool(opts.get("stage_index"))
            if stage_index is None:
                stage_index = True
            three_way = _coerce_bool(opts.get("three_way"))
            if three_way is None:
                three_way = True

            run_meta = _load_run(run_id)
            if not run_meta:
                return {"ok": False, "error": f"Run not found: {run_id}", "run_id": run_id, "slug": slug}

            repo_root = find_repo_root(Path(cwd))
            # Ensure we only apply patches for runs belonging to this repo.
            expected_root = Path(run_meta.get("repo_root") or repo_root).resolve()
            if expected_root != repo_root.resolve():
                return {"ok": False, "error": "cwd does not match run repo_root", "run_id": run_id, "slug": slug}

            helper_res = _apply_patch_for_slug(
                run_meta,
                repo_root,
                slug,
                dry_run=bool(dry_run),
                stage_index=bool(stage_index),
                three_way=bool(three_way),
                force=bool(opts.get("force")),
            )
            elapsed_ms = int((time.monotonic() - start) * 1000)
            result: dict[str, Any] = {"run_id": run_id, **helper_res}
            if debug:
                result.setdefault("debug", {})
                result["debug"].update({"trace_id": trace_id, "elapsed_ms": elapsed_ms, "paths": {"repo_root": str(repo_root)}})
                if "command" in helper_res:
                    result["debug"]["command"] = helper_res["command"]
                if helper_res.get("patch_path"):
                    result["debug"].setdefault("paths", {})["patch_path"] = helper_res.get("patch_path")
            else:
                result.pop("command", None)
                result.pop("patch_path", None)
            return result
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_apply", "end", trace_id, cwd=cwd, run_id=run_id, slug=slug, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_apply_many")
    def code_squad_apply_many(
        cwd: str,
        run_id: str,
        slugs: list[str] | None = None,
        options: Any | None = None,
    ) -> dict[str, Any]:
        """
        Apply multiple collected patches in order. Default is dry-run; stop at first error.
        """
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_apply_many", "start", trace_id, cwd=cwd, run_id=run_id)
        try:
            dry_run = _coerce_bool(opts.get("dry_run"))
            if dry_run is None:
                dry_run = True
            stage_index = _coerce_bool(opts.get("stage_index"))
            if stage_index is None:
                stage_index = True
            three_way = _coerce_bool(opts.get("three_way"))
            if three_way is None:
                three_way = True
            stop_on_error = _coerce_bool(opts.get("stop_on_error"))
            if stop_on_error is None:
                stop_on_error = True
            order = str(opts.get("order") or "").strip().lower() or None
            detect_conflicts = _coerce_bool(opts.get("detect_conflicts"))
            if detect_conflicts is None:
                detect_conflicts = bool(dry_run)
            fail_on_conflicts = _coerce_bool(opts.get("fail_on_conflicts"))
            if fail_on_conflicts is None:
                fail_on_conflicts = False

            run_meta = _load_run(run_id)
            if not run_meta:
                return {"ok": False, "error": f"Run not found: {run_id}", "run_id": run_id}

            repo_root = find_repo_root(Path(cwd))
            expected_root = Path(run_meta.get("repo_root") or repo_root).resolve()
            if expected_root != repo_root.resolve():
                return {"ok": False, "error": "cwd does not match run repo_root", "run_id": run_id}

            target_slugs: list[str] = []
            if isinstance(slugs, list):
                for s in slugs:
                    s_val = str(s or "").strip()
                    if s_val and s_val not in target_slugs:
                        target_slugs.append(s_val)
            if not target_slugs:
                for t in run_meta.get("tasks", []):
                    slug_val = str(t.get("slug") or "").strip()
                    if slug_val:
                        target_slugs.append(slug_val)

            problems: list[str] = []
            if order in (None, "", "auto"):
                any_deps = any(isinstance(t.get("depends_on"), list) and t.get("depends_on") for t in run_meta.get("tasks", []))
                order = "topo" if any_deps else "run"

            if order == "topo":
                target_slugs, topo_problems = _topo_order_slugs(run_meta, target_slugs)
                problems.extend(topo_problems)

            conflicts: list[dict[str, Any]] = _detect_patch_conflicts(run_meta, target_slugs) if detect_conflicts else []
            if conflicts and fail_on_conflicts:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                response: dict[str, Any] = {
                    "ok": False,
                    "run_id": run_id,
                    "dry_run": bool(dry_run),
                    "stop_on_error": bool(stop_on_error),
                    "order": order,
                    "conflicts": conflicts,
                    "results": [],
                    "error_count": 0,
                    "problems": problems + ["patch conflicts detected"],
                }
                if debug:
                    response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "paths": {"repo_root": str(repo_root)}, "target_slugs": target_slugs}
                return response

            results: list[dict[str, Any]] = []
            for slug in target_slugs:
                helper_res = _apply_patch_for_slug(
                    run_meta,
                    repo_root,
                    slug,
                    dry_run=bool(dry_run),
                    stage_index=bool(stage_index),
                    three_way=bool(three_way),
                    force=bool(opts.get("force")),
                )
                result_entry = {"run_id": run_id, **helper_res}
                if not debug:
                    result_entry.pop("command", None)
                    result_entry.pop("patch_path", None)
                results.append(result_entry)
                if not helper_res.get("ok") and stop_on_error:
                    break

            error_count = len([r for r in results if not r.get("ok")])
            elapsed_ms = int((time.monotonic() - start) * 1000)
            response: dict[str, Any] = {
                "ok": error_count == 0,
                "run_id": run_id,
                "dry_run": bool(dry_run),
                "stop_on_error": bool(stop_on_error),
                "order": order,
                "conflicts": conflicts,
                "results": results,
                "error_count": error_count,
            }
            if problems:
                response["problems"] = problems
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "paths": {"repo_root": str(repo_root)}, "target_slugs": target_slugs}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_apply_many", "end", trace_id, cwd=cwd, run_id=run_id, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_run")
    def code_squad_run(
        cwd: str,
        tasks: list[dict[str, Any]],
        run_id: str | None = None,
        options: Any | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_run", "start", trace_id, cwd=cwd)
        try:
            if not tasks:
                return {"error": "No tasks provided"}
            repo_root = find_repo_root(Path(cwd))
            effective_config = _effective_config_for_cwd(cwd)
            resolved_run_id = slugify(run_id or uuid.uuid4().hex, fallback="run")
            run_dir = store.run_dir(resolved_run_id)
            worktree_base = ensure_repo_subpath(repo_root, repo_root / ".codex" / "code-squad" / "worktrees" / resolved_run_id)
            ensure_dir(worktree_base)

            defaults = {
                "model": opts.get("model"),
                "sandbox": opts.get("sandbox"),
                "approval_policy": opts.get("approval_policy"),
                "extra_config": opts.get("extra_config"),
                "max_touched_files": opts.get("max_touched_files"),
                "max_patch_bytes": opts.get("max_patch_bytes"),
            }

            enforce_sparse_checkout = _coerce_bool(opts.get("enforce_sparse_checkout"))
            if enforce_sparse_checkout is None:
                enforce_sparse_checkout = bool(getattr(effective_config, "enforce_sparse_checkout", True))

            early_scope_enforcement = _coerce_bool(opts.get("early_scope_enforcement"))
            if early_scope_enforcement is None:
                early_scope_enforcement = bool(getattr(effective_config, "early_scope_enforcement", True))

            strict_context_pack_scope = _coerce_bool(opts.get("strict_context_pack_scope"))
            if strict_context_pack_scope is None:
                strict_context_pack_scope = bool(getattr(effective_config, "strict_context_pack_scope", True))

            require_patch = _coerce_bool(opts.get("require_patch"))
            if require_patch is None:
                require_patch = bool(getattr(effective_config, "require_patch", True))

            auto_context_pack = _resolve_auto_context_pack(opts, effective_config)

            existing = _load_run(resolved_run_id)
            run_meta = existing or {
                "id": resolved_run_id,
                "created_at": utc_now_iso(),
                "repo_root": str(repo_root),
                "dispatch_base": str(config.dispatch_dir),
                "run_dir": str(run_dir),
                "worktree_base": str(worktree_base),
                "defaults": {
                    "model": defaults.get("model") or effective_config.default_model,
                    "sandbox": defaults.get("sandbox") or effective_config.default_sandbox,
                    "approval_policy": defaults.get("approval_policy") or effective_config.default_approval_policy,
                    "extra_config": defaults.get("extra_config") if defaults.get("extra_config") else [],
                },
                "guardrails": {
                    "enforce_sparse_checkout": enforce_sparse_checkout,
                    "early_scope_enforcement": early_scope_enforcement,
                    "strict_context_pack_scope": strict_context_pack_scope,
                    "require_patch": require_patch,
                },
                "tasks": [],
                "queue": [],
            }

            task_results: list[dict[str, Any]] = []
            debug_tasks: list[dict[str, Any]] = []
            existing_slugs = {str(t.get("slug") or "") for t in run_meta.get("tasks", []) if t.get("slug")}
            alias_map: dict[str, str] = {}
            for t in run_meta.get("tasks", []):
                slug_val = str(t.get("slug") or "").strip()
                name_val = str(t.get("name") or "").strip()
                if slug_val:
                    alias_map[slug_val] = slug_val
                if name_val and name_val not in alias_map and slug_val:
                    alias_map[name_val] = slug_val

            task_specs: list[dict[str, Any]] = []
            for idx, task in enumerate(tasks):
                name = str(task.get("name") or f"task-{idx+1}")
                prompt = str(task.get("prompt") or "")
                if not prompt.strip():
                    task_results.append({"name": name, "slug": None, "job_id": None, "state": "error", "error": "Empty prompt"})
                    continue
                slug = slugify(name, fallback=f"task-{idx+1}")
                base_slug = slug
                suffix = 2
                while slug in existing_slugs:
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1
                existing_slugs.add(slug)
                alias_map.setdefault(slug, slug)
                if name and name not in alias_map:
                    alias_map[name] = slug
                task_specs.append({"raw": task, "name": name, "prompt": prompt, "slug": slug})

            for spec in task_specs:
                task = spec["raw"]
                name = spec["name"]
                prompt = spec["prompt"]
                slug = spec["slug"]
                allow_globs = _parse_globs(task.get("allow_globs"))
                deny_globs = _parse_globs(task.get("deny_globs"))
                scope_name = str(task.get("scope_name") or "").strip() or None
                role = str(task.get("role") or "").strip() or None

                depends_on_raw = task.get("depends_on")
                depends_on: list[str] = []
                depends_errors: list[str] = []
                if isinstance(depends_on_raw, list):
                    for dep in depends_on_raw:
                        dep_alias = str(dep or "").strip()
                        if not dep_alias:
                            continue
                        resolved_dep = alias_map.get(dep_alias)
                        if not resolved_dep:
                            depends_errors.append(dep_alias)
                            continue
                        if resolved_dep == slug:
                            depends_errors.append(f"{dep_alias} (self)")
                            continue
                        if resolved_dep not in depends_on:
                            depends_on.append(resolved_dep)
                elif depends_on_raw is None:
                    depends_on = []
                else:
                    depends_errors.append(str(depends_on_raw))

                if depends_errors:
                    task_results.append({"name": name, "slug": slug, "job_id": None, "state": "error", "error": f"unknown depends_on: {depends_errors}"})
                    continue

                worktree_path = ensure_repo_subpath(repo_root, worktree_base / slug)
                task_enforce_sparse = _coerce_bool(task.get("enforce_sparse_checkout"))
                if task_enforce_sparse is None:
                    task_enforce_sparse = enforce_sparse_checkout

                task_early_scope = _coerce_bool(task.get("early_scope_enforcement"))
                if task_early_scope is None:
                    task_early_scope = early_scope_enforcement

                task_strict_context_scope = _coerce_bool(task.get("strict_context_pack_scope"))
                if task_strict_context_scope is None:
                    task_strict_context_scope = strict_context_pack_scope

                task_require_patch = _coerce_bool(task.get("require_patch"))
                if task_require_patch is None:
                    task_require_patch = require_patch
                include_dep_patches_flag = _coerce_bool(task.get("include_dep_patches"))
                include_dep_patches = bool(include_dep_patches_flag) if include_dep_patches_flag is not None else False
                if "dep_patch_max_bytes" in task:
                    raw_dep_patch_max_bytes = task.get("dep_patch_max_bytes")
                    if raw_dep_patch_max_bytes is None:
                        dep_patch_max_bytes = None
                    else:
                        try:
                            dep_patch_max_bytes = int(raw_dep_patch_max_bytes)
                        except (TypeError, ValueError):
                            dep_patch_max_bytes = DEFAULT_DEP_PATCH_MAX_BYTES
                        else:
                            if dep_patch_max_bytes <= 0:
                                dep_patch_max_bytes = None
                else:
                    dep_patch_max_bytes = DEFAULT_DEP_PATCH_MAX_BYTES

                task_context = task.get("context_pack") if isinstance(task.get("context_pack"), dict) else None
                task_context, filtered = _sanitize_context_pack(task_context, allow_globs=allow_globs, deny_globs=deny_globs)
                if filtered and task_strict_context_scope:
                    task_results.append(
                        {
                            "name": name,
                            "slug": slug,
                            "job_id": None,
                            "state": "error",
                            "error": f"context_pack contains out-of-scope paths: {sorted(set(filtered))[:8]}",
                        }
                    )
                    continue
                if task_context is None and auto_context_pack is not None:
                    query_val = str(task.get("context_query") or scope_name or name).strip()
                    if not query_val:
                        query_val = name
                    hints_val: list[str] = []
                    auto_hints = auto_context_pack.get("hints")
                    if isinstance(auto_hints, list):
                        hints_val.extend([str(h).strip() for h in auto_hints if str(h).strip()])
                    if scope_name:
                        hints_val.append(scope_name)
                    hints_val.extend(_extract_glob_prefixes(allow_globs))
                    glob_val = str(auto_context_pack.get("glob") or "**/*")
                    max_files_val = int(auto_context_pack.get("max_files", 12))
                    max_snippets_val = int(auto_context_pack.get("max_snippets", 24))
                    max_total_chars_val = int(auto_context_pack.get("max_total_chars", 20_000))
                    try:
                        task_context = _cached_context_pack(
                            cwd=str(repo_root),
                            query=query_val,
                            hints=hints_val,
                            glob=glob_val,
                            allow_globs=allow_globs,
                            deny_globs=deny_globs,
                            max_files=max_files_val,
                            max_snippets=max_snippets_val,
                            max_total_chars=max_total_chars_val,
                        )
                    except RipgrepNotFound:
                        task_context = None
                    task_context, _ = _sanitize_context_pack(task_context, allow_globs=allow_globs, deny_globs=deny_globs)

                max_touched_files = task.get("max_touched_files", defaults.get("max_touched_files"))
                max_patch_bytes = task.get("max_patch_bytes", defaults.get("max_patch_bytes"))
                try:
                    max_touched_files = int(max_touched_files) if max_touched_files is not None else None
                except (TypeError, ValueError):
                    max_touched_files = None
                try:
                    max_patch_bytes = int(max_patch_bytes) if max_patch_bytes is not None else None
                except (TypeError, ValueError):
                    max_patch_bytes = None
                if isinstance(max_touched_files, int) and max_touched_files <= 0:
                    max_touched_files = None
                if isinstance(max_patch_bytes, int) and max_patch_bytes <= 0:
                    max_patch_bytes = None
                limits = {"max_touched_files": max_touched_files, "max_patch_bytes": max_patch_bytes}
                if limits.get("max_touched_files") is None and limits.get("max_patch_bytes") is None:
                    limits = None

                composed_prompt = _compose_prompt_with_scope(
                    prompt,
                    task_context,
                    role=role,
                    allow_globs=allow_globs,
                    deny_globs=deny_globs,
                    limits=limits,
                )
                task_model = task.get("model") or defaults.get("model") or effective_config.default_model
                task_sandbox = task.get("sandbox") or defaults.get("sandbox") or effective_config.default_sandbox
                task_approval = task.get("approval_policy") or defaults.get("approval_policy") or effective_config.default_approval_policy
                raw_extra_config = task.get("extra_config") or defaults.get("extra_config") or []
                extra_config = _apply_reasoning_effort_cap(raw_extra_config, options=opts, task=task, effective_config=effective_config)
                job_id = f"{resolved_run_id}--{slug}-{uuid.uuid4().hex[:8]}"

                task_entry = {
                    "name": name,
                    "role": role,
                    "depends_on": depends_on,
                    "scope_name": scope_name,
                    "allow_globs": allow_globs,
                    "deny_globs": deny_globs,
                    "slug": slug,
                    "job_id": job_id,
                    "worktree": str(worktree_path),
                    "state": "queued",
                    "queued_at": utc_now_iso(),
                    "model": task_model,
                    "sandbox": task_sandbox,
                    "approval_policy": task_approval,
                    "extra_config": extra_config,
                    "prompt": composed_prompt,
                    "context_paths": [snip.get("path") for snip in (task_context.get("snippets") if task_context else [])],
                    "max_touched_files": max_touched_files,
                    "max_patch_bytes": max_patch_bytes,
                    "enforce_sparse_checkout": bool(task_enforce_sparse),
                    "early_scope_enforcement": bool(task_early_scope),
                    "strict_context_pack_scope": bool(task_strict_context_scope),
                    "require_patch": bool(task_require_patch),
                    "include_dep_patches": bool(include_dep_patches),
                    "dep_patch_max_bytes": dep_patch_max_bytes,
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
                            "max_touched_files": max_touched_files,
                            "max_patch_bytes": max_patch_bytes,
                            "depends_on": depends_on,
                            "role": role,
                            "include_dep_patches": bool(include_dep_patches),
                            "dep_patch_max_bytes": dep_patch_max_bytes,
                        }
                    )

            cycle_nodes = _dependency_cycle_nodes(run_meta.get("tasks", []))
            if cycle_nodes:
                now = utc_now_iso()
                for task in run_meta.get("tasks", []):
                    slug_val = str(task.get("slug") or "").strip()
                    if not slug_val or slug_val not in cycle_nodes:
                        continue
                    if str(task.get("state") or "").lower() != "queued":
                        continue
                    task["state"] = "failed"
                    task["error"] = "dependency cycle detected"
                    task["finished_at"] = now
                    task.pop("worker_enqueued_at", None)
                if isinstance(run_meta.get("queue"), list):
                    run_meta["queue"] = [s for s in run_meta.get("queue", []) if str(s or "").strip() not in cycle_nodes]

            _save_run(resolved_run_id, run_meta)
            enqueued = _enqueue_ready_tasks(resolved_run_id, run_meta, max_starts=None)
            if enqueued:
                _save_run(resolved_run_id, run_meta)

            now = utc_now_iso()
            run_meta["finalize"] = {
                "enabled": True,
                "state": "queued",
                "enqueued_at": now,
                "poll_interval": float(opts.get("poll_interval", 1.0)),
                "max_wait_seconds": int(opts.get("timeout_seconds", 3600)),
                "verify": bool(opts.get("verify", False)),
                "cleanup": bool(opts.get("cleanup", True)),
                "keep_failed": bool(opts.get("keep_failed", True)),
            }
            _save_run(resolved_run_id, run_meta)
            _timeline_append(resolved_run_id, "run.queued", tasks=len(run_meta.get("tasks", [])))
            _enqueue_finalize(resolved_run_id)
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

    @mcp.tool(name="code_squad_execute")
    def code_squad_execute(
        cwd: str,
        tasks: list[dict[str, Any]],
        run_id: str | None = None,
        options: Any | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        preflight_result: dict[str, Any] | None = None
        elapsed_ms: int | None = None
        ops_log("code_squad_execute", "start", trace_id, cwd=cwd)
        try:
            if not tasks:
                return {"error": "No tasks provided"}
            preflight_enabled = _coerce_bool(opts.get("preflight"))
            if preflight_enabled is None:
                preflight_enabled = True
            if preflight_enabled:
                preflight_result = _preflight_tasks(cwd, tasks, opts)
                if preflight_result.get("needs_user_confirm"):
                    elapsed_ms = int((time.monotonic() - start) * 1000)
                    response: dict[str, Any] = {
                        "ok": False,
                        "preflight": preflight_result,
                        "next_action": "confirm",
                        "message": "Preflight found gaps; answer questions before running",
                    }
                    if debug:
                        response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms}
                    return response
            run_res = code_squad_run(cwd, tasks, run_id=run_id, options=opts)
            if run_res.get("error"):
                return run_res
            resolved_run_id = run_res.get("run_id")
            poll_interval = float(opts.get("poll_interval", 1.0))
            wait_seconds = 0.0
            if "wait_seconds" in opts:
                try:
                    wait_seconds = float(opts.get("wait_seconds") or 0)
                except (TypeError, ValueError):
                    wait_seconds = 0.0
            max_wait = min(45.0, max(0.0, wait_seconds))
            deadline = time.monotonic() + max_wait

            run_meta = _load_run(resolved_run_id)
            if not run_meta:
                return {"error": "run not found after start", "run_id": resolved_run_id}

            while max_wait > 0:
                run_meta, _ = _refresh_task_states(resolved_run_id, run_meta, limit=None)
                _enqueue_ready_tasks(resolved_run_id, run_meta, max_starts=None)
                _save_run(resolved_run_id, run_meta)
                progress = _compute_progress(run_meta)
                if progress.get("active", 0) == 0:
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(max(0.2, poll_interval))

            run_meta = _load_run(resolved_run_id) or run_meta
            if preflight_result:
                task_entries = run_meta.get("tasks", []) if run_meta else []
                for idx, preflight_task in enumerate(preflight_result.get("tasks", [])):
                    if idx < len(task_entries):
                        preflight_task["slug"] = task_entries[idx].get("slug")
                artifacts = run_meta.get("artifacts") if isinstance(run_meta.get("artifacts"), dict) else {}
                run_meta["preflight"] = preflight_result
                try:
                    doc_path = _write_preflight_doc(resolved_run_id, run_meta or {}, preflight_result)
                    if doc_path:
                        artifacts["preflight_doc"] = str(doc_path)
                except Exception:
                    # Preflight artifacts are best-effort; continue execution even if doc write fails.
                    pass
                if artifacts:
                    run_meta["artifacts"] = artifacts
                _save_run(resolved_run_id, run_meta)
            progress = _compute_progress(run_meta)
            counts: dict[str, int] = dict(progress.get("counts") or {})
            next_poll_ms = int(max(200, min(5000, poll_interval * 1000))) if progress.get("active", 0) else 0

            index_path = _write_run_index(
                run_meta,
                extra={"execute": {"mode": "async", "wait_seconds": wait_seconds, "progress": progress}},
            )

            include_handles = bool(opts.get("include_handles", False)) or debug
            tasks_out: list[dict[str, Any]] = []
            for task in run_meta.get("tasks", []):
                state = str(task.get("state") or "unknown")
                message = task.get("last_message") or task.get("error")
                if not message:
                    message = "Running…" if state in ("running", "starting") else ("Queued" if state == "queued" else state)
                entry: dict[str, Any] = {"name": task.get("name"), "slug": task.get("slug"), "state": state, "message": message}
                if include_handles:
                    entry["job_id"] = task.get("job_id")
                tasks_out.append(entry)

            response: dict[str, Any] = {
                "run_id": resolved_run_id,
                "counts": counts,
                "progress": progress,
                "next_action": "wait" if progress.get("active", 0) else "collect/report",
                "next_poll_ms": next_poll_ms,
                "index_path": str(index_path),
                "recent_events": _timeline_tail(resolved_run_id, max_items=8),
                "tasks": tasks_out,
            }
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "run_meta": run_meta}
            if preflight_result:
                response["preflight"] = preflight_result
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_execute", "end", trace_id, cwd=cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_prune")
    def code_squad_prune(
        keep_days: int = 3,
        keep_failed_days: int = 1,
        keep_last_runs: int = 5,
        dry_run: bool = True,
        delete_run_artifacts: bool = False,
        options: Any | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_prune", "start", trace_id, cwd=None)
        try:
            base = Path(config.dispatch_dir)
            runs_dir = base / "runs"
            now = _utc_now()
            candidates: list[dict[str, Any]] = []
            if runs_dir.exists():
                for run_path in runs_dir.iterdir():
                    if not run_path.is_dir():
                        continue
                    meta_path = run_path / "run.json"
                    try:
                        meta = json.loads(meta_path.read_text(encoding="utf-8"))
                    except (FileNotFoundError, json.JSONDecodeError):
                        continue
                    created_at = _parse_utc_datetime(meta.get("created_at"))
                    if created_at is None:
                        continue
                    tasks = meta.get("tasks") or []
                    has_failed = any(_is_failed_like(t.get("state")) for t in tasks if isinstance(t, dict))
                    age_days = (now - created_at).total_seconds() / 86400.0
                    candidates.append({"run_id": meta.get("id") or run_path.name, "created_at": created_at, "age_days": age_days, "has_failed": has_failed})
            candidates.sort(key=lambda r: r["created_at"], reverse=True)
            keep_set = {c["run_id"] for c in candidates[: max(0, int(keep_last_runs))]}

            planned: list[dict[str, Any]] = []
            deleted: list[dict[str, Any]] = []
            skipped: list[dict[str, Any]] = []

            for c in candidates:
                run_id = c["run_id"]
                if run_id in keep_set:
                    skipped.append({**c, "reason": "keep_last_runs"})
                    continue
                threshold = float(keep_failed_days if c["has_failed"] else keep_days)
                if c["age_days"] <= threshold:
                    skipped.append({**c, "reason": "within_retention"})
                    continue
                planned.append({**c, "reason": "expired"})
                if dry_run:
                    continue
                res = code_squad_cleanup(run_id, delete_run_artifacts=delete_run_artifacts, options=options)
                deleted.append({**c, "cleanup": res, "deleted_run_artifacts": delete_run_artifacts})

            response: dict[str, Any] = {
                "keep_days": keep_days,
                "keep_failed_days": keep_failed_days,
                "keep_last_runs": keep_last_runs,
                "dry_run": dry_run,
                "delete_run_artifacts": delete_run_artifacts,
                "planned": planned,
                "deleted": deleted,
                "skipped": skipped,
            }
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "dispatch_dir": str(config.dispatch_dir)}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_prune", "end", trace_id, cwd=None, elapsed_ms=elapsed_ms)

    def _refresh_task_states(run_id: str, run_meta: dict[str, Any], *, limit: int | None = None) -> tuple[dict[str, Any], int]:
        dispatch = _dispatch_for_run(run_id)
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
        collect_dir = run_dir / "artifacts" / "collect"
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
            stdout_tail = status_res.get("stdout_tail") or ""
            slug = str(task.get("slug") or task.get("job_id") or "task")
            has_patch = "diff --git " in stdout_tail
            if not has_patch:
                patch_path = collect_dir / f"{slug}.patch"
                try:
                    if patch_path.exists() and "diff --git " in patch_path.read_text(encoding="utf-8", errors="replace"):
                        has_patch = True
                except OSError:
                    has_patch = False
            task["has_patch"] = has_patch

            if has_patch and bool(task.get("early_scope_enforcement", False)) and not bool(task.get("early_scope_checked", False)):
                job_id = task.get("job_id")
                patch_text = ""
                if job_id:
                    stdout_jsonl = run_dir / "jobs" / str(job_id) / "stdout.jsonl"
                    patch_text = _extract_patch_from_stdout(stdout_jsonl)
                if patch_text:
                    allow_globs = _parse_globs(task.get("allow_globs"))
                    deny_globs = _parse_globs(task.get("deny_globs"))
                    max_touched_files = task.get("max_touched_files")
                    max_patch_bytes = task.get("max_patch_bytes")
                    require_patch = bool(task.get("require_patch", False))
                    scope_ok, scope_payload, touched_files, patch_bytes = _evaluate_scope(
                        patch_text=patch_text,
                        scope_name=task.get("scope_name"),
                        allow_globs=allow_globs,
                        deny_globs=deny_globs,
                        max_touched_files=max_touched_files if isinstance(max_touched_files, int) else None,
                        max_patch_bytes=max_patch_bytes if isinstance(max_patch_bytes, int) else None,
                        require_patch=require_patch,
                    )
                    scope_artifact = dict(scope_payload)
                    scope_path = str(run_dir / "artifacts" / "scope" / f"{slug}.json")
                    scope_artifact["path"] = scope_path
                    _persist_collect_artifacts(run_dir=run_dir, slug=slug, patch_text=patch_text, touched_files=touched_files, scope_payload=scope_artifact)
                    task["scope"] = scope_artifact
                    task["early_scope_checked"] = True
                    _timeline_append(run_id, "scope.early_check", slug=slug, ok=scope_ok, touched_files=len(touched_files), patch_bytes=patch_bytes)
                    if not scope_ok:
                        if task.get("job_id") and task.get("state") in ("running", "starting"):
                            dispatch.cancel(job_id=str(task.get("job_id")), reason="scope_violation")
                        task["state"] = "failed"
                        task["error"] = f"scope violation: {scope_payload.get('violations')}"
                        task["finished_at"] = utc_now_iso()

            readable = _extract_readable_stdout(stdout_tail, status_res.get("last_message"))
            if readable:
                task["last_message"] = readable
            updated += 1
        return run_meta, updated

    @mcp.tool(name="code_squad_status")
    def code_squad_status(run_id: str, include_last_message: bool = True, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_status", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            run_meta, _ = _refresh_task_states(run_id, run_meta, limit=None)
            _enqueue_ready_tasks(run_id, run_meta, max_starts=None)
            _save_run(run_id, run_meta)

            progress = _compute_progress(run_meta)
            counts: dict[str, int] = dict(progress.get("counts") or {})
            poll_interval = 1.0
            finalize_cfg = run_meta.get("finalize") if isinstance(run_meta.get("finalize"), dict) else None
            if isinstance(finalize_cfg, dict) and finalize_cfg.get("poll_interval") is not None:
                try:
                    poll_interval = float(finalize_cfg.get("poll_interval") or 1.0)
                except (TypeError, ValueError):
                    poll_interval = 1.0
            next_poll_ms = int(max(200, min(5000, poll_interval * 1000))) if progress.get("active", 0) else 0
            include_handles = bool(opts.get("include_handles", False)) or debug

            tasks_out: list[dict[str, Any]] = []
            for task in run_meta.get("tasks", []):
                state = str(task.get("state") or "unknown")
                message = task.get("last_message") if include_last_message else None
                if not message:
                    message = task.get("error")
                if not message:
                    message = "Running…" if state in ("running", "starting") else ("Queued" if state == "queued" else state)
                entry: dict[str, Any] = {"name": task.get("name"), "slug": task.get("slug"), "state": state, "message": message, "has_patch": bool(task.get("has_patch"))}
                if include_handles:
                    entry["job_id"] = task.get("job_id")
                tasks_out.append(entry)

            response: dict[str, Any] = {
                "run_id": run_id,
                "counts": counts,
                "progress": progress,
                "next_action": "wait" if progress.get("active", 0) else "collect/report",
                "next_poll_ms": next_poll_ms,
                "recent_events": _timeline_tail(run_id, max_items=8),
                "tasks": tasks_out,
            }
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {
                    "trace_id": trace_id,
                    "elapsed_ms": elapsed_ms,
                    "defaults": run_meta.get("defaults"),
                    "run_meta": run_meta,
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
        max_items: int = 30,
        max_bytes: int = 4000,
        include_noise: bool = False,
        options: Any | None = None,
    ) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
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
                    if include_noise or debug:
                        events_out.append({"job_id": job_id, "event": _compact_event(ev)})
                    else:
                        if isinstance(ev, dict):
                            ev_type = ev.get("type")
                            if isinstance(ev_type, str) and ev_type in EVENT_NOISE_TYPES:
                                continue
                            item = ev.get("item")
                            if isinstance(item, dict):
                                item_type = item.get("type")
                                if isinstance(item_type, str) and item_type in NOISY_ITEM_TYPES:
                                    continue

                        text_snips = _iter_event_text(ev)
                        has_diff = any(isinstance(t, str) and "diff --git " in t for t in text_snips)
                        human = next(
                            (t for t in reversed(text_snips) if isinstance(t, str) and t.strip() and "diff --git " not in t),
                            None,
                        )
                        if not has_diff and not human:
                            continue

                        item_type = None
                        if isinstance(ev, dict) and isinstance(ev.get("item"), dict):
                            item_type = ev.get("item", {}).get("type")

                        if has_diff:
                            text_out = next((t for t in reversed(text_snips) if isinstance(t, str) and "diff --git " in t), "diff --git …")
                        else:
                            text_out = str(human or "").strip()
                            text_out = next((ln.strip() for ln in reversed(text_out.splitlines()) if ln.strip()), text_out)

                        events_out.append(
                            {
                                "job_id": job_id,
                                "event": {
                                    "type": (ev.get("type") if isinstance(ev, dict) else None),
                                    "item_type": item_type,
                                    "text": truncate_text(text_out, 240),
                                },
                            }
                        )
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
    def code_squad_collect(run_id: str, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_collect", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            include_patch = bool(opts.get("include_patch", False)) or debug
            results, debug_results = _collect_run(run_id, run_meta, include_patch=include_patch, debug=debug)
            response: dict[str, Any] = {"run_id": run_id, "results": results, "recent_events": _timeline_tail(run_id, max_items=12)}
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms, "tasks": debug_results}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_collect", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_verify")
    def code_squad_verify(run_id: str, job_id: str | None = None, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_verify", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            results, debug_results = _verify_run(run_id, run_meta, job_id=job_id, options=opts, debug=debug)
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
    def code_squad_tick(run_id: str, max_starts: int = 2, max_updates: int = 5, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_tick", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            run_meta, refreshed = _refresh_task_states(run_id, run_meta, limit=max_updates)
            enqueued = _enqueue_ready_tasks(run_id, run_meta, max_starts=max_starts)
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

    @mcp.tool(name="code_squad_report")
    def code_squad_report(run_id: str, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        elapsed_ms: int | None = None
        ops_log("code_squad_report", "start", trace_id, cwd=log_cwd)
        try:
            if not run_meta:
                return {"error": "run not found", "run_id": run_id}
            run_meta, _ = _refresh_task_states(run_id, run_meta, limit=None)
            _enqueue_ready_tasks(run_id, run_meta, max_starts=None)
            _save_run(run_id, run_meta)
            counts: dict[str, int] = {}
            for task in run_meta.get("tasks", []):
                state = str(task.get("state") or "unknown")
                counts[state] = counts.get(state, 0) + 1
            run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
            artifacts_dir = ensure_dir(run_dir / "artifacts")
            scope_dir = run_dir / "artifacts" / "scope"
            report_json = artifacts_dir / "report.json"
            report_md = artifacts_dir / "report.md"
            deps_graph_path: Path | None = None

            task_rows: list[dict[str, Any]] = []
            for task in run_meta.get("tasks", []):
                scope = task.get("scope") if isinstance(task.get("scope"), dict) else None
                if scope is None and (scope_dir / f"{task.get('slug') or task.get('job_id') or 'task'}.json").exists():
                    try:
                        scope = json.loads((scope_dir / f"{task.get('slug') or task.get('job_id') or 'task'}.json").read_text(encoding="utf-8"))
                    except json.JSONDecodeError:
                        scope = None
                task_rows.append(
                    {
                        "name": task.get("name"),
                        "role": task.get("role"),
                        "depends_on": task.get("depends_on"),
                        "slug": task.get("slug"),
                        "job_id": task.get("job_id"),
                        "state": task.get("state"),
                        "last_message": task.get("last_message"),
                        "worktree": task.get("worktree"),
                        "finished_at": task.get("finished_at"),
                        "error": task.get("error"),
                        "scope": scope,
                    }
                )

            slug_roles: dict[str, str | None] = {}
            dependency_edges: list[tuple[str, str]] = []

            def _mermaid_node_id(slug: str) -> str:
                cleaned = re.sub(r"[^A-Za-z0-9_]", "_", slug)
                return cleaned or "_"

            for task in task_rows:
                slug = str(task.get("slug") or "").strip()
                if slug:
                    slug_roles.setdefault(slug, task.get("role"))
                depends_on = task.get("depends_on")
                if isinstance(depends_on, list) and depends_on:
                    for dep_slug in depends_on:
                        dep_val = str(dep_slug or "").strip()
                        if dep_val:
                            dependency_edges.append((dep_val, slug))

            if dependency_edges:
                docs_dir = ensure_dir(run_dir / "artifacts" / "docs")
                deps_graph_path = docs_dir / "deps.mmd"
                unique_slugs = sorted({*slug_roles.keys(), *(slug for edge in dependency_edges for slug in edge)})
                node_ids: dict[str, str] = {}
                node_lines: list[str] = []
                for slug in unique_slugs:
                    if not slug:
                        continue
                    node_id = _mermaid_node_id(slug)
                    node_ids[slug] = node_id
                    role = slug_roles.get(slug)
                    label = f"{slug} ({role})" if role else slug
                    safe_label = label.replace('"', '\\"')
                    node_lines.append(f"    {node_id}[\"{safe_label}\"]")
                edge_lines: list[str] = []
                for dep_slug, task_slug in sorted({(src, dst) for src, dst in dependency_edges}):
                    source_id = node_ids.get(dep_slug)
                    target_id = node_ids.get(task_slug)
                    if not source_id or not target_id:
                        continue
                    edge_lines.append(f"    {source_id} --> {target_id}")
                deps_lines = ["graph TD", *node_lines, *edge_lines]
                deps_graph_path.write_text("\n".join(deps_lines), encoding="utf-8")
            else:
                stale_graph = run_dir / "artifacts" / "docs" / "deps.mmd"
                try:
                    stale_graph.unlink(missing_ok=True)
                except TypeError:
                    if stale_graph.exists():
                        stale_graph.unlink()
                deps_graph_path = None

            report_data = {
                "run_id": run_id,
                "created_at": run_meta.get("created_at"),
                "repo_root": run_meta.get("repo_root"),
                "counts": counts,
                "tasks": task_rows,
            }
            if deps_graph_path:
                report_data["deps_mermaid"] = str(deps_graph_path)
            report_json.write_text(json.dumps(report_data, ensure_ascii=False, indent=2), encoding="utf-8")

            lines = [
                "# Code Squad Report",
                "",
                f"- Run ID: {run_id}",
                f"- Created At: {run_meta.get('created_at')}",
                f"- Repo Root: {run_meta.get('repo_root')}",
                "",
                "## Tasks",
            ]
            for task in task_rows:
                slug = task.get("slug") or task.get("name")
                state = task.get("state")
                line = f"- {slug}: {state} (job_id={task.get('job_id')})"
                if task.get("error"):
                    line += f" error={task.get('error')}"
                scope = task.get("scope") if isinstance(task.get("scope"), dict) else None
                if scope and scope.get("ok") is False:
                    line += f" scope_violations={scope.get('violations')}"
                lines.append(line)
            if deps_graph_path:
                lines.extend(["", "## Dependency Graph", f"- Mermaid: {deps_graph_path}"])
            report_md.write_text("\n".join(lines), encoding="utf-8")
            report_refs = {"report_json": str(report_json), "report_md": str(report_md)}
            if deps_graph_path:
                report_refs["deps_mermaid"] = str(deps_graph_path)
            index_path = _write_run_index(run_meta, extra={"report": report_refs})

            response: dict[str, Any] = {"run_id": run_id, "report_json": str(report_json), "report_md": str(report_md), "index_path": str(index_path), "counts": counts}
            if deps_graph_path:
                response["deps_mermaid"] = str(deps_graph_path)
            elapsed_ms = int((time.monotonic() - start) * 1000)
            if debug:
                response["debug"] = {"trace_id": trace_id, "elapsed_ms": elapsed_ms}
            return response
        finally:
            if elapsed_ms is None:
                elapsed_ms = int((time.monotonic() - start) * 1000)
            ops_log("code_squad_report", "end", trace_id, cwd=log_cwd, elapsed_ms=elapsed_ms)

    @mcp.tool(name="code_squad_cancel")
    def code_squad_cancel(run_id: str, job_id: str | None = None, task_slug: str | None = None, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
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
    def code_squad_cleanup(run_id: str, delete_run_artifacts: bool = False, options: Any | None = None) -> dict[str, Any]:
        trace_id = uuid.uuid4().hex
        start = time.monotonic()
        run_meta = _load_run(run_id)
        log_cwd = run_meta.get("repo_root") if run_meta else None
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
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
