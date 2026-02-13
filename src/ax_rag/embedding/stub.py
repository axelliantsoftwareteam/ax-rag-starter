"""Deterministic hashing embedder — no external API required.

Produces reproducible embeddings by hashing text into a fixed-dimension vector.
Useful for development, testing, and running the full pipeline offline.

To swap in a real provider (OpenAI, Cohere, etc.), implement the same
``Embedder`` protocol and update the factory in this module.
"""

from __future__ import annotations

import hashlib
import math
import struct
from typing import Protocol

from ax_rag.core.config import settings


class Embedder(Protocol):
    """Minimal embedding interface."""

    @property
    def dim(self) -> int: ...

    def embed(self, text: str) -> list[float]: ...

    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbedder:
    """Deterministic embedding via SHA-256 expansion.

    The text is hashed, and the digest is expanded to fill the target
    dimension by iteratively hashing with an index salt.  The resulting
    vector is L2-normalised so cosine similarity behaves well.
    """

    def __init__(self, dim: int | None = None) -> None:
        self._dim = dim or settings.embedding_dim

    @property
    def dim(self) -> int:
        return self._dim

    def embed(self, text: str) -> list[float]:
        raw: list[float] = []
        base = text.encode("utf-8")
        idx = 0
        while len(raw) < self._dim:
            digest = hashlib.sha256(base + struct.pack(">I", idx)).digest()
            # Each SHA-256 digest gives 32 bytes → 8 floats (4 bytes each packed as float)
            for offset in range(0, 32, 4):
                if len(raw) >= self._dim:
                    break
                # Map 4 bytes to a float in [-1, 1]
                value = struct.unpack(">I", digest[offset : offset + 4])[0]
                raw.append((value / 0xFFFFFFFF) * 2 - 1)
            idx += 1

        # L2 normalise
        norm = math.sqrt(sum(x * x for x in raw))
        if norm > 0:
            raw = [x / norm for x in raw]
        return raw

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self.embed(t) for t in texts]


def get_embedder() -> Embedder:
    """Factory that returns the configured embedder."""
    return HashEmbedder()
