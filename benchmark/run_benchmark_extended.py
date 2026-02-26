#!/usr/bin/env python3
"""
llmprep Extended Token Benchmark
=================================
Extended version with more models, additional metrics, and deeper analysis.
Adds ungated models that don't require HF authentication.
"""

import csv
import json
import os
import sys
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Tokenizer definitions
# ---------------------------------------------------------------------------

TIKTOKEN_MODELS = {
    "gpt-4o": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "gpt-2": "gpt2",
    "text-davinci-003": "p50k_base",
}

HF_MODELS = [
    ("mistralai/Mistral-7B-v0.1", "Mistral-7B"),
    ("microsoft/phi-2", "Phi-2"),
    ("microsoft/phi-1_5", "Phi-1.5"),
    ("Qwen/Qwen2.5-0.5B", "Qwen-2.5"),
    ("Qwen/Qwen2-0.5B", "Qwen-2"),
    ("deepseek-ai/DeepSeek-V2-Lite", "DeepSeek-V2"),
    ("deepseek-ai/deepseek-coder-1.3b-base", "DeepSeek-Coder"),
    ("THUDM/glm-4-9b", "GLM-4"),
    ("01-ai/Yi-1.5-6B", "Yi-1.5"),
    ("EleutherAI/gpt-neox-20b", "GPT-NeoX"),
    ("EleutherAI/pythia-1b", "Pythia-1B"),
    ("EleutherAI/gpt-j-6b", "GPT-J"),
    ("tiiuae/falcon-7b", "Falcon-7B"),
    ("bigscience/bloom-560m", "BLOOM"),
    ("bigscience/bloomz-560m", "BLOOMZ"),
    ("allenai/OLMo-1B-hf", "OLMo-1B"),
    ("stabilityai/stablelm-2-1_6b", "StableLM-2"),
    ("HuggingFaceTB/SmolLM2-135M", "SmolLM-2"),
    ("HuggingFaceH4/starchat-beta", "StarChat"),
    ("codellama/CodeLlama-7b-hf", "CodeLlama-7B"),
    ("Salesforce/codegen-350M-mono", "CodeGen"),
    ("bigcode/starcoder", "StarCoder"),
    ("mosaicml/mpt-7b", "MPT-7B"),
    ("togethercomputer/RedPajama-INCITE-7B-Base", "RedPajama-7B"),
    ("facebook/opt-1.3b", "OPT-1.3B"),
]


def load_tiktoken_tokenizers():
    import tiktoken
    tokenizers = {}
    for model_name, encoding_name in TIKTOKEN_MODELS.items():
        try:
            enc = tiktoken.get_encoding(encoding_name)
            tokenizers[model_name] = ("tiktoken", enc)
            print(f"  [tiktoken] {model_name}")
        except Exception as e:
            print(f"  [tiktoken] SKIP {model_name}: {e}")
    return tokenizers


def load_hf_tokenizers():
    from transformers import AutoTokenizer
    tokenizers = {}
    for model_id, short_name in HF_MODELS:
        try:
            tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            tokenizers[short_name] = ("hf", tok)
            print(f"  [HF] {short_name}")
        except Exception as e:
            msg = str(e)
            if "gated" in msg.lower() or "restricted" in msg.lower():
                print(f"  [HF] SKIP {short_name} (gated)")
            else:
                print(f"  [HF] SKIP {short_name}: {msg[:80]}")
    return tokenizers


def count_tokens(tokenizer_entry, text: str) -> int:
    kind, tok = tokenizer_entry
    if kind == "tiktoken":
        return len(tok.encode(text))
    else:
        return len(tok.encode(text, add_special_tokens=False))


def read_file(path: str) -> str:
    with open(path, "r", errors="replace") as f:
        return f.read()


def read_ragpack_content(ragpack_dir: str) -> str:
    ragpack_path = Path(ragpack_dir) / "ragpack"
    if not ragpack_path.exists():
        return ""
    parts = []
    for fname in ["doc_chunks.jsonl", "tables.jsonl", "entities.json", "task_spec.json"]:
        fpath = ragpack_path / fname
        if fpath.exists():
            with open(fpath) as f:
                parts.append(f.read())
    return "\n".join(parts)


