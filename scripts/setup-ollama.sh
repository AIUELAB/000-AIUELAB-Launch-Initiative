#!/usr/bin/env bash

# Ollama Setup Script for Claude Code Template
# Supports macOS, Linux, and WSL
# 2025年版 - 完全無料のローカルLLM統合

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q Microsoft /proc/version 2>/dev/null; then
            echo "wsl"
        else
            echo "linux"
        fi
    else
        echo "unsupported"
    fi
}

# Install Ollama based on OS
install_ollama() {
    local os_type=$1

    log_info "Installing Ollama for $os_type..."

    case $os_type in
        macos)
            if command -v brew &> /dev/null; then
                brew install ollama
            else
                curl -fsSL https://ollama.com/install.sh | sh
            fi
            ;;
        linux|wsl)
            curl -fsSL https://ollama.com/install.sh | sh
            ;;
        *)
            log_error "Unsupported OS: $os_type"
            log_info "Please install Ollama manually from: https://ollama.com/download"
            exit 1
            ;;
    esac
}

# Start Ollama service
start_ollama() {
    log_info "Starting Ollama service..."

    # Check if Ollama is already running
    if pgrep -x "ollama" > /dev/null; then
        log_info "Ollama is already running"
    else
        # Start Ollama in background
        ollama serve > /dev/null 2>&1 &
        sleep 3

        if pgrep -x "ollama" > /dev/null; then
            log_success "Ollama service started"
        else
            log_warning "Could not start Ollama service automatically"
            log_info "Please run 'ollama serve' in a separate terminal"
        fi
    fi
}

# Download recommended models
download_models() {
    log_info "Downloading recommended models..."

    # List of recommended models for different use cases
    declare -a models=(
        "llama3.2:3b"      # Small, fast, good for code
        "mistral:7b"       # Balanced performance
        "deepseek-r1:1.5b" # Very small, fast responses
        "codellama:7b"     # Specialized for code
    )

    for model in "${models[@]}"; do
        log_info "Pulling $model..."
        if ollama pull "$model"; then
            log_success "Downloaded $model"
        else
            log_warning "Failed to download $model (may already exist)"
        fi
    done
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python Ollama integration..."

    # Check if in virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_warning "Not in a virtual environment. Activating venv..."
        if [[ -f "$PROJECT_ROOT/venv/bin/activate" ]]; then
            source "$PROJECT_ROOT/venv/bin/activate"
        else
            log_error "Virtual environment not found. Please create one first."
            exit 1
        fi
    fi

    # Install Ollama Python packages
    pip install ollama langchain-ollama llama-index-llms-ollama -q

    log_success "Python dependencies installed"
}

