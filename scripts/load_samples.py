#!/usr/bin/env python3
"""Load sample documents into the RAG system.

Usage:
    python scripts/load_samples.py          # uses default API URL
    python scripts/load_samples.py --url http://localhost:8000
"""

from __future__ import annotations

import argparse
import sys

import httpx

SAMPLES = [
    {
        "text": (
            "Retrieval-Augmented Generation (RAG) combines a retrieval system with a "
            "generative language model. When a user asks a question, the system first "
            "searches a knowledge base for relevant documents, then provides those "
            "documents as context to the language model for answer generation. This "
            "approach grounds the model's output in real data, significantly reducing "
            "hallucination compared to pure generation."
        ),
        "source": "sample/rag-overview",
    },
    {
        "text": (
            "Vector databases store data as high-dimensional vectors (embeddings). "
            "They enable similarity search by computing distances (cosine, Euclidean, "
            "dot product) between a query vector and stored vectors. Popular vector "
            "databases include pgvector (PostgreSQL extension), Pinecone, Weaviate, "
            "and Qdrant. pgvector is notable for integrating vector search directly "
            "into PostgreSQL, allowing hybrid queries that combine SQL filters with "
            "vector similarity."
        ),
        "source": "sample/vector-databases",
    },
    {
        "text": (
            "Text chunking is the process of splitting large documents into smaller, "
            "semantically meaningful pieces for embedding and retrieval. Common "
            "strategies include fixed-size chunking with overlap, sentence-based "
            "splitting, and recursive character splitting. The chunk size affects "
            "retrieval precision: smaller chunks are more precise but may lose context, "
            "while larger chunks preserve context but may introduce noise."
        ),
        "source": "sample/text-chunking",
    },
    {
        "text": (
            "Hybrid retrieval combines keyword-based search (like BM25 or SQL ILIKE) "
            "with dense vector similarity search. The results from both methods are "
            "merged using techniques such as Reciprocal Rank Fusion (RRF). Hybrid "
            "retrieval outperforms either method alone because keyword search excels "
            "at exact term matching while vector search captures semantic similarity."
        ),
        "source": "sample/hybrid-retrieval",
    },
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load sample documents")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()

    base = args.url.rstrip("/")
    print(f"Loading {len(SAMPLES)} sample documents into {base}")

    for sample in SAMPLES:
        resp = httpx.post(f"{base}/ingest", json=sample, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✓ {sample['source']}: {data['chunks_created']} chunks")
        else:
            print(f"  ✗ {sample['source']}: HTTP {resp.status_code} — {resp.text}")
            sys.exit(1)

    print("\nDone. Try: curl 'http://localhost:8000/search?q=vector+database'")


if __name__ == "__main__":
    main()
