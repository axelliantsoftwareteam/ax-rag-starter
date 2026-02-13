"""Text chunking with configurable size and overlap."""

from __future__ import annotations

from dataclasses import dataclass

from ax_rag.core.config import settings


@dataclass(frozen=True)
class Chunk:
    text: str
    index: int
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:
    """Split *text* into overlapping chunks.

    Attempts to break at sentence boundaries (". ") when possible,
    falling back to the hard ``chunk_size`` limit.
    """
    size = chunk_size if chunk_size is not None else settings.chunk_size
    overlap = chunk_overlap if chunk_overlap is not None else settings.chunk_overlap

    if size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("chunk_overlap must be >= 0 and < chunk_size")

    text = text.strip()
    if not text:
        return []

    chunks: list[Chunk] = []
    start = 0
    idx = 0

    while start < len(text):
        end = min(start + size, len(text))

        # Try to find a sentence boundary to break at
        if end < len(text):
            boundary = text.rfind(". ", start, end)
            if boundary > start:
                end = boundary + 2  # include the period and space

        chunk_text_str = text[start:end].strip()
        if chunk_text_str:
            chunks.append(Chunk(text=chunk_text_str, index=idx, start_char=start, end_char=end))
            idx += 1

        # Advance with overlap
        if end >= len(text):
            break
        start = end - overlap

    return chunks
