"""API smoke tests — validates routes without requiring a database.

These tests verify that the API endpoints are wired correctly and return
the expected status codes and schemas.  For full integration tests with
a live database, use ``docker compose up`` and run ``make test``.
"""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from ax_rag.api.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestHealthEndpoint:
    @pytest.mark.asyncio
    async def test_health_returns_ok(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestIngestValidation:
    @pytest.mark.asyncio
    async def test_ingest_empty_text_rejected(self, client: AsyncClient):
        resp = await client.post("/ingest", json={"text": ""})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_ingest_missing_body_rejected(self, client: AsyncClient):
        resp = await client.post("/ingest")
        assert resp.status_code == 422


class TestSearchValidation:
    @pytest.mark.asyncio
    async def test_search_missing_query_rejected(self, client: AsyncClient):
        resp = await client.get("/search")
        assert resp.status_code == 422


class TestAnswerValidation:
    @pytest.mark.asyncio
    async def test_answer_empty_question_rejected(self, client: AsyncClient):
        resp = await client.post("/answer", json={"question": ""})
        assert resp.status_code == 422
