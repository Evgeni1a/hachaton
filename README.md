# Nanobot Quote Generator

**Nanobot Quote Generator** is an AI-powered web app that generates original inspirational quotes using a local LLM (Ollama) orchestrated through the NanoBot AI agent framework with MCP tools.

---

## Product Context

### End Users
- Students and professionals who need quick daily inspiration for motivation or focus.
- Content creators looking for unique quotes for social media, presentations, or articles.
- Anyone seeking mood-based inspiration — whether they need energy before a workout, wisdom for reflection, or a love quote for a special moment.
- Developers and tech enthusiasts interested in seeing AI agents (NanoBot + MCP + Ollama) work in a practical, everyday tool.

### The Problem
People spend time searching for good quotes online, but most quote sites offer the same recycled clichés from famous figures. There's no personalization, no mood filtering, and no AI interaction. Users also can't get explanations or have a conversation about the meaning behind a quote.

### Our Solution
A one-sentence pitch: **A fully local AI quote generator that creates unique, mood-based quotes with an interactive bot you can talk to.**

---

## Features

- Instant mood-based quote generation (5+ categories: Motivation, Love, Success, Wisdom, Energy)
- Interactive chat with NanoBot for explanations and custom requests
- Save favorites and browse full history with category filters
- Daily statistics dashboard (quotes generated, top categories)
- Runs 100% locally via Ollama — no API keys, no cloud costs, fully private
- Extensible architecture via MCP protocol for future tool additions

---

## The Ecosystem

- **Central server:** hosted on a VM
- **Persistent:** a managed SQLite database ensuring quotes, favorites, history, and chat messages are always available
- **Instance engine:** an Ollama instance running a local LLM (e.g., llama3.2 or Qwen2)
- **AI agent gateway:** NanoBot framework orchestrating requests via MCP protocol
- **MCP tools server:** wraps Ollama API into typed tools (quotes_generate, quotes_chat, quotes_health)
- **Streamlit frontend:** UI for quote generation, chat, history, and statistics (falls back to direct Ollama if NanoBot offline)

---

## Deployment

### Prerequisites
- OS: Ubuntu 24.04 (or any Linux distribution)
- Tools: Docker and Docker Compose
- AI Engine: Ollama running on the host machine (`ollama pull llama3.2:1b`)

### Step-by-Step Instructions


```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and pip
sudo apt install python3 python3-pip -y

# 3. Clone the repository
git clone https://github.com/Evgeni1a/se-toolkit-hackathon.git
cd se-toolkit-hackathon

# 4. Install dependencies
pip3 install streamlit requests

# 5. (Optional) Install Ollama for local LLM
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b

# 6. Run the app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
