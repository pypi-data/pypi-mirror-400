from __future__ import annotations

import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

from ..context import RipgrepNotFound
from ..paths import safe_relpath


def normalize_relpath(path: str) -> str:
    """Normalize repo-relative paths for glob comparisons."""
    normalized = str(path or "").replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def parse_globs(value: Any) -> list[str] | None:
    """Coerce user-provided glob lists into normalized patterns."""
    if not isinstance(value, list):
        return None
    globs: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            globs.append(normalize_relpath(item.strip()))
    return globs or None


def matches_any(path: str, globs: list[str] | None) -> bool:
    """Return True when the path matches any pattern in globs."""
    if not globs:
        return False
    rel = normalize_relpath(path)
    rel_path = PurePosixPath(rel)
    for pat in globs:
        if rel_path.match(pat):
            return True
        if pat.endswith("/**"):
            prefix = pat[:-3].rstrip("/")
            if prefix and not any(ch in prefix for ch in "*?[]"):
                if rel == prefix or rel.startswith(prefix + "/"):
                    return True
    return False


def scoped(path: str, *, allow_globs: list[str] | None, deny_globs: list[str] | None) -> bool:
    """Check whether a path falls within the allow/deny scope."""
    if allow_globs and not matches_any(path, allow_globs):
        return False
    if deny_globs and matches_any(path, deny_globs):
        return False
    return True


def extract_glob_prefixes(globs: list[str] | None) -> list[str]:
    """Extract stable directory prefixes from user globs (if any)."""
    if not globs:
        return []
    prefixes: list[str] = []
    for raw in globs:
        if not isinstance(raw, str):
            continue
        s = normalize_relpath(raw.strip())
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


def rg_list_files(
    repo_root: Path,
    *,
    allow_globs: list[str] | None,
    deny_globs: list[str] | None,
    limit: int,
) -> list[str]:
    """Sample repo files within the provided glob scope."""
    globs: list[str] = []
    for item in allow_globs or []:
        if isinstance(item, str) and item.strip():
            globs.append(normalize_relpath(item.strip()))
    for item in deny_globs or []:
        if isinstance(item, str) and item.strip():
            globs.append("!" + normalize_relpath(item.strip()))
    cmd: list[str] = ["rg", "--files"]
    for g in globs:
        cmd += ["-g", g]
    cmd.append(".")
    try:
        res = subprocess.run(cmd, cwd=repo_root, check=False, capture_output=True, text=True)
    except FileNotFoundError as exc:  # pragma: no cover - environment specific
        raise RipgrepNotFound("ripgrep (rg) is required to preview scopes") from exc
    if res.returncode not in (0, 1):
        return []
    out: list[str] = []
    for line in (res.stdout or "").splitlines():
        p = line.strip()
        if not p:
            continue
        path_obj = Path(p)
        if path_obj.is_absolute():
            try:
                rel = safe_relpath(path_obj, repo_root)
            except ValueError:
                continue
            rel = normalize_relpath(rel)
        else:
            rel = normalize_relpath(str(path_obj))
        if not rel or rel.startswith(".."):
            continue
        if scoped(rel, allow_globs=allow_globs, deny_globs=deny_globs):
            out.append(rel)
        if len(out) >= max(1, int(limit or 0)):
            break
    return out
