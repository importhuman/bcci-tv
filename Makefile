.PHONY: help test lint format clean

# Default goal
help:
	@echo "Available commands (no manual install required):"
	@echo "  test        : Run all tests using uv run"
	@echo "  lint        : Check for linting issues using uvx ruff"
	@echo "  format      : Format code using uvx ruff"
	@echo "  clean       : Remove temporary files and caches"

test:
	@echo "Running tests..."
	uv run pytest

lint:
	@echo "Checking for linting issues..."
	uvx ruff check .

format:
	@echo "Formatting code..."
	uvx ruff check --fix .
	uvx ruff format .

clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache .venv
	find . -name "__pycache__" -type d -exec rm -rf {} +
