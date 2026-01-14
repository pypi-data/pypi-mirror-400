.PHONY: help test lint lint-fix format type-check fix build clean install-dev

help:
	@echo "Voiceground Development Commands"
	@echo ""
	@echo "  make install-dev    Install development dependencies"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linter (ruff check)"
	@echo "  make lint-fix      Run linter and auto-fix issues (ruff check --fix)"
	@echo "  make format        Format code (ruff format)"
	@echo "  make type-check    Run type checker (mypy)"
	@echo "  make fix           Auto-fix all issues (lint-fix + format)"
	@echo "  make build         Build the package"
	@echo "  make clean         Clean build artifacts"
	@echo "  make all           Run lint, type-check, and test"

install-dev:
	uv sync --group dev

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check --fix --unsafe-fixes .

format:
	uv run ruff format .

type-check:
	uv run mypy src/voiceground

fix: lint-fix format
	@echo "✅ Auto-fixed all issues"

build:
	python -m build

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .mypy_cache .ruff_cache

all: lint type-check test

