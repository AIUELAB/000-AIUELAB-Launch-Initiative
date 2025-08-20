#!/bin/bash

# Docker entrypoint for Claude Code isolated environment

set -e

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Claude Code Docker Environment${NC}"
echo "==============================="

# Check for required environment variables
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$CLAUDE_API_KEY" ]; then
    echo -e "${YELLOW}Warning: No API key found. Set ANTHROPIC_API_KEY or CLAUDE_API_KEY${NC}"
fi

# Set up environment from mounted .env.mcp if exists
if [ -f "/workspace/.env.mcp" ]; then
    echo "Loading environment from .env.mcp..."
    # shellcheck disable=SC2046
    export "$(grep -v '^#' /workspace/.env.mcp | xargs)"
fi

# Create MCP config if not exists
if [ ! -f "$HOME/.config/claude/claude_desktop_config.json" ]; then
    echo "Setting up MCP configuration..."
    mkdir -p $HOME/.config/claude

    # Create minimal MCP config
    cat > $HOME/.config/claude/claude_desktop_config.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "/workspace"]
    }
  }
}
EOF
fi

# Handle special flags
CLAUDE_FLAGS=""

# Check for --dangerously-skip-permissions
for arg in "$@"; do
    if [ "$arg" = "--dangerously-skip-permissions" ] || [ "$arg" = "--yolo" ]; then
        echo -e "${YELLOW}Running with --dangerously-skip-permissions${NC}"
        echo "Container isolation provides safety for unrestricted operations"
        CLAUDE_FLAGS="$CLAUDE_FLAGS --dangerously-skip-permissions"
        break
    fi
done

# Check for headless mode
for arg in "$@"; do
    if [ "$arg" = "-p" ] || [ "$arg" = "--prompt" ]; then
        echo "Running in headless mode..."
        CLAUDE_FLAGS="$CLAUDE_FLAGS --no-interactive"
        break
    fi
done

# Execute command
if [ "$1" = "claude" ]; then
    shift
    exec claude $CLAUDE_FLAGS "$@"
else
    exec "$@"
fi
