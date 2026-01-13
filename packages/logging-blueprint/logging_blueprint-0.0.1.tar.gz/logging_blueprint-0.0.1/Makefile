.DEFAULT_GOAL := help

SOURCE_DIRS := src tests benchmarks examples
DOC_FILES := README.md

### Makefile

.PHONY: help
help: ## Display this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@awk 'BEGIN {section="General"} /^### /{section=substr($$0,5); printf "\n\033[1m%s\033[0m\n", section} /^[a-zA-Z0-9_-]+:.*?## / {match($$0, /## (.*)$$/, a); printf "  \033[36m%-18s\033[0m %s\n", substr($$1,1,length($$1)-1), a[1]}' $(MAKEFILE_LIST)


### Installation

.PHONY: install
install: ## Install the project's dependencies with uv (**including all extras and dev dependencies**)
	uv sync --all-extras --dev

### Development

.PHONY: lint
lint: ## Run linters, formatters, and type checks
	uv run codespell --write-changes $(SOURCE_DIRS) $(DOC_FILES)
	uv run ruff check --fix $(SOURCE_DIRS)
	uv run ruff format $(SOURCE_DIRS)
	uv run mypy --config-file pyproject.toml $(SOURCE_DIRS)

.PHONY: build
build: ## Build wheel
	uv build --wheel

.PHONY: all
all: lint test build ## Run high-level verification (lint, test, build)

.PHONY: test
test: ## Run tests
	uv run pytest

.PHONY: bench
bench: ## Run microbenchmarks (pyperf)
	uv run python benchmarks/bench_logging_blueprint.py

.PHONY: fmt
fmt: ## Format code
	uv run ruff check --fix --exit-zero $(SOURCE_DIRS) >/dev/null
	uv run ruff format $(SOURCE_DIRS)

.PHONY: upgrade
upgrade: ## Upgrade dependencies
	uv sync --upgrade --all-extras --dev

.PHONY: clean
clean: ## Clean up build artifacts and caches
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +
