from typing import Any, TypedDict


class PipelineState(TypedDict, total=False):
    stage: str
    job_description_path: str
    candidates_path: str
    job_description: dict[str, Any]
    candidates: list[dict[str, Any]]
    draft_rubric: dict[str, Any]
    approved_rubric: dict[str, Any]
    original_scores: dict[str, Any]
    bias_audit: dict[str, Any]
    flagged_criteria: list[str]
    corrected_scores: dict[str, Any]
    final_ranking: list[dict[str, Any]]
    summaries_markdown: str
    artifacts: dict[str, str]
