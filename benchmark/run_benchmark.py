#!/usr/bin/env python3
"""
llmprep Token Benchmark
========================
Compares token counts for raw documents vs llmprep-processed ragpacks
across many open-source LLM tokenizers.

Measures:
  - Raw file token count
  - llmprep ragpack token count (combined JSONL/JSON outputs)
  - Token reduction percentage
  - Characters per token ratio
  - Information density metrics
"""

import csv
import json
import os
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Tokenizer loading helpers
# ---------------------------------------------------------------------------

TIKTOKEN_MODELS = {
    "gpt-4o": "o200k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "gpt-2": "gpt2",
    "text-davinci-003": "p50k_base",
}

HF_MODELS = [
    ("meta-llama/Llama-3.2-1B", "Llama-3.2"),
    ("mistralai/Mistral-7B-v0.1", "Mistral-7B"),
    ("microsoft/phi-2", "Phi-2"),
    ("Qwen/Qwen2.5-0.5B", "Qwen-2.5"),
    ("google/gemma-2-2b", "Gemma-2"),
    ("deepseek-ai/DeepSeek-V2-Lite", "DeepSeek-V2"),
    ("THUDM/glm-4-9b", "GLM-4"),
    ("01-ai/Yi-1.5-6B", "Yi-1.5"),
    ("EleutherAI/gpt-neox-20b", "GPT-NeoX"),
    ("tiiuae/falcon-7b", "Falcon-7B"),
    ("bigscience/bloom-560m", "BLOOM"),
    ("allenai/OLMo-1B-hf", "OLMo-1B"),
    ("stabilityai/stablelm-2-1_6b", "StableLM-2"),
    ("HuggingFaceTB/SmolLM2-135M", "SmolLM-2"),
    ("CohereForAI/c4ai-command-r-v01", "Command-R"),
]


def load_tiktoken_tokenizers():
    """Load tiktoken-based tokenizers (OpenAI models)."""
    import tiktoken
    tokenizers = {}
    for model_name, encoding_name in TIKTOKEN_MODELS.items():
        try:
            enc = tiktoken.get_encoding(encoding_name)
            tokenizers[model_name] = ("tiktoken", enc)
            print(f"  [tiktoken] Loaded {model_name} ({encoding_name})")
        except Exception as e:
            print(f"  [tiktoken] SKIP {model_name}: {e}")
    return tokenizers


def load_hf_tokenizers():
    """Load HuggingFace tokenizers for open-source models."""
    from transformers import AutoTokenizer
    tokenizers = {}
    for model_id, short_name in HF_MODELS:
        try:
            tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
            tokenizers[short_name] = ("hf", tok)
            print(f"  [HF] Loaded {short_name} ({model_id})")
        except Exception as e:
            print(f"  [HF] SKIP {short_name}: {e}")
    return tokenizers


def count_tokens(tokenizer_entry, text: str) -> int:
    """Count tokens for a given text using a tokenizer."""
    kind, tok = tokenizer_entry
    if kind == "tiktoken":
        return len(tok.encode(text))
    else:
        return len(tok.encode(text, add_special_tokens=False))


# ---------------------------------------------------------------------------
# Document and ragpack reading
# ---------------------------------------------------------------------------

def read_raw_document(path: str) -> str:
    """Read a raw document as text."""
    with open(path, "r", errors="replace") as f:
        return f.read()


def read_ragpack(ragpack_dir: str) -> str:
    """Read all ragpack output files and concatenate them."""
    ragpack_path = Path(ragpack_dir) / "ragpack"
    if not ragpack_path.exists():
        return ""

    parts = []
    target_files = [
        "doc_chunks.jsonl",
        "tables.jsonl",
        "entities.json",
        "task_spec.json",
        "manifest.json",
        "validation_report.json",
    ]
    for fname in target_files:
        fpath = ragpack_path / fname
        if fpath.exists():
            with open(fpath, "r") as f:
                parts.append(f.read())

    return "\n".join(parts)


def read_ragpack_content_only(ragpack_dir: str) -> str:
    """Read only the content-bearing ragpack files (chunks + tables + entities)."""
    ragpack_path = Path(ragpack_dir) / "ragpack"
    if not ragpack_path.exists():
        return ""

    parts = []
    content_files = ["doc_chunks.jsonl", "tables.jsonl", "entities.json", "task_spec.json"]
    for fname in content_files:
        fpath = ragpack_path / fname
        if fpath.exists():
            with open(fpath, "r") as f:
                parts.append(f.read())

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Benchmark result data
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    document: str
    doc_type: str
    doc_size_bytes: int
    model: str
    tokenizer_type: str
    raw_tokens: int
    ragpack_full_tokens: int
    ragpack_content_tokens: int
    raw_chars: int
    ragpack_full_chars: int
    ragpack_content_chars: int
    token_reduction_full_pct: float
    token_reduction_content_pct: float
    raw_chars_per_token: float
    ragpack_chars_per_token: float


