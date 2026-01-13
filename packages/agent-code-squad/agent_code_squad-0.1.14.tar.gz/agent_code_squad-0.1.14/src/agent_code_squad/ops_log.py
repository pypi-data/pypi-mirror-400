from __future__ import annotations

import traceback
from pathlib import Path
from typing import Any

from .paths import find_repo_root, ensure_dir
from .utils import utc_now_iso


def _log_path(cwd: str | None) -> Path:
    root = find_repo_root(Path(cwd or ".").resolve())
    return ensure_dir(root / ".codex") / "operations-log.md"


def log(tool: str, state: str, trace_id: str, *, cwd: str | None = None, msg: str | None = None, elapsed_ms: int | None = None) -> None:
    """
    Minimal, non-throwing ops log. Writes a single line per event.
    """
    try:
        line_parts: list[str] = [
            utc_now_iso(),
            f"tool={tool}",
            f"trace={trace_id}",
            f"state={state}",
        ]
        if elapsed_ms is not None:
            line_parts.append(f"elapsed_ms={elapsed_ms}")
        if msg:
            line_parts.append(f"msg={msg}")
        path = _log_path(cwd)
        with path.open("a", encoding="utf-8") as f:
            f.write(" ".join(line_parts) + "\n")
    except Exception:  # pragma: no cover - defensive
        try:
            fallback = Path.home() / ".codex" / "operations-log.md"
            ensure_dir(fallback.parent)
            with fallback.open("a", encoding="utf-8") as f:
                f.write(f"{utc_now_iso()} tool={tool} trace={trace_id} state={state} error={traceback.format_exc().strip()}\n")
        except Exception:
            return
