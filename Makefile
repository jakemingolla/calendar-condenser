.PHONY: uv
uv:  ## Install uv if it's not present.
	@command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/$(cat .uv-version)/install.sh | sh

.PHONY: install
install: uv ## Install dependencies
	uv sync --frozen

.PHONY: test
test:  ## Run tests
	uv run pytest

.PHONY: lint
lint:  ## Run linters
	uv run ruff check && uv run basedpyright

.PHONY: run
run:  ## Run the project
	uv run python -m src.main
