from __future__ import annotations

import hashlib
import json
import queue
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
}

NOISY_ITEM_TYPES = {"command_execution", "mcp_tool_call", "todo_list"}

EVENT_NOISE_TYPES = {
    "thread.started",
    "thread.created",
    "turn.started",
    "turn.created",
    "turn.delta",
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
    "run_started",
    "run_finished",
    "response_started",
    "response_completed",
    "response_finished",
    "heartbeat",
    "ping",
    "pong",
}


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
    return _compose_prompt_with_scope(task_prompt, context_pack, allow_globs=None, deny_globs=None, limits=None)


def _compose_prompt_with_scope(
    task_prompt: str,
    context_pack: dict[str, Any] | None,
    *,
    allow_globs: list[str] | None,
    deny_globs: list[str] | None,
    limits: dict[str, Any] | None,
) -> str:
    segments = [
        "You are a focused code-writing subagent. Produce git-style patches only, avoid speculation, and keep output minimal.",
        f"Subtask: {task_prompt.strip()}",
    ]
    scope_lines: list[str] = [
        "Rules:",
        "- Output MUST be a git-style patch (diff) only.",
        "- Keep changes minimal and directly related to the subtask.",
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
        return str(state or "").lower() in ("failed", "timeout")

    def _is_terminal_state(state: str | None) -> bool:
        return str(state or "").lower() in ("completed", "failed", "cancelled", "timeout")

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
        if extra:
            payload.update(extra)
        index_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return index_path

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

    def _try_parse_json(value: Any) -> Any:
        if not isinstance(value, str):
            return None
        s = value.strip()
        if not s:
            return None
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            try:
                return json.loads(s)
            except json.JSONDecodeError:
                return None
        return None

    def _iter_event_text(obj: Any) -> list[str]:
        out: list[str] = []

        def walk(node: Any) -> None:
            if node is None:
                return
            if isinstance(node, str):
                out.append(node)
                parsed = _try_parse_json(node)
                if parsed is not None:
                    walk(parsed)
                return
            if isinstance(node, list):
                for item in node:
                    walk(item)
                return
            if isinstance(node, dict):
                ctype = node.get("type")
                if isinstance(ctype, str) and (ctype in NOISE_EVENT_TYPES or ctype in NOISY_ITEM_TYPES):
                    return
                for key in ("text", "message", "content", "item"):
                    if key in node:
                        walk(node.get(key))
                return
            # ignore scalars

        walk(obj)
        return out

    def _extract_patch_from_stdout(stdout_jsonl: Path) -> str:
        try:
            lines = stdout_jsonl.read_text(encoding="utf-8", errors="replace").splitlines()
        except FileNotFoundError:
            return ""
        candidates: list[str] = []
        for line in lines:
            s = (line or "").strip()
            if not s:
                continue
            try:
                obj = json.loads(s)
            except json.JSONDecodeError:
                continue
            for text in _iter_event_text(obj):
                if "diff --git " in text:
                    candidates.append(text)
        if not candidates:
            return ""

        def normalize(text: str) -> str:
            start = text.find("diff --git ")
            if start == -1:
                return ""
            block = text[start:]
            cleaned_lines: list[str] = []
            for raw_line in block.splitlines():
                line = raw_line.rstrip("\n")
                if line.strip() == "```":
                    continue
                if line.strip().startswith("```"):
                    continue
                cleaned_lines.append(line)
            return "\n".join(cleaned_lines).strip() + "\n"

        best = ""
        for c in candidates:
            normalized = normalize(c)
            if len(normalized) > len(best):
                best = normalized
        return best

    def _touched_files_from_patch(patch_text: str) -> list[str]:
        touched: list[str] = []
        for line in (patch_text or "").splitlines():
            if not line.startswith("diff --git "):
                continue
            parts = line.split(" ")
            if len(parts) < 4:
                continue
            a_path = parts[2]
            if a_path.startswith("a/"):
                rel = _normalize_relpath(a_path[2:])
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

    def _apply_reasoning_effort_cap(extra_config: Any, *, options: dict[str, Any], task: dict[str, Any]) -> list[str]:
        """
        Enforce model_reasoning_effort <= configured max.
        - Default effort comes from server config.
        - Any existing model_reasoning_effort configs are removed and replaced.
        """
        requested = _normalize_effort(options.get("model_reasoning_effort") or options.get("reasoning_effort"))
        if requested is None:
            requested = _normalize_effort(task.get("model_reasoning_effort") or task.get("reasoning_effort"))
        if requested is None:
            requested = _normalize_effort(getattr(config, "default_reasoning_effort", None)) or "medium"
        max_effort = _normalize_effort(getattr(config, "max_reasoning_effort", None)) or "medium"
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

    def _collect_run(run_id: str, run_meta: dict[str, Any], *, include_patch: bool, debug: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        run_dir = Path(run_meta.get("run_dir") or store.run_dir(run_id))
        artifacts_dir = ensure_dir(run_dir / "artifacts" / "collect")
        scope_dir = ensure_dir(run_dir / "artifacts" / "scope")
        results: list[dict[str, Any]] = []
        debug_results: list[dict[str, Any]] = []
        for task in run_meta.get("tasks", []):
            job_id = task.get("job_id")
            slug = task.get("slug") or job_id or "task"
            allow_globs = _parse_globs(task.get("allow_globs"))
            deny_globs = _parse_globs(task.get("deny_globs"))
            patch_path = artifacts_dir / f"{slug}.patch"
            touched_path = artifacts_dir / f"{slug}.files.json"
            scope_path = scope_dir / f"{slug}.json"
            patch_text = ""
            if patch_path.exists():
                try:
                    cached = patch_path.read_text(encoding="utf-8", errors="replace")
                except OSError:
                    cached = ""
                if "diff --git " in cached:
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
            patch_bytes = len((patch_text or "").encode("utf-8", errors="replace"))
            patch_path.write_text(patch_text, encoding="utf-8")
            touched_path.write_text(json.dumps(normalized_touched, ensure_ascii=False), encoding="utf-8")

            not_allowed = [p for p in normalized_touched if allow_globs and not _matches_any(p, allow_globs)]
            denied = [p for p in normalized_touched if deny_globs and _matches_any(p, deny_globs)]
            limits_violation: dict[str, Any] = {}
            max_touched_files = task.get("max_touched_files")
            max_patch_bytes = task.get("max_patch_bytes")
            if isinstance(max_touched_files, int) and max_touched_files > 0 and len(normalized_touched) > max_touched_files:
                limits_violation["max_touched_files"] = {"limit": max_touched_files, "actual": len(normalized_touched)}
            if isinstance(max_patch_bytes, int) and max_patch_bytes > 0 and patch_bytes > max_patch_bytes:
                limits_violation["max_patch_bytes"] = {"limit": max_patch_bytes, "actual": patch_bytes}
            scope_ok = not not_allowed and not denied and not limits_violation
            scope_payload = {
                "path": str(scope_path),
                "scope_name": task.get("scope_name"),
                "allow_globs": allow_globs,
                "deny_globs": deny_globs,
                "touched_files": normalized_touched,
                "limits": {"max_touched_files": max_touched_files, "max_patch_bytes": max_patch_bytes, "patch_bytes": patch_bytes},
                "violations": {"not_allowed": not_allowed, "denied": denied, "limits": limits_violation},
                "ok": scope_ok,
            }
            if allow_globs or deny_globs or not scope_ok or limits_violation:
                scope_path.write_text(json.dumps(scope_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            _timeline_append(run_id, "collect.task", slug=task.get("slug"), ok=scope_ok, touched_files=len(normalized_touched), patch_bytes=patch_bytes)
            entry: dict[str, Any] = {
                "job_id": job_id,
                "name": task.get("name"),
                "slug": task.get("slug"),
                "patch_path": str(patch_path),
                "touched_files_path": str(touched_path),
                "touched_files": normalized_touched,
                "status": "empty" if not patch_text.strip() else "ok",
                "state": task.get("state"),
                "scope": scope_payload if (allow_globs or deny_globs or not scope_ok) else None,
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
    def code_squad_capabilities_get(options: Any | None = None) -> dict[str, Any]:
        opts = _coerce_options(options)
        debug = _debug_enabled(opts)
        result: dict[str, Any] = {
            "server": {"name": app_id, "defaults": {"model": config.default_model, "sandbox": config.default_sandbox, "approval_policy": config.default_approval_policy}},
            "tools": [
                "code_squad_capabilities_get",
                "code_squad_context_pack",
                "code_squad_run",
                "code_squad_execute",
                "code_squad_tick",
                "code_squad_status",
                "code_squad_events",
                "code_squad_collect",
                "code_squad_verify",
                "code_squad_report",
                "code_squad_prune",
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

            auto_context_pack = opts.get("auto_context_pack") if isinstance(opts.get("auto_context_pack"), dict) else None

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
                allow_globs = _parse_globs(task.get("allow_globs"))
                deny_globs = _parse_globs(task.get("deny_globs"))
                scope_name = str(task.get("scope_name") or "").strip() or None
                slug = slugify(name, fallback=f"task-{idx+1}")
                existing_slugs = {t.get("slug") for t in run_meta.get("tasks", [])}
                suffix = 2
                base_slug = slug
                while slug in existing_slugs:
                    slug = f"{base_slug}-{suffix}"
                    suffix += 1

                worktree_path = ensure_repo_subpath(repo_root, worktree_base / slug)
                task_context = task.get("context_pack") if isinstance(task.get("context_pack"), dict) else None
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
                    glob_val = str(auto_context_pack.get("glob") or "*.py")
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
                    allow_globs=allow_globs,
                    deny_globs=deny_globs,
                    limits=limits,
                )
                task_model = task.get("model") or defaults.get("model") or config.default_model
                task_sandbox = task.get("sandbox") or defaults.get("sandbox") or config.default_sandbox
                task_approval = task.get("approval_policy") or defaults.get("approval_policy") or config.default_approval_policy
                raw_extra_config = task.get("extra_config") or defaults.get("extra_config") or []
                extra_config = _apply_reasoning_effort_cap(raw_extra_config, options=opts, task=task)
                job_id = f"{resolved_run_id}--{slug}-{uuid.uuid4().hex[:8]}"

                task_entry = {
                    "name": name,
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
                        }
                    )

            _save_run(resolved_run_id, run_meta)
            # Immediately enqueue tasks to the background worker.
            now = utc_now_iso()
            for task_entry in run_meta.get("tasks", []):
                if task_entry.get("state") == "queued" and not task_entry.get("worker_enqueued_at"):
                    worker.enqueue(resolved_run_id, task_entry.get("slug"))
                    task_entry["worker_enqueued_at"] = now

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
        elapsed_ms: int | None = None
        ops_log("code_squad_execute", "start", trace_id, cwd=cwd)
        try:
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
                _save_run(resolved_run_id, run_meta)
                progress = _compute_progress(run_meta)
                if progress.get("active", 0) == 0:
                    break
                if time.monotonic() >= deadline:
                    break
                time.sleep(max(0.2, poll_interval))

            run_meta = _load_run(resolved_run_id) or run_meta
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

            report_data = {
                "run_id": run_id,
                "created_at": run_meta.get("created_at"),
                "repo_root": run_meta.get("repo_root"),
                "counts": counts,
                "tasks": task_rows,
            }
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
            report_md.write_text("\n".join(lines), encoding="utf-8")
            index_path = _write_run_index(run_meta, extra={"report": {"report_json": str(report_json), "report_md": str(report_md)}})

            response: dict[str, Any] = {"run_id": run_id, "report_json": str(report_json), "report_md": str(report_md), "index_path": str(index_path), "counts": counts}
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
