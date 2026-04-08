"""Client for Ollama API used by the MCP Quotes server."""

from __future__ import annotations

import requests


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_alive(self) -> dict:
        """Check if Ollama is running."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                return {"status": "ok", "models": [m.get("name") for m in models]}
            return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def generate_quote(self, topic: str, category: str = "general") -> dict:
        """Generate a quote via Ollama with category-specific prompt."""

        category_prompts = {
            "motivation": "motivational quote about pushing forward, never giving up, discipline, and hard work",
            "love": "warm quote about love, relationships, caring, and emotional connection",
            "success": "quote about winning, reaching the top, achieving success, and celebrating victories",
            "wisdom": "philosophical quote about life meaning, knowledge, and deep thinking",
            "energy": "high-energy quote about vitality, power, excitement, and being unstoppable",
            "general": "short inspiring quote about life, hope, and personal growth",
        }

        prompt_desc = category_prompts.get(category, category_prompts["general"])

        examples = {
            "motivation": "Rise, grind, repeat - champions are made when nobody watches.",
            "love": "Love is not about finding the perfect person, but seeing an imperfect one perfectly.",
            "success": "The view from the top is worth every step of the climb.",
            "wisdom": "The more you learn, the more you realize how much you don't know.",
            "energy": "Wake up like a storm - loud, powerful, unstoppable.",
            "general": "Every sunrise is a new chance to shine.",
        }

        example = examples.get(category, examples["general"])

        prompt = (
            f"You are a creative quote generator. Generate ONE original quote.\n"
            f"Topic: {prompt_desc}\n"
            f"Context: {topic}\n"
            f"Rules:\n"
            f"- Exactly 10-20 words\n"
            f"- No famous people names\n"
            f"- Do NOT mention love unless the topic is about love\n"
            f"- Make it unique and creative\n"
            f"- Return ONLY the quote, nothing else\n\n"
            f"Example: {example}"
        )

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.9, "max_tokens": 100},
                },
                timeout=60,
            )
            if resp.status_code == 200:
                result = resp.json()
                quote = result.get("response", "").strip().strip('"\'')
                return {"status": "ok", "quote": quote, "category": category, "topic": topic}
            return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def chat(self, message: str, system_prompt: str = "") -> dict:
        """Chat with the nanobot via Ollama."""
        full_prompt = ""
        if system_prompt:
            full_prompt += system_prompt + "\n\n"
        full_prompt += f"User: {message}\nNanobot:"

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {"temperature": 0.8, "max_tokens": 500},
                },
                timeout=60,
            )
            if resp.status_code == 200:
                result = resp.json()
                text = result.get("response", "").strip()
                return {"status": "ok", "response": text}
            return {"status": "error", "code": resp.status_code}
        except Exception as e:
            return {"status": "error", "message": str(e)}
