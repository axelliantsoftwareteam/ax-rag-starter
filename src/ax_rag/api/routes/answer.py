"""POST /answer — retrieve context then compose an answer."""

from __future__ import annotations

from fastapi import APIRouter

from ax_rag.core.logging import get_logger
from ax_rag.core.models import AnswerRequest, AnswerResponse, SearchResult
from ax_rag.retrieval.hybrid import hybrid_retrieve
from ax_rag.storage.pg import async_session

router = APIRouter()
logger = get_logger(__name__)


def _compose_answer(question: str, context_chunks: list[str]) -> str:
    """Build an answer from retrieved context.

    In a production system this would call an LLM.  For the starter kit we
    return the concatenated context with a header — demonstrating the full
    retrieval pipeline without requiring an external API key.
    """
    if not context_chunks:
        return "No relevant context found for your question."

    context = "\n\n---\n\n".join(context_chunks)
    return (
        f"Based on {len(context_chunks)} retrieved passage(s):\n\n"
        f"{context}\n\n"
        f'(In production, an LLM would synthesise an answer to: "{question}")'
    )


@router.post("/answer", response_model=AnswerResponse, tags=["Answer"])
async def answer(body: AnswerRequest) -> AnswerResponse:
    """Retrieve relevant context and compose an answer."""
    logger.info("answer", question=body.question, top_k=body.top_k)

    async with async_session() as session:
        scored = await hybrid_retrieve(session, body.question, top_k=body.top_k)

    sources = [
        SearchResult(
            chunk_id=s.chunk_id,
            text=s.text,
            score=s.score,
            source=s.source,
            created_at=s.created_at,
        )
        for s in scored
    ]

    composed = _compose_answer(body.question, [s.text for s in scored])

    return AnswerResponse(
        question=body.question,
        answer=composed,
        sources=sources,
    )
