"""Configuration helpers for EXASPOON agents following spoon-core patterns."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    """Runtime settings shared by all agents."""

    openai_api_key: str
    openai_base_url: Optional[str]
    model_name: str
    mcp_base_url: Optional[str]
    supabase_url: Optional[str]
    supabase_service_key: Optional[str]

    # Additional config from config.json
    app_config: Dict[str, Any]
    agents_config: Dict[str, Any]
    graph_config: Dict[str, Any]
    llm_config: Dict[str, Any]
    mcp_config: Dict[str, Any]
    routing_config: Dict[str, Any]
    logging_config: Dict[str, Any]


_DEF_MODEL = "openai/gpt-oss-120b"


def load_config_json() -> Dict[str, Any]:
    """Load configuration from config.json in project root."""
    config_path = Path(__file__).resolve().parent.parent.parent.parent / "config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Return default configuration if config.json doesn't exist
    return {
        "app": {"name": "exaspoon", "version": "1.0.0"},
        "agents": {},
        "graph": {"default_agent": "ontology", "persist_session": False},
        "llm": {"temperature": 0.2, "max_tokens": 4000, "timeout": 30},
        "mcp": {"transport": "sse", "timeout": 10, "retry_attempts": 3},
        "routing": {
            "intent_confidence_threshold": 0.7,
            "keyword_fallback_enabled": True,
        },
        "logging": {"level": "INFO"},
    }


def load_settings(dotenv_path: str | None = None) -> Settings:
    """Load settings from config.json, environment variables and optional .env file."""

    # Load config.json first
    config_json = load_config_json()

    # Load .env file from project root
    env_file_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if env_file_path.exists():
        load_dotenv(env_file_path)

    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    return Settings(
        openai_api_key=openai_key,
        openai_base_url=os.getenv("OPENAI_BASE_URL"),
        model_name=os.getenv("OPENAI_MODEL", _DEF_MODEL),
        mcp_base_url=os.getenv("EXASPOON_MCP_URL", "http://127.0.0.1:8787"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY"),
        app_config=config_json.get("app", {}),
        agents_config=config_json.get("agents", {}),
        graph_config=config_json.get("graph", {}),
        llm_config=config_json.get("llm", {}),
        mcp_config=config_json.get("mcp", {}),
        routing_config=config_json.get("routing", {}),
        logging_config=config_json.get("logging", {}),
    )
