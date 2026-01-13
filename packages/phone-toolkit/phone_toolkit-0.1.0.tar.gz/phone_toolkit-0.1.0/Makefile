# Makefile for phone-toolkit project
# Supports both uv (recommended) and pip

.PHONY: help install install-dev test lint format type-check clean build publish-test publish

# Detect if uv is available
UV := $(shell command -v uv 2> /dev/null)

# Detect virtual environment and set Python/tool paths
VENV_EXISTS := $(shell [ -d .venv ] && echo 1 || echo 0)
ifeq ($(VENV_EXISTS),1)
    VENV_BIN := .venv/bin
    PYTHON := $(VENV_BIN)/python
    PYTEST := $(VENV_BIN)/pytest
    RUFF := $(VENV_BIN)/ruff
    MYPY := $(VENV_BIN)/mypy
    TWINE := $(VENV_BIN)/twine
else
    PYTHON := python
    PYTEST := pytest
    RUFF := ruff
    MYPY := mypy
    TWINE := twine
endif

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

install: ## Install package (runtime dependencies only)
ifdef UV
	@echo "Using uv..."
	uv pip install -e .
else
	@echo "Using pip..."
	pip install -e .
endif

install-dev: ## Install package with dev dependencies
ifdef UV
	@echo "Using uv..."
	uv pip install -e ".[dev]"
else
	@echo "Using pip..."
	pip install -e ".[dev]"
endif

test: ## Run tests with coverage
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PYTEST) --cov=phone_parser --cov-report=term-missing --cov-report=html

test-quick: ## Run tests without coverage
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(PYTEST) -v

lint: ## Run linter
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(RUFF) check src tests

lint-fix: ## Run linter with auto-fix
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(RUFF) check --fix src tests

format: ## Format code
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(RUFF) format src tests

format-check: ## Check code formatting
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(RUFF) format --check src tests

type-check: ## Run type checker
	@if [ $(VENV_EXISTS) -eq 0 ]; then \
		echo "❌ Virtual environment not found. Run 'make setup' first."; \
		exit 1; \
	fi
	$(MYPY) src

qa: lint format-check type-check test ## Run all quality checks

clean: ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
ifdef UV
	uv pip install build
else
	pip install build
endif
	$(PYTHON) -m build

publish-test: build ## Publish to TestPyPI
ifdef UV
	uv pip install twine
else
	pip install twine
endif
	$(TWINE) check dist/*
	$(TWINE) upload --repository testpypi dist/*

publish: build ## Publish to PyPI
ifdef UV
	uv pip install twine
else
	pip install twine
endif
	$(TWINE) check dist/*
	$(TWINE) upload dist/*

venv: ## Create virtual environment using uv (if available) or venv
ifdef UV
	@echo "Creating virtual environment with uv..."
	uv venv
else
	@echo "Creating virtual environment with venv..."
	python -m venv .venv
endif
	@echo "Activate with: source .venv/bin/activate"

setup: venv install-dev ## Full setup: create venv and install dependencies
	@echo "Setup complete! Don't forget to activate: source .venv/bin/activate"

.DEFAULT_GOAL := help