def read_ragpack_full(ragpack_dir: str) -> str:
    ragpack_path = Path(ragpack_dir) / "ragpack"
    if not ragpack_path.exists():
        return ""
    parts = []
    for fname in ["doc_chunks.jsonl", "tables.jsonl", "entities.json",
                   "task_spec.json", "manifest.json", "validation_report.json"]:
        fpath = ragpack_path / fname
        if fpath.exists():
            with open(fpath) as f:
                parts.append(f.read())
    return "\n".join(parts)


def read_ragpack_chunks_only(ragpack_dir: str) -> str:
    """Read only the doc_chunks.jsonl for a pure text-content comparison."""
    fpath = Path(ragpack_dir) / "ragpack" / "doc_chunks.jsonl"
    if fpath.exists():
        with open(fpath) as f:
            return f.read()
    return ""


@dataclass
class Result:
    document: str
    doc_type: str
    doc_size_bytes: int
    model: str
    raw_tokens: int
    ragpack_content_tokens: int
    ragpack_full_tokens: int
    ragpack_chunks_tokens: int
    raw_chars: int
    ragpack_content_chars: int
    token_change_content_pct: float
    token_change_full_pct: float
    token_change_chunks_pct: float
    raw_chars_per_token: float
    ragpack_chars_per_token: float


def run():
    print("=" * 70)
    print("llmprep Extended Token Benchmark")
    print("=" * 70)

    doc_dir = Path("benchmark/test_documents")
    ragpack_base = Path("benchmark/ragpacks")
    documents = sorted(doc_dir.iterdir())
    print(f"\n{len(documents)} test documents\n")

    print("Loading tokenizers...")
    all_tokenizers = {}
    all_tokenizers.update(load_tiktoken_tokenizers())
    all_tokenizers.update(load_hf_tokenizers())
    n_tok = len(all_tokenizers)
    print(f"\n{n_tok} tokenizers loaded\n")

    total = len(documents) * n_tok
    print(f"Running {total} benchmark tests...")
    print("-" * 70)

    results: list[Result] = []
    count = 0
    t0 = time.time()

    for doc_path in documents:
        doc_name = doc_path.stem
        doc_ext = doc_path.suffix.lstrip(".")
        doc_size = doc_path.stat().st_size

        raw_text = read_file(str(doc_path))
        rp_dir = str(ragpack_base / doc_name)
        rp_content = read_ragpack_content(rp_dir)
        rp_full = read_ragpack_full(rp_dir)
        rp_chunks = read_ragpack_chunks_only(rp_dir)

        for model_name, tok_entry in all_tokenizers.items():
            count += 1
            rt = count_tokens(tok_entry, raw_text)
            ct = count_tokens(tok_entry, rp_content)
            ft = count_tokens(tok_entry, rp_full)
            cht = count_tokens(tok_entry, rp_chunks) if rp_chunks else 0

            def pct_change(raw, processed):
                return ((raw - processed) / raw * 100) if raw > 0 else 0

            results.append(Result(
                document=doc_name,
                doc_type=doc_ext,
                doc_size_bytes=doc_size,
                model=model_name,
                raw_tokens=rt,
                ragpack_content_tokens=ct,
                ragpack_full_tokens=ft,
                ragpack_chunks_tokens=cht,
                raw_chars=len(raw_text),
                ragpack_content_chars=len(rp_content),
                token_change_content_pct=round(pct_change(rt, ct), 2),
                token_change_full_pct=round(pct_change(rt, ft), 2),
                token_change_chunks_pct=round(pct_change(rt, cht), 2),
                raw_chars_per_token=round(len(raw_text) / rt, 2) if rt else 0,
                ragpack_chars_per_token=round(len(rp_content) / ct, 2) if ct else 0,
            ))

            if count % 50 == 0 or count == total:
                print(f"  [{count:>4d}/{total}] {time.time()-t0:.1f}s")

    elapsed = time.time() - t0
    print(f"\n{count} tests completed in {elapsed:.1f}s\n")

    # Save CSV
    results_dir = Path("benchmark/results")
    results_dir.mkdir(exist_ok=True)
    csv_path = results_dir / "extended_benchmark_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Document", "Doc_Type", "Doc_Size_Bytes", "Model",
                     "Raw_Tokens", "Ragpack_Content_Tokens", "Ragpack_Full_Tokens",
                     "Ragpack_Chunks_Tokens", "Raw_Chars", "Ragpack_Content_Chars",
                     "Token_Change_Content_Pct", "Token_Change_Full_Pct",
                     "Token_Change_Chunks_Pct",
                     "Raw_Chars_Per_Token", "Ragpack_Chars_Per_Token"])
        for r in results:
            w.writerow([r.document, r.doc_type, r.doc_size_bytes, r.model,
                         r.raw_tokens, r.ragpack_content_tokens, r.ragpack_full_tokens,
                         r.ragpack_chunks_tokens, r.raw_chars, r.ragpack_content_chars,
                         r.token_change_content_pct, r.token_change_full_pct,
                         r.token_change_chunks_pct,
                         r.raw_chars_per_token, r.ragpack_chars_per_token])
    print(f"CSV: {csv_path}")

    # Generate report
    generate_extended_report(results, results_dir)


