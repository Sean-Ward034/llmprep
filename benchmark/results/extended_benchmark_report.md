# llmprep Extended Token Benchmark Report

**Date**: 2026-02-26 18:00:44
**Total measurements**: 420
**Models**: 28
**Documents**: 15
**Document types**: csv, html, txt

## Key Findings

llmprep converts raw documents into structured, LLM-ready ragpacks containing:
- **doc_chunks.jsonl**: Text broken into semantically meaningful chunks with metadata
- **tables.jsonl**: Extracted and structured table data
- **entities.json**: Named entities, dates, amounts, organizations extracted
- **task_spec.json**: Inferred task categories and heuristics
- **manifest.json**: Processing metadata (hashes, timing, config)
- **validation_report.json**: Data quality checks

The ragpack format trades token count for **structure and reliability**:
- JSON wrapping adds overhead but makes content machine-parseable
- Entity extraction pre-computes information that LLMs would otherwise infer
- Chunk boundaries prevent mid-sentence splits common with naive truncation
- Deterministic hashing enables caching and change detection

## Token Overhead by Output Layer

Comparing different layers of ragpack output to understand where tokens go:

| Model | Chunks Only (Δ%) | Content (chunks+tables+entities+tasks) (Δ%) | Full (all files) (Δ%) |
|-------|------------------:|--------------------------------------------:|----------------------:|
| BLOOM | -136.2% | -315.7% | -360.7% |
| BLOOMZ | -136.2% | -315.7% | -360.7% |
| CodeGen | -130.5% | -276.2% | -316.2% |
| CodeLlama-7B | -147.3% | -300.8% | -342.3% |
| DeepSeek-Coder | -156.2% | -310.9% | -354.0% |
| DeepSeek-V2 | -163.7% | -319.4% | -363.5% |
| Falcon-7B | -124.2% | -268.1% | -307.3% |
| GLM-4 | -137.8% | -287.2% | -325.7% |
| GPT-J | -119.1% | -256.9% | -294.8% |
| GPT-NeoX | -131.5% | -278.6% | -319.1% |
| Mistral-7B | -153.8% | -307.4% | -350.1% |
| OLMo-1B | -131.5% | -278.6% | -319.1% |
| OPT-1.3B | -119.1% | -256.9% | -294.8% |
| Phi-1.5 | -130.5% | -276.2% | -316.2% |
| Phi-2 | -130.5% | -276.2% | -316.2% |
| Pythia-1B | -131.5% | -278.6% | -319.1% |
| Qwen-2 | -165.7% | -323.9% | -366.5% |
| Qwen-2.5 | -165.7% | -323.9% | -366.5% |
| RedPajama-7B | -131.5% | -278.6% | -319.1% |
| SmolLM-2 | -166.4% | -325.6% | -370.7% |
| StableLM-2 | -165.6% | -323.7% | -366.2% |
| StarChat | -151.6% | -303.5% | -344.5% |
| Yi-1.5 | -172.8% | -357.2% | -406.3% |
| gpt-2 | -119.1% | -256.9% | -294.8% |
| gpt-3.5-turbo | -121.6% | -265.5% | -301.8% |
| gpt-4 | -121.6% | -265.5% | -301.8% |
| gpt-4o | -125.2% | -271.2% | -308.3% |
| text-davinci-003 | -130.8% | -276.6% | -316.6% |

## Per-Model Token Analysis

