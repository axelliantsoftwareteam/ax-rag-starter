.PHONY: setup up down test lint fmt typecheck run clean logs

# ── Setup ─────────────────────────────────────────────────────────────────────
setup:
	python -m venv .venv
	.venv/bin/pip install -e ".[dev]"
	@echo "\n✓ Run 'source .venv/bin/activate' to activate the virtualenv"

# ── Docker ────────────────────────────────────────────────────────────────────
up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f

# ── Quality ───────────────────────────────────────────────────────────────────
lint:
	ruff check src/ tests/ scripts/
	ruff format --check src/ tests/ scripts/

fmt:
	ruff check --fix src/ tests/ scripts/
	ruff format src/ tests/ scripts/

typecheck:
	mypy src/

# ── Test ──────────────────────────────────────────────────────────────────────
test:
	pytest -v

test-cov:
	coverage run -m pytest -v
	coverage report -m --fail-under=80

# ── Run (local dev) ──────────────────────────────────────────────────────────
run:
	uvicorn ax_rag.api.main:app --reload --host 0.0.0.0 --port 8000

# ── Housekeeping ──────────────────────────────────────────────────────────────
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache htmlcov .coverage dist build *.egg-info
