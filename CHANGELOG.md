# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-02-13

### Added

- FastAPI service with `/ingest`, `/search`, and `/answer` endpoints.
- PostgreSQL + pgvector storage backend via `docker-compose`.
- Deterministic hashing embedding stub (no external API required).
- Text chunking with configurable size and overlap.
- Hybrid retrieval combining keyword scoring and vector cosine similarity.
- Structured logging with trace-id propagation via `structlog`.
- Admin scripts: `scripts/reindex.py` and `scripts/load_samples.py`.
- Docker support with multi-stage `Dockerfile` and `docker-compose.yml`.
- GitHub Actions CI for linting, testing, and Docker builds.
- Full documentation: README, SECURITY, CONTRIBUTING, CODE_OF_CONDUCT.
- Unit tests for chunking, embedding, and retrieval; API smoke test.

[0.1.0]: https://github.com/axelliant/ax-rag-starter/releases/tag/v0.1.0
