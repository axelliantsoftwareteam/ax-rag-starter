"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ax_rag.api.middleware import TraceMiddleware
from ax_rag.api.routes import answer, ingest, search
from ax_rag.core.logging import setup_logging
from ax_rag.storage.pg import init_db, shutdown_db


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    await init_db()
    yield
    await shutdown_db()


app = FastAPI(
    title="ax-rag-starter",
    description=(
        "End-to-end RAG starter kit with ingestion, hybrid retrieval, and answer "
        "composition. Built by Axelliant — https://axelliant.com"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(TraceMiddleware)

app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(answer.router)


@app.get("/health", tags=["System"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
