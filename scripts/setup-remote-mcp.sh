#!/bin/bash

# Setup script for Remote MCP Servers
# Configures OAuth tokens and remote server connections

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCP_CONFIG_DIR="$PROJECT_ROOT/mcp-config"
ENV_FILE="$PROJECT_ROOT/.env.mcp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}                     Remote MCP Server Setup                                     ${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to add or update environment variable
update_env_var() {
    local key=$1
    local value=$2
    local env_file=$3
    
    if grep -q "^${key}=" "$env_file"; then
        # Update existing variable
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^${key}=.*|${key}=${value}|" "$env_file"
        else
            sed -i "s|^${key}=.*|${key}=${value}|" "$env_file"
        fi
    else
        # Add new variable
        echo "${key}=${value}" >> "$env_file"
    fi
}

# Check for Claude Code installation
echo -e "\n${YELLOW}Checking Claude Code installation...${NC}"
if command_exists claude; then
    echo -e "${GREEN}✓ Claude Code is installed${NC}"
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo -e "  Version: $CLAUDE_VERSION"
else
    echo -e "${RED}✗ Claude Code is not installed${NC}"
    echo -e "  Please install Claude Code first: https://claude.ai/download"
    exit 1
fi

# Create .env.mcp if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    echo -e "\n${YELLOW}Creating .env.mcp file...${NC}"
    cp "$MCP_CONFIG_DIR/.env.mcp.example" "$ENV_FILE"
    echo -e "${GREEN}✓ Created .env.mcp${NC}"
fi

# Menu for server selection
echo -e "\n${YELLOW}Select remote MCP servers to configure:${NC}"
echo "1) Linear (Issue tracking)"
echo "2) Notion (Knowledge base)"
echo "3) Sentry (Error monitoring)"
echo "4) Apidog (API documentation)"
echo "5) SimpleScraper (Web scraping)"
echo "6) Custom server"
echo "7) Configure all"
echo "0) Exit"

read -p "Enter your choice (0-7): " choice

configure_linear() {
    echo -e "\n${BLUE}Configuring Linear...${NC}"
    echo "Get your API key from: https://linear.app/settings/api"
    read -p "Enter Linear API Key: " linear_key
    if [ ! -z "$linear_key" ]; then
        update_env_var "LINEAR_API_KEY" "$linear_key" "$ENV_FILE"
        echo -e "${GREEN}✓ Linear configured${NC}"
    fi
}

configure_notion() {
    echo -e "\n${BLUE}Configuring Notion...${NC}"
    echo "Create an integration at: https://www.notion.so/my-integrations"
    read -p "Enter Notion Client ID: " notion_id
    read -p "Enter Notion Client Secret: " notion_secret
    if [ ! -z "$notion_id" ] && [ ! -z "$notion_secret" ]; then
        update_env_var "NOTION_CLIENT_ID" "$notion_id" "$ENV_FILE"
        update_env_var "NOTION_CLIENT_SECRET" "$notion_secret" "$ENV_FILE"
        echo -e "${GREEN}✓ Notion configured${NC}"
    fi
}

configure_sentry() {
    echo -e "\n${BLUE}Configuring Sentry...${NC}"
    echo "Get your auth token from: https://sentry.io/settings/account/api/auth-tokens/"
    read -p "Enter Sentry Auth Token: " sentry_token
    if [ ! -z "$sentry_token" ]; then
        update_env_var "SENTRY_AUTH_TOKEN" "$sentry_token" "$ENV_FILE"
        echo -e "${GREEN}✓ Sentry configured${NC}"
    fi
}

configure_apidog() {
    echo -e "\n${BLUE}Configuring Apidog...${NC}"
    echo "Get your API key from your Apidog account settings"
    read -p "Enter Apidog API Key: " apidog_key
    if [ ! -z "$apidog_key" ]; then
        update_env_var "APIDOG_API_KEY" "$apidog_key" "$ENV_FILE"
        echo -e "${GREEN}✓ Apidog configured${NC}"
    fi
}

configure_simplescraper() {
    echo -e "\n${BLUE}Configuring SimpleScraper...${NC}"
    echo "Get your API key from: https://simplescraper.io/account/api"
    read -p "Enter SimpleScraper API Key: " scraper_key
    if [ ! -z "$scraper_key" ]; then
        update_env_var "SIMPLESCRAPER_API_KEY" "$scraper_key" "$ENV_FILE"
        echo -e "${GREEN}✓ SimpleScraper configured${NC}"
    fi
}

