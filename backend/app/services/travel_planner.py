"""
Travel planner service — converts agent state to API response schema.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from app.agents.graph import run_travel_agent
from app.agents.state import TravelAgentState
from app.schemas.travel import (
    Attraction,
    Coordinates,
    ItineraryItem,
    RouteInfo,
    SafetyAdvisory,
    SourceLink,
    TravelPlanResponse,
    WeatherData,
)

logger = logging.getLogger(__name__)


def _build_weather(raw: Optional[dict[str, Any]]) -> Optional[WeatherData]:
    if not raw:
        return None
    if raw.get("unavailable_reason") and raw.get("temperature_c") is None:
        return WeatherData(
            unavailable_reason=raw["unavailable_reason"],
            is_forecast=raw.get("is_forecast", False),
            forecast_date=raw.get("forecast_date"),
        )
    if raw.get("error"):
        return WeatherData(unavailable_reason=f"Error: {raw['error']}")
    return WeatherData(
        temperature_c=raw.get("temperature_c"),
        feels_like_c=raw.get("feels_like_c"),
        condition=raw.get("condition"),
        description=raw.get("description"),
        humidity_percent=raw.get("humidity_percent"),
        wind_speed_kmh=raw.get("wind_speed_kmh"),
        icon=raw.get("icon"),
        is_forecast=raw.get("is_forecast", False),
        forecast_date=raw.get("forecast_date"),
        retrieved_at=raw.get("retrieved_at"),
        unavailable_reason=raw.get("unavailable_reason"),
    )


def _build_attractions(raw: list[dict[str, Any]]) -> list[Attraction]:
    results = []
    for a in raw:
        coord = None
        if a.get("coordinates"):
            c = a["coordinates"]
            coord = Coordinates(lat=c["lat"], lon=c["lon"])
        results.append(Attraction(
            name=a.get("name", ""),
            category=a.get("category"),
            address=a.get("address"),
            coordinates=coord,
            opening_hours=a.get("opening_hours"),
        ))
    return results


def _build_route(raw: Optional[dict[str, Any]], origin: Optional[str], destination: Optional[str], mode: Optional[str]) -> Optional[RouteInfo]:
    if not raw or raw.get("error"):
        return None
    return RouteInfo(
        origin=origin,
        destination=destination,
        distance_km=raw.get("distance_km"),
        duration_minutes=raw.get("duration_minutes"),
        mode=raw.get("mode", mode),
        geometry=raw.get("geometry"),
        external_nav_url=raw.get("external_nav_url"),
        summary=(
            f"{raw.get('distance_km', '?')} km · "
            f"~{raw.get('duration_minutes', '?')} min by {mode or 'car'}"
        ),
    )


def _build_advisories(raw: list[dict[str, Any]]) -> list[SafetyAdvisory]:
    results = []
    for a in raw:
        results.append(SafetyAdvisory(
            type=a.get("type", "general"),
            severity=a.get("severity", "unknown"),
            summary=a.get("summary", ""),
            source_url=a.get("source_url"),
            source_title=a.get("source_title"),
            published_at=a.get("published_at"),
            retrieved_at=a.get("retrieved_at"),
            verified=a.get("verified", False),
        ))
    return results


def _build_sources(raw: list[dict[str, Any]]) -> list[SourceLink]:
    results = []
    seen = set()
    for s in raw:
        url = s.get("url", "")
        if url and url not in seen:
            seen.add(url)
            results.append(SourceLink(
                title=s.get("title", url),
                url=url,
                snippet=s.get("snippet"),
                published_at=s.get("published_at"),
                retrieved_at=s.get("retrieved_at"),
            ))
    return results


def _build_itinerary(raw: list[dict[str, Any]]) -> list[ItineraryItem]:
    results = []
    for item in raw:
        coord = None
        if item.get("coordinates"):
            c = item["coordinates"]
            coord = Coordinates(lat=c["lat"], lon=c["lon"])
        results.append(ItineraryItem(
            time=item.get("time"),
            title=item.get("title", ""),
            description=item.get("description"),
            location=item.get("location"),
            coordinates=coord,
            duration_minutes=item.get("duration_minutes"),
            type=item.get("type", "activity"),
        ))
    return results


async def plan_trip(message: str, session_id: Optional[str] = None) -> TravelPlanResponse:
    """Run the agent and convert the result to the API response schema."""
    if not session_id:
        session_id = str(uuid.uuid4())

    state = await run_travel_agent(message, session_id)

    # Destination coordinates
    dest_coords = None
    if state.get("dest_lat") and state.get("dest_lon"):
        dest_coords = Coordinates(lat=state["dest_lat"], lon=state["dest_lon"])

    return TravelPlanResponse(
        session_id=state.get("session_id", session_id),
        message_type=state.get("message_type", "travel_plan"),
        summary=state.get("summary") or state.get("clarification_question"),
        clarification_needed=state.get("clarification_question"),
        destination=state.get("destination"),
        origin=state.get("origin"),
        travel_date=state.get("travel_date"),
        travel_date_interpreted=state.get("travel_date_interpreted"),
        transport_mode=state.get("transport_mode"),
        weather=_build_weather(state.get("weather_data")),
        attractions=_build_attractions(state.get("attractions", [])),
        route=_build_route(
            state.get("route_data"),
            state.get("origin"),
            state.get("destination"),
            state.get("transport_mode"),
        ),
        itinerary=_build_itinerary(state.get("itinerary", [])),
        safety_advisories=_build_advisories(state.get("safety_advisories", [])),
        sources=_build_sources(state.get("sources", [])),
        destination_coordinates=dest_coords,
        missing_information=state.get("missing_info", []),
        data_warnings=state.get("data_warnings", []),
        tools_used=state.get("tools_used", []),
        tools_unavailable=state.get("tools_unavailable", []),
    )
