from __future__ import annotations

import hashlib
import json
import os
import signal
import subprocess
import threading
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import ensure_dir
from .utils import read_json, utc_now_iso, write_json


def _sha256(text: str) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _read_text_tail(path: Path, max_bytes: int) -> str | None:
    if max_bytes <= 0:
        return None
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            start = max(0, size - max_bytes)
            f.seek(start)
            data = f.read()
            return data.decode("utf-8", errors="replace")
    except FileNotFoundError:
        return None


def _read_jsonl_events_from_offset(path: Path, start_offset: int, *, max_bytes: int, max_items: int) -> tuple[list[dict[str, Any]], int, bool]:
    events: list[dict[str, Any]] = []
    start = max(0, int(start_offset or 0))
    if max_bytes <= 0 or max_items <= 0:
        return events, start, False
    try:
        with path.open("rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            if start >= size:
                return events, size, False
            f.seek(start)
            buf = f.read(max_bytes)
    except FileNotFoundError:
        return events, start, False

    i = 0
    consumed = 0
    while i < len(buf) and len(events) < max_items:
        j = buf.find(b"\n", i)
        if j == -1:
            break
        line = buf[i:j].strip()
        i = j + 1
        consumed = i
        if not line:
            continue
        try:
            obj = json.loads(line.decode("utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    next_cursor = start + consumed
    has_more = next_cursor < size
    return events, next_cursor, has_more


def _safe_kill(pid: int) -> None:
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    except PermissionError:
        return


@dataclass(frozen=True)
class DispatchConfig:
    jobs_dir: Path
    verbosity: int = 0


class CodexDispatch:
    def __init__(self, config: DispatchConfig):
        self._config = config
        ensure_dir(self._config.jobs_dir)
        self._lock = threading.Lock()
        self._threads: dict[str, threading.Thread] = {}

    @property
    def jobs_dir(self) -> Path:
        return self._config.jobs_dir

    def _job_dir(self, job_id: str) -> Path:
        return self.jobs_dir / job_id

    def _meta_path(self, job_id: str) -> Path:
        return self._job_dir(job_id) / "meta.json"

    def load_meta(self, job_id: str) -> dict[str, Any] | None:
        return read_json(self._meta_path(job_id))

    def _write_meta(self, job_id: str, data: dict[str, Any]) -> None:
        with self._lock:
            write_json(self._meta_path(job_id), data)

    def start(
        self,
        *,
        prompt: str,
        model: str | None,
        cwd: str | None,
        sandbox: str | None,
        approval_policy: str | None,
        extra_config: list[str] | None = None,
        env: dict[str, str] | None = None,
        job_id: str | None = None,
        job_id_prefix: str | None = None,
    ) -> dict[str, Any]:
        resolved_job_id = str(job_id).strip() if job_id else ""
        if not resolved_job_id:
            base_id = uuid.uuid4().hex
            resolved_job_id = f"{job_id_prefix}--{base_id}" if job_id_prefix else base_id

        existing_meta = self.load_meta(resolved_job_id)
        if existing_meta and existing_meta.get("status"):
            artifacts = existing_meta.get("artifacts") or {}
            return {
                "job_id": resolved_job_id,
                "status": existing_meta.get("status"),
                "artifacts": artifacts,
                "existing": True,
            }

        job_dir = self._job_dir(resolved_job_id)
        ensure_dir(job_dir)
        stdout_path = job_dir / "stdout.jsonl"
        stderr_path = job_dir / "stderr.log"
        last_msg_path = job_dir / "last_message.txt"

        cmd: list[str] = ["codex"]
        if approval_policy:
            cmd += ["-a", approval_policy]
        if model:
            cmd += ["-m", model]
        if sandbox:
            cmd += ["-s", sandbox]
        for cfg in extra_config or []:
            if cfg:
                cmd += ["-c", cfg]
        # Worktrees often have a `.git` file (not a directory). Codex CLI's repo check can treat
        # these as "not inside a git repo" unless `--skip-git-repo-check` is provided.
        cmd += ["exec"]
        if cwd:
            cmd += ["-C", cwd]
        cmd += ["--skip-git-repo-check", "--json", "--color", "never", "--output-last-message", str(last_msg_path), "-"]

        meta = {
            "id": resolved_job_id,
            "created_at": utc_now_iso(),
            "status": "running",
            "prompt_sha256": _sha256(prompt),
            "cwd": cwd,
            "model": model,
            "sandbox": sandbox,
            "approval_policy": approval_policy,
            "command": cmd,
            "artifacts": {
                "job_dir": str(job_dir),
                "stdout_jsonl": str(stdout_path),
                "stderr_log": str(stderr_path),
                "last_message": str(last_msg_path),
            },
            "pid": None,
        }
        self._write_meta(resolved_job_id, meta)

        def run() -> None:
            try:
                env_vars = os.environ.copy()
                if env:
                    env_vars.update({str(k): str(v) for k, v in env.items()})
                with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
                    process = subprocess.Popen(
                        cmd,
                        stdin=subprocess.PIPE,
                        stdout=out,
                        stderr=err,
                        env=env_vars,
                    )
                    assert process.stdin is not None
                    self._write_meta(resolved_job_id, {**meta, "pid": process.pid})
                    process.stdin.write((prompt or "").encode("utf-8"))
                    process.stdin.close()
                    exit_code = process.wait()
                final_meta = self.load_meta(resolved_job_id) or meta
                final_meta.update(
                    {
                        "status": "completed" if exit_code == 0 else "failed",
                        "exit_code": exit_code,
                        "finished_at": utc_now_iso(),
                    }
                )
                self._write_meta(resolved_job_id, final_meta)
            except Exception as exc:  # pragma: no cover - defensive
                fail_meta = self.load_meta(resolved_job_id) or meta
                fail_meta.update({"status": "failed", "error": repr(exc), "finished_at": utc_now_iso()})
                self._write_meta(resolved_job_id, fail_meta)

        thread = threading.Thread(target=run, name=f"codex-dispatch-{resolved_job_id}", daemon=True)
        with self._lock:
            self._threads[resolved_job_id] = thread
        thread.start()

        return {"job_id": resolved_job_id, "status": "running", "artifacts": meta["artifacts"]}

    def status(
        self,
        *,
        job_id: str,
        include_last_message: bool = True,
        last_message_max_bytes: int = 2000,
        stdout_max_bytes: int = 4000,
        stderr_max_bytes: int = 4000,
    ) -> dict[str, Any]:
        meta = self.load_meta(job_id)
        if not meta:
            return {"found": False, "job_id": job_id}

        artifacts = meta.get("artifacts") or {}
        stdout_path = Path(str(artifacts.get("stdout_jsonl") or ""))
        stderr_path = Path(str(artifacts.get("stderr_log") or ""))
        last_msg_path = Path(str(artifacts.get("last_message") or ""))

        stdout_tail = _read_text_tail(stdout_path, stdout_max_bytes)
        stderr_tail = _read_text_tail(stderr_path, stderr_max_bytes)
        last_message = _read_text_tail(last_msg_path, last_message_max_bytes) if include_last_message else None

        return {
            "found": True,
            "job_id": job_id,
            "meta": meta,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "last_message": last_message,
        }

    def events(
        self,
        *,
        job_id: str,
        cursor: int | None = None,
        max_items: int = 100,
        max_bytes: int = 4000,
    ) -> dict[str, Any]:
        meta = self.load_meta(job_id)
        if not meta:
            return {"found": False, "job_id": job_id, "events": [], "cursor": cursor or 0, "has_more": False}
        artifacts = meta.get("artifacts") or {}
        stdout_path = Path(str(artifacts.get("stdout_jsonl") or ""))
        events, next_cursor, has_more = _read_jsonl_events_from_offset(
            stdout_path,
            cursor or 0,
            max_bytes=max_bytes,
            max_items=max_items,
        )
        return {"found": True, "job_id": job_id, "events": events, "cursor": next_cursor, "has_more": has_more}

    def cancel(self, *, job_id: str, reason: str | None = None) -> dict[str, Any]:
        meta = self.load_meta(job_id)
        if not meta:
            return {"found": False, "job_id": job_id}
        pid = meta.get("pid")
        if isinstance(pid, int):
            _safe_kill(pid)
        updated = {**meta, "status": "cancelled", "cancel_reason": reason, "finished_at": utc_now_iso()}
        self._write_meta(job_id, updated)
        return {"found": True, "job_id": job_id, "status": "cancelled"}
