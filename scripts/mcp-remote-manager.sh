#!/bin/bash

# MCP Remote Server Manager
# CLI tool for managing remote MCP server connections

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MCP_CONFIG_DIR="$PROJECT_ROOT/mcp-config"
REMOTE_CONFIG="$MCP_CONFIG_DIR/remote-servers.json"
ENV_FILE="$PROJECT_ROOT/.env.mcp"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
# shellcheck disable=SC2034
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Command
COMMAND=${1:-help}

# Functions
show_banner() {
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}                        MCP Remote Server Manager v1.0                           ${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

show_help() {
    show_banner
    echo -e "\n${YELLOW}Usage:${NC} $0 [command] [options]"
    echo
    echo -e "${YELLOW}Commands:${NC}"
    echo -e "  ${GREEN}list${NC}              List all configured remote servers"
    echo -e "  ${GREEN}add${NC}               Add a new remote server"
    echo -e "  ${GREEN}remove${NC}            Remove a remote server"
    echo -e "  ${GREEN}test${NC}              Test connectivity to servers"
    echo -e "  ${GREEN}status${NC}            Show server status"
    echo -e "  ${GREEN}auth${NC}              Manage authentication"
    echo -e "  ${GREEN}profile${NC}           Apply a server profile"
    echo -e "  ${GREEN}logs${NC}              View server logs"
    echo -e "  ${GREEN}config${NC}            Edit configuration"
    echo -e "  ${GREEN}help${NC}              Show this help message"
    echo
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 list                    # List all servers"
    echo "  $0 add linear sse          # Add Linear via SSE"
    echo "  $0 test linear             # Test Linear connection"
    echo "  $0 auth refresh notion     # Refresh Notion OAuth token"
    echo "  $0 profile hybrid          # Apply hybrid profile"
    echo
}

list_servers() {
    echo -e "\n${BLUE}Configured Remote MCP Servers:${NC}\n"

    if command -v claude >/dev/null 2>&1; then
        # Use Claude CLI if available
        claude mcp list --remote 2>/dev/null || true
    fi

    # Also show from config file
    if [ -f "$REMOTE_CONFIG" ]; then
        echo -e "\n${YELLOW}From configuration file:${NC}"
        python3 -c "
import json
with open('$REMOTE_CONFIG') as f:
    config = json.load(f)
    servers = config.get('remoteMcpServers', {})
    for name, details in servers.items():
        transport = details.get('transport', 'unknown')
        url = details.get('url', 'no-url')
        desc = details.get('description', '')
        print(f'  • {name:20} [{transport:4}] {desc}')
        print(f'    {url}')
"
    fi
}

add_server() {
    local name=${2:-}
    local transport=${3:-sse}
    local url=${4:-}

    if [ -z "$name" ]; then
        echo -e "${YELLOW}Available servers to add:${NC}"
        echo "  1) Linear (Issue tracking)"
        echo "  2) Notion (Knowledge base)"
        echo "  3) Sentry (Error monitoring)"
        echo "  4) Apidog (API documentation)"
        echo "  5) SimpleScraper (Web scraping)"
        echo "  6) Custom server"
        echo
        read -p "Select server (1-6): " choice

        case $choice in
            1)
                name="linear"
                transport="sse"
                url="https://mcp.linear.app/sse"
                echo -e "\n${YELLOW}Get your Linear API key from:${NC}"
                echo "https://linear.app/settings/api"
                read -p "Enter Linear API Key: " api_key
                header="Authorization: Bearer $api_key"
                ;;
            2)
                name="notion"
                transport="http"
                url="https://api.notion.com/v1/mcp"
                echo -e "\n${YELLOW}Create Notion integration at:${NC}"
                echo "https://www.notion.so/my-integrations"
                read -p "Enter Client ID: " client_id
                read -p "Enter Client Secret: " client_secret
                oauth="--oauth-client-id \"$client_id\" --oauth-client-secret \"$client_secret\""
                ;;
            3)
                name="sentry"
                transport="sse"
                url="https://sentry.io/api/mcp/sse"
                echo -e "\n${YELLOW}Get Sentry auth token from:${NC}"
                echo "https://sentry.io/settings/account/api/auth-tokens/"
                read -p "Enter Auth Token: " auth_token
                header="Authorization: Bearer $auth_token"
                ;;
            4)
                name="apidog"
                transport="http"
                url="https://api.apidog.com/mcp"
                read -p "Enter Apidog API Key: " api_key
                header="X-API-Key: $api_key"
                ;;
            5)
                name="simplescraper"
                transport="sse"
                url="https://api.simplescraper.io/mcp/sse"
                read -p "Enter SimpleScraper API Key: " api_key
                header="X-API-Key: $api_key"
                ;;
            6)
                read -p "Enter server name: " name
                read -p "Enter transport (sse/http): " transport
                read -p "Enter server URL: " url
                read -p "Enter auth header (optional): " header
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                exit 1
                ;;
        esac
    fi

    echo -e "\n${YELLOW}Adding server: $name${NC}"

    # Add using Claude CLI
    if command -v claude >/dev/null 2>&1; then
        if [ ! -z "$header" ]; then
            claude mcp add --transport "$transport" "$name" "$url" --header "$header" 2>/dev/null || true
        elif [ ! -z "$oauth" ]; then
            eval "claude mcp add --transport \"$transport\" \"$name\" \"$url\" $oauth" 2>/dev/null || true
        else
            claude mcp add --transport "$transport" "$name" "$url" 2>/dev/null || true
        fi

        echo -e "${GREEN}✓ Server added: $name${NC}"
    else
        echo -e "${RED}Claude CLI not found. Please install Claude Code.${NC}"
        exit 1
    fi
}

