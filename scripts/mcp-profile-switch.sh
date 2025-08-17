#!/bin/bash

# MCP Profile Switcher
# Switch between different MCP server configurations

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Project paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCP_CONFIG_DIR="$PROJECT_ROOT/mcp-config"
PROFILES_DIR="$MCP_CONFIG_DIR/profiles"
CLAUDE_CONFIG="$HOME/.config/claude/claude_desktop_config.json"

# Function to display usage
usage() {
    echo -e "${BLUE}MCP Profile Switcher${NC}"
    echo -e "Usage: $0 [profile]"
    echo -e "\nAvailable profiles:"
    echo -e "  ${GREEN}minimal${NC}  - Minimal setup (Serena only)"
    echo -e "  ${GREEN}standard${NC} - Standard development setup"
    echo -e "  ${GREEN}full${NC}     - Full setup with all servers"
    echo -e "\nExample: $0 minimal"
    exit 1
}

# Function to list available profiles
list_profiles() {
    echo -e "${BLUE}Available MCP Profiles:${NC}"
    for profile in "$PROFILES_DIR"/*.json; do
        if [ -f "$profile" ]; then
            name=$(basename "$profile" .json)
            desc=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$profile" | sed 's/.*: *"\(.*\)"/\1/')
            echo -e "  ${GREEN}$name${NC} - $desc"
        fi
    done
}

# Function to switch profile
switch_profile() {
    local profile=$1
    local profile_file="$PROFILES_DIR/${profile}.json"
    
    if [ ! -f "$profile_file" ]; then
        echo -e "${RED}Error: Profile '$profile' not found${NC}"
        list_profiles
        exit 1
    fi
    
    # Backup current configuration
    if [ -f "$CLAUDE_CONFIG" ]; then
        cp "$CLAUDE_CONFIG" "${CLAUDE_CONFIG}.backup"
        echo -e "${BLUE}Backed up current configuration${NC}"
    fi
    
    # Copy new profile
    cp "$profile_file" "$CLAUDE_CONFIG"
    echo -e "${GREEN}✓ Switched to '$profile' profile${NC}"
    
    # Show profile details
    desc=$(grep -o '"description"[[:space:]]*:[[:space:]]*"[^"]*"' "$profile_file" | sed 's/.*: *"\(.*\)"/\1/')
    echo -e "${BLUE}Profile: ${NC}$desc"
    
    # Count active servers
    server_count=$(grep -c '"command"' "$profile_file" || true)
    echo -e "${BLUE}Active servers: ${NC}$server_count"
    
    echo -e "\n${YELLOW}Please restart Claude Code for changes to take effect${NC}"
}

# Main execution
if [ $# -eq 0 ]; then
    list_profiles
    echo ""
    usage
fi

case "$1" in
    list|--list|-l)
        list_profiles
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        switch_profile "$1"
        ;;
esac