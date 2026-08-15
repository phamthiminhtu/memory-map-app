# Eval System

## Overview

Two-layer hybrid eval for the memory retrieval pipeline.

- Layer 1: deterministic fact coverage — checks if `must_include` keywords appear in the retrieved context
- Layer 2: LLM judge with a hallucination-penalty rubric (score 1-5, anything with a hallucination capped at 2)
- A case passes when `fact_coverage >= 0.5` AND `llm_score >= 3`

## Running

```bash
# Default (Anthropic / Haiku)
python -m eval.run_eval

# Groq / Llama
LLM_PROVIDER=groq python -m eval.run_eval
```

Results are saved to `eval/results/run_<timestamp>.json`.

## Files

- `eval/run_eval.py` — entry point
- `eval/golden_set.json` — test cases with questions and `must_include` facts
- `eval/results/` — timestamped result files
- `backend/utils/constants/eval.py` — model names, pass thresholds, default provider

## Golden Set

Each case has:
- `id`, `intent` — identifier and category (temporal, narrative, multi-source)
- `question` — the query passed to `MemoryService.synthesize_memories`
- `must_include` — list of strings that must appear in the retrieved context to pass

## Date-Aware Re-ranking

Pure vector similarity ranks semantically similar entries, not necessarily date-matching ones. Fixed with:

- `extract_date_range(query)` in `backend/utils/text_cleaning.py` — parses dates and ranges from natural language (e.g. "July 14, 2026", "between July 25 and July 30", "first week of August 2026")
- `rerank_by_date(memories, date_range)` — multiplies distance by `DATE_BOOST_FACTOR = 0.5` for memories whose date falls within the range
- Applied in `MemoryService.synthesize_memories`: when a date range is detected, fetch `n_results * 3` results before boosting, to ensure date-relevant entries are not cut off by semantic rank

## Data Ingestion

- Text diary entries live in `data/text/YYYY-MM-DD.txt`; ingest via `scripts/bulk_ingest_image.py --type text --full-refresh`
- Image filenames encode date and description (e.g. `2026-07-14_hiking_ridge_trail.png`); `ImageDataLoader.save_image_memory` parses these into `date` and `text` metadata fields
- Both `date` and `title` fields in metadata are checked during re-ranking for backwards compatibility with older ingested records

## Results (2026-08-15)

| Run | Pass rate | avg coverage | avg LLM score (max 5) |
|-----|-----------|--------------|---------------|
| Before fixes | 0/9 (0%) | 0.06 | 1.22 |
| After data fix | 6/9 (67%) | 0.73 | 3.67 |
| After re-ranking | 9/9 (100%) | 0.96 | 4.67 |