# ---------------------------------------------------------------------------
# Main benchmark runner
# ---------------------------------------------------------------------------

def run_benchmark():
    print("=" * 70)
    print("llmprep Token Benchmark")
    print("=" * 70)
    print()

    # Discover documents
    doc_dir = Path("benchmark/test_documents")
    ragpack_base = Path("benchmark/ragpacks")
    documents = sorted(doc_dir.iterdir())
    print(f"Found {len(documents)} test documents\n")

    # Load tokenizers
    print("Loading tokenizers...")
    all_tokenizers = {}
    all_tokenizers.update(load_tiktoken_tokenizers())
    all_tokenizers.update(load_hf_tokenizers())
    print(f"\nLoaded {len(all_tokenizers)} tokenizers total\n")

    if not all_tokenizers:
        print("ERROR: No tokenizers loaded. Exiting.")
        sys.exit(1)

    # Run benchmarks
    results: list[BenchmarkResult] = []
    test_count = 0
    total_tests = len(documents) * len(all_tokenizers)

    print(f"Running {total_tests} benchmark tests ({len(documents)} docs x {len(all_tokenizers)} models)...")
    print("-" * 70)

    t_start = time.time()

    for doc_path in documents:
        doc_name = doc_path.stem
        doc_ext = doc_path.suffix.lstrip(".")
        doc_size = doc_path.stat().st_size

        raw_text = read_raw_document(str(doc_path))
        ragpack_dir = ragpack_base / doc_name
        ragpack_full_text = read_ragpack(str(ragpack_dir))
        ragpack_content_text = read_ragpack_content_only(str(ragpack_dir))

        for model_name, tokenizer_entry in all_tokenizers.items():
            test_count += 1

            raw_tokens = count_tokens(tokenizer_entry, raw_text)
            ragpack_full_tokens = count_tokens(tokenizer_entry, ragpack_full_text)
            ragpack_content_tokens = count_tokens(tokenizer_entry, ragpack_content_text)

            reduction_full = ((raw_tokens - ragpack_full_tokens) / raw_tokens * 100) if raw_tokens > 0 else 0
            reduction_content = ((raw_tokens - ragpack_content_tokens) / raw_tokens * 100) if raw_tokens > 0 else 0
            raw_cpt = len(raw_text) / raw_tokens if raw_tokens > 0 else 0
            ragpack_cpt = len(ragpack_full_text) / ragpack_full_tokens if ragpack_full_tokens > 0 else 0

            result = BenchmarkResult(
                document=doc_name,
                doc_type=doc_ext,
                doc_size_bytes=doc_size,
                model=model_name,
                tokenizer_type=tokenizer_entry[0],
                raw_tokens=raw_tokens,
                ragpack_full_tokens=ragpack_full_tokens,
                ragpack_content_tokens=ragpack_content_tokens,
                raw_chars=len(raw_text),
                ragpack_full_chars=len(ragpack_full_text),
                ragpack_content_chars=len(ragpack_content_text),
                token_reduction_full_pct=round(reduction_full, 2),
                token_reduction_content_pct=round(reduction_content, 2),
                raw_chars_per_token=round(raw_cpt, 2),
                ragpack_chars_per_token=round(ragpack_cpt, 2),
            )
            results.append(result)

            if test_count % 50 == 0 or test_count == total_tests:
                elapsed = time.time() - t_start
                print(f"  [{test_count:>4d}/{total_tests}] {elapsed:.1f}s elapsed")

    elapsed_total = time.time() - t_start
    print(f"\nCompleted {test_count} tests in {elapsed_total:.1f}s\n")

    # Save raw results as CSV
    results_dir = Path("benchmark/results")
    results_dir.mkdir(exist_ok=True)

    csv_path = results_dir / "benchmark_results.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([
            "Document", "Doc_Type", "Doc_Size_Bytes", "Model", "Tokenizer_Type",
            "Raw_Tokens", "Ragpack_Full_Tokens", "Ragpack_Content_Tokens",
            "Raw_Chars", "Ragpack_Full_Chars", "Ragpack_Content_Chars",
            "Token_Reduction_Full_Pct", "Token_Reduction_Content_Pct",
            "Raw_Chars_Per_Token", "Ragpack_Chars_Per_Token",
        ])
        for r in results:
            w.writerow([
                r.document, r.doc_type, r.doc_size_bytes, r.model, r.tokenizer_type,
                r.raw_tokens, r.ragpack_full_tokens, r.ragpack_content_tokens,
                r.raw_chars, r.ragpack_full_chars, r.ragpack_content_chars,
                r.token_reduction_full_pct, r.token_reduction_content_pct,
                r.raw_chars_per_token, r.ragpack_chars_per_token,
            ])
    print(f"Raw results saved to {csv_path}")

    # ---------------------------------------------------------------------------
    # Generate summary report
    # ---------------------------------------------------------------------------
    generate_report(results, results_dir)


