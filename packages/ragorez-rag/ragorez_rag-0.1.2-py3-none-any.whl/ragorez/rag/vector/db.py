from abc import ABC, abstractmethod
from typing import List, Any


class SearchResponse:
    def __init__(self, answers: List[str], full_response: Any = None):
        self.answers = answers
        self.full_response = full_response


class DataBaseProvider(ABC):

    @abstractmethod
    def search(self, query: str, n_results: int = 5) -> SearchResponse:
        pass
