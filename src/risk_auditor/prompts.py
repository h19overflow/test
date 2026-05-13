from langchain_core.prompts import ChatPromptTemplate

RUBRIC_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an expert hiring rubric designer. "
                "Create a six-criterion hiring rubric for the given job. "
                "Do not reward items listed in explicitly_not_required. "
                "Ground every criterion firmly in the job description."
            ),
        ),
        (
            "human",
            "Job description JSON:\n{job_description}",
        ),
    ]
)

SCORING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are an impartial candidate evaluator. "
                "Score every candidate against every approved rubric criterion. "
                "Return per-criterion scores and rationales only — "
                "do NOT include or calculate total_weighted_score; that is computed in code."
            ),
        ),
        (
            "human",
            (
                "Job description JSON:\n{job_description}\n\n"
                "Approved rubric JSON:\n{rubric}\n\n"
                "Candidates JSON:\n{candidates}"
            ),
        ),
    ]
)

BIAS_AUDIT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a bias auditor reviewing candidate scores before any ranking is created. "
                "Detect name or nationality signals, credential prestige, employer prestige, "
                "geography, startup/corporate context, and any criteria correlated with demographic signals. "
                "Be rigorous: flag anything that could unfairly advantage or disadvantage a candidate."
            ),
        ),
        (
            "human",
            (
                "Candidates JSON:\n{candidates}\n\n"
                "Approved rubric JSON:\n{rubric}\n\n"
                "Original scores JSON:\n{original_scores}"
            ),
        ),
    ]
)

RESCORING_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a bias-correcting rescorer. "
                "Re-score ONLY the flagged criteria using the anonymized candidates provided. "
                "Do not score unflagged criteria. "
                "You MUST NOT attempt to infer or request candidate names."
            ),
        ),
        (
            "human",
            (
                "Flagged criteria JSON:\n{flagged_criteria}\n\n"
                "Rubric criteria JSON:\n{rubric}\n\n"
                "Anonymized candidates JSON:\n{candidates}\n\n"
                "Original scores JSON:\n{original_scores}"
            ),
        ),
    ]
)

SUMMARY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a hiring committee advisor writing candidate summaries. "
                "Do NOT change scores or rankings. "
                "Include strengths, gaps, interview focus areas, hire confidence, "
                "five tailored questions for the rank-one candidate, and a cohort analysis."
            ),
        ),
        (
            "human",
            (
                "Job description JSON:\n{job_description}\n\n"
                "Approved rubric JSON:\n{rubric}\n\n"
                "Final ranking JSON:\n{final_ranking}\n\n"
                "Final score source:\n{final_score_source}\n\n"
                "Top candidates JSON:\n{top_candidates}\n\n"
                "Bias audit JSON:\n{bias_audit}"
            ),
        ),
    ]
)
