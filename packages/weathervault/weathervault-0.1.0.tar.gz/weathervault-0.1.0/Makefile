# Python command - uses venv if available, otherwise system python
VENV_PYTHON := .venv/bin/python
PYTHON := $(shell if [ -f $(VENV_PYTHON) ]; then echo $(VENV_PYTHON); else command -v python3 2> /dev/null || command -v python 2> /dev/null; fi)

.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: test
test: ## Run tests with pytest
	@$(PYTHON) -m pytest tests/ -v

.PHONY: test-offline
test-offline: ## Run only offline tests (no network required)
	@$(PYTHON) -m pytest tests/ -v -m "not network"

.PHONY: test-network
test-network: ## Run only network tests
	@$(PYTHON) -m pytest tests/ -v -m "network"

.PHONY: test-coverage
test-coverage: ## Run tests with coverage report
	@$(PYTHON) -m pytest \
		--cov=weathervault \
		--cov-report=term-missing \
		--cov-report=html \
		tests/ -v

.PHONY: test-verbose
test-verbose: ## Run tests with verbose output
	@$(PYTHON) -m pytest tests/ -vv

.PHONY: lint
lint: ## Run ruff formatter and linter
	@$(PYTHON) -m ruff format
	@$(PYTHON) -m ruff check --fix

.PHONY: format
format: ## Format code with ruff
	@$(PYTHON) -m ruff format

.PHONY: check-format
check-format: ## Check code formatting without making changes
	@$(PYTHON) -m ruff format --check
	@$(PYTHON) -m ruff check

.PHONY: check
check: lint test ## Run all checks (lint and test)

.PHONY: clean
clean: clean-build clean-pyc clean-test ## Remove all build, test, coverage and Python artifacts

.PHONY: clean-build
clean-build: ## Remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

.PHONY: clean-pyc
clean-pyc: ## Remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: clean-test
clean-test: ## Remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .ruff_cache/

.PHONY: clean-cache
clean-cache: ## Remove downloaded weather data cache
	rm -fr weather_cache/
	find . -name '*.gz' -exec rm -f {} +

.PHONY: build
build: clean ## Build source and wheel distribution
	@$(PYTHON) -m build

.PHONY: dist
dist: build ## Alias for build

.PHONY: install
install: ## Install the package in editable mode
	@pip install -e .

.PHONY: install-dev
install-dev: ## Install package with development dependencies
	@pip install -e ".[dev]"

.PHONY: uninstall
uninstall: ## Uninstall the package
	@pip uninstall -y weathervault

.PHONY: reinstall
reinstall: uninstall install ## Reinstall the package

.PHONY: dev-setup
dev-setup: ## Set up development environment
	@python3 -m venv .venv
	@.venv/bin/pip install -e ".[dev]"
	@echo "Development environment ready. Activate with: source .venv/bin/activate"
