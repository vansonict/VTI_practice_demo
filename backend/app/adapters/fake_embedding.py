"""Embedding giả lập (T1.1): băm từ (feature hashing) thành vector chuẩn hóa.

Xác định được và có ý nghĩa *từ vựng* (văn bản trùng từ → cosine cao), đủ để test truy xuất khi chưa có
mô hình thật (ADR-004, T1.7). Không mô phỏng ngữ nghĩa.
"""

import hashlib
import math
import re

_WORD = re.compile(r"\w+", re.UNICODE)


class FakeEmbedding:
    def __init__(self, dim: int = 768) -> None:
        self._dim = dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed_passages(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(t) for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vec = [0.0] * self._dim
        for word in _WORD.findall(text.lower()):
            h = int.from_bytes(hashlib.blake2b(word.encode(), digest_size=8).digest(), "big")
            vec[h % self._dim] += 1.0 if (h >> 63) == 0 else -1.0
        norm = math.sqrt(sum(x * x for x in vec))
        return [x / norm for x in vec] if norm else vec
