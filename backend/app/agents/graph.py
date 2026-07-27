from langgraph.graph import StateGraph, END
from app.agents.state import ComplaintAgentState
from app.agents.nodes import (
    completeness_check_node,
    risk_classification_node,
    summary_node,
    root_cause_capa_node,
    duplicate_detection_node,
)


def build_complaint_graph():
    """Builds the LangGraph pipeline that analyzes a new complaint:

    completeness_check -> risk_classification -> summary -> root_cause_capa -> duplicate_detection -> END

    Each node is independent and only reads/writes its own state keys, so the sequence can be
    reordered or nodes can be run in parallel branches if desired later.
    """
    graph = StateGraph(ComplaintAgentState)

    graph.add_node("completeness_check", completeness_check_node)
    graph.add_node("risk_classification", risk_classification_node)
    graph.add_node("summary", summary_node)
    graph.add_node("root_cause_capa", root_cause_capa_node)
    graph.add_node("duplicate_detection", duplicate_detection_node)

    graph.set_entry_point("completeness_check")
    graph.add_edge("completeness_check", "risk_classification")
    graph.add_edge("risk_classification", "summary")
    graph.add_edge("summary", "root_cause_capa")
    graph.add_edge("root_cause_capa", "duplicate_detection")
    graph.add_edge("duplicate_detection", END)

    return graph.compile()


# Compiled once at import time; reused across requests.
complaint_graph = build_complaint_graph()


def run_complaint_analysis(complaint_input: dict, existing_complaints: list) -> dict:
    """Runs the full analysis pipeline for one complaint and returns the resulting state dict."""
    initial_state: ComplaintAgentState = {
        **complaint_input,
        "existing_complaints": existing_complaints,
    }
    final_state = complaint_graph.invoke(initial_state)
    return final_state
