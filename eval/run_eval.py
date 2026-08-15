"""
Hybrid eval: Layer 1 deterministic fact coverage + Layer 2 LLM judge with hallucination penalty.
Loads golden_set.json, runs each question through MemoryService, scores with both layers,
saves results to results/run_<timestamp>.json.

Set LLM_PROVIDER=groq to use Llama via Groq (needs GROQ_MEMORY_MAP_APP_API_KEY).
Default provider is Anthropic (needs ANTHROPIC_MEMORY_MAP_APP_API_KEY).
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Callable

import anthropic
from groq import Groq
from backend.services.memory_service import MemoryService
from backend.utils.constants.anthropic import API_KEY_ENV_VAR as ANTHROPIC_API_KEY_ENV_VAR
from backend.utils.constants.groq import API_KEY_ENV_VAR as GROQ_MEMORY_MAP_APP_API_KEY_ENV_VAR
from backend.utils.constants.eval import (
    ANTHROPIC_EVAL_MODEL,
    GROQ_EVAL_MODEL,
    DEFAULT_LLM_PROVIDER,
    FACT_COVERAGE_THRESHOLD,
    LLM_SCORE_THRESHOLD,
)

GOLDEN_SET_PATH = Path(__file__).parent / "golden_set.json"
RESULTS_DIR = Path(__file__).parent / "results"

JUDGE_PROMPT = """You are evaluating a memory retrieval system. Given a user question and the retrieved memories, score the quality of the retrieval.

Question: {question}

Retrieved memories:
{context}

Must-include facts (these MUST appear in the memories to be correct):
{must_include}

Score the response on this scale:
5 - All facts correct, nothing invented
4 - All facts correct, but missing minor details
3 - Missing significant facts, but nothing stated is false
2 - Contains at least one hallucinated/incorrect fact
1 - Mostly hallucinated or contradicts the source memories

A response with ANY hallucinated/incorrect fact cannot score above 2, regardless of fluency or how much else it got right.

Return ONLY valid JSON in this format:
{{"score": <1-5>, "rationale": "<explanation>", "hallucination_detected": <true|false>}}"""


def get_api_key(env_var: str) -> str:
    key = os.environ.get(env_var)
    if not key:
        raise ValueError(f"{env_var} environment variable not set")
    return key


def make_llm_call(provider: str) -> tuple[Callable[[str], str], str]:
    """Returns (call_fn, model_name). call_fn takes a prompt and returns the LLM response text."""
    if provider == "groq":
        client = Groq(api_key=get_api_key(GROQ_MEMORY_MAP_APP_API_KEY_ENV_VAR))
        model = GROQ_EVAL_MODEL
        def call_fn(prompt: str) -> str:
            return client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=512,
            ).choices[0].message.content.strip()
    else:  # anthropic (default)
        client = anthropic.Anthropic(api_key=get_api_key(ANTHROPIC_API_KEY_ENV_VAR))
        model = ANTHROPIC_EVAL_MODEL
        def call_fn(prompt: str) -> str:
            return client.messages.create(
                model=model,
                max_tokens=512,
                temperature=0,
                messages=[{"role": "user", "content": prompt}],
            ).content[0].text.strip()
    return call_fn, model


def fact_coverage(context: str, must_include: list) -> tuple:
    hits = [fact for fact in must_include if fact.lower() in context.lower()]
    return len(hits) / len(must_include), hits


def format_memories_as_context(synthesis_result) -> str:
    parts = []
    for mem in synthesis_result.timeline:
        metadata = mem.get("metadata", {})
        text = metadata.get("text", mem.get("text", ""))
        mem_type = metadata.get("type", "unknown")
        date = metadata.get("date", metadata.get("timestamp", ""))
        if date:
            parts.append(f"[{mem_type.upper()} | {date}] {text}")
        else:
            parts.append(f"[{mem_type.upper()}] {text}")
    return "\n\n".join(parts) if parts else "(no memories retrieved)"


def llm_judge(call_fn: Callable[[str], str], question: str, context: str, must_include: list) -> dict:
    prompt = JUDGE_PROMPT.format(
        question=question,
        context=context,
        must_include=", ".join(must_include),
    )
    raw = call_fn(prompt)
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    if not raw:
        raise ValueError("LLM judge returned empty response")
    return json.loads(raw)


def run_eval():
    provider = os.environ.get("LLM_PROVIDER", DEFAULT_LLM_PROVIDER)
    call_fn, model = make_llm_call(provider)
    print(f"Using provider={provider}, model={model}")

    service = MemoryService()

    with open(GOLDEN_SET_PATH) as f:
        golden_set = json.load(f)

    results = []

    for case in golden_set:
        print(f"Running: {case['id']} ({case['intent']})...")

        synthesis = service.synthesize_memories(case["question"], n_results_per_type=10)
        context = format_memories_as_context(synthesis)

        # Layer 1: deterministic fact coverage
        coverage_score, keywords_found = fact_coverage(context, case["must_include"])

        # Layer 2: LLM judge with hallucination penalty rubric
        judge_result = llm_judge(call_fn, case["question"], context, case["must_include"])

        result = {
            "id": case["id"],
            "intent": case["intent"],
            "question": case["question"],
            "must_include": case["must_include"],
            "fact_coverage": round(coverage_score, 2),
            "keywords_found": keywords_found,
            "llm_score": judge_result["score"],
            "rationale": judge_result["rationale"],
            "hallucination_detected": judge_result["hallucination_detected"],
            "retrieved_count": synthesis.combined_count,
            "passed": coverage_score >= FACT_COVERAGE_THRESHOLD and judge_result["score"] >= LLM_SCORE_THRESHOLD,
        }
        results.append(result)

        print(
            f"  fact_coverage={coverage_score:.2f}, llm_score={judge_result['score']}, "
            f"hallucination={judge_result['hallucination_detected']}, passed={result['passed']}"
        )

    # Aggregate summary
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    avg_coverage = round(sum(r["fact_coverage"] for r in results) / total, 2)
    avg_llm_score = round(sum(r["llm_score"] for r in results) / total, 2)

    RESULTS_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = RESULTS_DIR / f"run_{timestamp}.json"

    with open(output_path, "w") as f:
        json.dump(
            {
                "run_timestamp": datetime.now().isoformat(),
                "provider": provider,
                "model": model,
                "total_cases": total,
                "passed": passed,
                "pass_rate": round(passed / total, 2),
                "avg_fact_coverage": avg_coverage,
                "avg_llm_score": avg_llm_score,
                "cases": results,
            },
            f,
            indent=2,
        )

    print(f"\nSummary [{provider} / {model}]: {passed}/{total} passed | avg_coverage={avg_coverage} | avg_llm_score={avg_llm_score}")
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    run_eval()
