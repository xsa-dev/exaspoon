.PHONY: help install dev test lint format clean run shell

# Default target
help:
	@echo "🥄 SpoonAI Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install    Install dependencies with uv"
	@echo "  dev        Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  test       Run tests"
	@echo "  lint       Run linting"
	@echo "  format     Format code"
	@echo "  shell      Activate virtual shell"
	@echo "  run        Run the application"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean      Clean cache and build artifacts"
	@echo "  sync       Sync dependencies"

# Setup & Installation
install:
	uv sync

dev:
	uv sync --dev

# Development
test:
	uv run pytest

lint:
	uv run ruff check
	uv run mypy spoon_ai

format:
	uv run ruff format
	uv black spoon_ai

shell:
	uv shell

run:
	uv run python -m spoon_ai

# Maintenance
clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist
	uv cache clean

sync:
	uv sync