| Model | Avg Raw Tokens | Avg Ragpack Content Tokens | Avg Overhead Ratio | Avg Chars/Token (raw) | Avg Chars/Token (ragpack) |
|-------|---------------:|---------------------------:|-------------------:|----------------------:|--------------------------:|
| BLOOM | 27,588 | 40,714 | 1.48x | 3.57 | 2.64 |
| BLOOMZ | 27,588 | 40,714 | 1.48x | 3.57 | 2.64 |
| CodeGen | 31,328 | 36,399 | 1.16x | 3.03 | 2.68 |
| CodeLlama-7B | 43,875 | 50,260 | 1.15x | 2.50 | 2.07 |
| DeepSeek-Coder | 43,537 | 49,885 | 1.15x | 2.53 | 2.07 |
| DeepSeek-V2 | 42,461 | 48,479 | 1.14x | 2.78 | 2.22 |
| Falcon-7B | 30,915 | 36,049 | 1.17x | 2.98 | 2.67 |
| GLM-4 | 31,668 | 35,892 | 1.13x | 3.24 | 2.82 |
| GPT-J | 31,399 | 36,399 | 1.16x | 2.88 | 2.68 |
| GPT-NeoX | 30,875 | 36,016 | 1.17x | 3.04 | 2.67 |
| Mistral-7B | 43,316 | 49,635 | 1.15x | 2.57 | 2.10 |
| OLMo-1B | 30,875 | 36,016 | 1.17x | 3.04 | 2.67 |
| OPT-1.3B | 31,399 | 36,399 | 1.16x | 2.88 | 2.68 |
| Phi-1.5 | 31,328 | 36,399 | 1.16x | 3.03 | 2.68 |
| Phi-2 | 31,328 | 36,399 | 1.16x | 3.03 | 2.68 |
| Pythia-1B | 30,875 | 36,016 | 1.17x | 3.04 | 2.67 |
| Qwen-2 | 41,861 | 46,869 | 1.12x | 2.95 | 2.36 |
| Qwen-2.5 | 41,861 | 46,869 | 1.12x | 2.95 | 2.36 |
| RedPajama-7B | 30,875 | 36,016 | 1.17x | 3.04 | 2.67 |
| SmolLM-2 | 42,840 | 49,085 | 1.15x | 2.73 | 2.15 |
| StableLM-2 | 41,861 | 46,870 | 1.12x | 2.95 | 2.36 |
| StarChat | 42,628 | 48,581 | 1.14x | 2.70 | 2.22 |
| Yi-1.5 | 42,551 | 62,966 | 1.48x | 2.74 | 1.88 |
| gpt-2 | 31,399 | 36,399 | 1.16x | 2.88 | 2.68 |
| gpt-3.5-turbo | 30,073 | 33,996 | 1.13x | 3.27 | 2.98 |
| gpt-4 | 30,073 | 33,996 | 1.13x | 3.27 | 2.98 |
| gpt-4o | 29,936 | 34,650 | 1.16x | 3.29 | 2.94 |
| text-davinci-003 | 31,327 | 36,399 | 1.16x | 3.04 | 2.68 |

## Per-Document Token Analysis

| Document | Type | Size | Avg Raw Tokens | Avg Ragpack Tokens | Overhead Ratio | Content Richness |
|----------|------|-----:|---------------:|-------------------:|---------------:|-----------------:|
| code_review | txt | 3.5KB | 1,068 | 4,089 | 3.83x | 11ch/0tb/0ent |
| dashboard_report | html | 3.3KB | 1,469 | 2,957 | 2.01x | 2ch/2tb/0ent |
| employee_directory | html | 24.7KB | 11,188 | 17,685 | 1.58x | 14ch/1tb/0ent |
| financial_report | txt | 3.3KB | 938 | 4,163 | 4.44x | 8ch/0tb/0ent |
| inventory | csv | 35.7KB | 19,225 | 21,353 | 1.11x | 0ch/2tb/0ent |
| iot_sensor_data | csv | 138.1KB | 87,547 | 95,970 | 1.10x | 0ch/8tb/0ent |
| legal_contract | txt | 7.6KB | 1,833 | 11,680 | 6.37x | 40ch/0tb/0ent |
| meeting_notes | txt | 4.2KB | 1,178 | 10,821 | 9.19x | 20ch/0tb/0ent |
| memo_short | txt | 776B | 191 | 2,431 | 12.72x | 7ch/0tb/0ent |
| product_docs | html | 6.8KB | 2,495 | 4,057 | 1.63x | 4ch/4tb/0ent |
| research_abstracts | txt | 5.9KB | 1,237 | 3,553 | 2.87x | 9ch/0tb/0ent |
| sales_data | csv | 38.0KB | 20,059 | 22,897 | 1.14x | 0ch/3tb/0ent |
| support_tickets | csv | 20.7KB | 7,968 | 9,229 | 1.16x | 0ch/1tb/0ent |
| system_metrics | csv | 510.8KB | 365,946 | 395,786 | 1.08x | 0ch/29tb/0ent |
| technical_spec | txt | 4.8KB | 1,394 | 11,738 | 8.42x | 17ch/0tb/0ent |

