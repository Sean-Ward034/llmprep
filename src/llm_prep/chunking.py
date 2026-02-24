"""Deterministic text chunking."""

from __future__ import annotations

import re
from typing import Iterable

from llm_prep.normalize import normalize_text


def is_heading(line: str) -> bool:
    candidate = line.strip()
    if not candidate:
        return False
    if len(candidate) > 80:
        return False
    if candidate.isupper() and len(candidate) >= 3:
        return True
    if candidate.endswith(":") and len(candidate.split()) <= 10:
        return True
    return False


def split_paragraphs(text: str) -> list[str]:
    normalized = normalize_text(text)
    if not normalized:
        return []
    parts = [part.strip() for part in re.split(r"\n\s*\n", normalized) if part.strip()]
    return parts


def _split_long_paragraph(paragraph: str, target: int) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", paragraph)
    if len(sentences) == 1:
        chunks = [paragraph[i : i + target] for i in range(0, len(paragraph), target)]
        return [chunk.strip() for chunk in chunks if chunk.strip()]

    out: list[str] = []
    cursor: list[str] = []
    total = 0
    for sentence in sentences:
        if not sentence:
            continue
        if total + len(sentence) + 1 > target * 1.2 and cursor:
            out.append(" ".join(cursor).strip())
            cursor = [sentence]
            total = len(sentence)
            continue
        cursor.append(sentence)
        total += len(sentence) + 1
    if cursor:
        out.append(" ".join(cursor).strip())
    return out


def chunk_text(paragraphs: Iterable[str], target_chars: int = 1000) -> list[str]:
    chunks: list[str] = []
    buffer: list[str] = []
    size = 0

    for paragraph in paragraphs:
        p = paragraph.strip()
        if not p:
            continue
        if len(p) > target_chars * 1.2:
            split = _split_long_paragraph(p, target_chars)
        else:
            split = [p]
        for segment in split:
            is_boundary = is_heading(segment.split("\n", 1)[0])
            seg_len = len(segment)
            if is_boundary and buffer:
                chunks.append("\n\n".join(buffer).strip())
                buffer = []
                size = 0
            if size + seg_len > target_chars * 1.2 and buffer:
                chunks.append("\n\n".join(buffer).strip())
                buffer = [segment]
                size = seg_len
            else:
                buffer.append(segment)
                size += seg_len
    if buffer:
        chunks.append("\n\n".join(buffer).strip())
    return [chunk for chunk in chunks if chunk]

