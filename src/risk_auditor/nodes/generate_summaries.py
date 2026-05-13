import json

from risk_auditor.artifacts import BIAS_AUDIT, CANDIDATE_SCORES, HIRING_SUMMARIES, append_llm_call, read_json
from risk_auditor.base_agent import BaseAgent
from risk_auditor.prompts import SUMMARY_PROMPT
from risk_auditor.schemas import SummaryReport
from risk_auditor.stages import PipelineStage
from risk_auditor.state import PipelineState
from risk_auditor.validation import require_stage


def generate_summaries(state: PipelineState) -> PipelineState:
    require_stage(state, PipelineStage.RANKING_FINALISED)
    top_ids = [item["candidate_id"] for item in state["final_ranking"][:3]]
    top_candidates = [item for item in state["candidates"] if item["id"] in top_ids]
    final_score_source = read_json(CANDIDATE_SCORES).get("ranking_source", "")
    prompt_kwargs = {
        "job_description": json.dumps(state["job_description"], indent=2),
        "rubric": json.dumps(state["approved_rubric"], indent=2),
        "final_ranking": json.dumps(state["final_ranking"], indent=2),
        "final_score_source": final_score_source,
        "top_candidates": json.dumps(top_candidates, indent=2),
        "bias_audit": json.dumps(state["bias_audit"], indent=2),
    }
    agent = BaseAgent(SummaryReport)
    report = agent.invoke(SUMMARY_PROMPT, **prompt_kwargs)
    markdown = _to_markdown(report)
    with open(HIRING_SUMMARIES, "w", encoding="utf-8") as handle:
        handle.write(markdown)
    rendered = SUMMARY_PROMPT.format_messages(**prompt_kwargs)[-1].content
    append_llm_call(
        stage=PipelineStage.SUMMARIES_GENERATED.value,
        prompt=rendered,
        model=agent.model_name,
        input_artifacts=[state.get("job_description_path", "data/job_description.json"), state.get("candidates_path", "data/candidates.json"), CANDIDATE_SCORES, BIAS_AUDIT],
        output_artifact=HIRING_SUMMARIES,
        candidate_names_included=True,
    )
    return {"summaries_markdown": markdown, "stage": PipelineStage.SUMMARIES_GENERATED.value}


def _to_markdown(report: SummaryReport) -> str:
    lines = ["# Hiring Summaries", ""]
    for item in report.top_candidates[:3]:
        lines.extend([f"## {item.candidate_id}", item.summary, "", "### Strengths"])
        lines.extend(f"- {value}" for value in item.strengths)
        lines.append("### Gaps")
        lines.extend(f"- {value}" for value in item.gaps)
        lines.append("### Interview focus areas")
        lines.extend(f"- {value}" for value in item.interview_focus_areas[:3])
        lines.extend([f"**Hire confidence:** {item.hire_confidence}", item.confidence_justification, ""])
    lines.append("## Rank 1 interview questions")
    lines.extend(f"- {value}" for value in report.rank_one_interview_questions[:5])
    lines.extend(["", "## Cohort analysis", report.cohort_analysis])
    if report.counter_intuitive_pick:
        lines.extend(["", "## Counter-intuitive pick", report.counter_intuitive_pick])
    if report.blind_reranking_comparison:
        lines.extend(["", "## Blind re-ranking comparison", report.blind_reranking_comparison])
    return "\n".join(lines) + "\n"
