from typing import Literal

from langgraph.types import Command, interrupt

from risk_auditor.artifacts import SCORING_RUBRIC, write_json
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import require_stage, validate_rubric


def approve_rubric(state: PipelineState) -> Command[Literal["generate_rubric", "score_candidates"]]:
    require_stage(state, PipelineStage.RUBRIC_GENERATED)
    decision = interrupt(
        {
            "checkpoint": "rubric_approval",
            "question": "Approve, edit, or regenerate the rubric?",
            "draft_rubric": state["draft_rubric"],
            "allowed_actions": ["approve", "edit", "regenerate"],
            "resume_schema": {"action": "approve | edit | regenerate", "edited_rubric": "required for edit"},
        }
    )
    action = decision.get("action") if isinstance(decision, dict) else None
    if action == "regenerate":
        return Command(update={"stage": PipelineStage.INIT.value}, goto="generate_rubric")
    rubric_data = decision.get("edited_rubric") if action == "edit" else state["draft_rubric"]
    if action not in {"approve", "edit"} or not isinstance(rubric_data, dict):
        raise ValueError("Resume payload must approve, edit, or regenerate the rubric")
    rubric = validate_rubric(rubric_data).model_dump()
    write_json(SCORING_RUBRIC, rubric)
    artifacts = {**state.get("artifacts", {}), "scoring_rubric": SCORING_RUBRIC}
    return Command(
        update={"approved_rubric": rubric, "artifacts": artifacts, "stage": PipelineStage.RUBRIC_APPROVED.value},
        goto="score_candidates",
    )
