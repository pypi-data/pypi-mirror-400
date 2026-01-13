.PHONY: help develop lint format typecheck test clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

develop: ## Set up development environment
	uv sync --group dev
	uv pip install -e .
	uv run --group dev pre-commit install

lint: ## Run ruff linter
	uv run --group dev ruff check src/ tests/

format: ## Format code with ruff
	uv run --group dev ruff format src/ tests/

typecheck: ## Run type checker
	uv run --group dev pyright

test: ## Run tests
	uv run --group dev pytest

clean: ## Delete generated parameterized files
	uv run qparameterize --clean
