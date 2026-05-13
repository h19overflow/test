import copy
import json

from risk_auditor.artifacts import CANDIDATE_SCORES, SCORING_RUBRIC, append_llm_call, update_candidate_scores
from risk_auditor.base_agent import BaseAgent
from risk_auditor.prompts import RESCORING_PROMPT
from risk_auditor.schemas import ScoringBatch
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import recompute_scores, require_stage


def maybe_rescore(state: PipelineState) -> PipelineState:
    require_stage(state, PipelineStage.BIAS_AUDITED)
    if not state["bias_audit"].get("audit_complete"):
        raise RuntimeError("Bias audit must be complete before rescore")
    flagged = state.get("flagged_criteria", [])
    if not flagged:
        update_candidate_scores(corrected_scores=state["original_scores"], scores_changed=False)
        return {"corrected_scores": state["original_scores"], "stage": PipelineStage.BIAS_AUDITED.value}
    anonymized = [{"id": item["id"], "summary": item["summary"]} for item in state["candidates"]]
    rubric = {"criteria": [item for item in state["approved_rubric"]["criteria"] if item["name"] in flagged]}
    prompt_kwargs = {
        "flagged_criteria": json.dumps(flagged, indent=2),
        "rubric": json.dumps(rubric, indent=2),
        "candidates": json.dumps(anonymized, indent=2),
        "original_scores": json.dumps(state["original_scores"], indent=2),
    }
    agent = BaseAgent(ScoringBatch)
    rescored = agent.invoke(RESCORING_PROMPT, **prompt_kwargs).model_dump()
    corrected = _merge_scores(state["original_scores"], rescored, set(flagged))
    corrected = recompute_scores(corrected, state["approved_rubric"])
    changed = corrected != state["original_scores"]
    update_candidate_scores(corrected_scores=corrected, flagged_criteria=flagged, scores_changed=changed)
    rendered = RESCORING_PROMPT.format_messages(**prompt_kwargs)[-1].content
    append_llm_call(
        stage=PipelineStage.FLAGGED_RESCORING_COMPLETE.value,
        prompt=rendered,
        model=agent.model_name,
        input_artifacts=["bias_audit.json", CANDIDATE_SCORES, SCORING_RUBRIC],
        output_artifact=CANDIDATE_SCORES,
        candidate_names_included=False,
    )
    return {"corrected_scores": corrected, "stage": PipelineStage.FLAGGED_RESCORING_COMPLETE.value}


def _merge_scores(original: dict, rescored: dict, flagged: set[str]) -> dict:
    corrected = copy.deepcopy(original)
    by_id = {item["candidate_id"]: item for item in corrected["candidate_scores"]}
    for candidate in rescored["candidate_scores"]:
        target = by_id.get(candidate["candidate_id"])
        if target is None:
            continue
        replacement = {score["criterion_name"]: score for score in candidate["scores"] if score["criterion_name"] in flagged}
        target["scores"] = [replacement.get(score["criterion_name"], score) for score in target["scores"]]
    return corrected
