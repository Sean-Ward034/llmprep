"""Heuristic task extraction from plain text content."""

from __future__ import annotations

import re
from typing import Iterable

from llm_prep import SCHEMA_VERSION
from llm_prep.models import TaskItem, TaskSpecData
from llm_prep.normalize import stable_id


TASK_PREFIXES = ("please", "need to", "we should", "i want", "can you")


def _task_confidence(line: str) -> float:
    lower = line.lower().strip()
    if re.match(r"^[-*•]\s+", line) or re.match(r"^\d+\.\s+", line):
        return 0.9
    if lower.startswith(TASK_PREFIXES):
        return 0.75
    if "action items" in lower:
        return 0.7
    return 0.55


def extract_tasks(text_segments: Iterable[dict]) -> TaskSpecData:
    tasks: list[TaskItem] = []
    for seg in text_segments:
        locator = seg.get("locator", "unknown")
        text = seg.get("text", "")
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lower = line.lower()
            is_candidate = bool(re.match(r"^[-*•]\s+", line))
            is_candidate = is_candidate or bool(re.match(r"^\d+\.\s+", line))
            is_candidate = is_candidate or lower.startswith(TASK_PREFIXES)
            is_candidate = is_candidate or lower.startswith("action items:")
            if not is_candidate:
                continue
            cleaned = re.sub(r"^[-*•]\s+|^\d+\.\s+", "", line).strip()
            task_id = stable_id([locator, cleaned])
            tasks.append(
                TaskItem(
                    id=task_id,
                    title=cleaned[:120],
                    description=cleaned,
                    priority_hint="high" if cleaned.lower().startswith(("please", "need to")) else None,
                    source_locator=locator,
                    confidence=_task_confidence(line),
                )
            )
    # Stable order for deterministic output.
    tasks.sort(key=lambda item: (item.id, item.source_locator))
    return TaskSpecData(schema_version=SCHEMA_VERSION, tasks=tasks)