## Token Analysis by Document Type

| Type | # Docs | Avg Raw Tokens | Avg Ragpack Tokens | Avg Overhead Ratio |
|------|-------:|---------------:|-------------------:|-------------------:|
| csv | 5 | 100,149 | 109,047 | 1.09x |
| html | 3 | 5,051 | 8,233 | 1.63x |
| txt | 7 | 1,120 | 6,925 | 6.18x |

## Analysis by Document Size

| Size Category | # Docs | Avg Overhead Ratio | Avg Extra Tokens |
|---------------|-------:|-------------------:|-----------------:|
| Small (< 5 KB) | 6 | 6.78x | +4,994 |
| Medium (5-25 KB) | 5 | 2.73x | +4,297 |
| Large (25-100 KB) | 2 | 1.13x | +2,483 |
| Very Large (> 100 KB) | 2 | 1.09x | +19,131 |

## Document × Model Token Overhead Ratio

Values show ragpack/raw token ratio (1.0 = same size, >1.0 = ragpack larger).

| Document | BLOOM | BLOOMZ | CodeGen | CodeLlama-7B | DeepSeek-Cod | DeepSeek-V2 | Falcon-7B | GLM-4 | GPT-J | GPT-NeoX | Mistral-7B | OLMo-1B | OPT-1.3B | Phi-1.5 | Phi-2 | Pythia-1B | Qwen-2 | Qwen-2.5 | RedPajama-7B | SmolLM-2 | StableLM-2 | StarChat | Yi-1.5 | gpt-2 | gpt-3.5-turb | gpt-4 | gpt-4o | text-davinci |
|----------|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|----------:|
| code_review | 3.58x | 3.58x | 3.56x | 4.03x | 4.01x | 4.14x | 3.50x | 4.01x | 3.53x | 3.62x | 4.06x | 3.62x | 3.53x | 3.56x | 3.56x | 3.62x | 4.44x | 4.44x | 3.62x | 4.11x | 4.41x | 4.13x | 4.23x | 3.53x | 3.76x | 3.76x | 3.82x | 3.57x |
| dashboard_report | 2.94x | 2.94x | 1.88x | 2.10x | 1.90x | 2.08x | 1.89x | 1.85x | 1.88x | 1.87x | 2.10x | 1.87x | 1.88x | 1.88x | 1.88x | 1.87x | 2.01x | 2.01x | 1.87x | 2.09x | 2.01x | 2.05x | 3.36x | 1.88x | 1.78x | 1.78x | 1.80x | 1.88x |
| employee_directory | 2.42x | 2.42x | 1.48x | 1.66x | 1.50x | 1.61x | 1.48x | 1.39x | 1.48x | 1.51x | 1.64x | 1.51x | 1.48x | 1.48x | 1.48x | 1.51x | 1.52x | 1.52x | 1.51x | 1.64x | 1.52x | 1.61x | 2.70x | 1.48x | 1.36x | 1.36x | 1.38x | 1.48x |
| financial_report | 4.67x | 4.67x | 4.67x | 4.78x | 5.02x | 5.10x | 4.58x | 4.56x | 2.85x | 4.72x | 4.86x | 4.72x | 2.85x | 4.67x | 4.67x | 4.72x | 4.78x | 4.78x | 4.72x | 5.29x | 4.78x | 4.72x | 4.86x | 2.85x | 4.30x | 4.30x | 4.36x | 4.72x |
| inventory | 1.51x | 1.51x | 1.08x | 1.06x | 1.07x | 1.07x | 1.08x | 1.06x | 1.08x | 1.08x | 1.06x | 1.08x | 1.08x | 1.08x | 1.08x | 1.08x | 1.05x | 1.05x | 1.08x | 1.06x | 1.05x | 1.06x | 1.41x | 1.08x | 1.06x | 1.06x | 1.08x | 1.08x |
| iot_sensor_data | 1.30x | 1.30x | 1.08x | 1.07x | 1.07x | 1.07x | 1.08x | 1.05x | 1.08x | 1.08x | 1.07x | 1.08x | 1.08x | 1.08x | 1.08x | 1.08x | 1.04x | 1.04x | 1.08x | 1.07x | 1.04x | 1.07x | 1.37x | 1.08x | 1.05x | 1.05x | 1.10x | 1.08x |
| legal_contract | 5.79x | 5.79x | 6.03x | 6.50x | 6.90x | 7.27x | 5.91x | 6.28x | 6.03x | 5.99x | 6.89x | 5.99x | 6.03x | 6.03x | 6.03x | 5.99x | 7.26x | 7.26x | 5.99x | 7.24x | 7.26x | 6.79x | 7.43x | 6.03x | 5.81x | 5.81x | 5.89x | 6.03x |
| meeting_notes | 9.34x | 9.34x | 8.97x | 9.20x | 9.60x | 9.68x | 8.50x | 9.10x | 8.97x | 8.92x | 9.44x | 8.92x | 8.97x | 8.97x | 8.97x | 8.92x | 9.95x | 9.95x | 8.92x | 9.82x | 9.94x | 9.07x | 9.65x | 8.97x | 8.56x | 8.56x | 8.69x | 8.97x |
| memo_short | 12.47x | 12.47x | 11.93x | 13.20x | 13.69x | 13.85x | 11.62x | 12.59x | 11.93x | 12.22x | 13.40x | 12.22x | 11.93x | 11.93x | 11.93x | 12.22x | 14.21x | 14.21x | 12.22x | 13.99x | 14.21x | 13.13x | 14.83x | 11.93x | 11.67x | 11.67x | 11.93x | 11.93x |
| product_docs | 2.26x | 2.26x | 1.54x | 1.75x | 1.67x | 1.71x | 1.58x | 1.53x | 1.35x | 1.56x | 1.74x | 1.56x | 1.35x | 1.54x | 1.54x | 1.56x | 1.68x | 1.68x | 1.56x | 1.81x | 1.68x | 1.76x | 2.22x | 1.35x | 1.45x | 1.45x | 1.46x | 1.54x |
| research_abstracts | 2.74x | 2.74x | 2.78x | 2.92x | 3.05x | 3.16x | 2.74x | 2.84x | 2.78x | 2.80x | 2.96x | 2.80x | 2.78x | 2.78x | 2.78x | 2.80x | 3.12x | 3.12x | 2.80x | 3.19x | 3.12x | 2.94x | 3.00x | 2.78x | 2.65x | 2.65x | 2.68x | 2.78x |
| sales_data | 1.60x | 1.60x | 1.10x | 1.08x | 1.09x | 1.09x | 1.11x | 1.09x | 1.10x | 1.10x | 1.08x | 1.10x | 1.10x | 1.10x | 1.10x | 1.10x | 1.08x | 1.08x | 1.10x | 1.09x | 1.08x | 1.08x | 1.52x | 1.10x | 1.09x | 1.09x | 1.10x | 1.10x |
| support_tickets | 1.56x | 1.56x | 1.12x | 1.10x | 1.12x | 1.13x | 1.12x | 1.11x | 1.12x | 1.12x | 1.12x | 1.12x | 1.12x | 1.12x | 1.12x | 1.12x | 1.10x | 1.10x | 1.12x | 1.12x | 1.10x | 1.11x | 1.55x | 1.12x | 1.11x | 1.11x | 1.13x | 1.12x |
| system_metrics | 1.36x | 1.36x | 1.06x | 1.05x | 1.05x | 1.05x | 1.06x | 1.04x | 1.06x | 1.06x | 1.05x | 1.06x | 1.06x | 1.06x | 1.06x | 1.06x | 1.03x | 1.03x | 1.06x | 1.05x | 1.03x | 1.05x | 1.37x | 1.06x | 1.04x | 1.04x | 1.06x | 1.06x |
| technical_spec | 8.82x | 8.82x | 8.13x | 8.61x | 8.90x | 8.92x | 7.96x | 8.59x | 7.30x | 8.14x | 8.63x | 8.14x | 7.30x | 8.13x | 8.13x | 8.14x | 9.32x | 9.32x | 8.14x | 9.28x | 9.32x | 8.96x | 9.08x | 7.30x | 8.14x | 8.14x | 8.19x | 8.13x |