# Create Ollama integration script
create_integration_script() {
    log_info "Creating Ollama integration module..."

    cat > "$PROJECT_ROOT/src/ollama_integration.py" << 'EOF'
"""
Ollama Integration for Claude Code Template
完全無料のローカルLLM統合
"""

import os
from typing import Optional, List, Dict, Any
import ollama
from langchain_ollama import OllamaLLM, ChatOllama
from llama_index.llms.ollama import Ollama as LlamaIndexOllama


class OllamaManager:
    """Ollama LLM Manager for local inference"""

    def __init__(self, model: str = "llama3.2:3b"):
        self.model = model
        self.client = ollama.Client()
        self.langchain_llm = OllamaLLM(model=model)
        self.langchain_chat = ChatOllama(model=model)
        self.llamaindex_llm = LlamaIndexOllama(model=model)

    def chat(self, prompt: str, system: Optional[str] = None) -> str:
        """Simple chat interface"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat(
            model=self.model,
            messages=messages
        )
        return response["message"]["content"]

    def stream_chat(self, prompt: str, system: Optional[str] = None):
        """Streaming chat interface"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat(
            model=self.model,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            yield chunk["message"]["content"]

    def generate(self, prompt: str) -> str:
        """Simple generation interface"""
        response = self.client.generate(
            model=self.model,
            prompt=prompt
        )
        return response["response"]

    def list_models(self) -> List[Dict[str, Any]]:
        """List available models"""
        return self.client.list()["models"]

    def pull_model(self, model_name: str):
        """Download a new model"""
        return self.client.pull(model_name)

    def embeddings(self, text: str) -> List[float]:
        """Generate embeddings"""
        response = self.client.embeddings(
            model=self.model,
            prompt=text
        )
        return response["embedding"]


# Example usage functions
def code_review(code: str, model: str = "codellama:7b") -> str:
    """Use Ollama for code review"""
    manager = OllamaManager(model)
    system = "You are an expert code reviewer. Analyze the code for bugs, performance issues, and best practices."
    prompt = f"Review this code:\n\n{code}"
    return manager.chat(prompt, system)


def explain_code(code: str, model: str = "llama3.2:3b") -> str:
    """Use Ollama to explain code"""
    manager = OllamaManager(model)
    system = "You are a helpful programming tutor. Explain code clearly and concisely."
    prompt = f"Explain this code:\n\n{code}"
    return manager.chat(prompt, system)


def generate_tests(code: str, model: str = "codellama:7b") -> str:
    """Generate unit tests for code"""
    manager = OllamaManager(model)
    system = "You are an expert at writing comprehensive unit tests. Generate pytest tests."
    prompt = f"Write unit tests for this code:\n\n{code}"
    return manager.chat(prompt, system)


def refactor_code(code: str, model: str = "codellama:7b") -> str:
    """Suggest refactoring for code"""
    manager = OllamaManager(model)
    system = "You are an expert at code refactoring. Suggest improvements for clarity, performance, and maintainability."
    prompt = f"Refactor this code:\n\n{code}"
    return manager.chat(prompt, system)


if __name__ == "__main__":
    # Test the integration
    print("Testing Ollama integration...")

    manager = OllamaManager()

    # List available models
    print("\nAvailable models:")
    for model in manager.list_models():
        print(f"  - {model['name']}")

    # Simple test
    response = manager.chat("Write a Python function to calculate factorial")
    print(f"\nTest response:\n{response}")

    print("\nOllama integration is working!")
EOF

    log_success "Integration script created"
}

# Create example configuration
create_config() {
    log_info "Creating Ollama configuration..."

    cat > "$PROJECT_ROOT/.ollama.yml" << 'EOF'
# Ollama Configuration for Claude Code Template

# Default model for different tasks
models:
  chat: llama3.2:3b
  code: codellama:7b
  analysis: mistral:7b
  fast: deepseek-r1:1.5b

# Model parameters
parameters:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 2048
  seed: 42

# System prompts for different use cases
prompts:
  code_review: |
    You are an expert code reviewer. Focus on:
    - Security vulnerabilities
    - Performance issues
    - Code quality and best practices
    - Potential bugs

  documentation: |
    You are a technical documentation expert.
    Write clear, concise, and accurate documentation.

  testing: |
    You are a testing expert. Generate comprehensive test cases
    including edge cases and error scenarios.

  refactoring: |
    You are a refactoring expert. Suggest improvements for:
    - Code clarity and readability
    - Performance optimization
    - Design patterns and architecture

# Performance settings
performance:
  num_threads: 8
  num_gpu: 1  # Set to 0 if no GPU
  batch_size: 512
EOF

    log_success "Configuration created"
}

# Main execution
main() {
    log_info "Starting Ollama setup for Claude Code Template..."

    # Detect OS
    OS_TYPE=$(detect_os)
    log_info "Detected OS: $OS_TYPE"

    # Check if Ollama is installed
    if command -v ollama &> /dev/null; then
        log_info "Ollama is already installed"
    else
        install_ollama "$OS_TYPE"
    fi

    # Start Ollama service
    start_ollama

    # Download models
    read -p "Download recommended models? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        download_models
    fi

    # Install Python dependencies
    install_python_deps

    # Create integration script
    create_integration_script

    # Create configuration
    create_config

    log_success "Ollama setup completed!"
    log_info "You can now use Ollama in your Python code:"
    echo "  from ollama_integration import OllamaManager"
    echo "  manager = OllamaManager()"
    echo "  response = manager.chat('Hello!')"
    echo ""
    log_info "To test the integration, run:"
    echo "  python src/ollama_integration.py"
}

# Run main function
main "$@"
