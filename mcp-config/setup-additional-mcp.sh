#!/bin/bash
# 追加MCPサーバーのセットアップスクリプト
# 2025年最新版 - 必要に応じて選択的にインストール

set -e

# カラー出力
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  Additional MCP Servers Setup${NC}"
echo -e "${BLUE}  追加MCPサーバーセットアップ${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# 利用可能な追加MCPサーバーリスト
declare -A MCP_SERVERS=(
    ["memory"]="@modelcontextprotocol/server-memory"
    ["sequential-thinking"]="@modelcontextprotocol/server-sequential-thinking"
    ["puppeteer"]="@modelcontextprotocol/server-puppeteer"
    ["postgres"]="@modelcontextprotocol/server-postgres"
    ["slack"]="@modelcontextprotocol/server-slack"
    ["gitlab"]="@modelcontextprotocol/server-gitlab"
    ["google-drive"]="@modelcontextprotocol/server-gdrive"
    ["google-maps"]="@modelcontextprotocol/server-google-maps"
    ["aws"]="@aws/mcp-server-aws"
    ["gcp"]="@google-cloud/mcp-server-gcp"
    ["azure"]="@azure/mcp-server-azure"
    ["docker"]="@modelcontextprotocol/server-docker"
    ["kubernetes"]="@modelcontextprotocol/server-kubernetes"
    ["discord"]="@modelcontextprotocol/server-discord"
    ["notion"]="@modelcontextprotocol/server-notion"
    ["obsidian"]="mcp-server-obsidian"
    ["linear"]="@modelcontextprotocol/server-linear"
    ["sentry"]="@modelcontextprotocol/server-sentry"
    ["datadog"]="@modelcontextprotocol/server-datadog"
    ["jira"]="@modelcontextprotocol/server-jira"
    ["confluence"]="@modelcontextprotocol/server-confluence"
    ["salesforce"]="@modelcontextprotocol/server-salesforce"
    ["stripe"]="@modelcontextprotocol/server-stripe"
    ["shopify"]="@modelcontextprotocol/server-shopify"
    ["twilio"]="@modelcontextprotocol/server-twilio"
    ["sendgrid"]="@modelcontextprotocol/server-sendgrid"
    ["reddit"]="@modelcontextprotocol/server-reddit"
    ["hacker-news"]="@modelcontextprotocol/server-hackernews"
    ["arxiv"]="@modelcontextprotocol/server-arxiv"
    ["wikipedia"]="@modelcontextprotocol/server-wikipedia"
    ["wolfram-alpha"]="@modelcontextprotocol/server-wolfram"
    ["openweather"]="@modelcontextprotocol/server-weather"
    ["news-api"]="@modelcontextprotocol/server-news"
    ["youtube"]="@modelcontextprotocol/server-youtube"
    ["spotify"]="@modelcontextprotocol/server-spotify"
)

# サーバーの説明
declare -A MCP_DESCRIPTIONS=(
    ["memory"]="長期記憶管理・コンテキスト保持"
    ["sequential-thinking"]="順次思考処理・推論チェーン"
    ["puppeteer"]="ブラウザ自動化（Playwright代替）"
    ["postgres"]="PostgreSQLデータベース連携"
    ["slack"]="Slackワークスペース統合"
    ["gitlab"]="GitLab統合（Issue、MR、CI/CD）"
    ["google-drive"]="Google Drive統合"
    ["google-maps"]="Google Maps API統合"
    ["aws"]="AWS全サービス統合"
    ["gcp"]="Google Cloud Platform統合"
    ["azure"]="Microsoft Azure統合"
    ["docker"]="Dockerコンテナ管理"
    ["kubernetes"]="Kubernetesクラスター管理"
    ["discord"]="Discord統合"
    ["notion"]="Notionワークスペース統合"
    ["obsidian"]="Obsidianノート管理"
    ["linear"]="Linear Issue管理"
    ["sentry"]="Sentryエラー監視"
    ["datadog"]="Datadog監視・分析"
    ["jira"]="Jira Issue管理"
    ["confluence"]="Confluenceドキュメント管理"
    ["salesforce"]="Salesforce CRM統合"
    ["stripe"]="Stripe決済統合"
    ["shopify"]="Shopify Eコマース統合"
    ["twilio"]="Twilio通信API"
    ["sendgrid"]="SendGridメール配信"
    ["reddit"]="Reddit API統合"
    ["hacker-news"]="Hacker News統合"
    ["arxiv"]="arXiv論文検索"
    ["wikipedia"]="Wikipedia検索・閲覧"
    ["wolfram-alpha"]="Wolfram Alpha計算エンジン"
    ["openweather"]="OpenWeather天気予報"
    ["news-api"]="ニュースAPI統合"
    ["youtube"]="YouTube API統合"
    ["spotify"]="Spotify音楽統合"
)

