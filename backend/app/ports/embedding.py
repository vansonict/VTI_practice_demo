"""EmbeddingPort (SDD §3.2, SAD §2.5 EI-2)."""

from typing import Protocol


class EmbeddingUnavailable(Exception):
    pass


class EmbeddingPort(Protocol):
    @property
    def dim(self) -> int: ...

    def embed_passages(self, texts: list[str]) -> list[list[float]]: ...

    def embed_query(self, text: str) -> list[float]: ...
