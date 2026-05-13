import json

from risk_auditor.artifacts import append_llm_call
from risk_auditor.base_agent import BaseAgent
from risk_auditor.prompts import RUBRIC_PROMPT
from risk_auditor.schemas import Rubric
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import require_stage, validate_rubric


def generate_rubric(state: PipelineState) -> PipelineState:
    require_stage(state, PipelineStage.INIT)
    prompt_kwargs = {"job_description": json.dumps(state["job_description"], indent=2)}
    agent = BaseAgent(Rubric)
    rubric = validate_rubric(agent.invoke(RUBRIC_PROMPT, **prompt_kwargs).model_dump())
    rendered = RUBRIC_PROMPT.format_messages(**prompt_kwargs)[-1].content
    append_llm_call(
        stage=PipelineStage.RUBRIC_GENERATED.value,
        prompt=rendered,
        model=agent.model_name,
        input_artifacts=[state.get("job_description_path", "data/job_description.json")],
        output_artifact="state.draft_rubric",
        candidate_names_included=False,
    )
    return {"draft_rubric": rubric.model_dump(), "stage": PipelineStage.RUBRIC_GENERATED.value}
