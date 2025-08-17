#!/bin/bash

# GitHub MCP Server Native Setup Script
# This script downloads and installs the GitHub MCP Server binary

set -e

echo "🚀 GitHub MCP Server Native Setup"
echo "================================="

# Detect OS and architecture
OS=$(uname -s)
ARCH=$(uname -m)

# Map architecture names
if [ "$ARCH" = "x86_64" ]; then
    ARCH_NAME="x86_64"
elif [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; then
    ARCH_NAME="arm64"
else
    echo "❌ Unsupported architecture: $ARCH"
    exit 1
fi

# Map OS names
if [ "$OS" = "Darwin" ]; then
    OS_NAME="Darwin"
    EXT="tar.gz"
elif [ "$OS" = "Linux" ]; then
    OS_NAME="Linux"
    EXT="tar.gz"
else
    echo "❌ Unsupported OS: $OS"
    exit 1
fi

# GitHub MCP Server version
VERSION="v0.12.1"
BINARY_NAME="github-mcp-server_${OS_NAME}_${ARCH_NAME}.${EXT}"
DOWNLOAD_URL="https://github.com/github/github-mcp-server/releases/download/${VERSION}/${BINARY_NAME}"

echo "📦 Downloading GitHub MCP Server ${VERSION} for ${OS_NAME} ${ARCH_NAME}..."

# Create bin directory if it doesn't exist
mkdir -p bin

# Download and extract
cd bin
curl -L -o github-mcp-server.tar.gz "$DOWNLOAD_URL"

echo "📂 Extracting binary..."
tar -xzf github-mcp-server.tar.gz

# Make executable
chmod +x github-mcp-server

# Clean up
rm github-mcp-server.tar.gz

# Verify installation
echo "✅ Verifying installation..."
cd ..
./bin/github-mcp-server --version

echo ""
echo "✨ GitHub MCP Server installed successfully!"
echo ""
echo "Next steps:"
echo "1. Ensure your .env file contains GITHUB_PAT"
echo "2. Run: python test_github_mcp.py"
echo "3. Or use: python src/github_mcp_integration.py"