def generate_extended_report(results: list[Result], results_dir: Path):
    lines = []
    w = lines.append

    models = sorted(set(r.model for r in results))
    documents = sorted(set(r.document for r in results))
    doc_types = sorted(set(r.doc_type for r in results))

    w("# llmprep Extended Token Benchmark Report")
    w("")
    w(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    w(f"**Total measurements**: {len(results)}")
    w(f"**Models**: {len(models)}")
    w(f"**Documents**: {len(documents)}")
    w(f"**Document types**: {', '.join(doc_types)}")
    w("")

    # ---- KEY FINDINGS ----
    w("## Key Findings")
    w("")
    w("llmprep converts raw documents into structured, LLM-ready ragpacks containing:")
    w("- **doc_chunks.jsonl**: Text broken into semantically meaningful chunks with metadata")
    w("- **tables.jsonl**: Extracted and structured table data")
    w("- **entities.json**: Named entities, dates, amounts, organizations extracted")
    w("- **task_spec.json**: Inferred task categories and heuristics")
    w("- **manifest.json**: Processing metadata (hashes, timing, config)")
    w("- **validation_report.json**: Data quality checks")
    w("")
    w("The ragpack format trades token count for **structure and reliability**:")
    w("- JSON wrapping adds overhead but makes content machine-parseable")
    w("- Entity extraction pre-computes information that LLMs would otherwise infer")
    w("- Chunk boundaries prevent mid-sentence splits common with naive truncation")
    w("- Deterministic hashing enables caching and change detection")
    w("")

    # ---- TOKEN OVERHEAD BY FORMAT ----
    w("## Token Overhead by Output Layer")
    w("")
    w("Comparing different layers of ragpack output to understand where tokens go:")
    w("")
    w("| Model | Chunks Only (Δ%) | Content (chunks+tables+entities+tasks) (Δ%) | Full (all files) (Δ%) |")
    w("|-------|------------------:|--------------------------------------------:|----------------------:|")

    for model in models:
        mr = [r for r in results if r.model == model]
        avg_chunks = sum(r.token_change_chunks_pct for r in mr) / len(mr)
        avg_content = sum(r.token_change_content_pct for r in mr) / len(mr)
        avg_full = sum(r.token_change_full_pct for r in mr) / len(mr)
        w(f"| {model} | {avg_chunks:+.1f}% | {avg_content:+.1f}% | {avg_full:+.1f}% |")
    w("")

    # ---- PER-MODEL OVERVIEW ----
    w("## Per-Model Token Analysis")
    w("")
    w("| Model | Avg Raw Tokens | Avg Ragpack Content Tokens | Avg Overhead Ratio | Avg Chars/Token (raw) | Avg Chars/Token (ragpack) |")
    w("|-------|---------------:|---------------------------:|-------------------:|----------------------:|--------------------------:|")
    for model in models:
        mr = [r for r in results if r.model == model]
        avg_raw = sum(r.raw_tokens for r in mr) / len(mr)
        avg_rp = sum(r.ragpack_content_tokens for r in mr) / len(mr)
        ratio = avg_rp / avg_raw if avg_raw else 0
        avg_cpt_raw = sum(r.raw_chars_per_token for r in mr) / len(mr)
        avg_cpt_rp = sum(r.ragpack_chars_per_token for r in mr) / len(mr)
        w(f"| {model} | {avg_raw:,.0f} | {avg_rp:,.0f} | {ratio:.2f}x | {avg_cpt_raw:.2f} | {avg_cpt_rp:.2f} |")
    w("")

    # ---- PER-DOCUMENT OVERVIEW ----
    w("## Per-Document Token Analysis")
    w("")
    w("| Document | Type | Size | Avg Raw Tokens | Avg Ragpack Tokens | Overhead Ratio | Content Richness |")
    w("|----------|------|-----:|---------------:|-------------------:|---------------:|-----------------:|")
    for doc in documents:
        dr = [r for r in results if r.document == doc]
        doc_type = dr[0].doc_type
        doc_size = dr[0].doc_size_bytes
        avg_raw = sum(r.raw_tokens for r in dr) / len(dr)
        avg_rp = sum(r.ragpack_content_tokens for r in dr) / len(dr)
        ratio = avg_rp / avg_raw if avg_raw else 0
        size_str = f"{doc_size/1024:.1f}KB" if doc_size > 1024 else f"{doc_size}B"

        ragpack_path = Path("benchmark/ragpacks") / doc / "ragpack"
        chunks_file = ragpack_path / "doc_chunks.jsonl"
        entities_file = ragpack_path / "entities.json"
        tables_file = ragpack_path / "tables.jsonl"
        n_chunks = 0
        n_entities = 0
        n_tables = 0
        if chunks_file.exists():
            with open(chunks_file) as f:
                n_chunks = sum(1 for _ in f)
        if entities_file.exists():
            with open(entities_file) as f:
                data = json.load(f)
                n_entities = len(data.get("entities", []))
        if tables_file.exists():
            with open(tables_file) as f:
                n_tables = sum(1 for _ in f)
        richness = f"{n_chunks}ch/{n_tables}tb/{n_entities}ent"
        w(f"| {doc} | {doc_type} | {size_str} | {avg_raw:,.0f} | {avg_rp:,.0f} | {ratio:.2f}x | {richness} |")
    w("")

    # ---- BY DOCUMENT TYPE ----
    w("## Token Analysis by Document Type")
    w("")
    w("| Type | # Docs | Avg Raw Tokens | Avg Ragpack Tokens | Avg Overhead Ratio |")
    w("|------|-------:|---------------:|-------------------:|-------------------:|")
    for dtype in doc_types:
        tr = [r for r in results if r.doc_type == dtype]
        n_docs = len(set(r.document for r in tr))
        avg_raw = sum(r.raw_tokens for r in tr) / len(tr)
        avg_rp = sum(r.ragpack_content_tokens for r in tr) / len(tr)
        ratio = avg_rp / avg_raw if avg_raw else 0
        w(f"| {dtype} | {n_docs} | {avg_raw:,.0f} | {avg_rp:,.0f} | {ratio:.2f}x |")
    w("")

    # ---- SIZE CATEGORY ----
    w("## Analysis by Document Size")
    w("")
    size_cats = [
        ("Small (< 5 KB)", 0, 5*1024),
        ("Medium (5-25 KB)", 5*1024, 25*1024),
        ("Large (25-100 KB)", 25*1024, 100*1024),
        ("Very Large (> 100 KB)", 100*1024, float("inf")),
    ]
    w("| Size Category | # Docs | Avg Overhead Ratio | Avg Extra Tokens |")
    w("|---------------|-------:|-------------------:|-----------------:|")
    for cat_name, lo, hi in size_cats:
        cr = [r for r in results if lo <= r.doc_size_bytes < hi]
        if cr:
            n_docs = len(set(r.document for r in cr))
            ratios = [(r.ragpack_content_tokens / r.raw_tokens if r.raw_tokens else 0) for r in cr]
            avg_ratio = sum(ratios) / len(ratios)
            avg_extra = sum(r.ragpack_content_tokens - r.raw_tokens for r in cr) / len(cr)
            w(f"| {cat_name} | {n_docs} | {avg_ratio:.2f}x | {avg_extra:+,.0f} |")
    w("")

    # ---- CROSS-REFERENCE TABLE ----
    w("## Document × Model Token Overhead Ratio")
    w("")
    w("Values show ragpack/raw token ratio (1.0 = same size, >1.0 = ragpack larger).")
    w("")

    header = "| Document |"
    sep = "|----------|"
    for m in models:
        short = m[:12]
        header += f" {short} |"
        sep += "----------:|"
    w(header)
    w(sep)

    for doc in documents:
        row = f"| {doc[:20]} |"
        for model in models:
            match = [r for r in results if r.document == doc and r.model == model]
            if match:
                r = match[0]
                ratio = r.ragpack_content_tokens / r.raw_tokens if r.raw_tokens else 0
                row += f" {ratio:.2f}x |"
            else:
                row += " - |"
        w(row)
    w("")

    # ---- BEST/WORST CASES ----
    w("## Most Efficient Conversions (lowest overhead)")
    w("")
    w("| Rank | Document | Model | Raw Tokens | Ragpack Tokens | Ratio |")
    w("|-----:|----------|-------|-----------:|---------------:|------:|")
    by_ratio = sorted(results, key=lambda r: (r.ragpack_content_tokens / r.raw_tokens) if r.raw_tokens else 999)
    for i, r in enumerate(by_ratio[:15], 1):
        ratio = r.ragpack_content_tokens / r.raw_tokens if r.raw_tokens else 0
        w(f"| {i} | {r.document} | {r.model} | {r.raw_tokens:,} | {r.ragpack_content_tokens:,} | {ratio:.2f}x |")
    w("")

    w("## Highest Overhead Conversions")
    w("")
    w("| Rank | Document | Model | Raw Tokens | Ragpack Tokens | Ratio |")
    w("|-----:|----------|-------|-----------:|---------------:|------:|")
    for i, r in enumerate(by_ratio[-15:], 1):
        ratio = r.ragpack_content_tokens / r.raw_tokens if r.raw_tokens else 0
        w(f"| {i} | {r.document} | {r.model} | {r.raw_tokens:,} | {r.ragpack_content_tokens:,} | {ratio:.2f}x |")
    w("")

    # ---- STATISTICS ----
    w("## Statistical Summary")
    w("")
    ratios = [(r.ragpack_content_tokens / r.raw_tokens if r.raw_tokens else 0) for r in results]
    ratios_sorted = sorted(ratios)
    n = len(ratios_sorted)
    mean_r = sum(ratios) / n
    median_r = ratios_sorted[n // 2]
    variance = sum((x - mean_r) ** 2 for x in ratios) / n
    std_r = variance ** 0.5

    w("| Metric | Value |")
    w("|--------|------:|")
    w(f"| Total measurements | {n} |")
    w(f"| Mean overhead ratio | {mean_r:.2f}x |")
    w(f"| Median overhead ratio | {median_r:.2f}x |")
    w(f"| Std deviation | {std_r:.2f} |")
    w(f"| Min ratio (best) | {min(ratios):.2f}x |")
    w(f"| Max ratio (worst) | {max(ratios):.2f}x |")
    w(f"| P10 | {ratios_sorted[int(n*0.1)]:.2f}x |")
    w(f"| P25 | {ratios_sorted[int(n*0.25)]:.2f}x |")
    w(f"| P75 | {ratios_sorted[int(n*0.75)]:.2f}x |")
    w(f"| P90 | {ratios_sorted[int(n*0.9)]:.2f}x |")
    w("")

    # ---- MODEL FAMILIES ----
    w("## Model Family Comparison")
    w("")
    families = {
        "OpenAI": [m for m in models if m.startswith("gpt") or m.startswith("text-")],
        "Meta": [m for m in models if "Llama" in m or "OPT" in m or "Code" in m and "Llama" in m],
        "Mistral": [m for m in models if "Mistral" in m],
        "Microsoft": [m for m in models if "Phi" in m],
        "Alibaba (Qwen)": [m for m in models if "Qwen" in m],
        "DeepSeek": [m for m in models if "DeepSeek" in m],
        "EleutherAI": [m for m in models if m in ("GPT-NeoX", "Pythia-1B", "GPT-J")],
        "BigScience": [m for m in models if "BLOOM" in m],
        "Code Models": [m for m in models if any(c in m for c in ["Code", "Star", "CodeGen"])],
        "Other": [m for m in models if not any(k in m for k in
            ["gpt", "text-", "Llama", "OPT", "Mistral", "Phi", "Qwen", "DeepSeek",
             "GPT-Neo", "GPT-J", "Pythia", "BLOOM", "Code", "Star", "CodeGen"])],
    }

    w("| Family | Models | Avg Overhead Ratio | Avg Raw Tokens/Doc |")
    w("|--------|-------:|-------------------:|-------------------:|")
    for family, fam_models in families.items():
        fam_models = [m for m in fam_models if m in models]
        if not fam_models:
            continue
        fr = [r for r in results if r.model in fam_models]
        if fr:
            ratios_f = [(r.ragpack_content_tokens/r.raw_tokens if r.raw_tokens else 0) for r in fr]
            avg_ratio = sum(ratios_f) / len(ratios_f)
            avg_raw = sum(r.raw_tokens for r in fr) / len(fr)
            w(f"| {family} | {len(fam_models)} | {avg_ratio:.2f}x | {avg_raw:,.0f} |")
    w("")

    # ---- WHAT YOU GET FOR THE TOKENS ----
    w("## What You Get for the Token Overhead")
    w("")
    w("For each document, llmprep extracts structured information that would otherwise")
    w("require the LLM to infer. This table shows the structured output per document:")
    w("")
    w("| Document | Type | Raw Size | Chunks | Tables | Entities | Tasks | Structure Density |")
    w("|----------|------|------:|-------:|-------:|---------:|------:|------------------:|")

    for doc in documents:
        dr = [r for r in results if r.document == doc][0]
        ragpack_path = Path("benchmark/ragpacks") / doc / "ragpack"

        n_chunks = 0
        n_entities = 0
        n_tables = 0
        n_tasks = 0

        chunks_file = ragpack_path / "doc_chunks.jsonl"
        if chunks_file.exists():
            with open(chunks_file) as f:
                n_chunks = sum(1 for _ in f)

        entities_file = ragpack_path / "entities.json"
        if entities_file.exists():
            with open(entities_file) as f:
                data = json.load(f)
                n_entities = len(data.get("entities", []))

        tables_file = ragpack_path / "tables.jsonl"
        if tables_file.exists():
            with open(tables_file) as f:
                n_tables = sum(1 for _ in f)

        task_file = ragpack_path / "task_spec.json"
        if task_file.exists():
            with open(task_file) as f:
                data = json.load(f)
                n_tasks = len(data.get("tasks", []))

        total_structures = n_chunks + n_tables + n_entities + n_tasks
        density = total_structures / (dr.doc_size_bytes / 1024) if dr.doc_size_bytes > 0 else 0
        size_str = f"{dr.doc_size_bytes/1024:.1f}KB" if dr.doc_size_bytes > 1024 else f"{dr.doc_size_bytes}B"
        w(f"| {doc} | {dr.doc_type} | {size_str} | {n_chunks} | {n_tables} | {n_entities} | {n_tasks} | {density:.1f}/KB |")
    w("")

    w("---")
    w(f"*Extended benchmark: {len(results)} measurements across {len(models)} models and {len(documents)} documents.*")

    report_path = results_dir / "extended_benchmark_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"Report: {report_path}")

    # Print summary
    print(f"\n{'='*70}")
    print("EXTENDED BENCHMARK SUMMARY")
    print(f"{'='*70}")
    print(f"Tests:           {len(results)}")
    print(f"Models:          {len(models)}")
    print(f"Documents:       {len(documents)}")
    print(f"Mean overhead:   {mean_r:.2f}x")
    print(f"Median overhead: {median_r:.2f}x")
    print(f"Min overhead:    {min(ratios):.2f}x")
    print(f"Max overhead:    {max(ratios):.2f}x")
    print()

    print("Per-Model Summary:")
    print(f"  {'Model':<20s} {'Overhead':>10s} {'Avg Raw':>12s} {'Avg Ragpack':>12s}")
    print("  " + "-" * 58)
    for model in models:
        mr = [r for r in results if r.model == model]
        avg_raw = sum(r.raw_tokens for r in mr) / len(mr)
        avg_rp = sum(r.ragpack_content_tokens for r in mr) / len(mr)
        ratio = avg_rp / avg_raw if avg_raw else 0
        print(f"  {model:<20s} {ratio:>9.2f}x {avg_raw:>12,.0f} {avg_rp:>12,.0f}")


if __name__ == "__main__":
    run()
