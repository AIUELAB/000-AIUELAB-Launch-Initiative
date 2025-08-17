# Makefile for Claude Code MCP Template
# 2025年最新ベストプラクティス対応

.PHONY: help setup install clean test lint format type-check coverage pre-commit run docker-build docker-run check-env load-keys validate-mcp

# デフォルトターゲット
.DEFAULT_GOAL := help

# 変数
PYTHON := python3
PIP := $(PYTHON) -m pip
VENV := venv
VENV_ACTIVATE := . $(VENV)/bin/activate

# カラー出力
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

help: ## このヘルプメッセージを表示
	@echo "$(GREEN)Claude Code MCP Template - Makefile$(NC)"
	@echo "$(YELLOW)使用方法: make [ターゲット]$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

setup: ## プロジェクトの初期セットアップ（仮想環境作成、依存関係インストール）
	@echo "$(YELLOW)🚀 Setting up project...$(NC)"
	@if [ ! -d "$(VENV)" ]; then \
		echo "Creating virtual environment..."; \
		$(PYTHON) -m venv $(VENV); \
	fi
	@echo "Installing dependencies..."
	@$(VENV_ACTIVATE) && $(PIP) install --upgrade pip setuptools wheel
	@$(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	@$(VENV_ACTIVATE) && pre-commit install
	@echo "$(GREEN)✅ Setup complete!$(NC)"

install: ## 依存関係をインストール
	@echo "$(YELLOW)📦 Installing dependencies...$(NC)"
	@$(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed!$(NC)"

clean: ## 一時ファイルとキャッシュをクリーンアップ
	@echo "$(YELLOW)🧹 Cleaning up...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.pyd" -delete
	@find . -type f -name ".coverage" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".sessions" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Cleanup complete!$(NC)"

test: ## テストを実行
	@echo "$(YELLOW)🧪 Running tests...$(NC)"
	@$(VENV_ACTIVATE) && pytest tests/ -v --tb=short
	@echo "$(GREEN)✅ Tests complete!$(NC)"

lint: ## リントチェックを実行
	@echo "$(YELLOW)🔍 Running linters...$(NC)"
	@$(VENV_ACTIVATE) && ruff check src tests
	@echo "$(GREEN)✅ Linting complete!$(NC)"

format: ## コードフォーマットを実行
	@echo "$(YELLOW)✨ Formatting code...$(NC)"
	@$(VENV_ACTIVATE) && ruff format src tests
	@$(VENV_ACTIVATE) && ruff check --fix src tests
	@echo "$(GREEN)✅ Formatting complete!$(NC)"

type-check: ## 型チェックを実行
	@echo "$(YELLOW)🔍 Running type checker...$(NC)"
	@$(VENV_ACTIVATE) && mypy src --ignore-missing-imports
	@echo "$(GREEN)✅ Type checking complete!$(NC)"

coverage: ## カバレッジ付きでテストを実行
	@echo "$(YELLOW)📊 Running tests with coverage...$(NC)"
	@$(VENV_ACTIVATE) && pytest tests/ --cov=src --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Coverage report generated! Open htmlcov/index.html$(NC)"

pre-commit: ## pre-commitフックを実行
	@echo "$(YELLOW)🔒 Running pre-commit hooks...$(NC)"
	@$(VENV_ACTIVATE) && pre-commit run --all-files
	@echo "$(GREEN)✅ Pre-commit checks complete!$(NC)"

run: ## アプリケーションを実行
	@echo "$(YELLOW)🚀 Running application...$(NC)"
	@$(VENV_ACTIVATE) && $(PYTHON) src/main.py run

check-env: ## 環境をチェック
	@echo "$(YELLOW)🔍 Checking environment...$(NC)"
	@$(VENV_ACTIVATE) && $(PYTHON) src/main.py check-env

load-keys: ## APIキーをロード
	@echo "$(YELLOW)🔑 Loading API keys...$(NC)"
	@./scripts/load-keys.sh --auto
	@echo "$(GREEN)✅ API keys loaded!$(NC)"

validate-mcp: ## MCP設定を検証
	@echo "$(YELLOW)🔍 Validating MCP configuration...$(NC)"
	@$(VENV_ACTIVATE) && $(PYTHON) scripts/validate_mcp_config.py

all: clean setup format lint type-check test ## 全てのチェックを実行
	@echo "$(GREEN)✅ All checks complete!$(NC)"

summary: ## プロジェクトサマリーを表示
	@./scripts/display-summary.sh
