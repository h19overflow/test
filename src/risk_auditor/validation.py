from __future__ import annotations

from typing import Any

from risk_auditor.schemas import Rubric
from risk_auditor.stages import PipelineStage


def require_stage(state: dict[str, Any], stage: PipelineStage) -> None:
    current = state.get("stage")
    if current != stage.value:
        raise RuntimeError(f"Expected stage {stage}, found {current}")


def validate_job_description(job: dict[str, Any]) -> None:
    required = {"role", "company", "requirements", "nice_to_have", "explicitly_not_required"}
    missing = required - set(job)
    if missing:
        raise ValueError(f"Missing job description keys: {sorted(missing)}")


def validate_candidates(candidates: list[dict[str, Any]]) -> None:
    ids = [candidate.get("id") for candidate in candidates]
    if len(ids) != len(set(ids)):
        raise ValueError("Candidate IDs must be unique")
    for candidate in candidates:
        missing = {"id", "name", "summary"} - set(candidate)
        if missing:
            raise ValueError(f"Candidate {candidate.get('id')} missing {sorted(missing)}")


def normalize_rubric(data: dict[str, Any]) -> dict[str, Any]:
    rubric = Rubric.model_validate(data).model_dump()
    total = sum(item["weight"] for item in rubric["criteria"])
    if total <= 0:
        raise ValueError("Rubric weights must have a positive sum")
    normalized = []
    for item in rubric["criteria"]:
        normalized.append({**item, "weight": round(item["weight"] / total, 6)})
    drift = round(1.0 - sum(item["weight"] for item in normalized), 6)
    normalized[-1]["weight"] = round(normalized[-1]["weight"] + drift, 6)
    return {"criteria": normalized}


def validate_rubric(data: dict[str, Any]) -> Rubric:
    normalized = normalize_rubric(data)
    total = sum(item["weight"] for item in normalized["criteria"])
    if abs(total - 1.0) > 0.01:
        raise ValueError("Rubric weights must sum to 1.0")
    return Rubric.model_validate(normalized)


def rubric_names(rubric: dict[str, Any]) -> list[str]:
    return [criterion["name"] for criterion in rubric["criteria"]]


def recompute_scores(batch: dict[str, Any], rubric: dict[str, Any]) -> dict[str, Any]:
    weights = {criterion["name"]: criterion["weight"] for criterion in rubric["criteria"]}
    for candidate in batch["candidate_scores"]:
        total = sum(score["score"] * weights[score["criterion_name"]] for score in candidate["scores"])
        candidate["total_weighted_score"] = round(total, 4)
    return batch


def validate_scoring_batch(batch: dict[str, Any], candidate_ids: set[str], criteria: set[str]) -> None:
    scored_ids = [item["candidate_id"] for item in batch["candidate_scores"]]
    if set(scored_ids) != candidate_ids or len(scored_ids) != len(candidate_ids):
        raise ValueError("Every candidate must be scored exactly once")
    for item in batch["candidate_scores"]:
        names = [score["criterion_name"] for score in item["scores"]]
        if set(names) != criteria or len(names) != len(criteria):
            raise ValueError(f"Candidate {item['candidate_id']} is missing criterion scores")
