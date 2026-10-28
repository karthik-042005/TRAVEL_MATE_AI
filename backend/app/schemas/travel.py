"""TravelMate AI — Pydantic schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


# ─── Request models ────────────────────────────────────────────────────────────


class TravelPlanRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = Field(default=None)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1)


# ─── Shared sub-models ─────────────────────────────────────────────────────────


class Coordinates(BaseModel):
    lat: float
    lon: float


class WeatherData(BaseModel):
    temperature_c: Optional[float] = None
    feels_like_c: Optional[float] = None
    condition: Optional[str] = None
    humidity_percent: Optional[int] = None
    wind_speed_kmh: Optional[float] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    is_forecast: bool = False
    forecast_date: Optional[str] = None
    retrieved_at: Optional[str] = None
    unavailable_reason: Optional[str] = None


class Attraction(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    address: Optional[str] = None
    opening_hours: Optional[str] = None
    rating: Optional[float] = None
    source_url: Optional[str] = None


class RouteInfo(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    distance_km: Optional[float] = None
    duration_minutes: Optional[int] = None
    mode: Optional[str] = None
    summary: Optional[str] = None
    geometry: Optional[list[list[float]]] = None  # [[lat,lon],…]
    external_nav_url: Optional[str] = None


class SafetyAdvisory(BaseModel):
    type: str  # "road_closure" | "landslide" | "weather_warning" | "general"
    severity: str  # "low" | "medium" | "high" | "unknown"
    summary: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    published_at: Optional[str] = None
    retrieved_at: Optional[str] = None
    verified: bool = False


class SourceLink(BaseModel):
    title: str
    url: str
    snippet: Optional[str] = None
    published_at: Optional[str] = None
    retrieved_at: Optional[str] = None


class ItineraryItem(BaseModel):
    time: Optional[str] = None
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    coordinates: Optional[Coordinates] = None
    duration_minutes: Optional[int] = None
    type: str = "activity"  # "activity" | "travel" | "meal" | "accommodation"


# ─── Top-level response ────────────────────────────────────────────────────────


class TravelPlanResponse(BaseModel):
    session_id: str
    message_type: str = "travel_plan"  # "travel_plan" | "clarification" | "error"

    # Narrative summary
    summary: Optional[str] = None
    clarification_needed: Optional[str] = None

    # Parsed trip details
    destination: Optional[str] = None
    origin: Optional[str] = None
    travel_date: Optional[str] = None
    travel_date_interpreted: Optional[str] = None
    transport_mode: Optional[str] = None

    # Structured data
    weather: Optional[WeatherData] = None
    attractions: list[Attraction] = Field(default_factory=list)
    route: Optional[RouteInfo] = None
    itinerary: list[ItineraryItem] = Field(default_factory=list)
    safety_advisories: list[SafetyAdvisory] = Field(default_factory=list)
    sources: list[SourceLink] = Field(default_factory=list)

    # Destination coordinates for map centre
    destination_coordinates: Optional[Coordinates] = None

    # Meta
    missing_information: list[str] = Field(default_factory=list)
    data_warnings: list[str] = Field(default_factory=list)
    generated_at: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat() + "Z"
    )

    # Tool status snapshot
    tools_used: list[str] = Field(default_factory=list)
    tools_unavailable: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
    ollama_reachable: bool = False
    ollama_model: str = ""
    configured_tools: dict[str, bool] = Field(default_factory=dict)
    missing_keys: list[str] = Field(default_factory=list)


class ToolStatusResponse(BaseModel):
    tools: dict[str, bool]
    missing_keys: list[str]
    note: str = (
        "Keys are read from backend/.env. "
        "Values are never exposed through this endpoint."
    )
