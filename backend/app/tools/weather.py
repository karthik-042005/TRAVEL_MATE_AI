"""
Weather tool using OpenWeatherMap API.
Clearly distinguishes current observations, forecasts, and seasonal info.
Never fabricates weather data.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone, timedelta
from typing import Any, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OWM_BASE = "https://api.openweathermap.org/data/2.5"
FORECAST_MAX_DAYS = 5  # free-tier OpenWeatherMap forecast limit


def _no_key() -> dict[str, Any]:
    return {
        "error": "OPENWEATHER_API_KEY not configured",
        "available": False,
        "unavailable_reason": "Weather service not configured.",
    }


def _celsius(kelvin: float) -> float:
    return round(kelvin - 273.15, 1)


def _kmh(ms: float) -> float:
    return round(ms * 3.6, 1)


def _date_within_forecast_range(target_date: Optional[str]) -> tuple[bool, str]:
    """Check if a date string (YYYY-MM-DD or natural) is within 5-day forecast range."""
    if not target_date:
        return True, ""  # no date = use current
    try:
        td = datetime.strptime(target_date[:10], "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()
        delta = (td - today).days
        if delta < 0:
            return False, f"Date {target_date} is in the past. Showing current weather instead."
        if delta > FORECAST_MAX_DAYS:
            return False, (
                f"Date {target_date} is {delta} days away — outside the free-tier "
                f"{FORECAST_MAX_DAYS}-day forecast window. A date-specific forecast "
                "is unavailable. Climate/seasonal information may be shown instead."
            )
        return True, ""
    except ValueError:
        return True, ""  # Can't parse — proceed and let API handle


async def get_current_weather(location: str, lat: Optional[float] = None, lon: Optional[float] = None) -> dict[str, Any]:
    """Get current weather conditions."""
    if not settings.openweather_api_key:
        return _no_key()

    params: dict[str, Any] = {"appid": settings.openweather_api_key, "units": "metric"}
    if lat is not None and lon is not None:
        params.update({"lat": lat, "lon": lon})
    else:
        params["q"] = location

    retrieved_at = datetime.now(timezone.utc).isoformat()

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{OWM_BASE}/weather", params=params)
            resp.raise_for_status()
            d = resp.json()
            return {
                "temperature_c": round(d["main"]["temp"], 1),
                "feels_like_c": round(d["main"]["feels_like"], 1),
                "condition": d["weather"][0]["main"],
                "description": d["weather"][0]["description"].capitalize(),
                "humidity_percent": d["main"]["humidity"],
                "wind_speed_kmh": _kmh(d["wind"]["speed"]),
                "icon": d["weather"][0]["icon"],
                "is_forecast": False,
                "retrieved_at": retrieved_at,
                "location_resolved": d.get("name", location),
                "available": True,
            }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Location not found: {location}", "available": True}
        logger.error("OWM current error %s", e)
        return {"error": str(e), "available": True}
    except Exception as e:
        logger.error("OWM current error: %s", e)
        return {"error": str(e), "available": True}


async def get_weather_forecast(
    location: str,
    target_date: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
) -> dict[str, Any]:
    """Get weather forecast. Clearly states when date is outside forecast range."""
    if not settings.openweather_api_key:
        return _no_key()

    in_range, reason = _date_within_forecast_range(target_date)
    if not in_range:
        if "in the past" in reason:
            current = await get_current_weather(location, lat, lon)
            current["unavailable_reason"] = reason
            current["is_forecast"] = True
            current["forecast_date"] = target_date
            return current
        return {
            "is_forecast": True,
            "forecast_date": target_date,
            "unavailable_reason": reason,
            "available": True,
        }

    params: dict[str, Any] = {
        "appid": settings.openweather_api_key,
        "units": "metric",
        "cnt": 40,  # 5 days × 8 slots/day
    }
    if lat is not None and lon is not None:
        params.update({"lat": lat, "lon": lon})
    else:
        params["q"] = location

    retrieved_at = datetime.now(timezone.utc).isoformat()

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(f"{OWM_BASE}/forecast", params=params)
            resp.raise_for_status()
            data = resp.json()

        items = data.get("list", [])
        if not items:
            return {"error": "No forecast data", "available": True}

        # If a specific date is requested, pick the closest noon slot
        if target_date:
            try:
                td = datetime.strptime(target_date[:10], "%Y-%m-%d")
                target_ts = td.replace(hour=12, tzinfo=timezone.utc).timestamp()
                best = min(items, key=lambda x: abs(x["dt"] - target_ts))
            except ValueError:
                best = items[0]
        else:
            best = items[0]

        w = best["weather"][0]
        m = best["main"]
        return {
            "temperature_c": round(m["temp"], 1),
            "feels_like_c": round(m["feels_like"], 1),
            "temp_min_c": round(m["temp_min"], 1),
            "temp_max_c": round(m["temp_max"], 1),
            "condition": w["main"],
            "description": w["description"].capitalize(),
            "humidity_percent": m["humidity"],
            "wind_speed_kmh": _kmh(best["wind"]["speed"]),
            "icon": w["icon"],
            "is_forecast": True,
            "forecast_date": target_date,
            "forecast_time_utc": datetime.fromtimestamp(best["dt"], tz=timezone.utc).isoformat(),
            "retrieved_at": retrieved_at,
            "available": True,
        }
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": f"Location not found: {location}", "available": True}
        logger.error("OWM forecast error %s", e)
        return {"error": str(e), "available": True}
    except Exception as e:
        logger.error("OWM forecast error: %s", e)
        return {"error": str(e), "available": True}
