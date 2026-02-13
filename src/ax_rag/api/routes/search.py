"""GET /search — hybrid keyword + vector search."""

from __future__ import annotations

from fastapi import APIRouter, Query

from ax_rag.core.logging import get_logger
from ax_rag.core.models import SearchResponse, SearchResult
from ax_rag.retrieval.hybrid import hybrid_retrieve
from ax_rag.storage.pg import async_session

router = APIRouter()
logger = get_logger(__name__)


@router.get("/search", response_model=SearchResponse, tags=["Retrieval"])
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(default=5, ge=1, le=50),
) -> SearchResponse:
    """Hybrid retrieval: keyword + vector similarity with reciprocal rank fusion."""
    logger.info("search", query=q, top_k=top_k)

    async with async_session() as session:
        scored = await hybrid_retrieve(session, q, top_k=top_k)

    results = [
        SearchResult(
            chunk_id=s.chunk_id,
            text=s.text,
            score=s.score,
            source=s.source,
            created_at=s.created_at,
        )
        for s in scored
    ]
    return SearchResponse(query=q, results=results, count=len(results))
