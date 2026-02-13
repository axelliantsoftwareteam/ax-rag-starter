# Contributing to ax-rag-starter

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. **Fork** the repository and clone your fork.
2. Create a feature branch: `git checkout -b feat/my-feature`.
3. Set up the development environment:

```bash
make setup
source .venv/bin/activate
cp .env.example .env
```

4. Start the backing services:

```bash
docker compose up -d postgres
```

## Development Workflow

### Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
make fmt     # auto-format
make lint    # check style
make typecheck  # mypy strict mode
```

### Running Tests

```bash
make test        # run all tests
make test-cov    # with coverage report
```

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add hybrid retrieval scoring
fix: handle empty chunk lists in ingestion
docs: update quickstart section
test: add retrieval ranking edge cases
```

## Pull Request Process

1. Ensure `make lint` and `make test` pass.
2. Update documentation if your change affects the public API or configuration.
3. Add or update tests for new functionality.
4. Keep PRs focused — one logical change per PR.
5. Fill in the PR template and link any related issues.

## Reporting Bugs

Open a [GitHub Issue](https://github.com/axelliant/ax-rag-starter/issues) with:

- A clear title and description.
- Steps to reproduce.
- Expected vs. actual behaviour.
- Environment details (OS, Python version, Docker version).

## Security Vulnerabilities

Please report security issues to **security@axelliant.com** — see [SECURITY.md](SECURITY.md).

## Contact

- General: [info@axelliant.com](mailto:info@axelliant.com)
- Website: [axelliant.com](https://axelliant.com)

## License

By contributing, you agree that your contributions will be licensed under the [Apache License 2.0](LICENSE).
