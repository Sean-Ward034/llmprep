#!/usr/bin/env python3
"""
Prototype: Compact LLM-optimized output format for llmprep.

Goals:
  1. MINIMIZE token usage (smaller than raw input where possible)
  2. STRUCTURE data so LLMs produce better output

Key design decisions:
  - Markdown tables instead of JSON arrays for tabular data
  - Row sampling for large datasets (schema + stats + sample)
  - Clean text with minimal wrapping (no JSON per-chunk)
  - Compact entity/task representation
  - Strip all machine metadata (checksums, UUIDs, provenance)
"""

import csv
import json
import os
import re
import statistics
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


def compact_csv(path: Path, sample_rows: int = 20) -> str:
    """Convert CSV to a compact, LLM-optimized representation.

    Strategy:
    - Include column names and inferred types
    - Show row count and basic stats for numeric columns
    - Sample rows (first N + last 5) instead of including everything
    - Use Markdown table format (far fewer tokens than JSON arrays)
    """
    with open(path, newline="", errors="replace") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if not rows:
        return "[Empty CSV file]"

    headers = rows[0]
    data = rows[1:]
    total_rows = len(data)

    # Infer types and compute stats for numeric columns
    col_stats: dict[int, dict[str, Any]] = {}
    for col_idx, header in enumerate(headers):
        values = [r[col_idx] for r in data if col_idx < len(r) and r[col_idx].strip()]
        numeric_vals = []
        for v in values:
            try:
                numeric_vals.append(float(v))
            except ValueError:
                pass

        if len(numeric_vals) > len(values) * 0.5:
            col_stats[col_idx] = {
                "type": "numeric",
                "min": min(numeric_vals),
                "max": max(numeric_vals),
                "mean": statistics.mean(numeric_vals),
            }
        else:
            unique = set(values)
            if len(unique) <= 15:
                col_stats[col_idx] = {"type": "categorical", "values": sorted(unique)[:15]}
            else:
                col_stats[col_idx] = {"type": "text", "unique": len(unique)}

    lines = []
    lines.append(f"# {path.name}")
    lines.append(f"Rows: {total_rows} | Columns: {len(headers)}")
    lines.append("")

    # Column summary
    lines.append("## Schema")
    for i, h in enumerate(headers):
        stats = col_stats.get(i, {})
        if stats.get("type") == "numeric":
            lines.append(f"- **{h}** (numeric): range [{stats['min']:.4g}, {stats['max']:.4g}], mean {stats['mean']:.4g}")
        elif stats.get("type") == "categorical":
            vals = ", ".join(stats["values"][:10])
            lines.append(f"- **{h}** (categorical): {vals}")
        else:
            lines.append(f"- **{h}** (text): {stats.get('unique', '?')} unique values")
    lines.append("")

    # Sample rows as Markdown table
    if total_rows <= sample_rows:
        sample = data
        lines.append(f"## All Data ({total_rows} rows)")
    else:
        head_n = min(sample_rows - 5, total_rows)
        tail_n = min(5, total_rows - head_n)
        sample = data[:head_n]
        if tail_n > 0:
            sample.append(["..." for _ in headers])
            sample.extend(data[-tail_n:])
        lines.append(f"## Sample ({head_n} of {total_rows} rows, plus last {tail_n})")

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for row in sample:
        cells = [(row[i] if i < len(row) else "") for i in range(len(headers))]
        lines.append("| " + " | ".join(cells) + " |")

    return "\n".join(lines)


