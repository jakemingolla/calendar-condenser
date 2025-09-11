.PHONY: uv help install test lint run
uv:  ## Install uv if it's not present.
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/$(cat .uv-version)/install.sh | sh

help:  ## Show this help message
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  help - Show this help message"
	@echo "  install - Install dependencies"
	@echo "  run - Run the project"
	@echo "  lint - Run linting"
	@echo "  test - Run all tests"
	@echo "  test-only - Run tests with the 'only' marker"
	@echo "  test-unit - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  dev - Run the project in development mode"

install: uv ## Install dependencies
	uv sync --frozen

test-unit:  ## Run unit tests
	uv run python -m pytest test/unit/

test-integration:  ## Run integration tests
	uv run python -m pytest test/integration/

test:  ## Run tests
	@make test-unit && make test-integration

test-only:  ## Run tests with the 'only' marker
	uv run python -m pytest -s -m only test/

lint:  ## Run linters
	uv run ruff check && uv run basedpyright

dev:   ## Run the project in development mode
	@uvicorn src.api.main:app --reload
