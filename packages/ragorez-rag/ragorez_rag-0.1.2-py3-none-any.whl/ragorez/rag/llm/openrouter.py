from typing import Optional

import requests

from .llm_provider import LLMProvider


class OpenRouterProvider(LLMProvider):

    def __init__(self,
                 api_key: str,
                 model_name: str,
                 **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.timeout_seconds = kwargs.get('timeout_seconds') or 60

    def generate(self,
                 prompt: str,
                 system_message: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> str:
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout_seconds
            )
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
        except Exception as e:
            raise e
