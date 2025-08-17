#!/bin/bash

# Claude Code テンプレート セットアップスクリプト
# このスクリプトは仮想環境を作成し、必要な依存関係をインストールします

set -e  # エラーが発生したら即座に終了

# カラー出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_info "Claude Code テンプレート セットアップを開始します..."
log_info "プロジェクトディレクトリ: $PROJECT_ROOT"

# Python3の存在確認
if ! command -v python3 &> /dev/null; then
    log_error "Python3が見つかりません。Python3をインストールしてください。"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_info "Python バージョン: $PYTHON_VERSION"

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
    log_info "依存関係をインストールしています..."
    pip install -r requirements.txt
    log_success "すべての依存関係がインストールされました"

    # pre-commit のセットアップ
    if command -v pre-commit >/dev/null 2>&1; then
        log_info "pre-commit を初期化しています..."
        pre-commit install || true
    fi
else
    log_warning "requirements.txtが見つかりません"
fi

# .envファイルの作成
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    log_info ".env.exampleから.envファイルを作成しています..."
    cp .env.example .env
    log_success ".envファイルが作成されました"
    log_warning ".envファイルを編集して、必要な環境変数を設定してください"
elif [ -f ".env" ]; then
    log_info ".envファイルは既に存在します"
else
    log_warning ".env.exampleが見つかりません"
fi

# ディレクトリ構造の確認
log_info "プロジェクト構造を確認しています..."
directories=("src" "tests" "scripts")
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
            git commit -m "Initial commit: Claude Code template"
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
    if pytest tests/ -v; then
        log_success "すべてのテストが成功しました"
    else
        log_warning "一部のテストが失敗しました"
    fi
fi

# セットアップ完了メッセージ
echo ""
log_success "セットアップが完了しました！"
echo ""
echo -e "${BLUE}次のステップ:${NC}"
echo "1. 仮想環境を有効化: source venv/bin/activate"
echo "2. .envファイルを編集して環境変数を設定"
echo "3. アプリケーションを実行: python src/main.py run"
echo "4. テストを実行: pytest tests/"
echo "5. Claude Codeを起動: claude-code"
echo ""
echo -e "${GREEN}Happy Coding with Claude Code! 🎉${NC}"

# オプション: VS Codeを開く
if command -v code &> /dev/null; then
    log_info "VS Codeでプロジェクトを開きますか？ (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        code .
    fi
fi
