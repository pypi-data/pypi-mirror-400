from __future__ import annotations

from pathlib import Path
from typing import Any

from ..config import SquadConfig
from ..context import RipgrepNotFound
from .scopes import extract_glob_prefixes, parse_globs, rg_list_files

EXECUTION_MODES = {"direct", "batch-worktree", "fanout"}


def coerce_execution_mode(value: Any) -> str | None:
    """Normalize execution_mode inputs."""
    if not value:
        return None
    mode = str(value).strip().lower()
    return mode if mode in EXECUTION_MODES else None


def analyze_scope_layout(
    repo_root: Path,
    task_defs: list[dict[str, Any]],
    *,
    precomputed_scope: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Inspect scopes to inform execution mode."""
    prefix_counts: dict[str, int] = {}
    missing_allow = False
    sample_counts: list[int | None] = []
    task_prefixes: list[list[str]] = []
    tasks_with_prefix = 0

    for idx, task in enumerate(task_defs):
        allow = parse_globs(task.get("allow_globs"))
        deny = parse_globs(task.get("deny_globs"))
        if allow is None:
            missing_allow = True
        prefixes = extract_glob_prefixes(allow)
        task_prefixes.append(prefixes)
        if prefixes:
            tasks_with_prefix += 1
        for prefix in prefixes:
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1
        sample_count: int | None = None
        if precomputed_scope and idx < len(precomputed_scope or []):
            pre_item = precomputed_scope[idx] or {}
            if isinstance(pre_item.get("sample_count"), int):
                sample_count = int(pre_item["sample_count"])
        if sample_count is None and allow is not None:
            try:
                sample_count = len(rg_list_files(repo_root, allow_globs=allow, deny_globs=deny, limit=4))
            except RipgrepNotFound:
                sample_count = None
        sample_counts.append(sample_count)

    distinct_prefixes = sorted(prefix_counts.keys())
    overlap_prefixes = sorted(prefix for prefix, count in prefix_counts.items() if count > 1)
    numeric_samples = [count for count in sample_counts if isinstance(count, int)]
    max_sample = max(numeric_samples) if numeric_samples else None
    has_overlap = bool(overlap_prefixes)
    multi_project = (
        tasks_with_prefix >= 2
        and not missing_allow
        and not has_overlap
        and len(distinct_prefixes) >= tasks_with_prefix
    )

    return {
        "task_count": len(task_defs),
        "max_sample": max_sample,
        "missing_allow": missing_allow,
        "has_overlap": has_overlap,
        "overlap_prefixes": overlap_prefixes,
        "samples": sample_counts,
        "task_prefixes": task_prefixes,
        "distinct_prefixes": distinct_prefixes,
        "tasks_with_prefix": tasks_with_prefix,
        "multi_project": multi_project,
    }


def select_execution_mode(
    *,
    repo_root: Path,
    tasks: list[dict[str, Any]],
    opts: dict[str, Any],
    effective_config: SquadConfig,
    precomputed_scope: list[dict[str, Any]] | None = None,
) -> tuple[str, dict[str, Any]]:
    """Choose execution strategy for the provided tasks."""
    explicit = coerce_execution_mode(opts.get("execution_mode"))
    if explicit:
        return explicit, {"explicit": True, "reason": "explicit"}

    analysis = analyze_scope_layout(repo_root, tasks, precomputed_scope=precomputed_scope)
    worker_limit = getattr(effective_config, "worker_concurrency", None)
    try:
        worker_limit_val = max(1, int(worker_limit))
    except (TypeError, ValueError):
        worker_limit_val = 1

    task_count = analysis["task_count"]
    max_sample = analysis["max_sample"]
    missing_allow = analysis["missing_allow"]
    small_scope = max_sample is not None and max_sample <= 3
    multi_project = bool(analysis.get("multi_project"))

    if multi_project:
        max_tasks_for_fanout = max(4, worker_limit_val * 2)
        if worker_limit_val > 1 and 2 <= task_count <= max_tasks_for_fanout:
            mode = "fanout"
            reason = "multi_project_fanout"
        else:
            mode = "batch-worktree"
            reason = "multi_project_batch"
    else:
        if task_count <= 1:
            mode = "direct"
            reason = "single_task"
        elif task_count <= 2 and small_scope and not missing_allow:
            mode = "direct"
            reason = "small_scope"
        else:
            mode = "batch-worktree"
            reason = "shared_scope"

    return mode, {
        "explicit": False,
        "analysis": {**analysis, "worker_concurrency": worker_limit_val},
        "reason": reason,
    }
