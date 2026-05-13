from enum import StrEnum


class PipelineStage(StrEnum):
    INIT = "INIT"
    RUBRIC_GENERATED = "RUBRIC_GENERATED"
    RUBRIC_APPROVED = "RUBRIC_APPROVED"
    CANDIDATES_SCORED = "CANDIDATES_SCORED"
    BIAS_AUDITED = "BIAS_AUDITED"
    FLAGGED_RESCORING_COMPLETE = "FLAGGED_RESCORING_COMPLETE"
    RANKING_FINALISED = "RANKING_FINALISED"
    SUMMARIES_GENERATED = "SUMMARIES_GENERATED"


STAGE_ORDER = [
    PipelineStage.INIT,
    PipelineStage.RUBRIC_GENERATED,
    PipelineStage.RUBRIC_APPROVED,
    PipelineStage.CANDIDATES_SCORED,
    PipelineStage.BIAS_AUDITED,
    PipelineStage.FLAGGED_RESCORING_COMPLETE,
    PipelineStage.RANKING_FINALISED,
    PipelineStage.SUMMARIES_GENERATED,
]


def assert_at_least(current: PipelineStage, required: PipelineStage) -> None:
    if STAGE_ORDER.index(current) < STAGE_ORDER.index(required):
        raise RuntimeError(f"{required} is required before current stage {current}")
