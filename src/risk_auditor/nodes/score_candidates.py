import json
from pathlib import Path

from risk_auditor.artifacts import CANDIDATE_SCORES, SCORING_RUBRIC, append_llm_call, write_json
from risk_auditor.base_agent import BaseAgent
from risk_auditor.prompts import SCORING_PROMPT
from risk_auditor.schemas import ScoringBatch
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import recompute_scores, require_stage, rubric_names, validate_scoring_batch


def score_candidates(state: PipelineState) -> PipelineState:
    require_stage(state, PipelineStage.RUBRIC_APPROVED)
    if not Path(SCORING_RUBRIC).exists():
        raise RuntimeError("scoring_rubric.json is required before candidate scoring")
    prompt_kwargs = {
        "job_description": json.dumps(state["job_description"], indent=2),
        "rubric": json.dumps(state["approved_rubric"], indent=2),
        "candidates": json.dumps(state["candidates"], indent=2),
    }
    agent = BaseAgent(ScoringBatch)
    batch = agent.invoke(SCORING_PROMPT, **prompt_kwargs).model_dump()
    batch = recompute_scores(batch, state["approved_rubric"])
    validate_scoring_batch(batch, {item["id"] for item in state["candidates"]}, set(rubric_names(state["approved_rubric"])))
    rendered = SCORING_PROMPT.format_messages(**prompt_kwargs)[-1].content
    artifact = {
        "approved_rubric_reference": SCORING_RUBRIC,
        "original_scores": batch,
        "bias_audit_status": "not_started",
        "flagged_criteria": [],
        "corrected_scores": None,
        "scores_changed": False,
        "ranking_source": "",
        "final_ranking": [],
    }
    write_json(CANDIDATE_SCORES, artifact)
    append_llm_call(
        stage=PipelineStage.CANDIDATES_SCORED.value,
        prompt=rendered,
        model=agent.model_name,
        input_artifacts=[state.get("job_description_path", "data/job_description.json"), state.get("candidates_path", "data/candidates.json"), SCORING_RUBRIC],
        output_artifact=CANDIDATE_SCORES,
        candidate_names_included=True,
    )
    return {"original_scores": batch, "stage": PipelineStage.CANDIDATES_SCORED.value}
