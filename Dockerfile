FROM python:3.11-slim AS base

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

# ── Production image ──────────────────────────────────────────────────────────
FROM base AS production

COPY src/ src/
RUN pip install --no-cache-dir .

USER app

EXPOSE 8000

CMD ["uvicorn", "ax_rag.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
