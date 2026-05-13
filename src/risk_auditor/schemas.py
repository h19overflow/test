from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Criterion(StrictSchema):
    name: str = Field(min_length=1)
    weight: float = Field(gt=0)
    scale: Literal["0-10"] = "0-10"
    ten_point_description: str = Field(min_length=1)


class Rubric(StrictSchema):
    criteria: list[Criterion] = Field(min_length=6, max_length=6)


class CriterionScore(StrictSchema):
    criterion_name: str = Field(min_length=1)
    score: float = Field(ge=0, le=10)
    rationale: str = Field(min_length=1)


class CandidateScore(StrictSchema):
    candidate_id: str = Field(min_length=1)
    scores: list[CriterionScore] = Field(min_length=1)
    total_weighted_score: float | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def validate_unique_criteria(self) -> "CandidateScore":
        names = [item.criterion_name for item in self.scores]
        if len(names) != len(set(names)):
            raise ValueError("Candidate criterion scores must be unique")
        return self


class ScoringBatch(StrictSchema):
    candidate_scores: list[CandidateScore] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_candidates(self) -> "ScoringBatch":
        ids = [item.candidate_id for item in self.candidate_scores]
        if len(ids) != len(set(ids)):
            raise ValueError("Candidate scores must contain unique candidate IDs")
        return self


class RescoredCriterion(StrictSchema):
    candidate_id: str = Field(min_length=1)
    criterion_name: str = Field(min_length=1)
    score: float = Field(ge=0, le=10)
    rationale: str = Field(min_length=1)


class RescoringBatch(StrictSchema):
    rescored_criteria: list[RescoredCriterion] = Field(min_length=1)


class BiasFinding(StrictSchema):
    bias_type: str = Field(min_length=1)
    affected_candidates: list[str] = Field(default_factory=list)
    affected_criteria: list[str] = Field(default_factory=list)
    evidence: str = Field(min_length=1)
    severity: Literal["flagged", "watch", "clear"]

    @model_validator(mode="after")
    def validate_flagged_criteria(self) -> "BiasFinding":
        if self.severity == "flagged" and not self.affected_criteria:
            raise ValueError("Flagged bias findings must identify affected criteria")
        return self


class BiasAudit(StrictSchema):
    findings: list[BiasFinding]
    audit_complete: Literal[True] = True


class ScoreDelta(StrictSchema):
    candidate_id: str = Field(min_length=1)
    criterion_name: str = Field(min_length=1)
    original_score: float = Field(ge=0, le=10)
    corrected_score: float = Field(ge=0, le=10)
    delta: float
    reason: str = Field(min_length=1)


class RankingEntry(StrictSchema):
    candidate_id: str = Field(min_length=1)
    total_weighted_score: float = Field(ge=0)
    rank: int = Field(ge=1)


class CandidateScoresArtifact(StrictSchema):
    approved_rubric_reference: str = Field(min_length=1)
    original_scores: ScoringBatch
    bias_audit_status: Literal["not_started", "completed"]
    flagged_criteria: list[str] = Field(default_factory=list)
    corrected_scores: ScoringBatch | None = None
    score_deltas: list[ScoreDelta] = Field(default_factory=list)
    scores_changed: bool = False
    ranking_source: Literal["", "none", "original_scores", "corrected_scores"] = ""
    final_ranking: list[RankingEntry] = Field(default_factory=list)


class LLMCallRecord(StrictSchema):
    stage: str = Field(min_length=1)
    timestamp: str = Field(min_length=1)
    model: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    prompt_hash: str = Field(min_length=64, max_length=64)
    input_artifacts: list[str] = Field(min_length=1)
    output_artifact: str = Field(min_length=1)
    candidate_names_included: bool


class HiringSummary(StrictSchema):
    candidate_id: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    strengths: list[str] = Field(min_length=1)
    gaps: list[str] = Field(min_length=1)
    interview_focus_areas: list[str] = Field(min_length=3)
    hire_confidence: Literal["Strong Yes", "Yes", "Maybe", "No"]
    confidence_justification: str = Field(min_length=1)


class SummaryReport(StrictSchema):
    top_candidates: list[HiringSummary] = Field(min_length=1)
    rank_one_interview_questions: list[str] = Field(min_length=5)
    cohort_analysis: str = Field(min_length=1)
    counter_intuitive_pick: str | None = None
    blind_reranking_comparison: str | None = None
