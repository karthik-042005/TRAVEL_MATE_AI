"""
LangGraph StateGraph — TravelMate AI agent workflow.

Graph flow:
  parse_request → plan_research → [needs_clarification?] → END (clarification)
                                                         → retrieve_data
                                                         → validate_evidence
                                                         → generate_plan
                                                         → format_response → END
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from app.agents.nodes import (
    node_format_response,
    node_generate_plan,
    node_parse_request,
    node_plan_research,
    node_retrieve_data,
    node_validate_evidence,
)
from app.agents.state import TravelAgentState

logger = logging.getLogger(__name__)

# In-memory checkpointer — state is lost on restart
_memory = MemorySaver()


def _should_clarify(state: TravelAgentState) -> str:
    """Conditional edge: route to clarification or continue research."""
    if state.get("needs_clarification"):
        return "clarify"
    return "continue"


def build_graph() -> StateGraph:
    """Build and compile the TravelMate LangGraph workflow."""
    graph = StateGraph(TravelAgentState)

    # Register nodes
    graph.add_node("parse_request", node_parse_request)
    graph.add_node("plan_research", node_plan_research)
    graph.add_node("retrieve_data", node_retrieve_data)
    graph.add_node("validate_evidence", node_validate_evidence)
    graph.add_node("generate_plan", node_generate_plan)
    graph.add_node("format_response", node_format_response)

    # Entry point
    graph.set_entry_point("parse_request")

    # Edges
    graph.add_edge("parse_request", "plan_research")
    graph.add_conditional_edges(
        "plan_research",
        _should_clarify,
        {
            "clarify": "format_response",  # Skip retrieval if clarification needed
            "continue": "retrieve_data",
        },
    )
    graph.add_edge("retrieve_data", "validate_evidence")
    graph.add_edge("validate_evidence", "generate_plan")
    graph.add_edge("generate_plan", "format_response")
    graph.add_edge("format_response", END)

    return graph.compile(checkpointer=_memory)


# Module-level compiled graph (singleton)
travel_graph = build_graph()


async def run_travel_agent(
    user_message: str,
    session_id: Optional[str] = None,
) -> TravelAgentState:
    """
    Run the travel planning agent.
    Creates a new session ID if not provided.
    Reuses the InMemorySaver checkpoint for the same session_id.
    """
    if not session_id:
        session_id = str(uuid.uuid4())

    initial_state: TravelAgentState = {
        "user_message": user_message,
        "session_id": session_id,
        "message_type": "travel_plan",
        "retry_count": 0,
    }

    config = {"configurable": {"thread_id": session_id}}

    try:
        final_state = await travel_graph.ainvoke(initial_state, config=config)
        final_state["session_id"] = session_id
        return final_state
    except Exception as e:
        logger.error("Agent error: %s", e)
        return {
            "user_message": user_message,
            "session_id": session_id,
            "message_type": "error",
            "error": str(e),
            "summary": f"An error occurred while planning your trip: {e}",
            "missing_info": [],
            "data_warnings": [],
            "tools_used": [],
            "tools_unavailable": [],
            "attractions": [],
            "safety_advisories": [],
            "sources": [],
            "itinerary": [],
        }
