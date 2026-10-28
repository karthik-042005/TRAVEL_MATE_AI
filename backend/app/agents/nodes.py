"""
LangGraph agent nodes — A through F.

Node A: Parse request
Node B: Plan research
Node C: Retrieve data (parallel)
Node D: Validate evidence
Node E: Generate plan (LLM synthesis)
Node F: Format response
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from app.agents.prompts import PARSE_SYSTEM, SYNTHESIZE_SYSTEM
from app.agents.state import TravelAgentState
from app.config import settings
from app.tools import maps as maps_tool
from app.tools import weather as weather_tool
from app.tools.safety import research_safety
from app.tools.web_search import find_recent_attractions, search_web

logger = logging.getLogger(__name__)
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


# ─── Helper: call Ollama directly ──────────────────────────────────────────────


async def _ollama_chat(system: str, user: str, timeout: int = 60) -> str:
    """Call Ollama /api/chat and return the assistant message text."""
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "stream": False,
        "options": {"temperature": 0.3, "num_predict": 1024},
    }
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("message", {}).get("content", "")
    except Exception as e:
        logger.error("Ollama call failed: %s", e)
        raise


def _extract_json(text: str) -> dict[str, Any]:
    """Extract JSON from LLM response, handling markdown fences."""
    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text).replace("```", "").strip()
    # Find first { ... } block
    start = cleaned.find("{")
    end = cleaned.rfind("}") + 1
    if start == -1 or end == 0:
        return {}
    try:
        return json.loads(cleaned[start:end])
    except json.JSONDecodeError:
        return {}


# ─── Node A: Parse request ─────────────────────────────────────────────────────


async def node_parse_request(state: TravelAgentState) -> TravelAgentState:
    """Extract destination, date, origin, transport mode, preferences."""
    user_msg = state.get("user_message", "")
    logger.info("Node A: Parsing request: %r", user_msg[:100])

    system = PARSE_SYSTEM.format(today=TODAY)
    try:
        raw = await _ollama_chat(system, user_msg, timeout=45)
        parsed = _extract_json(raw)
    except Exception as e:
        logger.error("Parse node LLM error: %s", e)
        parsed = {}

    # Resolve ambiguous dates
    travel_date = parsed.get("travel_date")
    travel_date_interpreted = None
    if travel_date and re.match(r"^\d{4}-\d{2}-\d{2}$", str(travel_date)):
        travel_date_interpreted = travel_date
    elif travel_date:
        travel_date_interpreted = f"Interpreted from: '{travel_date}'"

    return {
        **state,
        "destination": parsed.get("destination"),
        "origin": parsed.get("origin"),
        "travel_date": travel_date,
        "travel_date_interpreted": travel_date_interpreted,
        "transport_mode": parsed.get("transport_mode", "car"),
        "preferences": parsed.get("preferences", []),
        "needs_clarification": parsed.get("needs_clarification", False),
        "clarification_question": parsed.get("clarification_question"),
        "tools_used": [],
        "tools_unavailable": [],
        "missing_info": [],
        "data_warnings": [],
        "search_results": [],
        "attractions": [],
        "safety_advisories": [],
        "sources": [],
        "itinerary": [],
        "retry_count": state.get("retry_count", 0),
    }


# ─── Node B: Plan research ──────────────────────────────────────────────────────


async def node_plan_research(state: TravelAgentState) -> TravelAgentState:
    """Determine which tools are needed based on available config and parsed state."""
    configured = settings.configured_tools()
    missing = settings.missing_keys()

    tools_unavailable = []
    if not configured["web_search"]:
        tools_unavailable.append("web_search (TAVILY_API_KEY missing)")
    if not configured["weather"]:
        tools_unavailable.append("weather (OPENWEATHER_API_KEY missing)")
    if not configured["maps"]:
        tools_unavailable.append("maps (GEOAPIFY_API_KEY missing)")

    logger.info("Node B: Research plan — configured=%s, missing=%s", configured, missing)

    return {
        **state,
        "tools_unavailable": tools_unavailable,
    }


# ─── Node C: Retrieve data ──────────────────────────────────────────────────────


async def node_retrieve_data(state: TravelAgentState) -> TravelAgentState:
    """Run independent retrieval tasks concurrently."""
    destination = state.get("destination", "")
    origin = state.get("origin")
    travel_date = state.get("travel_date")
    transport_mode = state.get("transport_mode", "car")
    configured = settings.configured_tools()
    tools_used = list(state.get("tools_used", []))

    logger.info("Node C: Retrieving data for destination=%r date=%r", destination, travel_date)

    # Build async tasks
    tasks = {}

    if configured["web_search"] and destination:
        tasks["attractions_search"] = find_recent_attractions(destination)
        tasks["general_search"] = search_web(f"travel guide {destination} best places to visit")

    if configured["weather"] and destination:
        if travel_date:
            tasks["weather"] = weather_tool.get_weather_forecast(destination, travel_date)
        else:
            tasks["weather"] = weather_tool.get_current_weather(destination)

    if configured["maps"] and destination:
        tasks["geocode_dest"] = maps_tool.geocode_location(destination)
        tasks["places"] = maps_tool.search_places(destination)

    if configured["safety_research"] and destination:
        tasks["safety"] = research_safety(destination, travel_date)

    # Run all tasks concurrently
    results: dict[str, Any] = {}
    if tasks:
        coro_list = list(tasks.values())
        keys = list(tasks.keys())
        try:
            outputs = await asyncio.gather(*coro_list, return_exceptions=True)
            for k, v in zip(keys, outputs):
                if isinstance(v, Exception):
                    logger.error("Task %s failed: %s", k, v)
                    results[k] = {"error": str(v)}
                else:
                    results[k] = v
        except Exception as e:
            logger.error("Retrieve gather error: %s", e)

    # Extract coordinates
    dest_lat = dest_lon = origin_lat = origin_lon = None
    if "geocode_dest" in results and not results["geocode_dest"].get("error"):
        geo = results["geocode_dest"]
        dest_lat = geo.get("lat")
        dest_lon = geo.get("lon")
        if configured["maps"]:
            tools_used.append("geocode")

    # If origin provided, geocode it and calculate route
    route_data = None
    if configured["maps"] and origin and dest_lat and dest_lon:
        try:
            origin_geo = await maps_tool.geocode_location(origin)
            origin_lat = origin_geo.get("lat")
            origin_lon = origin_geo.get("lon")
            if origin_lat and origin_lon:
                route_data = await maps_tool.calculate_route(
                    origin_lat, origin_lon, dest_lat, dest_lon, transport_mode or "drive"
                )
                tools_used.append("routing")
        except Exception as e:
            logger.error("Route calc error: %s", e)

    # Track tool usage
    if "attractions_search" in results:
        tools_used.append("web_search")
    if "weather" in results:
        tools_used.append("weather")
    if "places" in results:
        tools_used.append("places_search")
    if "safety" in results:
        tools_used.append("safety_research")

    return {
        **state,
        "weather_data": results.get("weather"),
        "places_data": results.get("places"),
        "search_results": (
            results.get("attractions_search", []) + results.get("general_search", [])
        ),
        "safety_data": results.get("safety"),
        "route_data": route_data,
        "dest_lat": dest_lat,
        "dest_lon": dest_lon,
        "origin_lat": origin_lat,
        "origin_lon": origin_lon,
        "tools_used": list(set(tools_used)),
    }


# ─── Node D: Validate evidence ─────────────────────────────────────────────────


async def node_validate_evidence(state: TravelAgentState) -> TravelAgentState:
    """Check timestamps, separate facts from forecasts, note missing data."""
    missing_info = list(state.get("missing_info", []))
    data_warnings = list(state.get("data_warnings", []))

    # Weather validation
    weather = state.get("weather_data")
    if not weather:
        missing_info.append("Weather data unavailable — OPENWEATHER_API_KEY not configured.")
    elif weather.get("unavailable_reason"):
        data_warnings.append(weather["unavailable_reason"])
    elif weather.get("error"):
        missing_info.append(f"Weather error: {weather['error']}")

    # Places / attractions
    places = state.get("places_data")
    attractions: list[dict] = []
    if places and places.get("places"):
        for p in places["places"]:
            if p.get("name") and p["name"] != "Unknown":
                attractions.append({
                    "name": p["name"],
                    "category": p.get("category"),
                    "address": p.get("address"),
                    "coordinates": (
                        {"lat": p["lat"], "lon": p["lon"]}
                        if p.get("lat") and p.get("lon") else None
                    ),
                    "opening_hours": p.get("opening_hours"),
                    "website": p.get("website"),
                })
    elif not settings.geoapify_api_key:
        missing_info.append(
            "Place search unavailable — GEOAPIFY_API_KEY not configured. "
            "Attractions sourced from web search only."
        )

    # Supplement attractions with web search results
    search_results = state.get("search_results", [])
    sources: list[dict] = []
    for r in search_results[:8]:
        title = r.get("title", "")
        url = r.get("url", "")
        snippet = r.get("content", r.get("snippet", ""))
        if url:
            sources.append({
                "title": title,
                "url": url,
                "snippet": snippet[:200],
                "published_at": r.get("published_date"),
                "retrieved_at": r.get("retrieved_at"),
            })

    # Route validation
    route = state.get("route_data")
    if not state.get("origin") and settings.geoapify_api_key:
        missing_info.append(
            "No origin provided — route cannot be calculated. "
            "Please specify your starting location."
        )
    elif route and route.get("error"):
        data_warnings.append(f"Route calculation issue: {route['error']}")

    # Safety data
    safety = state.get("safety_data")
    safety_advisories: list[dict] = []
    if safety:
        safety_advisories = safety.get("advisories", [])
        if safety.get("no_results_note"):
            data_warnings.append(safety["no_results_note"])
        if safety.get("disclaimer"):
            data_warnings.append(safety["disclaimer"])
    elif not settings.tavily_api_key:
        missing_info.append("Safety research unavailable — TAVILY_API_KEY not configured.")

    return {
        **state,
        "attractions": attractions,
        "sources": sources,
        "safety_advisories": safety_advisories,
        "missing_info": missing_info,
        "data_warnings": data_warnings,
    }


# ─── Node E: Generate plan ─────────────────────────────────────────────────────


async def node_generate_plan(state: TravelAgentState) -> TravelAgentState:
    """Use Ollama to synthesize a travel summary from validated data."""
    destination = state.get("destination", "the destination")
    travel_date = state.get("travel_date", "unspecified date")
    origin = state.get("origin", "unspecified origin")
    transport_mode = state.get("transport_mode", "unspecified transport")

    # Build data summary for LLM
    parts = []
    weather = state.get("weather_data")
    if weather and not weather.get("error") and not weather.get("unavailable_reason"):
        parts.append(
            f"Weather: {weather.get('condition', '')} "
            f"{weather.get('temperature_c', '')}°C, "
            f"humidity {weather.get('humidity_percent', '')}%, "
            f"wind {weather.get('wind_speed_kmh', '')} km/h"
        )
    elif weather and weather.get("unavailable_reason"):
        parts.append(f"Weather: {weather['unavailable_reason']}")

    attrs = state.get("attractions", [])
    if attrs:
        names = [a["name"] for a in attrs[:5]]
        parts.append(f"Nearby places: {', '.join(names)}")

    safety = state.get("safety_advisories", [])
    if safety:
        high = [s for s in safety if s.get("severity") == "high"]
        if high:
            parts.append(f"Safety: {len(high)} high-severity advisory(ies) found.")
        else:
            parts.append(f"Safety: {len(safety)} advisory report(s) found, no high-severity alerts.")
    else:
        parts.append("Safety: No specific advisories found (status unverified).")

    route = state.get("route_data")
    if route and not route.get("error"):
        parts.append(
            f"Route: {route.get('distance_km', '?')} km, "
            f"~{route.get('duration_minutes', '?')} minutes by {transport_mode}."
        )

    missing = state.get("missing_info", [])
    if missing:
        parts.append(f"Missing info: {'; '.join(missing[:3])}")

    data_summary = "\n".join(f"- {p}" for p in parts) if parts else "No data retrieved."

    system = SYNTHESIZE_SYSTEM.format(
        destination=destination,
        travel_date=travel_date,
        origin=origin,
        transport_mode=transport_mode,
        data_summary=data_summary,
    )

    try:
        summary = await _ollama_chat(system, "Please write the trip summary.", timeout=60)
    except Exception as e:
        logger.error("Synthesis LLM error: %s", e)
        summary = (
            f"I've gathered travel information for {destination}. "
            "Please review the details below. "
            f"Note: AI summary unavailable ({e})."
        )

    # Build simple itinerary from attractions
    itinerary = []
    for i, attr in enumerate(state.get("attractions", [])[:5]):
        itinerary.append({
            "time": f"{9 + i * 2}:00",
            "title": attr["name"],
            "description": attr.get("address") or attr.get("category", ""),
            "location": attr.get("address"),
            "coordinates": attr.get("coordinates"),
            "type": "activity",
            "duration_minutes": 90,
        })

    return {**state, "summary": summary.strip(), "itinerary": itinerary}


# ─── Node F: Format response ────────────────────────────────────────────────────


async def node_format_response(state: TravelAgentState) -> TravelAgentState:
    """Final formatting — ensures message_type is set."""
    if state.get("needs_clarification"):
        return {**state, "message_type": "clarification"}
    if state.get("error"):
        return {**state, "message_type": "error"}
    return {**state, "message_type": "travel_plan"}
