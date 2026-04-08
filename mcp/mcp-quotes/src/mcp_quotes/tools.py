"""Tool schemas, handlers, and registry for the Quotes MCP server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable

from mcp.types import Tool
from pydantic import BaseModel, Field

from mcp_quotes.client import OllamaClient


class NoArgs(BaseModel):
    """Empty input model for tools that only need server-side configuration."""


class GenerateQuoteArgs(BaseModel):
    topic: str = Field(description="Topic or theme for the quote, e.g. 'perseverance', 'morning motivation'")
    category: str = Field(
        default="general",
        description="Category: motivation, love, success, wisdom, energy, or general",
    )


class ChatArgs(BaseModel):
    message: str = Field(description="Message to send to the nanobot")


ToolPayload = dict[str, Any]
ToolHandler = Callable[[OllamaClient, BaseModel], Awaitable[ToolPayload]]


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    model: type[BaseModel]
    handler: ToolHandler

    def as_tool(self) -> Tool:
        schema = self.model.model_json_schema()
        schema.pop("$defs", None)
        schema.pop("title", None)
        return Tool(name=self.name, description=self.description, inputSchema=schema)


async def _health(client: OllamaClient, _args: BaseModel) -> ToolPayload:
    return client.is_alive()


async def _generate_quote(client: OllamaClient, args: BaseModel) -> ToolPayload:
    if not isinstance(args, GenerateQuoteArgs):
        raise TypeError(f"Expected {GenerateQuoteArgs.__name__}, got {type(args).__name__}")
    return client.generate_quote(topic=args.topic, category=args.category)


async def _chat(client: OllamaClient, args: BaseModel) -> ToolPayload:
    if not isinstance(args, ChatArgs):
        raise TypeError(f"Expected {ChatArgs.__name__}, got {type(args).__name__}")

    system_prompt = (
        "Ты - Нанобот, маленький умный робот-генератор цитат. "
        "Твоя задача: генерировать вдохновляющие цитаты, объяснять их смысл, "
        "предлагать цитаты по настроению и теме. Общайся дружелюбно и с юмором. "
        "Когда просишь цитату - сгенерируй ОДНУ короткую цитату (до 20 слов) в кавычках."
    )
    return client.chat(message=args.message, system_prompt=system_prompt)


TOOL_SPECS = (
    ToolSpec(
        "quotes_health",
        "Check if the Ollama quote generation service is healthy and list available models.",
        NoArgs,
        _health,
    ),
    ToolSpec(
        "quotes_generate",
        "Generate an inspirational quote on a given topic and category. "
        "Categories: motivation, love, success, wisdom, energy, general.",
        GenerateQuoteArgs,
        _generate_quote,
    ),
    ToolSpec(
        "quotes_chat",
        "Chat with the nanobot quote generator. Ask for quotes, explanations, or just talk.",
        ChatArgs,
        _chat,
    ),
)
TOOLS_BY_NAME = {spec.name: spec for spec in TOOL_SPECS}
