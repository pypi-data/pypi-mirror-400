from __future__ import annotations

import re
import subprocess
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any

from .paths import find_repo_root, safe_relpath
from .utils import truncate_text


class RipgrepNotFound(RuntimeError):
    pass


_ROOT_PRIORITY_GLOBS = [
    "AGENTS.md",
    "README",
    "README.*",
    "CONTRIBUTING",
    "CONTRIBUTING.*",
    "pyproject.toml",
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "package-lock.json",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
    "requirements.txt",
    "requirements*.txt",
    "Makefile",
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.*.yml",
    "kustomization.yaml",
    "Chart.yaml",
]


def _normalize_relpath(value: str) -> str:
    normalized = str(value or "").replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def _matches_any(path: str, globs: list[str] | None) -> bool:
    if not globs:
        return False
    rel_path = PurePosixPath(_normalize_relpath(path))
    return any(rel_path.match(_normalize_relpath(pat)) for pat in globs if isinstance(pat, str) and pat.strip())


def _rg_globs(glob: str, *, allow_globs: list[str] | None, deny_globs: list[str] | None) -> list[str]:
    globs: list[str] = []
    if glob:
        globs.append(str(glob))
    for item in allow_globs or []:
        if isinstance(item, str) and item.strip():
            globs.append(_normalize_relpath(item.strip()))
    for item in deny_globs or []:
        if isinstance(item, str) and item.strip():
            globs.append("!" + _normalize_relpath(item.strip()))
    out: list[str] = []
    for g in globs:
        if g and g not in out:
            out.append(g)
    return out


