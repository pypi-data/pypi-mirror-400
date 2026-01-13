.PHONY: help install install-dev test test-cov typecheck lint format security check build clean inspector

help:
	@echo "Available commands:"
	@echo "  make install      - Install package"
	@echo "  make install-dev  - Install package with dev dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make typecheck    - Run mypy type checking"
	@echo "  make lint         - Run ruff linter"
	@echo "  make format       - Format code with ruff"
	@echo "  make check        - Run all checks (lint + typecheck + test)"
	@echo "  make inspector    - Run MCP Inspector for interactive testing"
	@echo "  make build        - Build wheel package"
	@echo "  make clean        - Remove build artifacts and cache"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest --cov=s3_mcp --cov-report=term-missing --cov-report=html

typecheck:
	mypy s3_mcp

lint:
	ruff check .

format:
	ruff format .

check: lint typecheck test
	@echo "All checks passed!"

inspector:
	npx @modelcontextprotocol/inspector python -m s3_mcp.server

build:
	python -m build

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
