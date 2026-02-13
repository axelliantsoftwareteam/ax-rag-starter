"""Hybrid retrieval: combine keyword + vector results with reciprocal rank fusion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ax_rag.embedding.stub import get_embedder
from ax_rag.storage.pg import keyword_search, vector_search


@dataclass
class ScoredChunk:
    chunk_id: str
    text: str
    score: float
    source: str
    created_at: datetime


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    k: int = 60,
) -> dict[str, float]:
    """Compute RRF scores across multiple ranked lists.

    Each list contains chunk IDs ordered by relevance (best first).
    Returns a dict mapping chunk_id → fused score.
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank + 1)
    return scores


async def hybrid_retrieve(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[ScoredChunk]:
    """Run keyword + vector search in parallel and fuse results."""
    embedder = get_embedder()
    query_vec = embedder.embed(query)

    vec_results = await vector_search(session, query_vec, top_k=top_k * 2)
    kw_results = await keyword_search(session, query, top_k=top_k * 2)

    # Build lookup by chunk ID
    all_chunks = {}
    for row in vec_results + kw_results:
        all_chunks[row.id] = row

    # Ranked lists (IDs in relevance order)
    vec_ids = [r.id for r in vec_results]
    kw_ids = [r.id for r in kw_results]

    fused = reciprocal_rank_fusion([vec_ids, kw_ids])

    # Sort by fused score descending
    sorted_ids = sorted(fused, key=lambda cid: fused[cid], reverse=True)[:top_k]

    results: list[ScoredChunk] = []
    for cid in sorted_ids:
        row = all_chunks[cid]
        results.append(
            ScoredChunk(
                chunk_id=cid,  # type: ignore[arg-type]
                text=row.text,  # type: ignore[arg-type]
                score=round(fused[cid], 6),  # type: ignore[arg-type]
                source=row.source,  # type: ignore[arg-type]
                created_at=row.created_at,  # type: ignore[arg-type]
            )
        )
    return results
