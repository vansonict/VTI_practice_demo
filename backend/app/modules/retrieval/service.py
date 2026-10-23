from typing import Protocol

from app.ports.embedding import EmbeddingPort
from app.ports.llm import Evidence


class ChunkSearchRepository(Protocol):
    def search(self, query_vector: list[float], k: int) -> list[Evidence]:
        """Top-k đoạn theo cosine, **chỉ từ tài liệu READY** (BR-003)."""
        ...


class RetrievalService:
    def __init__(self, search: ChunkSearchRepository, embedding: EmbeddingPort, top_k: int) -> None:
        self._search = search
        self._embedding = embedding
        self._top_k = top_k

    def retrieve(self, query: str) -> list[Evidence]:
        return self._search.search(self._embedding.embed_query(query), self._top_k)