## Most Efficient Conversions (lowest overhead)

| Rank | Document | Model | Raw Tokens | Ragpack Tokens | Ratio |
|-----:|----------|-------|-----------:|---------------:|------:|
| 1 | system_metrics | Qwen-2.5 | 446,969 | 460,985 | 1.03x |
| 2 | system_metrics | Qwen-2 | 446,969 | 460,985 | 1.03x |
| 3 | system_metrics | StableLM-2 | 446,969 | 460,985 | 1.03x |
| 4 | system_metrics | gpt-4 | 312,220 | 323,935 | 1.04x |
| 5 | system_metrics | gpt-3.5-turbo | 312,220 | 323,935 | 1.04x |
| 6 | system_metrics | GLM-4 | 331,793 | 344,279 | 1.04x |
| 7 | iot_sensor_data | Qwen-2.5 | 104,233 | 108,508 | 1.04x |
| 8 | iot_sensor_data | Qwen-2 | 104,233 | 108,508 | 1.04x |
| 9 | iot_sensor_data | StableLM-2 | 104,233 | 108,508 | 1.04x |
| 10 | system_metrics | StarChat | 452,740 | 473,619 | 1.05x |
| 11 | iot_sensor_data | gpt-4 | 77,966 | 81,595 | 1.05x |
| 12 | iot_sensor_data | gpt-3.5-turbo | 77,966 | 81,595 | 1.05x |
| 13 | system_metrics | DeepSeek-V2 | 452,739 | 473,886 | 1.05x |
| 14 | iot_sensor_data | GLM-4 | 80,487 | 84,286 | 1.05x |
| 15 | system_metrics | CodeLlama-7B | 461,975 | 484,095 | 1.05x |

