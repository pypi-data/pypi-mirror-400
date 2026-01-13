from __future__ import annotations

import queue
import subprocess
import threading
import traceback
from pathlib import Path
from typing import Any, Callable

from .dispatch import CodexDispatch, DispatchConfig
from .event_utils import extract_patch_from_stdout
from .paths import ensure_dir, ensure_repo_subpath
from .utils import read_json, utc_now_iso, write_json

DEFAULT_DEP_PATCH_MAX_BYTES = 8000


class RunStore:
    def __init__(self, base_dir: Path, lock: threading.Lock | None = None):
        self._base = ensure_dir(base_dir)
        self._lock = lock or threading.Lock()

    def run_dir(self, run_id: str) -> Path:
        return ensure_dir(self._base / "runs" / run_id)

    def run_meta_path(self, run_id: str) -> Path:
        return self.run_dir(run_id) / "run.json"

    def load(self, run_id: str) -> dict[str, Any] | None:
        return read_json(self.run_meta_path(run_id))

    def save(self, run_id: str, data: dict[str, Any]) -> None:
        with self._lock:
            write_json(self.run_meta_path(run_id), data)

    def update(self, run_id: str, updater: Callable[[dict[str, Any]], dict[str, Any] | None]) -> dict[str, Any] | None:
        with self._lock:
            current = self.load(run_id) or {}
            updated = updater(current)
            if updated is not None:
                write_json(self.run_meta_path(run_id), updated)
            return updated


