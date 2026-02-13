#!/usr/bin/env python3
"""Re-embed all existing chunks (useful after changing the embedding model).

Usage:
    python scripts/reindex.py
"""

from __future__ import annotations

import asyncio

from sqlalchemy import text

from ax_rag.core.logging import get_logger, setup_logging
from ax_rag.embedding.stub import get_embedder
from ax_rag.storage.pg import async_session

logger = get_logger(__name__)


async def reindex() -> None:
    setup_logging()
    embedder = get_embedder()
    logger.info("reindex_started", embedding_dim=embedder.dim)

    async with async_session() as session:
        result = await session.execute(text("SELECT id, text FROM chunks"))
        rows = result.fetchall()

    logger.info("reindex_chunks_found", count=len(rows))

    batch_size = 100
    updated = 0

    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        texts = [r.text for r in batch]
        embeddings = embedder.embed_batch(texts)

        async with async_session() as session, session.begin():
            for row, emb in zip(batch, embeddings, strict=True):
                await session.execute(
                    text("UPDATE chunks SET embedding = :emb WHERE id = :id"),
                    {"emb": str(emb), "id": row.id},
                )
            updated += len(batch)

        logger.info("reindex_batch_complete", updated=updated, total=len(rows))

    logger.info("reindex_finished", total_updated=updated)


def main() -> None:
    asyncio.run(reindex())


if __name__ == "__main__":
    main()
