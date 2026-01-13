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

TIMELINE_EVENT_DESCRIPTIONS = {
    "run.queued": "任务已排队",
    "finalize.enqueued": "已排队收尾流程",
    "finalize.start": "开始收尾",
    "finalize.collect": "正在收集补丁",
    "finalize.verify": "正在校验",
    "finalize.cleanup": "正在清理工作树",
    "finalize.done": "收尾完成",
    "finalize.error": "收尾出错",
    "finalize.timeout": "收尾超时",
    "collect.task": "完成补丁收集",
    "scope.early_check": "完成范围校验",
}

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


def describe_timeline_event(event: dict[str, Any] | None) -> str:
    if not isinstance(event, dict):
        return ""
    name = str(event.get("event") or "").strip()
    if not name:
        return ""
    base = TIMELINE_EVENT_DESCRIPTIONS.get(name)
    if base:
        if name == "collect.task" and event.get("slug"):
            return f"{base}:{event['slug']}"
        if name == "scope.early_check" and event.get("slug"):
            return f"{base}:{event['slug']}"
        if name == "run.queued" and isinstance(event.get("tasks"), int):
            return f"{base}:{event['tasks']} 个"
        return base
    return name