remove_server() {
    local name=${2:-}

    if [ -z "$name" ]; then
        echo -e "${YELLOW}Enter server name to remove:${NC}"
        list_servers
        read -p "Server name: " name
    fi

    echo -e "\n${YELLOW}Removing server: $name${NC}"

    if command -v claude >/dev/null 2>&1; then
        claude mcp remove "$name" 2>/dev/null || true
        echo -e "${GREEN}✓ Server removed: $name${NC}"
    else
        echo -e "${RED}Claude CLI not found${NC}"
        exit 1
    fi
}

test_connectivity() {
    local server=${2:-all}

    echo -e "\n${BLUE}Testing Remote Server Connectivity${NC}\n"

    if [ "$server" = "all" ]; then
        # Test all servers
        if command -v claude >/dev/null 2>&1; then
            claude mcp test --all 2>/dev/null || true
        fi

        # Also run Python connectivity test
        echo -e "\n${YELLOW}Running comprehensive connectivity test...${NC}"
        python3 "$PROJECT_ROOT/src/remote_mcp_integration.py" 2>/dev/null || true
    else
        # Test specific server
        echo -e "Testing $server..."
        if command -v claude >/dev/null 2>&1; then
            claude mcp test "$server" 2>/dev/null || {
                echo -e "${RED}✗ Failed to connect to $server${NC}"
                exit 1
            }
            echo -e "${GREEN}✓ Successfully connected to $server${NC}"
        fi
    fi
}

show_status() {
    echo -e "\n${BLUE}Remote MCP Server Status${NC}\n"

    if command -v claude >/dev/null 2>&1; then
        claude mcp status --remote 2>/dev/null || true
    fi

    # Check environment variables
    echo -e "\n${YELLOW}Environment Variables:${NC}"

    check_env_var() {
        local var=$1
        local desc=$2
        if [ ! -z "${!var}" ]; then
            echo -e "  ${GREEN}✓${NC} $var is set ($desc)"
        else
            echo -e "  ${RED}✗${NC} $var is not set ($desc)"
        fi
    }

    if [ -f "$ENV_FILE" ]; then
        # shellcheck source=/dev/null
        source "$ENV_FILE"
    fi

    check_env_var "LINEAR_API_KEY" "Linear"
    check_env_var "NOTION_CLIENT_ID" "Notion OAuth"
    check_env_var "SENTRY_AUTH_TOKEN" "Sentry"
    check_env_var "APIDOG_API_KEY" "Apidog"
    check_env_var "SIMPLESCRAPER_API_KEY" "SimpleScraper"
}

