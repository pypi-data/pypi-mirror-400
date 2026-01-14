import chromadb

from .db import DataBaseProvider, SearchResponse


class ChromaDbProvider(DataBaseProvider):
    def __init__(self,
                 collection: chromadb.Collection):
        self.collection = collection

    def search(self, query: str, n_results: int = 5) -> SearchResponse:
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return SearchResponse(answers=results['documents'][0])
