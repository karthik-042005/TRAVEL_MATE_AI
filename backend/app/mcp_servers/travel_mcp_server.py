"""
TravelMate AI — Model Context Protocol (MCP) Server.
Exposes travel tools to any MCP client or LLM agent over standard stdio transport.
"""

from __future__ import annotations

import asyncio
from typing import Optional

from mcp.server.mcpserver import MCPServer

from app.tools.weather import get_current_weather, get_weather_forecast
from app.tools.maps import geocode_location, search_places as geo_search_places, calculate_route as geo_calculate_route
from app.tools.safety import research_safety
from app.tools.web_search import search_web

# Initialize MCP server
mcp_server = MCPServer("TravelMate-AI-MCP-Server")


@mcp_server.tool(name="get_weather", description="Get current weather or forecast for a destination")
async def get_weather(location: str, target_date: Optional[str] = None) -> str:
    """Retrieve weather data for a location, specifying date if forecast desired."""
    if target_date:
        res = await get_weather_forecast(location, target_date)
    else:
        res = await get_current_weather(location)
    return str(res)


@mcp_server.tool(name="search_places", description="Search attractions, sights, and parks in a destination")
async def search_places(location: str, limit: int = 5) -> str:
    """Search for tourist attractions, sights, and leisure points."""
    res = await geo_search_places(location, limit=limit)
    return str(res)


@mcp_server.tool(name="calculate_route", description="Calculate driving, walking, or transit route between two locations")
async def calculate_route(origin: str, destination: str, mode: str = "drive") -> str:
    """Geocode origin and destination and calculate the navigation route."""
    geo_orig = await geocode_location(origin)
    geo_dest = await geocode_location(destination)
    if "error" in geo_orig or "error" in geo_dest:
        return f"Error: Unable to geocode locations: {origin} -> {destination}"
    res = await geo_calculate_route(
        geo_orig["lat"], geo_orig["lon"], geo_dest["lat"], geo_dest["lon"], mode=mode
    )
    return str(res)


@mcp_server.tool(name="research_safety", description="Research road closures, landslide warnings, and travel advisories")
async def check_safety(destination: str, travel_date: Optional[str] = None) -> str:
    """Check recent travel warnings, weather advisories, or road conditions."""
    res = await research_safety(destination, travel_date)
    return str(res)


@mcp_server.tool(name="search_travel_web", description="Perform live web search for travel information, guides, and tips")
async def search_travel_web(query: str) -> str:
    """Search live web for up-to-date travel info."""
    res = await search_web(query)
    return str(res)


if __name__ == "__main__":
    mcp_server.run()
