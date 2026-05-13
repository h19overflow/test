from risk_auditor.artifacts import read_json
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import validate_candidates, validate_job_description


def load_inputs(state: PipelineState) -> PipelineState:
    job_path = state.get("job_description_path", "data/job_description.json")
    candidates_path = state.get("candidates_path", "data/candidates.json")
    job = read_json(job_path)
    candidates = read_json(candidates_path)
    validate_job_description(job)
    validate_candidates(candidates)
    return {
        "stage": PipelineStage.INIT.value,
        "job_description_path": job_path,
        "candidates_path": candidates_path,
        "job_description": job,
        "candidates": candidates,
        "artifacts": {},
    }
