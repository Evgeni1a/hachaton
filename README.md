# ✨ AI Quote Generator

**AI Quote Generator** is a one‑click web app that generates unique inspirational quotes using AI, stores your history, and lets you save favorites — perfect for students and professionals who need daily motivation even in restricted network environments.

---

## Product Context

### End Users
- Students and office workers needing quick inspiration or motivation.
- Developers working on university VMs where external AI tools (Telegram bots, ChatGPT) are restricted or require a VPN.

### The Problem
Traditional quote websites are cluttered with ads, require endless scrolling, and show the same repetitive quotes. Furthermore, university VMs often block access to external services, leaving users without fresh, unique content when they need a quick mental boost.

### Our Solution
A one‑sentence pitch: **A fully local, Dockerizable AI quote generator that creates unique quotes, saves history, and manages favorites directly on your VM.**

---

## Features and Implementation Plan

### Version 1: The Core Logic (Task 3)
- One‑Click Quote Generation: Generate a random inspirational quote with a single button press.
- Quote History: Automatically save every generated quote to SQLite database with timestamps.
- Clean Web Interface: Simple, intuitive layout with a prominent generate button.

### Version 2: The Interactive Experience (Task 4)
- Favorites System: Save quotes you love to a separate "Favorites" tab.
- Remove from Favorites: Delete quotes from favorites with one click.
- History & Favorites Tabs: Easy navigation between recent quotes and saved favorites.
- LLM Integration: Powered by local Ollama (llama3.2:1b) or OpenAI API for truly unique, AI‑generated quotes.
- Live Status Indicators: "Generating..." spinner and success toasts for better UX.

### Planned for Future Versions
- Dark/Light theme toggle
- Export favorites to PDF
- Copy quote to clipboard
- Quote categories and tags
- Daily quote notifications

---

## Usage

1. Open the web app in your browser (http://localhost:8501)
2. Click **"Generate New Quote"** button
3. The AI generates a unique quote — it appears on screen
4. The quote is automatically saved to **History**
5. Click **"Save to Favorites"** to bookmark quotes you love
6. View all your saved quotes in the **Favorites** tab

---

## Deployment

### Prerequisites
- **OS**: Ubuntu 24.04 (standard for university VMs)
- **Tools**: Docker and Docker Compose (optional) or Python 3.12+
- **AI Engine (optional)**: Ollama running on the host machine (`ollama pull llama3.2:1b`)

### Step‑by‑Step Instructions (without Docker)

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
