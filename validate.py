from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from langgraph.types import Command

from risk_auditor.artifacts import BIAS_AUDIT, CANDIDATE_SCORES, HIRING_SUMMARIES, LLM_CALLS, SCORING_RUBRIC
from risk_auditor.graph import compile_graph
from risk_auditor.schemas import BiasAudit, Rubric
from risk_auditor.validation import validate_candidates, validate_scoring_batch

ROOT = Path.cwd()
GENERATED_ARTIFACTS = [SCORING_RUBRIC, CANDIDATE_SCORES, BIAS_AUDIT, HIRING_SUMMARIES, LLM_CALLS]
ARCHIVED_FILES = ["data/job_description.json", "data/candidates.json", *GENERATED_ARTIFACTS]


def main() -> None:
    _remove_previous_artifacts()
    result = _run_graph()
    _validate_artifacts()
    output_dir = _archive_run(result)
    print(f"End-to-end graph validation passed: {output_dir}")


def _run_graph() -> dict:
    graph = compile_graph()
    config = {"configurable": {"thread_id": f"validate-{datetime.now().strftime('%Y%m%d%H%M%S')}"}}
    state = {"job_description_path": "data/job_description.json", "candidates_path": "data/candidates.json"}
    result = graph.invoke(state, config=config)
    while "__interrupt__" in result:
        result = graph.invoke(Command(resume={"action": "approve", "edited_rubric": None}), config=config)
    return result


def _validate_artifacts() -> None:
    for path in ARCHIVED_FILES:
        if not (ROOT / path).exists():
            raise SystemExit(f"Missing required artifact: {path}")
    rubric = Rubric.model_validate(_load_json(SCORING_RUBRIC))
    candidates = _load_json("data/candidates.json")
    validate_candidates(candidates)
    scores = _load_json(CANDIDATE_SCORES)
    audit = BiasAudit.model_validate(_load_json(BIAS_AUDIT))
    criteria = {item.name for item in rubric.criteria}
    validate_scoring_batch(scores["original_scores"], {item["id"] for item in candidates}, criteria)
    if scores["approved_rubric_reference"] != SCORING_RUBRIC:
        raise SystemExit("candidate_scores.json must reference scoring_rubric.json")
    if scores["final_ranking"] and scores["bias_audit_status"] != "completed":
        raise SystemExit("Ranking requires completed bias audit")
    if any(item.severity == "flagged" for item in audit.findings) and not scores["corrected_scores"]:
        raise SystemExit("Flagged findings require corrected scores")
    if not (ROOT / LLM_CALLS).read_text(encoding="utf-8").strip():
        raise SystemExit("llm_calls.jsonl must contain LLM call records")


def _archive_run(result: dict) -> Path:
    output_dir = ROOT / "output" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_recruitment_graph"
    output_dir.mkdir(parents=True, exist_ok=True)
    for path in ARCHIVED_FILES:
        src = ROOT / path
        target = output_dir / Path(path).name
        shutil.copy2(src, target)
    (output_dir / "graph_result.json").write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    metadata = {"script": "validate.py", "llm_mode": "openrouter", "status": "passed"}
    (output_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return output_dir


def _remove_previous_artifacts() -> None:
    for path in GENERATED_ARTIFACTS:
        target = ROOT / path
        if target.exists():
            target.unlink()


def _load_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