# 必要な環境変数
declare -A MCP_ENV_VARS=(
    ["postgres"]="DATABASE_URL"
    ["slack"]="SLACK_TOKEN SLACK_TEAM_ID"
    ["gitlab"]="GITLAB_TOKEN GITLAB_URL"
    ["google-drive"]="GOOGLE_CLIENT_ID GOOGLE_CLIENT_SECRET"
    ["google-maps"]="GOOGLE_MAPS_API_KEY"
    ["aws"]="AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_REGION"
    ["gcp"]="GOOGLE_APPLICATION_CREDENTIALS"
    ["azure"]="AZURE_SUBSCRIPTION_ID AZURE_TENANT_ID AZURE_CLIENT_ID AZURE_CLIENT_SECRET"
    ["discord"]="DISCORD_TOKEN"
    ["notion"]="NOTION_TOKEN"
    ["obsidian"]="OBSIDIAN_VAULT_PATH"
    ["linear"]="LINEAR_API_KEY"
    ["sentry"]="SENTRY_AUTH_TOKEN SENTRY_ORG"
    ["datadog"]="DD_API_KEY DD_APP_KEY"
    ["jira"]="JIRA_URL JIRA_EMAIL JIRA_API_TOKEN"
    ["confluence"]="CONFLUENCE_URL CONFLUENCE_EMAIL CONFLUENCE_API_TOKEN"
    ["salesforce"]="SALESFORCE_CLIENT_ID SALESFORCE_CLIENT_SECRET SALESFORCE_USERNAME SALESFORCE_PASSWORD"
    ["stripe"]="STRIPE_API_KEY"
    ["shopify"]="SHOPIFY_STORE_URL SHOPIFY_ACCESS_TOKEN"
    ["twilio"]="TWILIO_ACCOUNT_SID TWILIO_AUTH_TOKEN"
    ["sendgrid"]="SENDGRID_API_KEY"
    ["reddit"]="REDDIT_CLIENT_ID REDDIT_CLIENT_SECRET"
    ["wolfram-alpha"]="WOLFRAM_APP_ID"
    ["openweather"]="OPENWEATHER_API_KEY"
    ["news-api"]="NEWS_API_KEY"
    ["youtube"]="YOUTUBE_API_KEY"
    ["spotify"]="SPOTIFY_CLIENT_ID SPOTIFY_CLIENT_SECRET"
)

# インストール済みのサーバーをチェック
check_installed() {
    local server=$1
    local package=${MCP_SERVERS[$server]}

    if npm list -g "$package" &>/dev/null; then
        return 0
    else
        return 1
    fi
}

# サーバーリストを表示
show_server_list() {
    echo -e "${YELLOW}利用可能な追加MCPサーバー:${NC}"
    echo ""

    local i=1
    for server in "${!MCP_SERVERS[@]}"; do
        local status="${RED}✗${NC}"
        if check_installed "$server"; then
            status="${GREEN}✓${NC}"
        fi

        printf "%2d. [%b] %-25s - %s\n" "$i" "$status" "$server" "${MCP_DESCRIPTIONS[$server]}"
        ((i++))
    done | sort -k2

    echo ""
    echo -e "${GREEN}✓${NC} = インストール済み, ${RED}✗${NC} = 未インストール"
    echo ""
}

# サーバーをインストール
install_server() {
    local server=$1
    local package=${MCP_SERVERS[$server]}

    echo -e "${YELLOW}Installing $server...${NC}"

    # npmでインストール
    if npm install -g "$package"; then
        echo -e "${GREEN}✅ $server installed successfully!${NC}"

        # 必要な環境変数を表示
        if [[ -n "${MCP_ENV_VARS[$server]}" ]]; then
            echo -e "${YELLOW}📝 Required environment variables for $server:${NC}"
            for var in ${MCP_ENV_VARS[$server]}; do
                echo "   - $var"
            done
            echo -e "${YELLOW}💡 Add these to your .env.mcp file${NC}"
        fi

        return 0
    else
        echo -e "${RED}❌ Failed to install $server${NC}"
        return 1
    fi
}

