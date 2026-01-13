from __future__ import annotations

import os
import re
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    start = start.resolve()
    for path in [start, *start.parents]:
        git_marker = path / ".git"
        if git_marker.is_dir() or git_marker.is_file():
            return path
    for path in [start, *start.parents]:
        if (path / ".codex").is_dir():
            return path
    return start


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def slugify(value: str, fallback: str = "task") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9\-_.]+", "-", value or "").strip("-._")
    cleaned = re.sub(r"-{2,}", "-", cleaned)
    if not cleaned:
        cleaned = fallback
    return cleaned.lower()


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def safe_relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path.resolve())


def ensure_repo_subpath(root: Path, subpath: Path) -> Path:
    resolved = subpath.resolve()
    if not is_within(resolved, root):
        raise ValueError(f"Path {resolved} escapes repository root {root}")
    return resolved
