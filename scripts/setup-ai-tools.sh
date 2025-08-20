#!/bin/bash

# Setup script for free AI coding tools
# Compatible with Claude Code Template MCP

set -e

echo "🤖 Setting up AI Coding Tools..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_info() { echo -e "${YELLOW}ℹ${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }

# Check Python version
if ! python3 --version | grep -E "3\.(1[0-2]|9)" > /dev/null; then
    print_error "Python 3.9+ required"
    exit 1
fi

# Install Aider - AI pair programming tool
install_aider() {
    print_info "Installing Aider AI pair programming tool..."
    pip install aider-chat
    print_success "Aider installed successfully"

    # Create aider config
    cat > .aider.conf.yml << 'EOF'
# Aider configuration
model: gpt-4-turbo-preview
auto-commits: false
dirty-commits: false
pretty: true
stream: true
show-diffs: true
# Use with: aider --config .aider.conf.yml
EOF
    print_success "Aider configuration created"
}

# Install Code2prompt - Convert codebase to LLM prompts
install_code2prompt() {
    print_info "Installing code2prompt..."
    pip install code2prompt
    print_success "code2prompt installed"
}

# Install LLM CLI tool
install_llm() {
    print_info "Installing LLM CLI tool..."
    pip install llm
    print_success "LLM CLI installed"
}

# Setup SonarQube Docker Compose (Community Edition - Free)
setup_sonarqube() {
    print_info "Creating SonarQube docker-compose configuration..."
    cat > docker-compose.sonarqube.yml << 'EOF'
version: "3"

services:
  sonarqube:
    image: sonarqube:community
    container_name: sonarqube
    ports:
      - "9000:9000"
    environment:
      - SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true
    volumes:
      - sonarqube_data:/opt/sonarqube/data
      - sonarqube_extensions:/opt/sonarqube/extensions
      - sonarqube_logs:/opt/sonarqube/logs

volumes:
  sonarqube_data:
  sonarqube_extensions:
  sonarqube_logs:
EOF
    print_success "SonarQube configuration created"
    print_info "Run 'docker-compose -f docker-compose.sonarqube.yml up -d' to start SonarQube"
}

# Install DeepSource CLI (free for open source)
install_deepsource() {
    print_info "Installing DeepSource CLI..."
    curl https://deepsource.io/cli | sh || print_error "DeepSource installation failed (optional)"
}

# Main installation
main() {
    echo "════════════════════════════════════════════════════════"
    echo "        AI Coding Tools Installation"
    echo "════════════════════════════════════════════════════════"
    echo ""

    # Check if virtual environment is active
    if [ -z "$VIRTUAL_ENV" ]; then
        print_info "Activating virtual environment..."
        source venv/bin/activate || {
            print_error "Virtual environment not found. Please create it first."
            exit 1
        }
    fi

    # Install tools
    install_aider
    install_code2prompt
    install_llm
    setup_sonarqube
    install_deepsource

    echo ""
    echo "════════════════════════════════════════════════════════"
    print_success "AI Tools Setup Complete! 🎉"
    echo ""
    echo "Installed tools:"
    echo "  • Aider - AI pair programming (use: aider)"
    echo "  • code2prompt - Convert code to LLM prompts"
    echo "  • LLM CLI - Command-line LLM tool"
    echo "  • SonarQube - Code quality platform (docker-compose)"
    echo "  • DeepSource CLI - Code analysis (if available)"
    echo ""
    echo "Next steps:"
    echo "  1. Set your OpenAI API key: export OPENAI_API_KEY='your-key'"
    echo "  2. Start coding with Aider: aider <file>"
    echo "  3. Start SonarQube: docker-compose -f docker-compose.sonarqube.yml up -d"
    echo ""
    echo "════════════════════════════════════════════════════════"
}

# Run main function
main "$@"
