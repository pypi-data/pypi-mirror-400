# MCP TAXII Makefile
# Development and CI automation commands

.PHONY: help install sync lint format check test tests test-unit test-integration \
        test-server test-server-stop test-server-logs test-server-status \
        run clean ci coverage build publish-test publish

# Default target
.DEFAULT_GOAL := help

# Variables
PYTHON := uv run python
PYTEST := uv run pytest
RUFF := uv run ruff
TEST_SERVER_PORT := 8000
TEST_SERVER_PID_FILE := .test-server.pid

# Colors for output
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

##@ General

help: ## Show this help message
	@awk 'BEGIN {FS = ":.*##"; printf "\n$(CYAN)Usage:$(RESET)\n  make $(GREEN)<target>$(RESET)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2 } /^##@/ { printf "\n$(YELLOW)%s$(RESET)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Dependencies

install: ## Install all dependencies (including dev)
	uv sync --extra dev --extra test-server

sync: ## Sync dependencies
	uv sync

deps: install ## Alias for install

##@ Code Quality

lint: ## Run linting checks
	$(RUFF) check src/ tests/

lint-fix: ## Run linting and auto-fix issues
	$(RUFF) check --fix src/ tests/

format: ## Format code with ruff
	$(RUFF) format src/ tests/

format-check: ## Check code formatting without changes
	$(RUFF) format --check src/ tests/

check: lint format-check ## Run all code quality checks (lint + format)
	@echo "$(GREEN)All checks passed!$(RESET)"

##@ Testing

test: ## Run all unit tests
	$(PYTEST) tests/test_server.py -v

tests: test ## Alias for test

test-unit: test ## Run unit tests only

test-cov: ## Run tests with coverage report
	$(PYTEST) tests/test_server.py -v --cov=src --cov-report=term-missing --cov-report=html
	@echo "$(GREEN)Coverage report generated in htmlcov/$(RESET)"

coverage: test-cov ## Alias for test-cov

test-integration: test-server-start ## Run integration tests (starts test server)
	@echo "$(CYAN)Waiting for test server to start...$(RESET)"
	@sleep 2
	$(PYTEST) tests/test_integration.py -v || (make test-server-stop && exit 1)
	@make test-server-stop

test-all: ## Run all tests (unit + integration)
	@make test
	@make test-integration

##@ Test Server

test-server: ## Start TAXII test server (foreground)
	$(PYTHON) dev/taxii_test_server/run_server.py --port $(TEST_SERVER_PORT)

test-server-start: ## Start TAXII test server (background)
	@if [ -f $(TEST_SERVER_PID_FILE) ] && kill -0 $$(cat $(TEST_SERVER_PID_FILE)) 2>/dev/null; then \
		echo "$(YELLOW)Test server already running (PID: $$(cat $(TEST_SERVER_PID_FILE)))$(RESET)"; \
	else \
		echo "$(CYAN)Starting test server on port $(TEST_SERVER_PORT)...$(RESET)"; \
		$(PYTHON) dev/taxii_test_server/run_server.py --port $(TEST_SERVER_PORT) --no-reload > .test-server.log 2>&1 & \
		echo $$! > $(TEST_SERVER_PID_FILE); \
		echo "$(GREEN)Test server started (PID: $$(cat $(TEST_SERVER_PID_FILE)))$(RESET)"; \
	fi

test-server-stop: ## Stop TAXII test server
	@if [ -f $(TEST_SERVER_PID_FILE) ]; then \
		PID=$$(cat $(TEST_SERVER_PID_FILE)); \
		if kill -0 $$PID 2>/dev/null; then \
			echo "$(CYAN)Stopping test server (PID: $$PID)...$(RESET)"; \
			kill $$PID 2>/dev/null || true; \
			sleep 1; \
			kill -9 $$PID 2>/dev/null || true; \
			echo "$(GREEN)Test server stopped$(RESET)"; \
		else \
			echo "$(YELLOW)Test server not running$(RESET)"; \
		fi; \
		rm -f $(TEST_SERVER_PID_FILE); \
	else \
		echo "$(YELLOW)No PID file found$(RESET)"; \
	fi

test-server-status: ## Check test server status
	@if [ -f $(TEST_SERVER_PID_FILE) ] && kill -0 $$(cat $(TEST_SERVER_PID_FILE)) 2>/dev/null; then \
		echo "$(GREEN)Test server is running (PID: $$(cat $(TEST_SERVER_PID_FILE)))$(RESET)"; \
		echo "$(CYAN)URL: http://localhost:$(TEST_SERVER_PORT)/taxii21/$(RESET)"; \
	else \
		echo "$(RED)Test server is not running$(RESET)"; \
	fi

test-server-logs: ## Show test server logs
	@if [ -f .test-server.log ]; then \
		tail -f .test-server.log; \
	else \
		echo "$(YELLOW)No log file found. Start test server first.$(RESET)"; \
	fi

##@ Running

run: ## Run the MCP TAXII server
	$(PYTHON) -m mcp_taxii.server

##@ CI Commands

ci: install check test ## Run full CI pipeline (install, check, test)
	@echo "$(GREEN)CI pipeline completed successfully!$(RESET)"

ci-test: ## Run tests for CI (with XML coverage output)
	$(PYTEST) tests/test_server.py -v --cov=src --cov-report=xml --cov-report=term-missing

ci-integration: ## Run integration tests for CI
	@make test-server-start
	@sleep 3
	@$(PYTEST) tests/test_integration.py -v --cov=src --cov-report=xml --cov-report=term-missing --cov-append || (make test-server-stop && exit 1)
	@make test-server-stop

ci-full: install check ci-test ## Run full CI with coverage
	@echo "$(GREEN)Full CI completed successfully!$(RESET)"

##@ Cleanup

clean: test-server-stop ## Clean up generated files
	rm -rf .pytest_cache __pycache__ .coverage htmlcov coverage.xml
	rm -rf src/**/__pycache__ tests/__pycache__
	rm -rf .ruff_cache .test-server.log $(TEST_SERVER_PID_FILE)
	rm -rf dist build *.egg-info
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleaned up generated files$(RESET)"

clean-all: clean ## Deep clean (including .venv)
	rm -rf .venv uv.lock
	@echo "$(GREEN)Deep clean completed$(RESET)"

##@ Build & Publish

build: clean ## Build package for distribution
	uv build
	@echo "$(GREEN)Package built successfully!$(RESET)"
	@echo "$(CYAN)Distribution files:$(RESET)"
	@ls -la dist/

publish-test: build ## Publish to TestPyPI
	uv publish --publish-url https://test.pypi.org/legacy/
	@echo "$(GREEN)Published to TestPyPI!$(RESET)"
	@echo "$(CYAN)Install with: pip install -i https://test.pypi.org/simple/ mcp-taxii$(RESET)"

publish: build ## Publish to PyPI (requires confirmation)
	@echo "$(RED)WARNING: This will publish to PyPI!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || (echo "Aborted." && exit 1)
	uv publish
	@echo "$(GREEN)Published to PyPI!$(RESET)"
	@echo "$(CYAN)Install with: pip install mcp-taxii$(RESET)"

version: ## Show current version
	@grep "^version" pyproject.toml | head -1