class BackgroundWorker:
    """
    Processes queued tasks without blocking MCP tool calls. Performs heavy worktree/codex start steps.
    """

    def __init__(self, store: RunStore, verbosity: int = 0, concurrency: int = 2):
        self._store = store
        self._queue: queue.Queue[tuple[str, str]] = queue.Queue()
        self._verbosity = verbosity
        self._threads: list[threading.Thread] = []
        for i in range(max(1, int(concurrency))):
            thread = threading.Thread(target=self._loop, name=f"code-squad-worker-{i+1}", daemon=True)
            thread.start()
            self._threads.append(thread)

    def enqueue(self, run_id: str, slug: str) -> None:
        self._queue.put((run_id, slug))

    def _loop(self) -> None:
        while True:
            run_id, slug = self._queue.get()
            try:
                self._process(run_id, slug)
            except Exception:
                tb = traceback.format_exc()
                try:
                    self._mark_task(run_id, slug, state="failed", error=tb, finished=True)
                except Exception:
                    pass

    def _process(self, run_id: str, slug: str) -> None:
        run_meta = self._store.load(run_id)
        if not run_meta:
            return
        repo_root = Path(run_meta.get("repo_root") or ".").resolve()
        worktree_base = Path(run_meta.get("worktree_base") or (repo_root / ".codex" / "code-squad" / "worktrees" / run_id)).resolve()
        run_dir = self._store.run_dir(run_id)
        jobs_dir = ensure_dir(run_dir / "jobs")
        defaults = run_meta.get("defaults") or {}

        tasks = run_meta.get("tasks") or []
        task = next((t for t in tasks if t.get("slug") == slug), None)
        if not task:
            return
        if task.get("state") not in ("queued", "starting"):
            return

        worktree_path = Path(task.get("worktree") or worktree_base / slug)
        try:
            ensure_repo_subpath(repo_root, worktree_path)
        except ValueError as exc:
            self._mark_task(run_meta["id"], slug, state="failed", error=str(exc), finished=True)
            return

        # Mark as starting
        self._mark_task(run_meta["id"], slug, state="starting", started_at=utc_now_iso(), job_id=task.get("job_id"))

        if not worktree_path.exists():
            res = subprocess.run(
                ["git", "worktree", "add", "--detach", str(worktree_path)],
                cwd=repo_root,
                capture_output=True,
                text=True,
            )
            if res.returncode != 0:
                err_text = res.stderr or res.stdout or "git worktree add failed"
                self._mark_task(run_meta["id"], slug, state="failed", error=err_text, finished=True)
                return

        allow_globs = task.get("allow_globs")
        deny_globs = task.get("deny_globs")
        enforce_sparse = bool(task.get("enforce_sparse_checkout", False))
        if isinstance(allow_globs, list) and allow_globs:
            warning = self._try_sparse_checkout(worktree_path, allow_globs, deny_globs)
            if warning:
                if enforce_sparse:
                    self._mark_task(run_meta["id"], slug, state="failed", error=f"sparse-checkout failed: {warning}", finished=True)
                    return
                self._add_task_warning(run_id, slug, warning)

        dispatch = CodexDispatch(DispatchConfig(jobs_dir=jobs_dir, verbosity=self._verbosity))
        prompt = task.get("prompt") or ""
        if bool(task.get("include_dep_patches")):
            dep_context = self._build_dependency_patch_context(run_meta=run_meta, task=task, run_dir=run_dir)
            if dep_context:
                if prompt.strip():
                    prompt = f"{prompt.rstrip()}\n\n{dep_context}"
                else:
                    prompt = dep_context
        extra_config = task.get("extra_config") if isinstance(task.get("extra_config"), list) else []
        model = task.get("model") or defaults.get("model")
        sandbox = task.get("sandbox") or defaults.get("sandbox")
        approval_policy = task.get("approval_policy") or defaults.get("approval_policy")
        job_id = task.get("job_id")
        start_res = dispatch.start(
            prompt=prompt,
            model=model,
            cwd=str(worktree_path),
            sandbox=sandbox,
            approval_policy=approval_policy,
            extra_config=extra_config,
            job_id=job_id,
            job_id_prefix=run_id,
        )
        meta = dispatch.load_meta(start_res.get("job_id")) or {}
        pid = meta.get("pid")
        status = meta.get("status") or start_res.get("status") or "running"

        self._mark_task(
            run_meta["id"],
            slug,
            state=status if status in ("running", "completed", "failed", "cancelled") else "running",
            job_id=start_res.get("job_id"),
            pid=pid,
        )

    def _add_task_warning(self, run_id: str, slug: str, message: str) -> None:
        def updater(meta: dict[str, Any]) -> dict[str, Any]:
            tasks = meta.get("tasks") or []
            for t in tasks:
                if t.get("slug") != slug:
                    continue
                warnings = t.get("warnings")
                if not isinstance(warnings, list):
                    warnings = []
                warnings.append(str(message))
                t["warnings"] = warnings
            meta["tasks"] = tasks
            return meta

        self._store.update(run_id, updater)

    def _try_sparse_checkout(self, worktree_path: Path, allow_globs: list[Any], deny_globs: Any | None) -> str | None:
        def _prefixes(raw_globs: Any) -> list[str]:
            if not isinstance(raw_globs, list):
                return []
            prefixes: list[str] = []
            for raw in raw_globs:
                if not isinstance(raw, str):
                    continue
                s = raw.strip().replace("\\", "/")
                while s.startswith("./"):
                    s = s[2:]
                s = s.lstrip("/")
                if not s:
                    continue
                wildcard_positions = [i for i in (s.find("*"), s.find("?"), s.find("[")) if i != -1]
                cut = min(wildcard_positions) if wildcard_positions else len(s)
                prefix_raw = s[:cut]
                if not prefix_raw:
                    continue
                if prefix_raw.endswith("/"):
                    prefix = prefix_raw.rstrip("/")
                else:
                    prefix = prefix_raw.rsplit("/", 1)[0] if "/" in prefix_raw else ""
                prefix = prefix.strip("/")
                if not prefix or prefix.startswith(".."):
                    continue
                if prefix not in prefixes:
                    prefixes.append(prefix)
            return prefixes

        allow_prefixes = _prefixes(allow_globs)
        if not allow_prefixes:
            return None
        deny_prefixes = _prefixes(deny_globs)
        patterns: list[str] = []
        for p in allow_prefixes:
            patterns.append(f"{p}/**")
        for p in deny_prefixes:
            patterns.append(f"!{p}/**")

        init_res = subprocess.run(
            ["git", "sparse-checkout", "init", "--no-cone"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
        )
        if init_res.returncode != 0:
            return init_res.stderr or init_res.stdout or "git sparse-checkout init failed"

        set_res = subprocess.run(
            ["git", "sparse-checkout", "set", "--no-cone", "--skip-checks", "--stdin"],
            cwd=worktree_path,
            capture_output=True,
            text=True,
            input="\n".join(patterns) + "\n",
        )
        if set_res.returncode != 0:
            return set_res.stderr or set_res.stdout or "git sparse-checkout set failed"
        return None

    def _mark_task(
        self,
        run_id: str,
        slug: str,
        *,
        state: str | None = None,
        error: str | None = None,
        started_at: str | None = None,
        finished: bool = False,
        job_id: str | None = None,
        pid: int | None = None,
    ) -> None:
        def updater(meta: dict[str, Any]) -> dict[str, Any]:
            tasks = meta.get("tasks") or []
            for t in tasks:
                if t.get("slug") != slug:
                    continue
                if state:
                    t["state"] = state
                if error is not None:
                    t["error"] = error
                if job_id:
                    t["job_id"] = job_id
                if pid is not None:
                    t["pid"] = pid
                if started_at:
                    t["started_at"] = started_at
                if finished:
                    t["finished_at"] = utc_now_iso()
            meta["tasks"] = tasks
            return meta

        self._store.update(run_id, updater)

    def _build_dependency_patch_context(self, *, run_meta: dict[str, Any], task: dict[str, Any], run_dir: Path) -> str:
        depends_on_raw = task.get("depends_on") if isinstance(task.get("depends_on"), list) else []
        depends_on = [str(dep).strip() for dep in depends_on_raw if str(dep or "").strip()]
        if not depends_on:
            return ""
        tasks = run_meta.get("tasks") or []
        task_map = {str(t.get("slug") or ""): t for t in tasks if t.get("slug")}
        sections: list[str] = []
        max_bytes = self._resolve_dep_patch_limit(task)
        for dep_slug in depends_on:
            dep = task_map.get(dep_slug)
            if not dep:
                continue
            if str(dep.get("state") or "").lower() != "completed":
                continue
            patch_text = self._load_dependency_patch(run_dir=run_dir, dep_slug=dep_slug, dep_task=dep, max_bytes=max_bytes)
            if patch_text:
                sections.append(f"### {dep_slug}\n{patch_text.rstrip()}\n")
            else:
                sections.append(f"### {dep_slug}\npatch not found\n")
        if not sections:
            return ""
        header = "Dependency patches (read-only context)"
        return "\n\n".join([header] + sections)

    def _resolve_dep_patch_limit(self, task: dict[str, Any]) -> int | None:
        if "dep_patch_max_bytes" not in task:
            return DEFAULT_DEP_PATCH_MAX_BYTES
        raw_value = task.get("dep_patch_max_bytes")
        if raw_value is None:
            return None
        if isinstance(raw_value, int):
            return raw_value if raw_value > 0 else None
        try:
            coerced = int(raw_value)
        except (TypeError, ValueError):
            return DEFAULT_DEP_PATCH_MAX_BYTES
        return coerced if coerced > 0 else None

    def _load_dependency_patch(self, *, run_dir: Path, dep_slug: str, dep_task: dict[str, Any], max_bytes: int | None) -> str | None:
        patch_text = ""
        patch_path = run_dir / "artifacts" / "collect" / f"{dep_slug}.patch"
        if patch_path.exists():
            try:
                candidate = patch_path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                candidate = ""
            if "diff --git " in candidate:
                patch_text = candidate
        if not patch_text:
            job_id = dep_task.get("job_id")
            if job_id:
                stdout_path = run_dir / "jobs" / str(job_id) / "stdout.jsonl"
                patch_text = extract_patch_from_stdout(stdout_path)
        if not patch_text or "diff --git " not in patch_text:
            return None
        text = patch_text.strip()
        if not text:
            return None
        return self._truncate_patch(text, max_bytes)

    def _truncate_patch(self, text: str, max_bytes: int | None) -> str:
        trimmed = text.strip("\n")
        limit = max_bytes if isinstance(max_bytes, int) and max_bytes > 0 else None
        if limit is None:
            return trimmed + ("\n" if not trimmed.endswith("\n") else "")
        data = trimmed.encode("utf-8", errors="replace")
        if len(data) <= limit:
            return trimmed + ("\n" if not trimmed.endswith("\n") else "")
        sliced = data[:limit].decode("utf-8", errors="replace").rstrip()
        return f"{sliced}\n\n[truncated]\n"
