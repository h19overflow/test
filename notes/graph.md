# Recruitment graph notes

`src/risk_auditor/graph.py` aggregates the node files and compiles the `StateGraph`
with `InMemorySaver`. The only dynamic route is `approve_rubric`, so the graph does
not add a static edge from `approve_rubric` to `score_candidates`.

Node order: `load_inputs -> generate_rubric -> approve_rubric -> score_candidates
-> audit_bias -> maybe_rescore -> finalise_ranking -> generate_summaries`.