## Highest Overhead Conversions

| Rank | Document | Model | Raw Tokens | Ragpack Tokens | Ratio |
|-----:|----------|-------|-----------:|---------------:|------:|
| 1 | memo_short | OLMo-1B | 188 | 2,298 | 12.22x |
| 2 | memo_short | RedPajama-7B | 188 | 2,298 | 12.22x |
| 3 | memo_short | BLOOM | 172 | 2,144 | 12.47x |
| 4 | memo_short | BLOOMZ | 172 | 2,144 | 12.47x |
| 5 | memo_short | GLM-4 | 176 | 2,216 | 12.59x |
| 6 | memo_short | StarChat | 207 | 2,717 | 13.13x |
| 7 | memo_short | CodeLlama-7B | 220 | 2,904 | 13.20x |
| 8 | memo_short | Mistral-7B | 215 | 2,882 | 13.40x |
| 9 | memo_short | DeepSeek-Coder | 213 | 2,917 | 13.69x |
| 10 | memo_short | DeepSeek-V2 | 200 | 2,770 | 13.85x |
| 11 | memo_short | SmolLM-2 | 202 | 2,825 | 13.99x |
| 12 | memo_short | Qwen-2.5 | 183 | 2,601 | 14.21x |
| 13 | memo_short | Qwen-2 | 183 | 2,601 | 14.21x |
| 14 | memo_short | StableLM-2 | 183 | 2,601 | 14.21x |
| 15 | memo_short | Yi-1.5 | 204 | 3,025 | 14.83x |

