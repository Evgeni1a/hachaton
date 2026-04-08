# 🤖 Nanobot Quote Generator

AI-powered quote generator using **Nanobot** framework (HKUDS) with **MCP tools** and **Ollama** LLM.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌──────────────┐
│   Streamlit UI  │────▶│  Nanobot Gateway  │────▶│   Ollama     │
│   (port 8501)   │     │   (port 8502)     │     │  (llama3.2)  │
└─────────────────┘     └────────┬─────────┘     └──────────────┘
                                 │
                                 ▼
                    ┌──────────────────────┐
                    │  MCP Quotes Server    │
                    │  (stdio tools)        │
                    │                       │
                    │  • quotes_health      │
                    │  • quotes_generate    │
                    │  • quotes_chat        │
                    └──────────────────────┘
```

## Quick Start

### Option 1: Local (no Docker)

```bash
# 1. Install Ollama and pull model
ollama pull llama3.2:1b

# 2. Install MCP server
cd mcp/mcp-quotes
pip install -e .

# 3. Install nanobot
cd ../../nanobot-quote
pip install -e .

# 4. Run the Streamlit app
cd ..
pip install streamlit requests
streamlit run app.py
```

### Option 2: Docker Compose

```bash
# Start everything
docker-compose up -d

# Pull the model into Ollama container
docker exec nanobot-ollama ollama pull llama3.2:1b

# Check logs
docker logs -f nanobot-gateway
```

## MCP Tools

| Tool | Description | Args |
|------|-------------|------|
| `quotes_health` | Check Ollama status and models | None |
| `quotes_generate` | Generate a quote | `topic`, `category` |
| `quotes_chat` | Chat with nanobot | `message` |

## Categories

- 💪 **motivation** — perseverance, discipline, hard work
- ❤️ **love** — relationships, warmth, caring
- 🏆 **success** — winning, achievements, reaching the top
- 🧠 **wisdom** — philosophy, knowledge, deep thinking
- ⚡ **energy** — vitality, power, positive vibes
- 🌟 **general** — life, hope, personal growth

## Project Structure

```
hahaton/
├── app.py                          # Streamlit UI
├── quotes.db                       # SQLite database
├── docker-compose.yml              # Full stack orchestration
├── Dockerfile.nanobot             # Nanobot + MCP image
│
├── mcp/
│   └── mcp-quotes/                # MCP server for quotes
│       ├── src/mcp_quotes/
│       │   ├── __init__.py
│       │   ├── client.py          # Ollama HTTP client
│       │   ├── server.py          # MCP stdio server
│       │   ├── settings.py        # Pydantic settings
│       │   └── tools.py           # Tool definitions
│       └── pyproject.toml
│
└── nanobot-quote/                  # Nanobot gateway
    ├── entrypoint.py              # Config + launch script
    ├── config.json                # Base config
    ├── pyproject.toml             # Dependencies
    └── workspace/
        ├── SOUL.md                # Bot personality
        ├── TOOLS.md               # Tool documentation
        └── AGENTS.md              # Agent instructions
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NANOBOT_LLM_MODEL` | `llama3.2:1b` | Ollama model to use |
| `NANOBOT_OLLAMA_URL` | `http://localhost:11434` | Ollama endpoint |
| `NANOBOT_QUOTES_OLLAMA_URL` | same | MCP server Ollama URL |
| `NANOBOT_QUOTES_OLLAMA_MODEL` | same | MCP server Ollama model |
| `NANOBOT_GATEWAY_HOST` | `127.0.0.1` | Gateway bind address |
| `NANOBOT_GATEWAY_PORT` | `8502` | Gateway port |