manage_auth() {
    local action=${2:-list}
    local server=${3:-}

    case $action in
        list)
            echo -e "\n${BLUE}Authentication Status${NC}\n"
            if command -v claude >/dev/null 2>&1; then
                claude mcp auth list 2>/dev/null || true
            fi
            ;;
        refresh)
            if [ -z "$server" ]; then
                echo -e "${RED}Server name required${NC}"
                echo "Usage: $0 auth refresh <server>"
                exit 1
            fi
            echo -e "\n${YELLOW}Refreshing auth for $server...${NC}"
            if command -v claude >/dev/null 2>&1; then
                claude mcp auth refresh "$server" 2>/dev/null || true
                echo -e "${GREEN}✓ Auth refreshed for $server${NC}"
            fi
            ;;
        setup)
            echo -e "\n${YELLOW}Setting up authentication...${NC}"
            ./scripts/setup-remote-mcp.sh
            ;;
        *)
            echo -e "${RED}Unknown auth action: $action${NC}"
            echo "Valid actions: list, refresh, setup"
            exit 1
            ;;
    esac
}

apply_profile() {
    local profile=${2:-}

    if [ -z "$profile" ]; then
        echo -e "${YELLOW}Available profiles:${NC}"
        echo "  1) minimal   - Local servers only"
        echo "  2) standard  - Common local servers"
        echo "  3) remote    - Remote servers only"
        echo "  4) hybrid    - Local + Remote servers"
        echo "  5) full      - All servers enabled"
        echo
        read -p "Select profile (1-5): " choice

        case $choice in
            1) profile="minimal" ;;
            2) profile="standard" ;;
            3) profile="remote" ;;
            4) profile="hybrid" ;;
            5) profile="full" ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                exit 1
                ;;
        esac
    fi

    profile_file="$MCP_CONFIG_DIR/profiles/${profile}.json"

    if [ ! -f "$profile_file" ]; then
        echo -e "${RED}Profile not found: $profile${NC}"
        exit 1
    fi

    echo -e "\n${YELLOW}Applying profile: $profile${NC}"

    # Backup current config
    if [ -f "$MCP_CONFIG_DIR/claude_desktop_config.json" ]; then
        cp "$MCP_CONFIG_DIR/claude_desktop_config.json" "$MCP_CONFIG_DIR/claude_desktop_config.backup.json"
        echo -e "${GREEN}✓ Backed up current configuration${NC}"
    fi

    # Apply profile
    if [ "$profile" = "remote" ] || [ "$profile" = "hybrid" ]; then
        # Use remote-enabled config
        cp "$MCP_CONFIG_DIR/claude_desktop_config_remote.json" "$MCP_CONFIG_DIR/claude_desktop_config.json"
    else
        # Use standard config
        cp "$profile_file" "$MCP_CONFIG_DIR/claude_desktop_config.json"
    fi

    echo -e "${GREEN}✓ Profile applied: $profile${NC}"
    echo -e "${YELLOW}Restart Claude Code to apply changes${NC}"
}

view_logs() {
    local server=${2:-all}

    echo -e "\n${BLUE}MCP Server Logs${NC}\n"

    if [ "$server" = "all" ]; then
        if command -v claude >/dev/null 2>&1; then
            claude mcp logs --tail 50 2>/dev/null || true
        fi
    else
        if command -v claude >/dev/null 2>&1; then
            claude mcp logs "$server" --tail 50 2>/dev/null || true
        fi
    fi
}

edit_config() {
    echo -e "\n${YELLOW}Opening configuration files...${NC}"

    # Determine editor
    EDITOR=${EDITOR:-vim}

    if command -v code >/dev/null 2>&1; then
        EDITOR=code
    elif command -v cursor >/dev/null 2>&1; then
        EDITOR=cursor
    fi

    # Open config files
    $EDITOR "$REMOTE_CONFIG" "$MCP_CONFIG_DIR/claude_desktop_config_remote.json" "$ENV_FILE"

    echo -e "${GREEN}✓ Configuration files opened in $EDITOR${NC}"
}

# Main execution
case $COMMAND in
    list)
        list_servers
        ;;
    add)
        add_server "$@"
        ;;
    remove)
        remove_server "$@"
        ;;
    test)
        test_connectivity "$@"
        ;;
    status)
        show_status
        ;;
    auth)
        manage_auth "$@"
        ;;
    profile)
        apply_profile "$@"
        ;;
    logs)
        view_logs "$@"
        ;;
    config)
        edit_config
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Unknown command: $COMMAND${NC}"
        show_help
        exit 1
        ;;
esac

echo
