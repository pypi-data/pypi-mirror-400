from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .paths import ensure_dir, slugify
from .utils import read_json, utc_now_iso, write_json


@dataclass
class SharedKB:
    path: Path
    session_id: str
    repo_root: str
    head_sha: str
    epoch: int
    created_at: str
    updated_at: str
    static: dict[str, Any]
    recent_changes: list[dict[str, Any]]
    version: int = 1

    def _persist(self) -> None:
        payload: dict[str, Any] = {
            "version": int(self.version),
            "session_id": self.session_id,
            "repo_root": self.repo_root,
            "head_sha": self.head_sha,
            "epoch": int(self.epoch),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "static": self.static,
            "recent_changes": self.recent_changes,
        }
        write_json(self.path, payload)

    def maybe_rebuild_on_head_change(self, head_sha: str) -> str:
        new_head = str(head_sha or "").strip()
        if not new_head:
            return "hit"
        if new_head == self.head_sha:
            return "hit"
        self.epoch = max(1, int(self.epoch or 0)) + 1
        self.head_sha = new_head
        self.static = {}
        self.updated_at = utc_now_iso()
        self._persist()
        return "rebuild"

    def append_run_start(self, *, run_id: str, execution_mode: str, guardrails: dict[str, Any], defaults: dict[str, Any]) -> None:
        self.static = {
            "last_run": {
                "run_id": str(run_id or ""),
                "ts": utc_now_iso(),
                "execution_mode": str(execution_mode or ""),
                "guardrails": guardrails or {},
                "defaults": defaults or {},
                "epoch": int(self.epoch),
                "head_sha": self.head_sha,
            }
        }
        self.updated_at = utc_now_iso()
        self._persist()

    def append_collect(
        self,
        *,
        run_id: str,
        slug: str,
        touched_files: list[str],
        patch_bytes: int,
        scope_ok: bool,
        error: str | None,
    ) -> None:
        entry: dict[str, Any] = {
            "ts": utc_now_iso(),
            "run_id": str(run_id or ""),
            "slug": str(slug or ""),
            "touched_files": touched_files or [],
            "patch_bytes": int(patch_bytes or 0),
            "scope_ok": bool(scope_ok),
            "error": (str(error).strip() if error else None),
            "epoch": int(self.epoch),
            "head_sha": self.head_sha,
        }
        self.recent_changes.append(entry)
        if len(self.recent_changes) > 20:
            self.recent_changes = self.recent_changes[-20:]
        self.updated_at = utc_now_iso()
        self._persist()

    def summary(self) -> str:
        return f"shared_kb: epoch={int(self.epoch)}"


def load_or_init(*, dispatch_dir: Path, session_id: str, repo_root: Path) -> SharedKB:
    safe_session = slugify(str(session_id or ""), fallback="default")
    base = ensure_dir(Path(dispatch_dir) / "sessions" / safe_session)
    path = base / "kb.json"
    now = utc_now_iso()
    raw = read_json(path)
    if not isinstance(raw, dict):
        kb = SharedKB(
            path=path,
            session_id=safe_session,
            repo_root=str(repo_root.resolve()),
            head_sha="",
            epoch=1,
            created_at=now,
            updated_at=now,
            static={},
            recent_changes=[],
        )
        kb._persist()
        return kb

    try:
        epoch = int(raw.get("epoch") or 1)
    except (TypeError, ValueError):
        epoch = 1
    recent = raw.get("recent_changes") if isinstance(raw.get("recent_changes"), list) else []
    static = raw.get("static") if isinstance(raw.get("static"), dict) else {}
    kb = SharedKB(
        path=path,
        session_id=str(raw.get("session_id") or safe_session),
        repo_root=str(raw.get("repo_root") or str(repo_root.resolve())),
        head_sha=str(raw.get("head_sha") or ""),
        epoch=max(1, epoch),
        created_at=str(raw.get("created_at") or now),
        updated_at=str(raw.get("updated_at") or now),
        static=static,
        recent_changes=[item for item in recent if isinstance(item, dict)][-20:],
    )
    return kb
