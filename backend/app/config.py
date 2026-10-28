"""
TravelMate AI — Configuration
Loads environment variables from backend/.env relative to this file's location.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Always resolve .env relative to this config file, regardless of CWD
_ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Ollama
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # External APIs
    tavily_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    geoapify_api_key: Optional[str] = None

    # Application
    frontend_origin: str = "http://localhost:5173"
    request_timeout: int = 60  # seconds

    def configured_tools(self) -> dict[str, bool]:
        """Return which integrations have keys configured."""
        return {
            "web_search": bool(self.tavily_api_key),
            "weather": bool(self.openweather_api_key),
            "maps": bool(self.geoapify_api_key),
            "safety_research": bool(self.tavily_api_key),
        }

    def missing_keys(self) -> list[str]:
        missing = []
        if not self.tavily_api_key:
            missing.append("TAVILY_API_KEY")
        if not self.openweather_api_key:
            missing.append("OPENWEATHER_API_KEY")
        if not self.geoapify_api_key:
            missing.append("GEOAPIFY_API_KEY")
        return missing


settings = Settings()
