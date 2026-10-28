"""
TravelMate AI — FastAPI routes.
"""

from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter, HTTPException, status

from app.config import settings
from app.schemas.travel import (
    ChatRequest,
    HealthResponse,
    ToolStatusResponse,
    TravelPlanRequest,
    TravelPlanResponse,
)
from app.services.ollama_service import check_ollama
from app.services.travel_planner import plan_trip

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Backend health — checks Ollama connectivity."""
    ollama_info = await check_ollama()
    return HealthResponse(
        status="ok",
        ollama_reachable=ollama_info["reachable"],
        ollama_model=settings.ollama_model,
        configured_tools=settings.configured_tools(),
        missing_keys=settings.missing_keys(),
    )


@router.get("/api/v1/health", response_model=HealthResponse)
async def api_health():
    """API health with dependency check."""
    return await health_check()


@router.get("/api/v1/tools/status", response_model=ToolStatusResponse)
async def tool_status():
    """Tool configuration status — never exposes key values."""
    return ToolStatusResponse(
        tools=settings.configured_tools(),
        missing_keys=settings.missing_keys(),
    )


@router.post("/api/v1/travel/plan", response_model=TravelPlanResponse)
async def create_travel_plan(request: TravelPlanRequest):
    """Generate a travel plan from a natural language request."""
    session_id = request.session_id or str(uuid.uuid4())
    try:
        result = await plan_trip(request.message, session_id)
        return result
    except Exception as e:
        logger.error("Travel plan error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate travel plan: {str(e)[:200]}",
        )


@router.post("/api/v1/chat", response_model=TravelPlanResponse)
async def chat(request: ChatRequest):
    """Continue an existing travel planning conversation."""
    try:
        result = await plan_trip(request.message, request.session_id)
        return result
    except Exception as e:
        logger.error("Chat error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)[:200]}",
        )
