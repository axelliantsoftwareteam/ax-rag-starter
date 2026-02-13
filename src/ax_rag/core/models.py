"""Pydantic models for API request/response schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

# ── Ingestion ─────────────────────────────────────────────────────────────────


class IngestTextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Raw text to ingest")
    source: str = Field(default="manual", description="Source label for metadata")


class IngestResponse(BaseModel):
    document_id: str
    chunks_created: int
    message: str


# ── Search ────────────────────────────────────────────────────────────────────


class SearchResult(BaseModel):
    chunk_id: str
    text: str
    score: float
    source: str
    created_at: datetime


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    count: int


# ── Answer ────────────────────────────────────────────────────────────────────


class AnswerRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=50)


class AnswerResponse(BaseModel):
    question: str
    answer: str
    sources: list[SearchResult]
