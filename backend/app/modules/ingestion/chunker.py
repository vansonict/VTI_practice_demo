"""Chia đoạn trong phạm vi từng trang: không đoạn nào chứa văn bản của hai trang (để trích dẫn đúng trang)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkDraft:
    page: int  # bắt đầu từ 1
    ordinal: int
    text: str


def chunk_pages(pages: list[str], max_words: int, overlap_words: int) -> list[ChunkDraft]:
    if max_words <= 0 or not 0 <= overlap_words < max_words:
        raise ValueError("Cần max_words > 0 và 0 <= overlap_words < max_words")
    chunks: list[ChunkDraft] = []
    step = max_words - overlap_words
    for page_no, text in enumerate(pages, start=1):
        words = text.split()
        start = 0
        while start < len(words):
            chunks.append(
                ChunkDraft(page=page_no, ordinal=len(chunks), text=" ".join(words[start : start + max_words]))
            )
            if start + max_words >= len(words):
                break
            start += step
    return chunks
