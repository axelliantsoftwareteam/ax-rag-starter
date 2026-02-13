"""Unit tests for the text chunker."""

from __future__ import annotations

import pytest

from ax_rag.ingestion.chunker import chunk_text


class TestChunker:
    def test_empty_text_returns_no_chunks(self):
        assert chunk_text("") == []
        assert chunk_text("   ") == []

    def test_short_text_single_chunk(self):
        text = "Hello world."
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=10)
        assert len(chunks) == 1
        assert chunks[0].text == text
        assert chunks[0].index == 0

    def test_chunking_respects_size(self):
        text = "word " * 200  # 1000 chars
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
        for chunk in chunks:
            assert len(chunk.text) <= 100

    def test_overlap_creates_more_chunks(self):
        text = "a" * 300
        no_overlap = chunk_text(text, chunk_size=100, chunk_overlap=0)
        with_overlap = chunk_text(text, chunk_size=100, chunk_overlap=30)
        assert len(with_overlap) > len(no_overlap)

    def test_chunk_indices_are_sequential(self):
        text = "word " * 200
        chunks = chunk_text(text, chunk_size=100, chunk_overlap=10)
        indices = [c.index for c in chunks]
        assert indices == list(range(len(chunks)))

    def test_invalid_chunk_size_raises(self):
        with pytest.raises(ValueError, match="chunk_size must be positive"):
            chunk_text("hello", chunk_size=0, chunk_overlap=0)

    def test_overlap_ge_size_raises(self):
        with pytest.raises(ValueError, match="chunk_overlap"):
            chunk_text("hello", chunk_size=10, chunk_overlap=10)
