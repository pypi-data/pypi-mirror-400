.PHONY: help venv install dev-install test lint format type-check clean build publish

# Default target
help:
	@echo "PaperTrail Development Commands"
	@echo "================================"
	@echo "venv          - Create virtual environment"
	@echo "install       - Install package in production mode"
	@echo "dev-install   - Install package with dev dependencies"
	@echo "test          - Run test suite"
	@echo "test-cov      - Run tests with coverage report"
	@echo "lint          - Run linters (ruff)"
	@echo "format        - Format code (black + isort)"
	@echo "type-check    - Run type checker (mypy)"
	@echo "clean         - Remove build artifacts"
	@echo "build         - Build distribution packages"
	@echo "publish       - Publish to PyPI"
	@echo ""
	@echo "Quick start: make venv && source .venv/bin/activate && make dev-install"

# Virtual Environment
venv:
	@if [ ! -d .venv ]; then \
		echo "Creating virtual environment..."; \
		uv venv; \
		echo "✅ Virtual environment created at .venv"; \
		echo "Activate with: source .venv/bin/activate"; \
	else \
		echo "✅ Virtual environment already exists"; \
	fi

# Installation
install: venv
	@echo "Installing package..."
	uv pip install -e .

dev-install: venv
	@echo "Installing dev dependencies..."
	uv pip install -e ".[dev,async,postgresql]"
	@if command -v pre-commit > /dev/null; then pre-commit install; fi

# Testing
test: dev-install
	uv run pytest

test-cov: dev-install
	uv run pytest --cov=paper_trail --cov-report=html --cov-report=term

test-watch: dev-install
	uv run pytest-watch

# Code Quality
lint:
	uv run ruff check src/ tests/
	uv run black --check src/ tests/
	uv run isort --check-only src/ tests/

format:
	uv run black src/ tests/
	uv run isort src/ tests/
	uv run ruff check --fix src/ tests/

type-check:
	uv run mypy src/paper_trail

# Pre-commit
pre-commit:
	pre-commit run --all-files

# Cleaning
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Building
build: clean
	uv build

# Publishing
publish-test:
	uv publish --repository testpypi

publish:
	uv publish

# Database migrations (example)
migrate-create:
	alembic revision --autogenerate -m "$(msg)"

migrate-up:
	alembic upgrade head

migrate-down:
	alembic downgrade -1

# Documentation
docs:
	cd docs && make html

docs-serve:
	cd docs/_build/html && python -m http.server 8000

# Development utilities
shell:
	uv run python

notebook:
	uv run jupyter notebook examples/
