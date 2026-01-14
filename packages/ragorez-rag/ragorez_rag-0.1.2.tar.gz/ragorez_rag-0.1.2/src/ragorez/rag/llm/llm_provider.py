from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):

    @abstractmethod
    def generate(self,
                 prompt: str,
                 system_message: Optional[str] = None,
                 temperature: float = 0.7,
                 max_tokens: int = 1000) -> str:
        pass
