import json
from pathlib import Path

from risk_auditor.artifacts import BIAS_AUDIT, CANDIDATE_SCORES, SCORING_RUBRIC, append_llm_call, update_candidate_scores, write_json
from risk_auditor.base_agent import BaseAgent
from risk_auditor.prompts import BIAS_AUDIT_PROMPT
from risk_auditor.schemas import BiasAudit
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import require_stage


def audit_bias(state: PipelineState) -> PipelineState:
    require_stage(state, PipelineStage.CANDIDATES_SCORED)
    if not Path(CANDIDATE_SCORES).exists():
        raise RuntimeError("candidate_scores.json is required before bias audit")
    if state.get("final_ranking"):
        raise RuntimeError("Bias audit must complete before ranking")
    prompt = BIAS_AUDIT_PROMPT.format(
        candidates=json.dumps(state["candidates"], indent=2),
        rubric=json.dumps(state["approved_rubric"], indent=2),
        original_scores=json.dumps(state["original_scores"], indent=2),
    )
    agent = BaseAgent(BiasAudit)
    audit = agent.invoke(prompt).model_dump()
    flagged = sorted({criterion for finding in audit["findings"] if finding["severity"] == "flagged" for criterion in finding["affected_criteria"]})
    write_json(BIAS_AUDIT, audit)
    update_candidate_scores(bias_audit_status="completed", flagged_criteria=flagged)
    append_llm_call(
        stage=PipelineStage.BIAS_AUDITED.value,
        prompt=prompt,
        model=agent.model_name,
        input_artifacts=[state.get("candidates_path", "data/candidates.json"), SCORING_RUBRIC, CANDIDATE_SCORES],
        output_artifact=BIAS_AUDIT,
        candidate_names_included=True,
    )
    return {"bias_audit": audit, "flagged_criteria": flagged, "stage": PipelineStage.BIAS_AUDITED.value}
