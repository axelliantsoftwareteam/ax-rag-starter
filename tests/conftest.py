"""Shared test fixtures."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
def sample_text() -> str:
    return (
        "Retrieval-Augmented Generation (RAG) is a technique that combines information "
        "retrieval with language model generation. It first retrieves relevant documents "
        "from a knowledge base, then uses those documents as context to generate accurate "
        "and grounded responses. RAG is widely used for question answering, customer "
        "support, and knowledge management. The approach reduces hallucination by anchoring "
        "generation in retrieved evidence. Modern RAG systems use dense vector retrieval "
        "alongside traditional keyword search for hybrid retrieval."
    )


@pytest.fixture
async def api_client():
    """AsyncClient wired to the FastAPI app *without* database lifespan.

    Tests that hit the API routes requiring a database should be marked as
    integration tests and need a running PostgreSQL instance.
    """
    from ax_rag.api.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
