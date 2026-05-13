# approve_rubric

Uses LangGraph `interrupt()` for HITL approval. On approve/edit it validates and
writes `scoring_rubric.json`; on regenerate it routes back to `generate_rubric`.
No file writes happen before the interrupt resumes.