configure_custom() {
    echo -e "\n${BLUE}Configuring Custom Server...${NC}"
    read -p "Enter Custom MCP URL: " custom_url
    read -p "Enter Custom API Key: " custom_key
    read -p "Enter Custom Client ID: " custom_id
    if [ ! -z "$custom_url" ]; then
        update_env_var "CUSTOM_MCP_URL" "$custom_url" "$ENV_FILE"
        update_env_var "CUSTOM_API_KEY" "$custom_key" "$ENV_FILE"
        update_env_var "CUSTOM_CLIENT_ID" "$custom_id" "$ENV_FILE"
        echo -e "${GREEN}✓ Custom server configured${NC}"
    fi
}

# Process user choice
case $choice in
    1) configure_linear ;;
    2) configure_notion ;;
    3) configure_sentry ;;
    4) configure_apidog ;;
    5) configure_simplescraper ;;
    6) configure_custom ;;
    7)
        configure_linear
        configure_notion
        configure_sentry
        configure_apidog
        configure_simplescraper
        ;;
    0) 
        echo -e "${YELLOW}Exiting...${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Test remote server connectivity
echo -e "\n${YELLOW}Testing remote server connectivity...${NC}"

test_remote_server() {
    local name=$1
    local url=$2
    local auth_header=$3
    
    echo -n "Testing $name... "
    
    if [ ! -z "$auth_header" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -H "$auth_header" "$url" 2>/dev/null || echo "000")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    fi
    
    if [ "$response" = "200" ] || [ "$response" = "401" ] || [ "$response" = "403" ]; then
        echo -e "${GREEN}✓ Reachable${NC}"
    else
        echo -e "${RED}✗ Unreachable (HTTP $response)${NC}"
    fi
}

# Test configured servers
if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
    
    if [ ! -z "$LINEAR_API_KEY" ]; then
        test_remote_server "Linear" "https://api.linear.app/graphql" "Authorization: $LINEAR_API_KEY"
    fi
    
    if [ ! -z "$NOTION_CLIENT_ID" ]; then
        test_remote_server "Notion" "https://api.notion.com/v1" ""
    fi
    
    if [ ! -z "$SENTRY_AUTH_TOKEN" ]; then
        test_remote_server "Sentry" "https://sentry.io/api/0/" "Authorization: Bearer $SENTRY_AUTH_TOKEN"
    fi
fi

# Apply configuration
echo -e "\n${YELLOW}Applying configuration...${NC}"

# Backup existing config
if [ -f "$MCP_CONFIG_DIR/claude_desktop_config.json" ]; then
    cp "$MCP_CONFIG_DIR/claude_desktop_config.json" "$MCP_CONFIG_DIR/claude_desktop_config.backup.json"
    echo -e "${GREEN}✓ Backed up existing configuration${NC}"
fi

# Prompt to use remote config
read -p "Enable remote servers in Claude configuration? (y/n): " enable_remote
if [ "$enable_remote" = "y" ]; then
    cp "$MCP_CONFIG_DIR/claude_desktop_config_remote.json" "$MCP_CONFIG_DIR/claude_desktop_config.json"
    echo -e "${GREEN}✓ Remote servers enabled${NC}"
    
    # Add servers using Claude CLI
    echo -e "\n${YELLOW}Adding remote servers to Claude...${NC}"
    
    if [ ! -z "$LINEAR_API_KEY" ]; then
        echo "Adding Linear server..."
        claude mcp add --transport sse linear https://mcp.linear.app/sse 2>/dev/null || true
    fi
    
    if [ ! -z "$NOTION_CLIENT_ID" ]; then
        echo "Adding Notion server..."
        claude mcp add --transport http notion https://api.notion.com/v1/mcp 2>/dev/null || true
    fi
    
    if [ ! -z "$SENTRY_AUTH_TOKEN" ]; then
        echo "Adding Sentry server..."
        claude mcp add --transport sse sentry https://sentry.io/api/mcp/sse 2>/dev/null || true
    fi
fi

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}                     Remote MCP Setup Complete!                                  ${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo -e "\n${YELLOW}Next steps:${NC}"
echo "1. Restart Claude Code to apply changes"
echo "2. Use 'claude mcp list' to verify servers"
echo "3. Test remote servers with 'claude mcp test <server-name>'"

echo -e "\n${BLUE}Documentation:${NC}"
echo "- Remote MCP Servers: REMOTE_MCP_SERVERS.md"
echo "- OAuth Setup: https://modelcontextprotocol.io/docs/auth"
echo "- Transport Protocols: https://modelcontextprotocol.io/docs/transports"