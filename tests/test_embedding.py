"""Unit tests for the stub embedder."""

from __future__ import annotations

import math

from ax_rag.embedding.stub import HashEmbedder


class TestHashEmbedder:
    def setup_method(self):
        self.embedder = HashEmbedder(dim=128)

    def test_output_dimension(self):
        vec = self.embedder.embed("test")
        assert len(vec) == 128

    def test_deterministic(self):
        a = self.embedder.embed("hello world")
        b = self.embedder.embed("hello world")
        assert a == b

    def test_different_texts_different_embeddings(self):
        a = self.embedder.embed("cats are great")
        b = self.embedder.embed("dogs are great")
        assert a != b

    def test_unit_norm(self):
        vec = self.embedder.embed("normalise me")
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 1e-6

    def test_embed_batch(self):
        texts = ["one", "two", "three"]
        results = self.embedder.embed_batch(texts)
        assert len(results) == 3
        assert all(len(v) == 128 for v in results)
