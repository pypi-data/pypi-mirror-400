from __future__ import annotations

import queue
import subprocess
import threading
import traceback
from pathlib import Path
from typing import Any, Callable

from .dispatch import CodexDispatch, DispatchConfig
from .paths import ensure_dir, ensure_repo_subpath
from .utils import read_json, utc_now_iso, write_json


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
