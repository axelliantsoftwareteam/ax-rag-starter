"""POST /ingest — upload text or file for ingestion."""

from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from ax_rag.core.logging import get_logger
from ax_rag.core.models import IngestResponse, IngestTextRequest
from ax_rag.embedding.stub import get_embedder
from ax_rag.ingestion.chunker import chunk_text
from ax_rag.storage.pg import async_session, insert_chunks, insert_document

router = APIRouter()
logger = get_logger(__name__)


@router.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_text(body: IngestTextRequest) -> IngestResponse:
    """Ingest raw text: chunk, embed, and store."""
    embedder = get_embedder()
    chunks = chunk_text(body.text)
    logger.info("ingesting_text", source=body.source, num_chunks=len(chunks))

    async with async_session() as session, session.begin():
        doc_id = await insert_document(session, source=body.source, raw_text=body.text)
        chunk_rows = [
            {
                "text": c.text,
                "chunk_index": c.index,
                "source": body.source,
                "embedding": embedder.embed(c.text),
            }
            for c in chunks
        ]
        count = await insert_chunks(session, doc_id, chunk_rows)

    return IngestResponse(
        document_id=doc_id,
        chunks_created=count,
        message=f"Ingested {count} chunks from source '{body.source}'",
    )


@router.post("/ingest/file", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_file(file: UploadFile = File(...)) -> IngestResponse:  # noqa: B008
    """Ingest an uploaded text file."""
    content = (await file.read()).decode("utf-8")
    source = file.filename or "upload"
    logger.info("ingesting_file", filename=source, size=len(content))

    embedder = get_embedder()
    chunks = chunk_text(content)

    async with async_session() as session, session.begin():
        doc_id = await insert_document(session, source=source, raw_text=content)
        chunk_rows = [
            {
                "text": c.text,
                "chunk_index": c.index,
                "source": source,
                "embedding": embedder.embed(c.text),
            }
            for c in chunks
        ]
        count = await insert_chunks(session, doc_id, chunk_rows)

    return IngestResponse(
        document_id=doc_id,
        chunks_created=count,
        message=f"Ingested {count} chunks from file '{source}'",
    )
