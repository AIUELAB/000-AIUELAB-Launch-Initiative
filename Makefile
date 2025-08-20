# Makefile for Claude Code Template MCP
# 2025年版 - 最適化された開発コマンド

.PHONY: help
help: ## Show this help message
	@echo "Usage: make [target]"
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: install
install: ## Install all dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

.PHONY: format
format: ## Format code with Ruff
	ruff format src tests

.PHONY: lint
lint: ## Lint code with Ruff
	ruff check src tests --fix

.PHONY: type
type: ## Type check with mypy
	mypy src

.PHONY: test
test: ## Run tests
	pytest tests -v

.PHONY: coverage
coverage: ## Run tests with coverage
	pytest tests --cov=src --cov-report=html --cov-report=term

.PHONY: security
security: ## Run security checks
	bandit -r src/
	pip-audit
	safety check

.PHONY: pre-commit
pre-commit: ## Run all pre-commit hooks
	pre-commit run --all-files

.PHONY: clean
clean: ## Clean build artifacts
	rm -rf build dist *.egg-info
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -rf htmlcov .coverage
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

.PHONY: docs
docs: ## Serve documentation locally
	mkdocs serve

.PHONY: docs-build
docs-build: ## Build documentation
	mkdocs build

.PHONY: ollama
ollama: ## Setup Ollama integration
	./scripts/setup-ollama.sh

.PHONY: ollama-test
ollama-test: ## Test Ollama integration
	python src/ollama_integration.py

.PHONY: all
all: format lint type test ## Run all checks

.PHONY: ci
ci: lint type test security ## Run CI checks