def compact_html(path: Path) -> str:
    """Convert HTML to clean Markdown-like text + Markdown tables."""
    html = path.read_text(errors="replace")
    soup = BeautifulSoup(html, "lxml")

    # Remove noise
    for tag in soup(["script", "style", "noscript", "link", "meta"]):
        tag.extract()

    lines = []
    title = soup.find("title")
    if title:
        lines.append(f"# {title.get_text(strip=True)}")
        lines.append("")

    # Extract tables as Markdown
    tables_found = []
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [cell.get_text(separator=" ", strip=True) for cell in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if rows:
            tables_found.append(rows)
        table.extract()

    # Remaining text
    text = soup.get_text(separator="\n", strip=True)
    # Collapse excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    if text.strip():
        lines.append(text.strip())
        lines.append("")

    # Append tables
    for i, table_rows in enumerate(tables_found, 1):
        if not table_rows:
            continue
        headers = table_rows[0]
        lines.append(f"### Table {i}")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
        for row in table_rows[1:]:
            cells = [(row[j] if j < len(row) else "") for j in range(len(headers))]
            lines.append("| " + " | ".join(cells) + " |")
        lines.append("")

    return "\n".join(lines)


def compact_text(path: Path) -> str:
    """For text files, extract key-value pairs and structure minimally.

    Strategy: keep the text almost as-is, but prepend extracted
    entities/key-values in a compact header.
    """
    text = path.read_text(errors="replace").strip()

    # Extract key-value pairs (simple heuristic)
    kvs = []
    for line in text.split("\n"):
        line = line.strip()
        if ":" in line and len(line) < 200:
            parts = line.split(":", 1)
            key = parts[0].strip().lstrip("- ")
            val = parts[1].strip()
            if key and val and len(key) < 60:
                kvs.append((key, val))

    lines = []
    lines.append(f"# {path.name}")

    if kvs:
        lines.append("")
        lines.append("## Key Information")
        for k, v in kvs[:20]:
            lines.append(f"- **{k}**: {v}")

    lines.append("")
    lines.append("## Content")
    lines.append(text)

    return "\n".join(lines)


def process_file(path: Path) -> str:
    """Route to the appropriate compact processor."""
    ext = path.suffix.lower()
    if ext == ".csv":
        return compact_csv(path)
    elif ext in (".html", ".htm"):
        return compact_html(path)
    else:
        return compact_text(path)


def main():
    doc_dir = Path("benchmark/test_documents")
    out_dir = Path("benchmark/compact_output")
    out_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("Compact Format Prototype - Side-by-Side Comparison")
    print("=" * 70)
    print()
    print(f"{'Document':<25s} {'Raw':>8s} {'Ragpack':>8s} {'Compact':>8s} {'vs Raw':>8s} {'vs Ragpk':>8s}")
    print("-" * 75)

    total_raw = 0
    total_ragpack = 0
    total_compact = 0

    for doc in sorted(doc_dir.iterdir()):
        name = doc.stem
        ext = doc.suffix.lstrip(".")

        raw_size = doc.stat().st_size
        compact_text_out = process_file(doc)

        compact_path = out_dir / f"{name}.compact.md"
        compact_path.write_text(compact_text_out)
        compact_size = len(compact_text_out.encode("utf-8"))

        rp_dir = Path("benchmark/ragpacks") / name / "ragpack"
        rp_size = sum(
            f.stat().st_size
            for f in rp_dir.iterdir()
            if f.name not in ("run_log.jsonl",)
        )

        total_raw += raw_size
        total_ragpack += rp_size
        total_compact += compact_size

        vs_raw = compact_size / raw_size if raw_size else 0
        vs_rp = compact_size / rp_size if rp_size else 0

        print(f"{name:<25s} {raw_size:>7,d} {rp_size:>8,d} {compact_size:>8,d} {vs_raw:>7.2f}x {vs_rp:>7.2f}x")

    print("-" * 75)
    print(f"{'TOTAL':<25s} {total_raw:>7,d} {total_ragpack:>8,d} {total_compact:>8,d} "
          f"{total_compact/total_raw:>7.2f}x {total_compact/total_ragpack:>7.2f}x")
    print()

    # Now do token comparison using tiktoken
    print("Running token comparison with gpt-4o tokenizer...")
    import tiktoken
    enc = tiktoken.get_encoding("o200k_base")

    print()
    print(f"{'Document':<25s} {'Raw Tok':>8s} {'Ragpk Tok':>10s} {'Compact Tok':>12s} {'Savings vs Raw':>15s} {'Savings vs Rp':>15s}")
    print("-" * 90)

    total_raw_tok = 0
    total_rp_tok = 0
    total_compact_tok = 0

    for doc in sorted(doc_dir.iterdir()):
        name = doc.stem
        raw_text = doc.read_text(errors="replace")
        raw_tok = len(enc.encode(raw_text))

        rp_dir = Path("benchmark/ragpacks") / name / "ragpack"
        rp_parts = []
        for fname in ["doc_chunks.jsonl", "tables.jsonl", "entities.json", "task_spec.json"]:
            fp = rp_dir / fname
            if fp.exists():
                rp_parts.append(fp.read_text())
        rp_text = "\n".join(rp_parts)
        rp_tok = len(enc.encode(rp_text))

        compact_path = Path("benchmark/compact_output") / f"{name}.compact.md"
        compact_text_content = compact_path.read_text()
        compact_tok = len(enc.encode(compact_text_content))

        total_raw_tok += raw_tok
        total_rp_tok += rp_tok
        total_compact_tok += compact_tok

        savings_raw = (1 - compact_tok / raw_tok) * 100 if raw_tok else 0
        savings_rp = (1 - compact_tok / rp_tok) * 100 if rp_tok else 0

        print(f"{name:<25s} {raw_tok:>8,d} {rp_tok:>10,d} {compact_tok:>12,d} "
              f"{savings_raw:>+14.1f}% {savings_rp:>+14.1f}%")

    print("-" * 90)
    savings_raw_total = (1 - total_compact_tok / total_raw_tok) * 100
    savings_rp_total = (1 - total_compact_tok / total_rp_tok) * 100
    print(f"{'TOTAL':<25s} {total_raw_tok:>8,d} {total_rp_tok:>10,d} {total_compact_tok:>12,d} "
          f"{savings_raw_total:>+14.1f}% {savings_rp_total:>+14.1f}%")
    print()
    print(f"Compact format uses {total_compact_tok/total_raw_tok:.2f}x tokens vs raw input")
    print(f"Compact format uses {total_compact_tok/total_rp_tok:.2f}x tokens vs current ragpack")
    print(f"Current ragpack uses {total_rp_tok/total_raw_tok:.2f}x tokens vs raw input")


if __name__ == "__main__":
    main()
