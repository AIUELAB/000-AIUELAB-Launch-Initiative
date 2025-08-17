#!/bin/bash

# MCP Servers Setup Script
# このスクリプトはMCPサーバーをインストールし、設定を行います

set -e

# カラー出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ヘッダー表示
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}      MCP Servers Installation Script      ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# 必要なツールの確認
log_info "必要なツールを確認しています..."

# Node.jsの確認
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_success "Node.js $NODE_VERSION が見つかりました"
else
    log_error "Node.jsが見つかりません。Node.js 18以上をインストールしてください"
    echo "インストール方法: https://nodejs.org/"
    exit 1
fi

# npmの確認
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    log_success "npm $NPM_VERSION が見つかりました"
else
    log_error "npmが見つかりません"
    exit 1
fi

# Pythonの確認（uvx用）
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log_success "Python $PYTHON_VERSION が見つかりました"
else
    log_warning "Python3が見つかりません。一部のMCPサーバーが利用できない可能性があります"
fi

# uvの確認とインストール（Serenaに必須）
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version 2>/dev/null | cut -d' ' -f2)
    log_success "uv $UV_VERSION が見つかりました"
else
    log_warning "uvが見つかりません。Serena MCPサーバーに必須です。"
    log_info "uvをインストールしますか？ (Y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Nn]$ ]]; then
        log_info "uvをインストールしています..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        log_success "uvがインストールされました"
        # パスを更新
        export PATH="$HOME/.local/bin:$PATH"
    else
        log_warning "uvがないとSerenaとFirecrawl MCPサーバーが利用できません"
    fi
fi

# Serena MCPサーバーの設定
echo ""
log_info "Serena MCPサーバー（高度なコード操作）を設定しますか？"
echo "  Serenaは以下の機能を提供します："
echo "  • セマンティックコード検索（LSP対応）"
echo "  • 多言語対応（Python, TypeScript, Go, Rust等）"
echo "  • filesystemサーバーの上位互換"
echo -n "Serenaを有効にする場合は 'y' を入力: "
read -r enable_serena

if [[ "$enable_serena" =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}Serena設定:${NC}"
    echo "  1. uvx方式（推奨 - 自動更新）"
    echo "  2. ローカルインストール"
    echo "  3. Docker方式（実験的）"
    echo -n "選択してください (1-3): "
    read -r serena_choice

    case $serena_choice in
        2)
            log_info "Serenaをローカルにクローンしています..."
            git clone https://github.com/oraios/serena.git ~/serena
            log_success "Serenaがローカルにインストールされました"
            log_warning "claude_desktop_config.jsonでserena-localを有効にしてください"
            ;;
        3)
            log_info "Docker方式を選択しました"
            if command -v docker &> /dev/null; then
                log_success "Dockerが見つかりました"
                log_warning "claude_desktop_config.jsonでserena-dockerを有効にしてください"
            else
                log_error "Dockerがインストールされていません"
            fi
            ;;
        *)
            log_success "uvx方式（デフォルト）が設定されています"
            log_info "Claudeを再起動後、自動的にSerenaが利用可能になります"
            ;;
    esac

    log_warning "注意: Serenaとfilesystemサーバーを同時に使用すると競合する可能性があります"
    log_info "filesystemサーバーを無効にすることを推奨します"
fi

# MCPサーバーのインストール
echo ""
log_info "その他のMCPサーバーをインストールします..."
echo ""

# 基本的なMCPサーバー
MCP_SERVERS=(
    "@modelcontextprotocol/server-filesystem"
    "@modelcontextprotocol/server-github"
    "@context7/mcp-server"
    "@modelcontextprotocol/server-brave-search"
    "@executeautomation/playwright-mcp-server"
    "@win32user/mcp-ide"
    "@modelcontextprotocol/server-memory"
    "@modelcontextprotocol/server-puppeteer"
    "@modelcontextprotocol/server-sequential-thinking"
)

# オプショナルなMCPサーバー
OPTIONAL_SERVERS=(
    "@modelcontextprotocol/server-postgres"
    "@modelcontextprotocol/server-slack"
    "@modelcontextprotocol/server-gitlab"
    "@modelcontextprotocol/server-google-maps"
    "@modelcontextprotocol/server-aws"
    "@modelcontextprotocol/server-gcp"
    "@modelcontextprotocol/server-azure"
    "@modelcontextprotocol/server-docker"
    "@modelcontextprotocol/server-kubernetes"
)

# 基本MCPサーバーのインストール
echo -e "${CYAN}基本的なMCPサーバー:${NC}"
for server in "${MCP_SERVERS[@]}"; do
    echo -n "  - $server ... "
    if npm list -g "$server" &> /dev/null; then
        echo -e "${GREEN}インストール済み${NC}"
    else
        if npm install -g "$server" &> /dev/null; then
            echo -e "${GREEN}インストール完了${NC}"
        else
            echo -e "${YELLOW}インストール失敗（スキップ）${NC}"
        fi
    fi
done

# Pythonベースのサーバー
echo ""
echo -e "${CYAN}Pythonベースのサーバー:${NC}"
if command -v uvx &> /dev/null; then
    echo -n "  - mcp-server-fetch ... "
    echo -e "${GREEN}uvxで利用可能${NC}"
    echo -n "  - firecrawl-mcp-server ... "
    echo -e "${GREEN}uvxで利用可能${NC}"
