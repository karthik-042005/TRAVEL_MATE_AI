"""
Maps and places tool using Geoapify API.
Provides geocoding, places search, place details, and routing.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

GEOAPIFY_BASE = "https://api.geoapify.com/v1"
GEOAPIFY_ROUTING = "https://api.geoapify.com/v1/routing"
GEOAPIFY_PLACES = "https://api.geoapify.com/v2/places"
GEOAPIFY_GEOCODE = "https://api.geoapify.com/v1/geocode/search"


def _no_key() -> dict[str, Any]:
    return {"error": "GEOAPIFY_API_KEY not configured", "available": False}


async def geocode_location(location: str) -> dict[str, Any]:
    """Geocode a location string to coordinates."""
    if not settings.geoapify_api_key:
        return _no_key()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                GEOAPIFY_GEOCODE,
                params={"text": location, "apiKey": settings.geoapify_api_key, "limit": 1},
            )
            resp.raise_for_status()
            data = resp.json()
            features = data.get("features", [])
            if not features:
                return {"error": f"Could not geocode: {location}", "available": True}
            f = features[0]
            props = f.get("properties", {})
            coords = f.get("geometry", {}).get("coordinates", [None, None])
            return {
                "location": location,
                "lat": coords[1],
                "lon": coords[0],
                "formatted": props.get("formatted", location),
                "country": props.get("country"),
                "city": props.get("city"),
                "available": True,
            }
    except Exception as e:
        logger.error("Geocode error: %s", e)
        return {"error": str(e), "available": True}


async def search_places(
    location: str,
    categories: Optional[list[str]] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_m: int = 10000,
    limit: int = 10,
) -> dict[str, Any]:
    """Search for places near a location."""
    if not settings.geoapify_api_key:
        return _no_key()

    # If lat/lon not provided, geocode first
    if lat is None or lon is None:
        geo = await geocode_location(location)
        if "error" in geo and not geo.get("available"):
            return geo
        lat = geo.get("lat")
        lon = geo.get("lon")
        if lat is None or lon is None:
            return {"error": f"Could not determine coordinates for {location}", "places": []}

    cats = ",".join(categories) if categories else "tourism.attraction,tourism.sights,leisure.park"
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                GEOAPIFY_PLACES,
                params={
                    "categories": cats,
                    "filter": f"circle:{lon},{lat},{radius_m}",
                    "limit": limit,
                    "apiKey": settings.geoapify_api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            places = []
            for feature in data.get("features", []):
                p = feature.get("properties", {})
                c = feature.get("geometry", {}).get("coordinates", [None, None])
                places.append({
                    "name": p.get("name", "Unknown"),
                    "category": p.get("categories", [None])[0] if p.get("categories") else None,
                    "address": p.get("formatted"),
                    "lat": c[1],
                    "lon": c[0],
                    "website": p.get("website"),
                    "opening_hours": p.get("opening_hours"),
                    "rating": p.get("rating"),
                    "place_id": p.get("place_id"),
                })
            return {"places": places, "count": len(places), "available": True}
    except Exception as e:
        logger.error("Places search error: %s", e)
        return {"error": str(e), "places": [], "available": True}


async def calculate_route(
    origin_lat: float,
    origin_lon: float,
    dest_lat: float,
    dest_lon: float,
    mode: str = "drive",
) -> dict[str, Any]:
    """Calculate a route between two coordinate pairs."""
    if not settings.geoapify_api_key:
        return _no_key()

    # Map common mode names to Geoapify modes
    mode_map = {
        "car": "drive",
        "driving": "drive",
        "walk": "walk",
        "walking": "walk",
        "bike": "bicycle",
        "bicycle": "bicycle",
        "transit": "transit",
        "bus": "transit",
    }
    geo_mode = mode_map.get(mode.lower(), "drive")

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(
                GEOAPIFY_ROUTING,
                params={
                    "waypoints": f"{origin_lat},{origin_lon}|{dest_lat},{dest_lon}",
                    "mode": geo_mode,
                    "apiKey": settings.geoapify_api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            features = data.get("features", [])
            if not features:
                return {"error": "No route found", "available": True}
            f = features[0]
            props = f.get("properties", {})
            legs = props.get("legs", [])
            total_distance = sum(leg.get("distance", 0) for leg in legs)
            total_time = sum(leg.get("time", 0) for leg in legs)

            # Extract geometry for map rendering
            geometry = f.get("geometry", {})
            coords = []
            if geometry.get("type") == "MultiLineString":
                for line in geometry.get("coordinates", []):
                    coords.extend([[pt[1], pt[0]] for pt in line])  # [lat, lon]
            elif geometry.get("type") == "LineString":
                coords = [[pt[1], pt[0]] for pt in geometry.get("coordinates", [])]

            return {
                "distance_km": round(total_distance / 1000, 2),
                "duration_minutes": round(total_time / 60),
                "mode": geo_mode,
                "geometry": coords,
                "available": True,
                "external_nav_url": (
                    f"https://www.openstreetmap.org/directions?"
                    f"from={origin_lat},{origin_lon}&to={dest_lat},{dest_lon}"
                ),
            }
    except Exception as e:
        logger.error("Route calculation error: %s", e)
        return {"error": str(e), "available": True}
