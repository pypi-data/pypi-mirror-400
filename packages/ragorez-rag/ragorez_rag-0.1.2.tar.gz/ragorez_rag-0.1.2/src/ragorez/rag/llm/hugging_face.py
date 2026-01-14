from typing import Optional

import requests

from llm_provider import LLMProvider


class HuggingFaceProvider(LLMProvider):

    def __init__(self,
                 api_key: str,
                 model_name: str,
                 **kwargs):
        self.api_key = api_key
        self.model_name = model_name
        self.api_url = kwargs['api_url'] or f"https://api-inference.huggingface.co/models/{model_name}"
        self.timeout_seconds = kwargs['timeout_seconds'] or 60
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def generate(self,
                 prompt: str,
                 system_message: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> str:
        if system_message:
            full_prompt = f"{system_message}\n\n{prompt}"
        else:
            full_prompt = prompt

        payload = {
            "inputs": full_prompt,
            "parameters": {
                "temperature": temperature,
                "max_new_tokens": max_tokens,
                "return_full_text": False,
            }
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
                if isinstance(result, list):
                    if len(result) > 0:
                        return result[0].get('generated_text', '')
                elif isinstance(result, dict):
                    return result.get('generated_text', result.get('text', ''))
                else:
                    return str(result)
            else:
                error_msg = f"API error: {response.status_code}"
                error_details = response.json()
                error_msg += f" - {error_details.get('error', error_details)}"
                raise Exception(error_msg)
        except Exception as e:
            raise Exception(f"Error: {e}")
