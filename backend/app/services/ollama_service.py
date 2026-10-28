"""
Ollama service — verifies connectivity and model availability.
Uses langchain-ollama for LLM calls.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def check_ollama() -> dict[str, Any]:
    """Check Ollama connectivity and model availability."""
    base = settings.ollama_base_url
    model = settings.ollama_model

    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{base}/api/tags")
            resp.raise_for_status()
            data = resp.json()
            available_models = [m["name"] for m in data.get("models", [])]
            model_available = model in available_models or any(
                m.startswith(model.split(":")[0]) for m in available_models
            )
            return {
                "reachable": True,
                "model": model,
                "model_available": model_available,
                "available_models": available_models,
            }
    except httpx.ConnectError:
        return {
            "reachable": False,
            "model": model,
            "model_available": False,
            "error": f"Cannot connect to Ollama at {base}. Is it running?",
        }
    except Exception as e:
        return {
            "reachable": False,
            "model": model,
            "model_available": False,
            "error": str(e),
        }
