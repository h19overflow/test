from risk_auditor.artifacts import update_candidate_scores
from risk_auditor.stages import PipelineStage, assert_at_least
from risk_auditor.state import PipelineState


def finalise_ranking(state: PipelineState) -> PipelineState:
    assert_at_least(PipelineStage(state["stage"]), PipelineStage.BIAS_AUDITED)
    flagged = state.get("flagged_criteria", [])
    if flagged and state["stage"] != PipelineStage.FLAGGED_RESCORING_COMPLETE.value:
        raise RuntimeError("Flagged bias requires corrected scores before ranking")
    source = "corrected_scores" if flagged else "original_scores"
    scores = state.get(source)
    if not scores:
        raise RuntimeError(f"{source} is required before ranking")
    ranking = sorted(
        [
            {"candidate_id": item["candidate_id"], "total_weighted_score": item["total_weighted_score"], "rank": 0}
            for item in scores["candidate_scores"]
        ],
        key=lambda item: item["total_weighted_score"],
        reverse=True,
    )
    for index, item in enumerate(ranking, start=1):
        item["rank"] = index
    update_candidate_scores(ranking_source=source, final_ranking=ranking)
    return {"final_ranking": ranking, "stage": PipelineStage.RANKING_FINALISED.value}