# インタラクティブインストール
interactive_install() {
    show_server_list

    echo -e "${BLUE}インストールするサーバーを選択してください（複数可、スペース区切り）:${NC}"
    echo "例: memory puppeteer postgres"
    echo "all: 全てインストール"
    echo "recommended: 推奨セットをインストール"
    echo "q: 終了"
    echo ""

    read -p "> " selection

    if [[ "$selection" == "q" ]]; then
        echo "終了します"
        exit 0
    fi

    local servers_to_install=()

    if [[ "$selection" == "all" ]]; then
        servers_to_install=("${!MCP_SERVERS[@]}")
    elif [[ "$selection" == "recommended" ]]; then
        servers_to_install=("memory" "sequential-thinking" "postgres" "docker" "obsidian")
    else
        # shellcheck disable=SC2206
        read -r -a servers_to_install <<< "$selection"
    fi

    echo ""
    echo -e "${BLUE}以下のサーバーをインストールします:${NC}"
    for server in "${servers_to_install[@]}"; do
        if [[ -n "${MCP_SERVERS[$server]}" ]]; then
            echo "  - $server: ${MCP_DESCRIPTIONS[$server]}"
        else
            echo -e "  ${RED}✗ $server: 不明なサーバー${NC}"
        fi
    done

    echo ""
    read -p "続行しますか？ (y/n): " confirm

    if [[ "$confirm" != "y" ]]; then
        echo "キャンセルしました"
        exit 0
    fi

    echo ""
    for server in "${servers_to_install[@]}"; do
        if [[ -n "${MCP_SERVERS[$server]}" ]]; then
            if check_installed "$server"; then
                echo -e "${GREEN}✓ $server is already installed${NC}"
            else
                install_server "$server"
            fi
        fi
    done
}

# 設定例を生成
generate_config_example() {
    local server=$1

    echo -e "${BLUE}設定例 for $server:${NC}"
    echo ""
    echo '```json'

    case "$server" in
        "memory")
            cat << 'EOF'
"memory": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-memory"]
}
EOF
            ;;
        "postgres")
            cat << 'EOF'
"postgres": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres"],
  "env": {
    "DATABASE_URL": "${DATABASE_URL}"
  }
}
EOF
            ;;
        "docker")
            cat << 'EOF'
"docker": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-docker"],
  "env": {
    "DOCKER_HOST": "unix:///var/run/docker.sock"
  }
}
EOF
            ;;
        "obsidian")
            cat << 'EOF'
"obsidian": {
  "command": "npx",
  "args": ["-y", "mcp-server-obsidian", "/path/to/your/vault"]
}
EOF
            ;;
        *)
            echo "{}"
            ;;
    esac

    echo '```'
    echo ""
}

# ヘルプメッセージ
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  install [SERVER...]  指定したサーバーをインストール"
    echo "  list                インストール可能なサーバーリスト表示"
    echo "  check               インストール済みサーバーを確認"
    echo "  config [SERVER]     サーバーの設定例を表示"
    echo "  help                このヘルプメッセージを表示"
    echo ""
    echo "Examples:"
    echo "  $0                  # インタラクティブモード"
    echo "  $0 install memory   # memoryサーバーをインストール"
    echo "  $0 list            # サーバーリストを表示"
    echo "  $0 config postgres # PostgreSQL設定例を表示"
}

# メイン処理
case "${1:-}" in
    "install")
        shift
        if [[ $# -eq 0 ]]; then
            interactive_install
        else
            for server in "$@"; do
                if [[ -n "${MCP_SERVERS[$server]}" ]]; then
                    install_server "$server"
                else
                    echo -e "${RED}Unknown server: $server${NC}"
                fi
            done
        fi
        ;;
    "list")
        show_server_list
        ;;
    "check")
        echo -e "${BLUE}インストール済みMCPサーバー:${NC}"
        echo ""
        for server in "${!MCP_SERVERS[@]}"; do
            if check_installed "$server"; then
                echo -e "  ${GREEN}✓${NC} $server"
            fi
        done | sort
        ;;
    "config")
        if [[ -n "$2" ]]; then
            generate_config_example "$2"
        else
            echo "サーバー名を指定してください"
        fi
        ;;
    "help")
        show_help
        ;;
    *)
        interactive_install
        ;;
esac

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo -e "${YELLOW}💡 Remember to add the servers to your claude_desktop_config.json${NC}"
echo -e "${YELLOW}💡 And set required environment variables in .env.mcp${NC}"
