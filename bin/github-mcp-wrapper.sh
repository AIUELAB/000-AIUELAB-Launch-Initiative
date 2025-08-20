#!/bin/bash
# Wrapper script for GitHub MCP server that ensures PAT is set

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    # shellcheck disable=SC2046
    export "$(grep -v '^#' .env | xargs)"
fi

# Set the GitHub PAT
export GITHUB_PERSONAL_ACCESS_TOKEN="${GITHUB_PAT:-${GITHUB_PERSONAL_ACCESS_TOKEN}}"

# Run the actual server
exec "$(dirname "$0")/github-mcp-server" "$@"
