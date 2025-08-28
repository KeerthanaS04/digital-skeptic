from typing import Optional, List
import os
import requests
from dotenv import load_dotenv
load_dotenv()

class LLMClient:
    """
    Supports chat-based LLM providers: openai, perplexity, and groq.
    """

    def __init__(self, model: str = "gpt-4o-mini", provider: str = "openai", base_url: Optional[str] = None):
        self.provider = provider.lower()
        self.model = model

        if self.provider == "groq":
            from groq import Groq  # make sure 'groq' is in requirements
            self.api_key = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        else:
            self.api_key = (
                os.environ.get("OPENAI_API_KEY")
                if self.provider == "openai"
                else os.environ.get("PERPLEXITY_API_KEY")
            )
            self.base_url = base_url or (
                "https://api.openai.com/v1/chat/completions"
                if self.provider == "openai"
                else "https://api.perplexity.ai/chat/completions"
            )
            if not self.api_key:
                raise RuntimeError(f"{self.provider.upper()} API key not set.")

    def chat(self, messages: List[dict], temperature: float = 0.2, max_tokens: int = 600) -> str:
        if self.provider == "groq":
            resp = self.client.chat.completions.create(messages=messages, model=self.model)
            return resp.choices[0].message.content.strip()
        else:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            r = requests.post(self.base_url.rstrip("/"), json=payload, headers=headers, timeout=60)
            r.raise_for_status()
            data = r.json()
            try:
                return data["choices"][0]["message"]["content"].strip()
            except KeyError:
                return data["choices"][0].get("text", "").strip()
