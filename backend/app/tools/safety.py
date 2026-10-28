"""
Safety research tool — searches for road closures, landslide warnings, and advisories.
Uses Tavily web search prioritizing official sources.
Never guarantees safety; always notes unverified status.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app.tools.web_search import (
    search_official_road_closures,
    search_district_advisories,
    search_landslide_warnings,
    search_official_travel_advisories,
)

logger = logging.getLogger(__name__)


def _classify_severity(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["red alert", "high alert", "evacuate", "closed", "blocked"]):
        return "high"
    if any(w in text_lower for w in ["warning", "caution", "restricted", "delay"]):
        return "medium"
    if any(w in text_lower for w in ["watch", "monitor", "possibility", "minor"]):
        return "low"
    return "unknown"


async def research_safety(
    destination: str,
    travel_date: Optional[str] = None,
) -> dict[str, Any]:
    """
    Research safety conditions for a destination.
    Returns advisories parsed from web search results.
    """
    retrieved_at = datetime.now(timezone.utc).isoformat()

    # Run multiple searches
    road_results = await search_official_road_closures(destination, travel_date)
    landslide_results = await search_landslide_warnings(destination, travel_date)
    advisory_results = await search_official_travel_advisories(destination)
    district_results = await search_district_advisories(destination)

    advisories = []

    def parse_results(results: list[dict], advisory_type: str) -> None:
        for r in results:
            title = r.get("title", "")
            snippet = r.get("content", r.get("snippet", ""))
            url = r.get("url", "")
            pub = r.get("published_date")

            if not title and not snippet:
                continue

            text = f"{title} {snippet}"
            advisories.append({
                "type": advisory_type,
                "severity": _classify_severity(text),
                "summary": f"{title}: {snippet[:200]}" if snippet else title,
                "source_url": url,
                "source_title": title,
                "published_at": pub,
                "retrieved_at": retrieved_at,
                "verified": False,  # web search results are never verified ground truth
            })

    parse_results(road_results, "road_closure")
    parse_results(landslide_results, "landslide")
    parse_results(advisory_results, "general")
    parse_results(district_results, "general")

    disclaimer = (
        "Safety information is sourced from web search and has not been independently verified. "
        "Always check official sources before travel. "
        "This application cannot guarantee route safety."
    )

    if not advisories:
        return {
            "advisories": [],
            "disclaimer": disclaimer,
            "no_results_note": (
                f"No specific safety reports found for '{destination}' via web search. "
                "This does not confirm the route is clear."
            ),
            "retrieved_at": retrieved_at,
        }

    return {
        "advisories": advisories,
        "disclaimer": disclaimer,
        "retrieved_at": retrieved_at,
    }
