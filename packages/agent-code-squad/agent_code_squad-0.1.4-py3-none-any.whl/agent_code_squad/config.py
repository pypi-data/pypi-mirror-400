from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .paths import find_repo_root


def _env_first(names: list[str], default: str | None = None) -> str | None:
    for name in names:
        val = os.environ.get(name)
        if val is not None and str(val).strip() != "":
            return str(val)
    return default


def _env_int(name: str, default: int = 0) -> int:
    raw = os.environ.get(name)
    if raw is None or str(raw).strip() == "":
        return default
    try:
        return int(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class SquadConfig:
    dispatch_dir: Path
    default_model: str
    default_sandbox: str
    default_approval_policy: str
    verbosity: int
    worker_concurrency: int


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

    default_dispatch_dir = _env_first(
        ["AGENT_CODE_SQUAD_DISPATCH_DIR", "MCP_DISPATCH_DIR"],
        default=str(repo_root / ".codex" / "code-squad"),
    )
    resolved_dispatch_dir = Path(dispatch_dir or default_dispatch_dir or repo_root / ".codex" / "code-squad").expanduser()

    resolved_model = model or _env_first(["AGENT_CODE_SQUAD_MODEL"], default="gpt-5.1-codex-max") or "gpt-5.1-codex-max"
    resolved_sandbox = sandbox or _env_first(["AGENT_CODE_SQUAD_SANDBOX"], default="workspace-write") or "workspace-write"
    resolved_approval = approval_policy or _env_first(["AGENT_CODE_SQUAD_APPROVAL_POLICY"], default="never") or "never"
    resolved_verbosity = verbosity if verbosity is not None else _env_int("AGENT_CODE_SQUAD_VERBOSITY", 0)
    resolved_worker_concurrency = (
        worker_concurrency
        if worker_concurrency is not None
        else _env_int("AGENT_CODE_SQUAD_WORKER_CONCURRENCY", 2)
    )

    return SquadConfig(
        dispatch_dir=resolved_dispatch_dir,
        default_model=resolved_model,
        default_sandbox=resolved_sandbox,
        default_approval_policy=resolved_approval,
        verbosity=max(0, resolved_verbosity),
        worker_concurrency=max(1, int(resolved_worker_concurrency)),
    )
