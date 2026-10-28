"""
LangGraph agent state definition.
All data flows through this typed state dictionary.
"""

from __future__ import annotations

from typing import Any, Optional, TypedDict


class TravelAgentState(TypedDict, total=False):
    # Input
    user_message: str
    session_id: str

    # Parsed trip details
    destination: Optional[str]
    origin: Optional[str]
    travel_date: Optional[str]
    travel_date_interpreted: Optional[str]
    transport_mode: Optional[str]
    preferences: list[str]
    needs_clarification: bool
    clarification_question: Optional[str]

    # Coordinates
    dest_lat: Optional[float]
    dest_lon: Optional[float]
    origin_lat: Optional[float]
    origin_lon: Optional[float]

    # Tool results
    weather_data: Optional[dict[str, Any]]
    places_data: Optional[dict[str, Any]]
    route_data: Optional[dict[str, Any]]
    search_results: list[dict[str, Any]]
    safety_data: Optional[dict[str, Any]]

    # Validated / synthesized
    attractions: list[dict[str, Any]]
    safety_advisories: list[dict[str, Any]]
    sources: list[dict[str, Any]]
    missing_info: list[str]
    data_warnings: list[str]
    tools_used: list[str]
    tools_unavailable: list[str]

    # Final response
    summary: Optional[str]
    itinerary: list[dict[str, Any]]
    message_type: str  # "travel_plan" | "clarification" | "error"

    # Error tracking
    error: Optional[str]
    retry_count: int