## Statistical Summary

| Metric | Value |
|--------|------:|
| Total measurements | 420 |
| Mean overhead ratio | 3.92x |
| Median overhead ratio | 2.05x |
| Std deviation | 3.54 |
| Min ratio (best) | 1.03x |
| Max ratio (worst) | 14.83x |
| P10 | 1.07x |
| P25 | 1.11x |
| P75 | 5.99x |
| P90 | 9.28x |

## Model Family Comparison

| Family | Models | Avg Overhead Ratio | Avg Raw Tokens/Doc |
|--------|-------:|-------------------:|-------------------:|
| OpenAI | 5 | 3.67x | 30,562 |
| Meta | 2 | 3.79x | 37,637 |
| Mistral | 1 | 4.07x | 43,316 |
| Microsoft | 2 | 3.76x | 31,328 |
| Alibaba (Qwen) | 2 | 4.24x | 41,861 |
| DeepSeek | 2 | 4.15x | 42,999 |
| EleutherAI | 3 | 3.71x | 31,050 |
| BigScience | 2 | 4.16x | 27,588 |
| Code Models | 4 | 3.98x | 40,342 |
| Other | 7 | 4.03x | 35,941 |

## What You Get for the Token Overhead

For each document, llmprep extracts structured information that would otherwise
require the LLM to infer. This table shows the structured output per document:

| Document | Type | Raw Size | Chunks | Tables | Entities | Tasks | Structure Density |
|----------|------|------:|-------:|-------:|---------:|------:|------------------:|
| code_review | txt | 3.5KB | 11 | 0 | 0 | 0 | 3.1/KB |
| dashboard_report | html | 3.3KB | 2 | 2 | 0 | 0 | 1.2/KB |
| employee_directory | html | 24.7KB | 14 | 1 | 0 | 0 | 0.6/KB |
| financial_report | txt | 3.3KB | 8 | 0 | 0 | 10 | 5.5/KB |
| inventory | csv | 35.7KB | 0 | 2 | 0 | 0 | 0.1/KB |
| iot_sensor_data | csv | 138.1KB | 0 | 8 | 0 | 0 | 0.1/KB |
| legal_contract | txt | 7.6KB | 40 | 0 | 0 | 0 | 5.2/KB |
| meeting_notes | txt | 4.2KB | 20 | 0 | 0 | 39 | 14.1/KB |
| memo_short | txt | 776B | 7 | 0 | 0 | 3 | 13.2/KB |
| product_docs | html | 6.8KB | 4 | 4 | 0 | 0 | 1.2/KB |
| research_abstracts | txt | 5.9KB | 9 | 0 | 0 | 0 | 1.5/KB |
| sales_data | csv | 38.0KB | 0 | 3 | 0 | 0 | 0.1/KB |
| support_tickets | csv | 20.7KB | 0 | 1 | 0 | 0 | 0.0/KB |
| system_metrics | csv | 510.8KB | 0 | 29 | 0 | 0 | 0.1/KB |
| technical_spec | txt | 4.8KB | 17 | 0 | 0 | 51 | 14.3/KB |

---
*Extended benchmark: 420 measurements across 28 models and 15 documents.*