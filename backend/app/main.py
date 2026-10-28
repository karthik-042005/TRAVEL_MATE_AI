"""
TravelMate AI — FastAPI application entry point.
"""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import router
from app.config import settings

# ─── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ─── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="TravelMate AI",
    description="AI-powered travel planning API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS (restricted to configured frontend origin) ───────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# ─── Request timing middleware ──────────────────────────────────────────────────
@app.middleware("http")
async def add_timing(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = round((time.perf_counter() - start) * 1000)
    response.headers["X-Response-Time-Ms"] = str(elapsed)
    return response


# ─── Root endpoint ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "service": "TravelMate AI",
        "version": "1.0.0",
        "tagline": "Explore smarter. Travel better.",
        "docs": "/docs",
        "health": "/health",
    }


# ─── Include routes ────────────────────────────────────────────────────────────
app.include_router(router)


# ─── Startup log ───────────────────────────────────────────────────────────────
@app.on_event("startup")
async def startup_event():
    configured = settings.configured_tools()
    missing = settings.missing_keys()
    logger.info("TravelMate AI starting up")
    logger.info("Ollama: %s / %s", settings.ollama_base_url, settings.ollama_model)
    logger.info("Configured tools: %s", configured)
    if missing:
        logger.warning("Missing API keys: %s — related features disabled", missing)
    else:
        logger.info("All API keys configured.")
