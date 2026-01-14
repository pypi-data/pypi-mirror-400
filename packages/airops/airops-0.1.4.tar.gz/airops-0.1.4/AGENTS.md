# Agent Instructions

Instructions for AI agents working on this codebase.

## SDK Overview

The AirOps Tools SDK (`airops-sdk`) enables Content Engineers to build custom Python tools that integrate with AirOps (Workflow Studio, Grid, and AirOps Agents). Tools can call AirOps' internal Steps API to execute LLM calls, web scraping, and other step primitives.

A tool is defined by:
1. Input/output Pydantic models
2. An async handler function decorated with `@tool.handler`
3. A `Tool` instance that wraps metadata and provides the runtime

The SDK provides:
- A Steps API client for executing AirOps steps (async start/poll pattern)
- An HTTP runtime server with start/poll endpoints for tool execution
- A local testing UI for manual testing during development
- Input type annotations for AirOps workflow UI integration

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
