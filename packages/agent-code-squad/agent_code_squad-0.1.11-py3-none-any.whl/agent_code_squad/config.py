from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import find_repo_root


def _normalize_effort(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    v = value.strip().lower()
    return v if v in ("low", "medium", "high") else None


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError:
        return None
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _normalize_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "1", "yes", "y", "on"):
            return True
        if v in ("false", "0", "no", "n", "off"):
            return False
    return None


def _coerce_dict(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _project_config_path(repo_root: Path) -> Path:
    return repo_root / ".codex" / "code-squad" / "config.json"


def _load_project_config(repo_root: Path) -> dict[str, Any] | None:
    return _read_json(_project_config_path(repo_root))


def _get_nested(cfg: dict[str, Any], *keys: str) -> Any:
    cur: Any = cfg
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur.get(k)
    return cur


@dataclass(frozen=True)
class SquadConfig:
    dispatch_dir: Path
    default_model: str
    default_sandbox: str
    default_approval_policy: str
    verbosity: int
    worker_concurrency: int
    default_reasoning_effort: str
    max_reasoning_effort: str
    default_auto_context_pack: dict[str, Any]
    enforce_sparse_checkout: bool
    early_scope_enforcement: bool
    strict_context_pack_scope: bool
    require_patch: bool


def resolve_config(
    *,
    dispatch_dir: str | None = None,
    model: str | None = None,
    sandbox: str | None = None,
    approval_policy: str | None = None,
    verbosity: int | None = None,
    worker_concurrency: int | None = None,
    cwd: str | None = None,
) -> SquadConfig:
    start_dir = Path(cwd or os.getcwd()).resolve()
    repo_root = find_repo_root(start_dir)

    project_cfg = _load_project_config(repo_root) or {}
    default_dispatch_dir = str(repo_root / ".codex" / "code-squad")

    cfg_dispatch_dir = project_cfg.get("dispatch_dir")
    raw_dispatch_dir = str(cfg_dispatch_dir or dispatch_dir or default_dispatch_dir)
    resolved_dispatch_dir = Path(raw_dispatch_dir).expanduser()
    if not resolved_dispatch_dir.is_absolute():
        resolved_dispatch_dir = (repo_root / resolved_dispatch_dir).resolve()

    cfg_model = _get_nested(project_cfg, "defaults", "model")
    cfg_sandbox = _get_nested(project_cfg, "defaults", "sandbox")
    cfg_approval = _get_nested(project_cfg, "defaults", "approval_policy")
    cfg_verbosity = _get_nested(project_cfg, "defaults", "verbosity")
    cfg_worker_concurrency = _get_nested(project_cfg, "defaults", "worker_concurrency")
    cfg_auto_context_pack = _coerce_dict(_get_nested(project_cfg, "defaults", "auto_context_pack"))

    cfg_default_effort = _get_nested(project_cfg, "energy_saver", "default_reasoning_effort")
    cfg_max_effort = _get_nested(project_cfg, "energy_saver", "max_reasoning_effort")

    cfg_enforce_sparse = _normalize_bool(_get_nested(project_cfg, "guardrails", "enforce_sparse_checkout"))
    cfg_early_scope = _normalize_bool(_get_nested(project_cfg, "guardrails", "early_scope_enforcement"))
    cfg_strict_context_pack_scope = _normalize_bool(_get_nested(project_cfg, "guardrails", "strict_context_pack_scope"))
    cfg_require_patch = _normalize_bool(_get_nested(project_cfg, "guardrails", "require_patch"))

    resolved_model = str(cfg_model or model or "gpt-5.1-codex-max")
    resolved_sandbox = str(cfg_sandbox or sandbox or "workspace-write")
    resolved_approval = str(cfg_approval or approval_policy or "never")

    resolved_verbosity = verbosity if verbosity is not None else int(cfg_verbosity or 0)
    resolved_worker_concurrency = worker_concurrency if worker_concurrency is not None else int(cfg_worker_concurrency or 2)

    default_effort = _normalize_effort(cfg_default_effort) or "medium"
    max_effort = _normalize_effort(cfg_max_effort) or "medium"

    default_auto_context_pack: dict[str, Any] = {
        "enabled": True,
        "glob": "**/*",
        "max_files": 14,
        "max_snippets": 28,
        "max_total_chars": 16_000,
        "hints": [],
    }
    if cfg_auto_context_pack:
        default_auto_context_pack.update(cfg_auto_context_pack)
    if _normalize_bool(default_auto_context_pack.get("enabled")) is False:
        default_auto_context_pack["enabled"] = False

    return SquadConfig(
        dispatch_dir=resolved_dispatch_dir,
        default_model=resolved_model,
        default_sandbox=resolved_sandbox,
        default_approval_policy=resolved_approval,
        verbosity=max(0, resolved_verbosity),
        worker_concurrency=max(1, int(resolved_worker_concurrency)),
        default_reasoning_effort=default_effort,
        max_reasoning_effort=max_effort,
        default_auto_context_pack=default_auto_context_pack,
        enforce_sparse_checkout=cfg_enforce_sparse if cfg_enforce_sparse is not None else True,
        early_scope_enforcement=cfg_early_scope if cfg_early_scope is not None else True,
        strict_context_pack_scope=cfg_strict_context_pack_scope if cfg_strict_context_pack_scope is not None else True,
        require_patch=cfg_require_patch if cfg_require_patch is not None else True,
    )
