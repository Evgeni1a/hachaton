"""Entrypoint for Nanobot Quote Generator — configures and launches the gateway."""

import os
import sys
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from nanobot.config import load_config
    from nanobot.config.models import MCPServerConfig
except ImportError:
    print("ERROR: nanobot-ai not installed. Install it first:")
    print("  pip install nanobot-ai")
    print("  or: uv pip install nanobot-ai")
    sys.exit(1)

CONFIG_PATH = Path(__file__).parent / "config.json"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NANOBOT_")

    llm_model: str = "llama3.2:1b"
    ollama_url: str = "http://localhost:11434"
    gateway_host: str = "127.0.0.1"
    gateway_port: int = 8502


def _resolve_config(settings: Settings, config) -> dict:
    """Inject nanobot settings into the config dict."""
    config_dict = config.model_dump() if hasattr(config, "model_dump") else {}

    # LLM settings
    config_dict["llm"] = {
        "api_model": settings.llm_model,
        "api_base_url": f"{settings.ollama_url}/v1",
        "api_type": "openai",
    }

    # Gateway settings
    config_dict.setdefault("gateway", {})
    config_dict["gateway"]["host"] = settings.gateway_host
    config_dict["gateway"]["port"] = settings.gateway_port

    # MCP servers
    config_dict.setdefault("tools", {})
    config_dict["tools"].setdefault("mcp_servers", {})

    config_dict["tools"]["mcp_servers"]["quotes"] = {
        "command": sys.executable,
        "args": ["-m", "mcp_quotes"],
        "env": {
            "NANOBOT_QUOTES_OLLAMA_URL": settings.ollama_url,
            "NANOBOT_QUOTES_OLLAMA_MODEL": settings.llm_model,
        },
    }

    return config_dict


def main():
    settings = Settings()

    # Load base config
    if CONFIG_PATH.exists():
        config = load_config(CONFIG_PATH)
    else:
        # Create minimal default config
        from nanobot.config.models import Config
        config = Config()

    # Resolve settings
    resolved = _resolve_config(settings, config)

    # Save resolved config
    resolved_path = Path(__file__).parent / "config.resolved.json"
    import json
    resolved_path.write_text(json.dumps(resolved, indent=2, ensure_ascii=False))
    print(f"[nanobot] Resolved config saved to {resolved_path}")

    # Set workspace
    workspace = Path(__file__).parent / "workspace"
    workspace.mkdir(exist_ok=True)

    # Launch gateway
    print(f"[nanobot] Starting gateway on {settings.gateway_host}:{settings.gateway_port}")
    os.execvp(
        "nanobot",
        [
            "nanobot",
            "gateway",
            "--config",
            str(resolved_path),
            "--workspace",
            str(workspace),
        ],
    )


if __name__ == "__main__":
    main()
