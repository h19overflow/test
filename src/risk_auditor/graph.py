from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph

from risk_auditor.nodes import (
    approve_rubric,
    audit_bias,
    finalise_ranking,
    generate_rubric,
    generate_summaries,
    load_inputs,
    maybe_rescore,
    score_candidates,
)
from risk_auditor.state import PipelineState


def build_recruitment_graph() -> StateGraph:
    graph = StateGraph(PipelineState)
    graph.add_node("load_inputs", load_inputs)
    graph.add_node("generate_rubric", generate_rubric)
    graph.add_node("approve_rubric", approve_rubric)
    graph.add_node("score_candidates", score_candidates)
    graph.add_node("audit_bias", audit_bias)
    graph.add_node("maybe_rescore", maybe_rescore)
    graph.add_node("finalise_ranking", finalise_ranking)
    graph.add_node("generate_summaries", generate_summaries)
    graph.add_edge(START, "load_inputs")
    graph.add_edge("load_inputs", "generate_rubric")
    graph.add_edge("generate_rubric", "approve_rubric")
    graph.add_edge("score_candidates", "audit_bias")
    graph.add_edge("audit_bias", "maybe_rescore")
    graph.add_edge("maybe_rescore", "finalise_ranking")
    graph.add_edge("finalise_ranking", "generate_summaries")
    graph.add_edge("generate_summaries", END)
    return graph


def compile_graph():
    return build_recruitment_graph().compile(checkpointer=InMemorySaver())
