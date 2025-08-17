#!/bin/bash
# UV Package Manager Setup Script
# 2025年最新 - Rust製高速パッケージマネージャー

set -e

echo "🚀 UV Package Manager Setup"
echo "=========================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "✅ uv installed successfully"
else
    echo "✅ uv is already installed ($(uv --version))"
fi

# Create virtual environment with uv
echo ""
echo "🔧 Creating virtual environment with uv..."
if [ -d ".venv" ]; then
    echo "⚠️  Virtual environment already exists. Removing..."
    rm -rf .venv
fi

uv venv --python 3.11
echo "✅ Virtual environment created"

# Sync dependencies from pyproject.toml
echo ""
echo "📚 Installing dependencies..."
uv pip sync pyproject.toml

# Install development dependencies
echo ""
echo "🛠️  Installing development dependencies..."
uv pip install -e ".[dev]"

# Install beartype specifically
echo ""
echo "🐻 Installing Beartype for runtime type checking..."
uv pip install beartype

# Install security tools
echo ""
echo "🔐 Installing security tools..."
uv pip install semgrep safety

# Verify installations
echo ""
echo "✅ Verification:"
echo "  - uv version: $(uv --version)"
echo "  - Python: $(uv run python --version)"
echo "  - Beartype: $(uv run python -c 'import beartype; print(beartype.__version__)')"

echo ""
echo "🎉 UV setup complete!"
echo ""
echo "Usage:"
echo "  Activate environment: source .venv/bin/activate"
echo "  Install package: uv pip install <package>"
echo "  Sync dependencies: uv pip sync pyproject.toml"
echo "  Run with uv: uv run python script.py"
