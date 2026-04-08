# TOOLS — Nanobot Quote Generator

## Available MCP Tools

### quotes_health
Check if Ollama is running and list available models.
- No arguments needed
- Returns: status and list of models

### quotes_generate
Generate an inspirational quote on a specific topic.
- **topic** (string): What the quote should be about, e.g. "morning motivation", "never giving up"
- **category** (string): One of: motivation, love, success, wisdom, energy, general

### quotes_chat
Have a conversation with the nanobot.
- **message** (string): Your message to the nanobot

## Usage Tips
- Use `quotes_generate` when the user asks for a specific quote
- Use `quotes_chat` for general conversation about quotes
- Check `quotes_health` if generation fails
