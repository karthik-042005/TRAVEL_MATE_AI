"""
Web search tool using Tavily API.
Returns titles, URLs, snippets, and retrieval timestamps.
Never fabricates results — returns empty list when API is unavailable.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

TAVILY_API_URL = "https://api.tavily.com/search"


async def _tavily_search(
    query: str,
    max_results: int = 5,
    search_depth: str = "basic",
    include_domains: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    """Raw Tavily search call. Returns list of result dicts."""
    if not settings.tavily_api_key:
        logger.warning("TAVILY_API_KEY not configured — web search unavailable.")
        return []

    payload: dict[str, Any] = {
        "api_key": settings.tavily_api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": False,
        "include_raw_content": False,
    }
    if include_domains:
        payload["include_domains"] = include_domains

    retrieved_at = datetime.now(timezone.utc).isoformat()

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(TAVILY_API_URL, json=payload)
            resp.raise_for_status()
            data = resp.json()
            results = data.get("results", [])
            for r in results:
                r["retrieved_at"] = retrieved_at
            return results
    except httpx.HTTPStatusError as e:
        logger.error("Tavily HTTP error %s: %s", e.response.status_code, e.response.text[:200])
        return []
    except Exception as e:
        logger.error("Tavily search error: %s", e)
        return []


async def search_web(query: str, max_results: int = 5) -> list[dict[str, Any]]:
    """General web search."""
    return await _tavily_search(query, max_results=max_results)


async def find_recent_attractions(destination: str) -> list[dict[str, Any]]:
    """Search for tourist attractions at a destination."""
    query = f"tourist attractions things to do {destination} 2024 2025"
    return await _tavily_search(query, max_results=6, search_depth="basic")


async def search_travel_news(destination: str, date: Optional[str] = None) -> list[dict[str, Any]]:
    """Search for recent travel news about a destination."""
    query = f"travel news {destination}"
    if date:
        query += f" {date}"
    return await _tavily_search(query, max_results=4)


async def search_official_travel_advisories(destination: str) -> list[dict[str, Any]]:
    """Search for official travel advisories."""
    query = f"official travel advisory {destination} government"
    return await _tavily_search(
        query,
        max_results=5,
        include_domains=[
            "travel.state.gov",
            "gov.in",
            "india.gov.in",
            "tourism.gov.in",
            "tnpolice.gov.in",
        ],
    )


async def search_official_road_closures(destination: str, date: Optional[str] = None) -> list[dict[str, Any]]:
    """Search for road closure information."""
    query = f"road closure {destination} highway"
    if date:
        query += f" {date}"
    return await _tavily_search(query, max_results=5)


async def search_district_advisories(destination: str) -> list[dict[str, Any]]:
    """Search for district administration advisories."""
    query = f"{destination} district collector advisory notice 2024 2025"
    return await _tavily_search(query, max_results=4)


async def search_landslide_warnings(destination: str, date: Optional[str] = None) -> list[dict[str, Any]]:
    """Search for landslide warnings."""
    query = f"landslide warning {destination}"
    if date:
        query += f" {date}"
    return await _tavily_search(query, max_results=5)
