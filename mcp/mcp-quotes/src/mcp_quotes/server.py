"""Stdio MCP server for quote generation via Ollama."""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from pydantic import BaseModel

from mcp_quotes.client import OllamaClient
from mcp_quotes.settings import resolve_settings
from mcp_quotes.tools import TOOL_SPECS, TOOLS_BY_NAME, ToolPayload


def _text(data: ToolPayload) -> list[TextContent]:
    return [TextContent(type="text", text=json.dumps(data, ensure_ascii=False, indent=2))]


def create_server(client: OllamaClient) -> Server:
    server = Server("quotes")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [spec.as_tool() for spec in TOOL_SPECS]

    @server.call_tool()
    async def call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[TextContent]:
        spec = TOOLS_BY_NAME.get(name)
        if spec is None:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]
        try:
            args = spec.model.model_validate(arguments or {})
            return _text(await spec.handler(client, args))
        except Exception as exc:
            return [
                TextContent(type="text", text=f"Error: {type(exc).__name__}: {exc}")
            ]

    _ = list_tools, call_tool
    return server


async def main() -> None:
    settings = resolve_settings()
    client = OllamaClient(base_url=settings.ollama_url, model=settings.ollama_model)
    server = create_server(client)
    async with stdio_server() as (read_stream, write_stream):
        init_options = server.create_initialization_options()
        await server.run(read_stream, write_stream, init_options)


if __name__ == "__main__":
    asyncio.run(main())
