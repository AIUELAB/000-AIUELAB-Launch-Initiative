#!/bin/bash

# Claude Code MCP テンプレート セットアップスクリプト
# このスクリプトは仮想環境を作成し、必要な依存関係をインストールします

set -e  # エラーが発生したら即座に終了

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

# プロジェクトルートディレクトリに移動
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   Claude Code MCP Template Setup Script   ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

log_info "プロジェクトディレクトリ: $PROJECT_ROOT"

# オプション処理
WITH_KEYS=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --with-keys)
            WITH_KEYS=true
            shift
            ;;
        --help|-h)
            echo "使用方法: $0 [オプション]"
            echo ""
            echo "オプション:"
            echo "  --with-keys  キーフォルダからAPIキーを自動読み込み"
            echo "  -h, --help   このヘルプを表示"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Python3の存在確認
if ! command -v python3 &> /dev/null; then
    log_error "Python3が見つかりません。Python3をインストールしてください。"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Python バージョン: $PYTHON_VERSION"

# Node.jsの確認（MCP用）
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    log_info "Node.js バージョン: $NODE_VERSION"
else
    log_warning "Node.jsが見つかりません。MCPサーバーを使用するにはNode.js 18以上が必要です。"
fi

# 仮想環境の作成
if [ -d "venv" ]; then
    log_warning "既存の仮想環境が見つかりました。削除して再作成しますか？ (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        log_info "既存の仮想環境を削除しています..."
        rm -rf venv
    else
        log_info "既存の仮想環境を使用します。"
    fi
fi

if [ ! -d "venv" ]; then
    log_info "Python仮想環境を作成しています..."
    python3 -m venv venv
    log_success "仮想環境が作成されました"
else
    log_info "既存の仮想環境を使用します"
fi

# 仮想環境の有効化
log_info "仮想環境を有効化しています..."
source venv/bin/activate

# pipのアップグレード
log_info "pipをアップグレードしています..."
pip install --upgrade pip > /dev/null 2>&1

# 依存関係のインストール
if [ -f "requirements.txt" ]; then
    log_info "Python依存関係をインストールしています..."
    pip install -r requirements.txt
    log_success "すべてのPython依存関係がインストールされました"
else
    log_warning "requirements.txtが見つかりません"
fi

# .envファイルの作成
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    log_info ".env.exampleから.envファイルを作成しています..."
    cp .env.example .env
    log_success ".envファイルが作成されました"
elif [ -f ".env" ]; then
    log_info ".envファイルは既に存在します"
fi

# MCP環境変数ファイルの作成
if [ "$WITH_KEYS" = true ]; then
    # キーフォルダから自動読み込み
    log_info "キーフォルダからAPIキーを自動読み込みしています..."
    if [ -f "$SCRIPT_DIR/load-keys.sh" ]; then
        bash "$SCRIPT_DIR/load-keys.sh" --auto
        if [ $? -eq 0 ]; then
            log_success "APIキーが自動的に読み込まれました"
        else
            log_warning "APIキーの読み込みに失敗しました"
        fi
    else
        log_warning "load-keys.shスクリプトが見つかりません"
    fi
elif [ ! -f ".env.mcp" ] && [ ! -f "mcp-config/.env.mcp" ]; then
    # 手動設定の場合
    if [ -f "mcp-config/.env.mcp.example" ]; then
        log_info ".env.mcp.exampleから.env.mcpファイルを作成しています..."
        cp mcp-config/.env.mcp.example mcp-config/.env.mcp
        log_success ".env.mcpファイルが作成されました"
        log_warning "mcp-config/.env.mcpファイルを編集して、必要なAPIキーを設定してください"
    fi
elif [ -f ".env.mcp" ] || [ -f "mcp-config/.env.mcp" ]; then
    log_info ".env.mcpファイルは既に存在します"
fi

# MCPサーバーのセットアップ
echo ""
log_info "MCPサーバーをセットアップしますか？ (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    if [ -f "mcp-config/setup-mcp.sh" ]; then
        log_info "MCPサーバーをセットアップしています..."
        cd mcp-config
        bash setup-mcp.sh
        cd ..
    else
        log_warning "mcp-config/setup-mcp.shが見つかりません"
    fi
fi

# ディレクトリ構造の確認
log_info "プロジェクト構造を確認しています..."
directories=("src" "tests" "scripts" "mcp-config")
for dir in "${directories[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "  ${GREEN}✓${NC} $dir/"
    else
        echo -e "  ${RED}✗${NC} $dir/ (見つかりません)"
        mkdir -p "$dir"
        log_info "$dir/ ディレクトリを作成しました"
    fi
done

# Gitリポジトリの初期化（必要な場合）
if [ ! -d ".git" ]; then
    log_info "Gitリポジトリを初期化しますか？ (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        git init
        log_success "Gitリポジトリが初期化されました"

        # 最初のコミット
        log_info "初期コミットを作成しますか？ (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            git add .
            git commit -m "Initial commit: Claude Code MCP template"
            log_success "初期コミットが作成されました"
        fi
    fi
else
    log_info "Gitリポジトリは既に初期化されています"
fi

# テストの実行
log_info "テストを実行しますか？ (y/N)"
read -r response
if [[ "$response" =~ ^[Yy]$ ]]; then
    log_info "テストを実行しています..."
    if [ -d "tests" ] && [ -n "$(ls -A tests/*.py 2>/dev/null)" ]; then
        if pytest tests/ -v; then
            log_success "すべてのテストが成功しました"
        else
            log_warning "一部のテストが失敗しました"
        fi
    else
        log_warning "テストファイルが見つかりません"
    fi
fi

# セットアップ完了メッセージ
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}       セットアップが完了しました！          ${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${CYAN}次のステップ:${NC}"
echo "1. 仮想環境を有効化: source venv/bin/activate"
echo "2. .envファイルを編集して環境変数を設定"
echo "3. mcp-config/.env.mcpファイルにAPIキーを設定"
echo "4. アプリケーションを実行: python src/main.py"
echo "5. MCPサンプルを実行: python src/mcp_examples.py"
echo "6. Claude Codeを起動: claude-code"
echo ""
echo -e "${YELLOW}MCPサーバーの使用:${NC}"
echo "• Claudeで「/mcp」と入力してMCPサーバーを確認"
echo "• mcp__github__ でGitHub操作"
echo "• mcp__brave-search__ でWeb検索"
echo "• mcp__filesystem__ でファイル操作"
echo ""
echo -e "${GREEN}Happy Coding with Claude Code & MCP! 🚀${NC}"

# オプション: VS Codeを開く
if command -v code &> /dev/null; then
    log_info "VS Codeでプロジェクトを開きますか？ (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        code .
    fi
fi