else
    log_warning "uvがインストールされていないため、Pythonベースのサーバーは利用できません"
fi

# オプショナルサーバーのインストール確認
echo ""
log_info "オプショナルなMCPサーバーをインストールしますか？"
echo "  （クラウドサービスやデータベース連携用）"
echo -n "インストールする場合は 'y' を入力: "
read -r install_optional

if [[ "$install_optional" =~ ^[Yy]$ ]]; then
    echo -e "${CYAN}オプショナルなMCPサーバー:${NC}"
    for server in "${OPTIONAL_SERVERS[@]}"; do
        echo -n "  - $server ... "
        if npm list -g "$server" &> /dev/null; then
            echo -e "${GREEN}インストール済み${NC}"
        else
            if npm install -g "$server" &> /dev/null; then
                echo -e "${GREEN}インストール完了${NC}"
            else
                echo -e "${YELLOW}インストール失敗（スキップ）${NC}"
            fi
        fi
    done
fi

# 環境変数ファイルの作成
echo ""
log_info "環境変数ファイルを作成しています..."

ENV_FILE="../.env.mcp"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# MCP Servers Environment Variables
# このファイルに実際のAPIキーやトークンを設定してください

# GitHub
GITHUB_TOKEN=your_github_personal_access_token_here

# Brave Search
BRAVE_API_KEY=your_brave_api_key_here

# Firecrawl
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Slack (オプショナル)
SLACK_BOT_TOKEN=your_slack_bot_token_here
SLACK_TEAM_ID=your_slack_team_id_here

# GitLab (オプショナル)
GITLAB_TOKEN=your_gitlab_token_here

# Google Maps (オプショナル)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# AWS (オプショナル)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1

# Google Cloud Platform (オプショナル)
GOOGLE_APPLICATION_CREDENTIALS=path_to_service_account_json

# Azure (オプショナル)
AZURE_SUBSCRIPTION_ID=your_azure_subscription_id_here
AZURE_CLIENT_ID=your_azure_client_id_here
AZURE_CLIENT_SECRET=your_azure_client_secret_here
AZURE_TENANT_ID=your_azure_tenant_id_here
EOF
    log_success ".env.mcpファイルが作成されました"
    log_warning "必要なAPIキーを.env.mcpファイルに設定してください"
else
    log_info ".env.mcpファイルは既に存在します"
fi

# Claude Desktop設定のコピー
echo ""
log_info "Claude Desktop設定ファイルの配置場所を確認しています..."

# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

    if [ ! -d "$CONFIG_DIR" ]; then
        log_warning "Claudeアプリケーションがインストールされていない可能性があります"
        echo "Claudeデスクトップアプリをインストールしてください: https://claude.ai/download"
    else
        log_info "既存の設定をバックアップしますか？ (y/N)"
        read -r backup_response
        if [[ "$backup_response" =~ ^[Yy]$ ]]; then
            if [ -f "$CONFIG_FILE" ]; then
                cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
                log_success "設定がバックアップされました"
            fi
        fi

        log_info "MCP設定をClaude Desktopに適用しますか？ (y/N)"
        read -r apply_response
        if [[ "$apply_response" =~ ^[Yy]$ ]]; then
            cp claude_desktop_config.json "$CONFIG_FILE"
            log_success "MCP設定が適用されました"
            log_warning "Claudeアプリケーションを再起動してください"
        fi
    fi
# Windows
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "win32" ]]; then
    CONFIG_DIR="$APPDATA/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

    if [ ! -d "$CONFIG_DIR" ]; then
        log_warning "Claudeアプリケーションがインストールされていない可能性があります"
    else
        log_info "MCP設定をClaude Desktopに適用しますか？ (y/N)"
        read -r apply_response
        if [[ "$apply_response" =~ ^[Yy]$ ]]; then
            cp claude_desktop_config.json "$CONFIG_FILE"
            log_success "MCP設定が適用されました"
        fi
    fi
# Linux
else
    CONFIG_DIR="$HOME/.config/Claude"
    log_info "Linux環境での設定パス: $CONFIG_DIR"
fi

# 完了メッセージ
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}     MCPサーバーのセットアップが完了しました！     ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${CYAN}次のステップ:${NC}"
echo "1. .env.mcpファイルに必要なAPIキーを設定"
echo "2. Claudeデスクトップアプリを再起動"
echo "3. Claudeで「/mcp」と入力してMCPサーバーを確認"
echo ""
echo -e "${YELLOW}利用可能なMCPサーバー:${NC}"
echo "  • filesystem - ファイルシステム操作"
echo "  • github - GitHub統合"
echo "  • fetch - Web取得"
echo "  • context7 - ライブラリドキュメント"
echo "  • brave-search - Web検索"
echo "  • playwright - ブラウザ自動化"
echo "  • ide - IDE統合"
echo "  • firecrawl - Webスクレイピング"
echo "  • memory - メモリ管理"
echo "  • sequential-thinking - 順次思考"
echo ""
echo -e "${GREEN}Happy Coding with MCP! 🚀${NC}"
