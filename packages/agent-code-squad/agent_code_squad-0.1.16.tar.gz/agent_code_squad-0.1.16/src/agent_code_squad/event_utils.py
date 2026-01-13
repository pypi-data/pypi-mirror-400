from __future__ import annotations

import json
from pathlib import Path
from typing import Any


NOISE_EVENT_TYPES = {
    "thread.started",
    "thread.created",
    "turn.started",
    "turn.created",
    "turn.delta",
    "turn.completed",
    "turn.finished",
    "run.started",
    "run.finished",
    "response.started",
    "response.completed",
    "response.finished",
    "thread_started",
    "thread_created",
    "turn_started",
    "turn_created",
    "turn_delta",
    "turn_completed",
    "turn_finished",
    "run_started",
    "run_finished",
    "response_started",
    "response_completed",
    "response_finished",
    "heartbeat",
    "ping",
    "pong",
    "item.started",
    "item.updated",
}

NOISY_ITEM_TYPES = {"command_execution", "mcp_tool_call", "todo_list"}

EVENT_NOISE_TYPES = {
    "thread.started",
    "thread.created",
    "turn.started",
    "turn.created",
    "turn.delta",
    "run.started",
    "run.finished",
    "response.started",
    "response.completed",
    "response.finished",
    "thread_started",
    "thread_created",
    "turn_started",
    "turn_created",
    "turn_delta",
    "run_started",
    "run_finished",
    "response_started",
    "response_completed",
    "response_finished",
    "heartbeat",
    "ping",
    "pong",
}


def _try_parse_json(value: Any) -> Any:
    if not isinstance(value, str):
        return None
    s = value.strip()
    if not s:
        return None
    if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            return None
    return None


def iter_event_text(obj: Any) -> list[str]:
    out: list[str] = []

    def walk(node: Any) -> None:
        if node is None:
            return
        if isinstance(node, str):
            out.append(node)
            parsed = _try_parse_json(node)
            if parsed is not None:
                walk(parsed)
            return
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if isinstance(node, dict):
            ctype = node.get("type")
            if isinstance(ctype, str) and (ctype in NOISE_EVENT_TYPES or ctype in NOISY_ITEM_TYPES):
                return
            for key in ("text", "message", "content", "item"):
                if key in node:
                    walk(node.get(key))
            return
        # ignore scalars

    walk(obj)
    return out


def extract_patch_from_stdout(stdout_jsonl: Path) -> str:
    try:
        lines = stdout_jsonl.read_text(encoding="utf-8", errors="replace").splitlines()
    except FileNotFoundError:
        return ""
    candidates: list[str] = []
    for line in lines:
        s = (line or "").strip()
        if not s:
            continue
        try:
            obj = json.loads(s)
        except json.JSONDecodeError:
            continue
        for text in iter_event_text(obj):
            if "diff --git " in text:
                candidates.append(text)
    if not candidates:
        return ""

    def normalize(text: str) -> str:
        start = text.find("diff --git ")
        if start == -1:
            return ""
        block = text[start:]
        cleaned_lines: list[str] = []
        for raw_line in block.splitlines():
            line = raw_line.rstrip("\n")
            if line.strip() == "```":
                continue
            if line.strip().startswith("```"):
                continue
            cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip() + "\n"

    best = ""
    for c in candidates:
        normalized = normalize(c)
        if len(normalized) > len(best):
            best = normalized
    return best

