FROM python:3.11-slim AS base

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

# Install dependencies only (cached layer — rebuilds only when pyproject.toml changes)
COPY pyproject.toml ./
RUN pip install --no-cache-dir \
    "fastapi>=0.115,<1" \
    "uvicorn[standard]>=0.32,<1" \
    "asyncpg>=0.30,<1" \
    "pgvector>=0.3,<1" \
    "sqlalchemy[asyncio]>=2.0,<3" \
    "python-multipart>=0.0.12" \
    "pydantic>=2.0,<3" \
    "pydantic-settings>=2.0,<3" \
    "structlog>=24.0,<26"

# ── Production image ──────────────────────────────────────────────────────────
FROM base AS production

COPY src/ src/
RUN pip install --no-cache-dir .

USER app

EXPOSE 8000

CMD ["uvicorn", "ax_rag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
