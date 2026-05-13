from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUTPUT_DIR = ROOT / "output"
SCORING_RUBRIC = "output/scoring_rubric.json"
CANDIDATE_SCORES = "output/candidate_scores.json"
BIAS_AUDIT = "output/bias_audit.json"
HIRING_SUMMARIES = "output/hiring_summaries.md"
LLM_CALLS = "output/llm_calls.jsonl"


def _ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def read_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def write_json(path: str, data: Any) -> None:
    _ensure_output_dir()
    (ROOT / path).write_text(json.dumps(data, indent=2), encoding="utf-8")


def append_llm_call(
    *,
    stage: str,
    prompt: str,
    model: str,
    input_artifacts: list[str],
    output_artifact: str,
    candidate_names_included: bool,
) -> None:
    record = {
        "stage": stage,
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model,
        "provider": "openrouter",
        "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "input_artifacts": input_artifacts,
        "output_artifact": output_artifact,
        "candidate_names_included": candidate_names_included,
    }
    _ensure_output_dir()
    with (ROOT / LLM_CALLS).open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def update_candidate_scores(**updates: Any) -> dict[str, Any]:
    existing = read_json(CANDIDATE_SCORES) if (ROOT / CANDIDATE_SCORES).exists() else {}
    existing.update(updates)
    write_json(CANDIDATE_SCORES, existing)
    return existing
