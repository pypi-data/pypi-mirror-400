from __future__ import annotations

import uuid
from typing import Any, Tuple

from ..paths import slugify

DEFAULT_SUPERVISOR_CONTEXT = {
    "enabled": True,
    "glob": "**/*",
    "max_files": 8,
    "max_snippets": 16,
    "max_total_chars": 16_000,
    "hints": [],
}


def plan_run_id(prefix: str | None = None) -> str:
    """Generate a stable slug for supervisor-managed runs."""
    token = uuid.uuid4().hex[:8]
    base = prefix or "supervisor"
    return slugify(f"{base}-{token}", fallback="supervisor")


def _sanitize_task_name(raw: Any, fallback: str) -> str:
    name = str(raw or "").strip()
    return name or fallback


def build_supervisor_plan(
    query: str,
    allow_globs,
    deny_globs,
    *,
    options: dict[str, Any],
) -> Tuple[list[dict[str, Any]], str]:
    """
    Build a minimal plan from the provided query.

    Returns (tasks, decision_reason).
    """
    plan = options.get("plan")
    if isinstance(plan, list) and plan:
        tasks: list[dict[str, Any]] = []
        for idx, raw in enumerate(plan):
            if not isinstance(raw, dict):
                continue
            prompt = str(raw.get("prompt") or "").strip()
            if not prompt:
                continue
            name = _sanitize_task_name(raw.get("name"), f"task-{idx+1}")
            task_allow = raw.get("allow_globs", allow_globs)
            task_deny = raw.get("deny_globs", deny_globs)
            task_entry = {
                "name": name,
                "prompt": prompt,
                "role": raw.get("role"),
                "scope_name": raw.get("scope_name"),
                "context_query": raw.get("context_query") or prompt,
                "allow_globs": task_allow,
                "deny_globs": task_deny,
            }
            tasks.append(task_entry)
        if tasks:
            return tasks, "user-plan"

    default_name = _sanitize_task_name(options.get("task_name"), "supervisor-task")
    cleaned_query = query.strip()
    task = {
        "name": default_name,
        "prompt": cleaned_query,
        "role": options.get("role"),
        "scope_name": options.get("scope_name"),
        "context_query": options.get("context_query") or cleaned_query,
        "allow_globs": allow_globs,
        "deny_globs": deny_globs,
    }
    return [task], "default-single-task"


def supervisor_summary_lines(
    *,
    plan_tasks: list[dict[str, Any]],
    progress: dict[str, Any],
    next_action: str,
    decision_reason: str,
) -> list[str]:
    """Compose concise summary lines for supervise responses."""
    total = int(progress.get("total") or len(plan_tasks))
    done = int(progress.get("terminal") or 0)
    return [
        f"Plan: {len(plan_tasks)} task(s); decision={decision_reason}",
        f"Progress: {done}/{total} done; next={next_action}",
    ]
