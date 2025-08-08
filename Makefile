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
	@echo "  test - Run tests"

install: uv ## Install dependencies
	uv sync --frozen

test:  ## Run tests
	uv run pytest

lint:  ## Run linters
	uv run ruff check && uv run basedpyright

run:  ## Run the project
	@uv run python -m src.main
