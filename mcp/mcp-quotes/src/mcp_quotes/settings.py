"""Settings for the MCP Quotes server."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NANOBOT_QUOTES_")

    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:1b"


def resolve_settings() -> Settings:
    return Settings()