def generate_report(results: list[BenchmarkResult], results_dir: Path):
    """Generate a comprehensive markdown report from benchmark results."""
    report_lines = []
    rpt = report_lines.append

    rpt("# llmprep Token Benchmark Report")
    rpt("")
    rpt(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    rpt(f"**Total tests**: {len(results)}")

    models = sorted(set(r.model for r in results))
    documents = sorted(set(r.document for r in results))
    doc_types = sorted(set(r.doc_type for r in results))

    rpt(f"**Models tested**: {len(models)}")
    rpt(f"**Documents tested**: {len(documents)}")
    rpt(f"**Document types**: {', '.join(doc_types)}")
    rpt("")

    # --- Overall summary ---
    rpt("## Overall Summary")
    rpt("")
    total_raw = sum(r.raw_tokens for r in results)
    total_ragpack = sum(r.ragpack_content_tokens for r in results)
    total_ragpack_full = sum(r.ragpack_full_tokens for r in results)
    avg_reduction_content = sum(r.token_reduction_content_pct for r in results) / len(results)
    avg_reduction_full = sum(r.token_reduction_full_pct for r in results) / len(results)

    rpt(f"- **Total raw tokens** (across all tests): {total_raw:,}")
    rpt(f"- **Total ragpack content tokens**: {total_ragpack:,}")
    rpt(f"- **Total ragpack full tokens** (incl. metadata): {total_ragpack_full:,}")
    rpt(f"- **Average token reduction** (content only): {avg_reduction_content:.1f}%")
    rpt(f"- **Average token change** (full ragpack incl. metadata): {avg_reduction_full:.1f}%")
    rpt("")

    # --- Per-model summary ---
    rpt("## Token Reduction by Model")
    rpt("")
    rpt("| Model | Avg Raw Tokens | Avg Ragpack Tokens | Avg Reduction % | Best Reduction | Worst Reduction |")
    rpt("|-------|---------------:|-------------------:|----------------:|---------------:|----------------:|")

    for model in models:
        model_results = [r for r in results if r.model == model]
        avg_raw = sum(r.raw_tokens for r in model_results) / len(model_results)
        avg_ragpack = sum(r.ragpack_content_tokens for r in model_results) / len(model_results)
        avg_red = sum(r.token_reduction_content_pct for r in model_results) / len(model_results)
        best_red = max(r.token_reduction_content_pct for r in model_results)
        worst_red = min(r.token_reduction_content_pct for r in model_results)
        rpt(f"| {model} | {avg_raw:,.0f} | {avg_ragpack:,.0f} | {avg_red:.1f}% | {best_red:.1f}% | {worst_red:.1f}% |")
    rpt("")

    # --- Per-document summary ---
    rpt("## Token Reduction by Document")
    rpt("")
    rpt("| Document | Type | Size | Avg Raw Tokens | Avg Ragpack Tokens | Avg Reduction % |")
    rpt("|----------|------|-----:|---------------:|-------------------:|----------------:|")

    for doc in documents:
        doc_results = [r for r in results if r.document == doc]
        doc_type = doc_results[0].doc_type
        doc_size = doc_results[0].doc_size_bytes
        avg_raw = sum(r.raw_tokens for r in doc_results) / len(doc_results)
        avg_ragpack = sum(r.ragpack_content_tokens for r in doc_results) / len(doc_results)
        avg_red = sum(r.token_reduction_content_pct for r in doc_results) / len(doc_results)
        size_str = f"{doc_size/1024:.1f} KB" if doc_size > 1024 else f"{doc_size} B"
        rpt(f"| {doc} | {doc_type} | {size_str} | {avg_raw:,.0f} | {avg_ragpack:,.0f} | {avg_red:.1f}% |")
    rpt("")

    # --- Per document type summary ---
    rpt("## Token Reduction by Document Type")
    rpt("")
    rpt("| Type | # Docs | Avg Raw Tokens | Avg Ragpack Tokens | Avg Reduction % |")
    rpt("|------|-------:|---------------:|-------------------:|----------------:|")

    for dtype in doc_types:
        type_results = [r for r in results if r.doc_type == dtype]
        n_docs = len(set(r.document for r in type_results))
        avg_raw = sum(r.raw_tokens for r in type_results) / len(type_results)
        avg_ragpack = sum(r.ragpack_content_tokens for r in type_results) / len(type_results)
        avg_red = sum(r.token_reduction_content_pct for r in type_results) / len(type_results)
        rpt(f"| {dtype} | {n_docs} | {avg_raw:,.0f} | {avg_ragpack:,.0f} | {avg_red:.1f}% |")
    rpt("")

    # --- Characters per token analysis ---
    rpt("## Characters Per Token Analysis")
    rpt("")
    rpt("Higher characters-per-token means more efficient encoding.")
    rpt("")
    rpt("| Model | Raw Chars/Token | Ragpack Chars/Token | Efficiency Change |")
    rpt("|-------|----------------:|--------------------:|------------------:|")

    for model in models:
        model_results = [r for r in results if r.model == model]
        avg_raw_cpt = sum(r.raw_chars_per_token for r in model_results) / len(model_results)
        avg_rag_cpt = sum(r.ragpack_chars_per_token for r in model_results) / len(model_results)
        change = ((avg_rag_cpt - avg_raw_cpt) / avg_raw_cpt * 100) if avg_raw_cpt > 0 else 0
        rpt(f"| {model} | {avg_raw_cpt:.2f} | {avg_rag_cpt:.2f} | {change:+.1f}% |")
    rpt("")

    # --- Full detailed cross-reference ---
    rpt("## Detailed Results: Document × Model (Content Token Reduction %)")
    rpt("")

    header = "| Document |"
    sep = "|----------|"
    for m in models:
        short = m[:10]
        header += f" {short} |"
        sep += "--------:|"
    rpt(header)
    rpt(sep)

    for doc in documents:
        row = f"| {doc} |"
        for model in models:
            match = [r for r in results if r.document == doc and r.model == model]
            if match:
                row += f" {match[0].token_reduction_content_pct:+.1f}% |"
            else:
                row += " - |"
        rpt(row)
    rpt("")

    # --- Size category analysis ---
    rpt("## Token Reduction by Document Size Category")
    rpt("")

    size_cats = [
        ("Small (< 5 KB)", 0, 5 * 1024),
        ("Medium (5-25 KB)", 5 * 1024, 25 * 1024),
        ("Large (25-100 KB)", 25 * 1024, 100 * 1024),
        ("Very Large (> 100 KB)", 100 * 1024, float("inf")),
    ]

    rpt("| Size Category | # Docs | Avg Reduction % | Avg Raw Tokens | Avg Ragpack Tokens |")
    rpt("|---------------|-------:|----------------:|---------------:|-------------------:|")

    for cat_name, lo, hi in size_cats:
        cat_results = [r for r in results if lo <= r.doc_size_bytes < hi]
        if cat_results:
            n_docs = len(set(r.document for r in cat_results))
            avg_red = sum(r.token_reduction_content_pct for r in cat_results) / len(cat_results)
            avg_raw = sum(r.raw_tokens for r in cat_results) / len(cat_results)
            avg_rag = sum(r.ragpack_content_tokens for r in cat_results) / len(cat_results)
            rpt(f"| {cat_name} | {n_docs} | {avg_red:.1f}% | {avg_raw:,.0f} | {avg_rag:,.0f} |")
    rpt("")

    # --- Top 10 best reductions ---
    rpt("## Top 10 Best Token Reductions")
    rpt("")
    rpt("| Rank | Document | Model | Raw Tokens | Ragpack Tokens | Reduction |")
    rpt("|-----:|----------|-------|-----------:|---------------:|----------:|")
    sorted_by_reduction = sorted(results, key=lambda r: r.token_reduction_content_pct, reverse=True)
    for i, r in enumerate(sorted_by_reduction[:10], 1):
        rpt(f"| {i} | {r.document} | {r.model} | {r.raw_tokens:,} | {r.ragpack_content_tokens:,} | {r.token_reduction_content_pct:.1f}% |")
    rpt("")

    # --- Top 10 worst (most expansion) ---
    rpt("## Top 10 Most Token Expansion (ragpack larger than raw)")
    rpt("")
    rpt("| Rank | Document | Model | Raw Tokens | Ragpack Tokens | Expansion |")
    rpt("|-----:|----------|-------|-----------:|---------------:|----------:|")
    sorted_by_expansion = sorted(results, key=lambda r: r.token_reduction_content_pct)
    for i, r in enumerate(sorted_by_expansion[:10], 1):
        rpt(f"| {i} | {r.document} | {r.model} | {r.raw_tokens:,} | {r.ragpack_content_tokens:,} | {r.token_reduction_content_pct:+.1f}% |")
    rpt("")

    # --- Statistical summary ---
    rpt("## Statistical Summary")
    rpt("")
    reductions = [r.token_reduction_content_pct for r in results]
    reductions_sorted = sorted(reductions)
    n = len(reductions_sorted)
    mean_red = sum(reductions) / n
    median_red = reductions_sorted[n // 2]
    p10 = reductions_sorted[int(n * 0.1)]
    p25 = reductions_sorted[int(n * 0.25)]
    p75 = reductions_sorted[int(n * 0.75)]
    p90 = reductions_sorted[int(n * 0.9)]
    variance = sum((x - mean_red) ** 2 for x in reductions) / n
    std_dev = variance ** 0.5

    rpt(f"| Metric | Value |")
    rpt(f"|--------|------:|")
    rpt(f"| Mean reduction | {mean_red:.1f}% |")
    rpt(f"| Median reduction | {median_red:.1f}% |")
    rpt(f"| Std deviation | {std_dev:.1f}% |")
    rpt(f"| P10 | {p10:.1f}% |")
    rpt(f"| P25 | {p25:.1f}% |")
    rpt(f"| P75 | {p75:.1f}% |")
    rpt(f"| P90 | {p90:.1f}% |")
    rpt(f"| Min | {min(reductions):.1f}% |")
    rpt(f"| Max | {max(reductions):.1f}% |")
    rpt("")

    # --- Model family comparison ---
    rpt("## Model Family Comparison")
    rpt("")
    families = {
        "OpenAI (tiktoken)": [m for m in models if m.startswith("gpt") or m.startswith("text-")],
        "Meta (Llama)": [m for m in models if "Llama" in m or "llama" in m],
        "Mistral": [m for m in models if "Mistral" in m],
        "Microsoft (Phi)": [m for m in models if "Phi" in m],
        "Google (Gemma)": [m for m in models if "Gemma" in m],
        "Alibaba (Qwen)": [m for m in models if "Qwen" in m],
        "DeepSeek": [m for m in models if "DeepSeek" in m],
        "Other Open Source": [m for m in models if not any(
            k in m for k in ["gpt", "text-", "Llama", "llama", "Mistral", "Phi", "Gemma", "Qwen", "DeepSeek"]
        )],
    }

    rpt("| Family | Models | Avg Reduction % | Avg Raw Tokens |")
    rpt("|--------|-------:|----------------:|---------------:|")
    for family, fam_models in families.items():
        if not fam_models:
            continue
        fam_results = [r for r in results if r.model in fam_models]
        if fam_results:
            avg_red = sum(r.token_reduction_content_pct for r in fam_results) / len(fam_results)
            avg_raw = sum(r.raw_tokens for r in fam_results) / len(fam_results)
            rpt(f"| {family} | {len(fam_models)} | {avg_red:.1f}% | {avg_raw:,.0f} |")
    rpt("")

    rpt("---")
    rpt(f"*Report generated by llmprep benchmark suite with {len(results)} individual measurements.*")

    # Write report
    report_path = results_dir / "benchmark_report.md"
    with open(report_path, "w") as f:
        f.write("\n".join(report_lines))
    print(f"Report saved to {report_path}")

    # Also print summary to stdout
    print("\n" + "=" * 70)
    print("BENCHMARK SUMMARY")
    print("=" * 70)
    print(f"Total tests:          {len(results)}")
    print(f"Models:               {len(models)}")
    print(f"Documents:            {len(documents)}")
    print(f"Mean token reduction: {mean_red:.1f}%")
    print(f"Median reduction:     {median_red:.1f}%")
    print(f"Best reduction:       {max(reductions):.1f}%")
    print(f"Worst reduction:      {min(reductions):.1f}%")
    print()

    # Print per-model summary
    print("Per-Model Average Token Reduction:")
    print(f"  {'Model':<25s} {'Avg Reduction':>15s} {'Avg Raw Tokens':>15s}")
    print("  " + "-" * 57)
    for model in models:
        model_results = [r for r in results if r.model == model]
        avg_red = sum(r.token_reduction_content_pct for r in model_results) / len(model_results)
        avg_raw = sum(r.raw_tokens for r in model_results) / len(model_results)
        print(f"  {model:<25s} {avg_red:>14.1f}% {avg_raw:>15,.0f}")
    print()


if __name__ == "__main__":
    run_benchmark()