def _list_files(root: Path, glob: str, *, allow_globs: list[str] | None = None, deny_globs: list[str] | None = None) -> list[Path]:
    try:
        globs = _rg_globs(glob, allow_globs=allow_globs, deny_globs=deny_globs)
        res = subprocess.run(
            ["rg", "--files", *[part for g in globs for part in ("-g", g)], str(root)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:  # pragma: no cover - environment specific
        raise RipgrepNotFound("ripgrep (rg) is required to build context packs") from exc
    if res.returncode not in (0, 1):
        return []
    files: list[Path] = []
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        files.append(Path(line.strip()))
    return files


def _search_term(term: str, root: Path, glob: str, *, allow_globs: list[str] | None = None, deny_globs: list[str] | None = None) -> list[tuple[Path, int]]:
    if not term or not term.strip():
        return []
    try:
        globs = _rg_globs(glob, allow_globs=allow_globs, deny_globs=deny_globs)
        res = subprocess.run(
            ["rg", "--no-heading", "--line-number", "--color", "never", *[part for g in globs for part in ("--glob", g)], term, str(root)],
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:  # pragma: no cover - environment specific
        raise RipgrepNotFound("ripgrep (rg) is required to build context packs") from exc
    if res.returncode not in (0, 1):
        return []
    matches: list[tuple[Path, int]] = []
    for line in res.stdout.splitlines():
        parts = line.split(":", 2)
        if len(parts) < 2:
            continue
        path_part, line_part = parts[0], parts[1]
        try:
            line_no = int(line_part)
        except ValueError:
            continue
        matches.append((Path(path_part), line_no))
    return matches


def _extract_snippet(path: Path, line_no: int, *, context_lines: int = 6) -> tuple[int, int, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return 1, 1, ""

    if path.suffix == ".py":
        block = _extract_python_block(lines, line_no)
        if block is not None:
            start_idx, end_idx = block
            start = start_idx + 1
            end = end_idx + 1
            text = "\n".join(lines[start_idx : end_idx + 1])
            return start, end, text

    start = max(1, line_no - context_lines)
    end = min(len(lines), line_no + context_lines)
    text = "\n".join(lines[start - 1 : end])
    return start, end, text


def _extract_head(path: Path, *, max_lines: int = 80) -> tuple[int, int, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return 1, 1, ""
    end = min(len(lines), max(1, int(max_lines)))
    return 1, end, "\n".join(lines[:end])


_PY_DEFCLASS_RE = re.compile(r"^\s*(def|class)\s+[A-Za-z_][A-Za-z0-9_]*\b")


def _extract_python_block(lines: list[str], line_no: int) -> tuple[int, int] | None:
    if not lines:
        return None
    idx = max(0, min(int(line_no) - 1, len(lines) - 1))

    def _indent(s: str) -> int:
        return len(s) - len(s.lstrip(" "))

    header_idx: int | None = None
    header_indent = 0
    for i in range(idx, -1, -1):
        if _PY_DEFCLASS_RE.match(lines[i]):
            header_idx = i
            header_indent = _indent(lines[i])
            break
    if header_idx is None:
        return None

    end_idx = len(lines) - 1
    for j in range(header_idx + 1, len(lines)):
        if _PY_DEFCLASS_RE.match(lines[j]) and _indent(lines[j]) <= header_indent:
            end_idx = j - 1
            break
    if end_idx < header_idx:
        end_idx = header_idx
    return header_idx, end_idx


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


def _scoped(rel: str, *, allow_globs: list[str] | None, deny_globs: list[str] | None) -> bool:
    if allow_globs and not _matches_any(rel, allow_globs):
        return False
    if deny_globs and _matches_any(rel, deny_globs):
        return False
    return True


def _priority_paths(repo_root: Path, *, allow_globs: list[str] | None, deny_globs: list[str] | None) -> list[Path]:
    priority: list[Path] = []

    def add(path: Path) -> None:
        try:
            rel = safe_relpath(path, repo_root)
        except ValueError:
            return
        if not _scoped(rel, allow_globs=allow_globs, deny_globs=deny_globs):
            return
        if path not in priority:
            priority.append(path)

    # Repo-root constraints + entry docs/configs.
    for pat in _ROOT_PRIORITY_GLOBS:
        for p in repo_root.glob(pat):
            if p.is_file():
                add(p)

    # If scoped to a module prefix, try a few common "module entry" files under that prefix.
    for prefix in _extract_glob_prefixes(allow_globs):
        base = repo_root / prefix
        if not base.exists() or not base.is_dir():
            continue
        for pat in ("AGENTS.md", "README", "README.*", "__init__.py", "main.*", "index.*", "app.*", "server.*", "cli.*"):
            for p in base.glob(pat):
                if p.is_file():
                    add(p)

    return priority


def build_context_pack(
    *,
    cwd: str,
    query: str,
    hints: list[str] | None = None,
    glob: str = "*.py",
    allow_globs: list[str] | None = None,
    deny_globs: list[str] | None = None,
    max_files: int = 12,
    max_snippets: int = 24,
    max_total_chars: int = 20_000,
) -> dict[str, Any]:
    repo_root = find_repo_root(Path(cwd))
    files_considered = _list_files(repo_root, glob, allow_globs=allow_globs, deny_globs=deny_globs)

    snippets: list[dict[str, Any]] = []
    seen_paths: set[Path] = set()
    total_chars = 0

    for path in _priority_paths(repo_root, allow_globs=allow_globs, deny_globs=deny_globs):
        if len(snippets) >= max_snippets or len(seen_paths) >= max_files:
            break
        start, end, text = _extract_head(path, max_lines=80)
        rel_path = safe_relpath(path, repo_root)
        snippet_text = truncate_text(text, max_total_chars - total_chars) if max_total_chars > total_chars else ""
        snippets.append({"path": rel_path, "start_line": start, "end_line": end, "text": snippet_text})
        total_chars += len(snippet_text)
        seen_paths.add(path)
        if total_chars >= max_total_chars:
            break

    terms: list[str] = []
    if query:
        terms.append(query)
    if hints:
        terms.extend([h for h in hints if h])

    matches: list[tuple[Path, int]] = []
    for term in terms:
        term_matches = _search_term(term, repo_root, glob, allow_globs=allow_globs, deny_globs=deny_globs)
        for match in term_matches:
            matches.append(match)

    # Deduplicate and order by path + line
    unique_matches: list[tuple[Path, int]] = []
    seen_keys: set[tuple[Path, int]] = set()
    for path, line_no in sorted(matches, key=lambda t: (str(t[0]), t[1])):
        key = (path, line_no)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_matches.append(key)

    if allow_globs or deny_globs:
        scoped: list[tuple[Path, int]] = []
        for path, line_no in unique_matches:
            rel = safe_relpath(path, repo_root)
            if allow_globs and not _matches_any(rel, allow_globs):
                continue
            if deny_globs and _matches_any(rel, deny_globs):
                continue
            scoped.append((path, line_no))
        unique_matches = scoped

    # If nothing matched, seed with the first files so the pack is not empty.
    if not unique_matches and files_considered:
        for path in files_considered[: max_files]:
            unique_matches.append((path, 1))

    for path, line_no in unique_matches:
        if len(snippets) >= max_snippets or len(seen_paths) >= max_files:
            break
        if path in seen_paths:
            continue
        start, end, text = _extract_snippet(path, line_no)
        rel_path = safe_relpath(path, repo_root)
        snippet_text = truncate_text(text, max_total_chars - total_chars) if max_total_chars > total_chars else ""
        snippets.append(
            {
                "path": rel_path,
                "start_line": start,
                "end_line": end,
                "text": snippet_text,
            }
        )
        total_chars += len(snippet_text)
        seen_paths.add(path)
        if total_chars >= max_total_chars:
            break

    return {
        "root": str(repo_root),
        "query": query,
        "hints": hints or [],
        "glob": glob,
        "allow_globs": allow_globs or [],
        "deny_globs": deny_globs or [],
        "limits": {
            "max_files": max_files,
            "max_snippets": max_snippets,
            "max_total_chars": max_total_chars,
        },
        "files_considered": [safe_relpath(p, repo_root) for p in files_considered[:max_files]],
        "snippets": snippets,
        "truncated": total_chars >= max_total_chars,
    }
