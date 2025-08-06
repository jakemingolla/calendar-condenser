.ONESHELL:
SHELL = /bin/zsh
.SHELLFLAGS = -e

.PHONY: help install run lint test

virtual_environment_directory = .venv

help:
	@echo "Usage: make <target>"
	@echo "Targets:"
	@echo "  help - Show this help message"
	@echo "  install - Install dependencies"
	@echo "  run - Run the project"
	@echo "  lint - Run linting"
	@echo "  test - Run tests"

$(virtual_environment_directory):
	uv venv

install: $(virtual_environment_directory)
	uv sync --frozen

run: $(virtual_environment_directory)
	@. $(virtual_environment_directory)/bin/activate && python -m src.main

lint:
	@. $(virtual_environment_directory)/bin/activate; \
	ruff check; \
	basedpyright

test:
	@. $(virtual_environment_directory)/bin/activate; \
	pytest
