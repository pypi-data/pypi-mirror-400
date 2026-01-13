# Agent Instructions

Instructions for AI agents working on this codebase.

## Environment

- Python 3.13+ required
- Use `uv` for all commands

## Running Tests

```bash
uv sync --extra dev
uv run python -m pytest tests/ -v
```

## Linting

```bash
uv run python -m ruff check src/ tests/
```

Auto-fix issues:
```bash
uv run python -m ruff check src/ tests/ --fix
```

## Formatting

```bash
uv run python -m ruff format src/ tests/
```

Check without modifying:
```bash
uv run python -m ruff format src/ tests/ --check
```

## Type Checking

```bash
uv run python -m mypy src/
```

## All Checks

Run all checks before committing:
```bash
uv sync --extra dev && \
uv run python -m ruff check src/ tests/ && \
uv run python -m ruff format src/ tests/ --check && \
uv run python -m mypy src/ && \
uv run python -m pytest tests/ -v
```
