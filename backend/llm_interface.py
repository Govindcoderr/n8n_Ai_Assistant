import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LLMInterface:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env")

        self.url = "https://api.groq.com/openai/v1/chat/completions"

    def ask(self, prompt: str) -> str:
        payload = {
            "model": "openai/gpt-oss-120b",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.url,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        return response.json()["choices"][0]["message"]["content"]
