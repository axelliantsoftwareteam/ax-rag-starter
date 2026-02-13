"""PostgreSQL + pgvector storage layer."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, DateTime, Index, Integer, String, Text, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from ax_rag.core.config import settings
from ax_rag.core.logging import get_logger

logger = get_logger(__name__)


# ── ORM ───────────────────────────────────────────────────────────────────────


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    source = Column(String(512), nullable=False)
    raw_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))


class ChunkRow(Base):
    __tablename__ = "chunks"

    id = Column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    document_id = Column(String(36), nullable=False, index=True)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    source = Column(String(512), nullable=False)
    embedding = Column(Vector(settings.embedding_dim))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    __table_args__ = (Index("ix_chunks_embedding", "embedding", postgresql_using="ivfflat"),)


# ── Engine / Session ──────────────────────────────────────────────────────────

engine = create_async_engine(settings.database_url, echo=False, pool_size=5, max_overflow=10)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    """Create tables and install pgvector extension."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")


async def shutdown_db() -> None:
    """Dispose of the engine connection pool."""
    await engine.dispose()
    logger.info("database_shutdown")


# ── CRUD helpers ──────────────────────────────────────────────────────────────


async def insert_document(session: AsyncSession, source: str, raw_text: str) -> str:
    doc = Document(source=source, raw_text=raw_text)
    session.add(doc)
    await session.flush()
    return doc.id  # type: ignore[return-value]


async def insert_chunks(
    session: AsyncSession,
    document_id: str,
    chunks: list[dict[str, object]],
) -> int:
    """Insert chunk rows.  Each dict must have keys: text, chunk_index, source, embedding."""
    rows = [
        ChunkRow(
            document_id=document_id,
            text=c["text"],
            chunk_index=c["chunk_index"],
            source=c["source"],
            embedding=c["embedding"],
        )
        for c in chunks
    ]
    session.add_all(rows)
    await session.flush()
    return len(rows)


async def vector_search(
    session: AsyncSession,
    query_embedding: list[float],
    top_k: int = 5,
) -> list[ChunkRow]:
    """Return the *top_k* closest chunks by cosine distance."""
    result = await session.execute(
        text(
            """
            SELECT id, document_id, text, chunk_index, source, embedding, created_at
            FROM chunks
            ORDER BY embedding <=> :qvec
            LIMIT :k
            """
        ).bindparams(qvec=str(query_embedding), k=top_k),
    )
    rows = result.fetchall()
    return [
        ChunkRow(
            id=r.id,
            document_id=r.document_id,
            text=r.text,
            chunk_index=r.chunk_index,
            source=r.source,
            embedding=r.embedding,
            created_at=r.created_at,
        )
        for r in rows
    ]


async def keyword_search(
    session: AsyncSession,
    query: str,
    top_k: int = 5,
) -> list[ChunkRow]:
    """Simple keyword search using SQL ILIKE on chunk text."""
    terms = query.strip().split()
    if not terms:
        return []

    # Build a WHERE clause that requires all terms to be present (AND logic)
    conditions = " AND ".join(f"text ILIKE :t{i}" for i in range(len(terms)))
    params = {f"t{i}": f"%{term}%" for i, term in enumerate(terms)}
    params["k"] = top_k  # type: ignore[assignment]

    result = await session.execute(
        text(
            f"""
            SELECT id, document_id, text, chunk_index, source, embedding, created_at
            FROM chunks
            WHERE {conditions}
            LIMIT :k
            """
        ).bindparams(**params),
    )
    rows = result.fetchall()
    return [
        ChunkRow(
            id=r.id,
            document_id=r.document_id,
            text=r.text,
            chunk_index=r.chunk_index,
            source=r.source,
            embedding=r.embedding,
            created_at=r.created_at,
        )
        for r in rows
    ]
