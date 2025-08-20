#!/bin/bash

# Vercel 自動デプロイスクリプト
# aiuelab.com のデプロイを自動化

set -euo pipefail

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 設定
PROJECT_NAME="aiuelab"
DOMAIN="aiuelab.com"
VERCEL_TEAM="aiuelab"

# ログ関数
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vercel CLI チェック
check_vercel_cli() {
    if ! command -v vercel &> /dev/null; then
        log_error "Vercel CLI がインストールされていません"
        log_info "インストール中..."
        npm install -g vercel
    else
        log_success "Vercel CLI が検出されました: $(vercel --version)"
    fi
}

# ログイン状態確認
check_login() {
    log_info "Vercel ログイン状態を確認中..."

    if vercel whoami &> /dev/null; then
        USER=$(vercel whoami)
        log_success "ログイン済み: $USER"
        return 0
    else
        log_warning "ログインが必要です"
        return 1
    fi
}

# 自動ログイン（トークン使用）
auto_login() {
    # 環境変数からトークンを取得
    if [ -f ".env" ]; then
        source .env
    fi

    if [ -f ".env.vercel" ]; then
        source .env.vercel
    fi

    if [ -z "${VERCEL_TOKEN:-}" ]; then
        log_error "VERCEL_TOKEN が設定されていません"
        log_info "以下の手順でトークンを取得してください："
        echo "1. https://vercel.com/account/tokens にアクセス"
        echo "2. 'Create Token' をクリック"
        echo "3. トークンをコピー"
        echo "4. .env.vercel ファイルに追加: VERCEL_TOKEN=your_token"
        return 1
    fi

    # トークンでログイン
    export VERCEL_TOKEN
    log_success "トークンを使用してログイン成功"
}

# プロジェクトリンク
link_project() {
    log_info "プロジェクトをリンク中..."

    if [ -f ".vercel/project.json" ]; then
        log_success "プロジェクトは既にリンク済み"
    else
        vercel link --yes --project=$PROJECT_NAME --scope=$VERCEL_TEAM
        log_success "プロジェクトをリンクしました"
    fi
}

# デプロイ実行
deploy() {
    local ENVIRONMENT="${1:-production}"
    local MESSAGE="${2:-Auto deploy from script}"

    log_info "デプロイを開始します..."
    log_info "環境: $ENVIRONMENT"
    log_info "メッセージ: $MESSAGE"

    if [ "$ENVIRONMENT" == "production" ]; then
        # 本番環境へのデプロイ
        DEPLOYMENT_URL=$(vercel --prod --token=$VERCEL_TOKEN --yes 2>&1 | grep -o 'https://[^ ]*' | tail -1)
    else
        # プレビュー環境へのデプロイ
        DEPLOYMENT_URL=$(vercel --token=$VERCEL_TOKEN --yes 2>&1 | grep -o 'https://[^ ]*' | tail -1)
    fi

    if [ -n "$DEPLOYMENT_URL" ]; then
        log_success "デプロイ成功！"
        log_info "URL: $DEPLOYMENT_URL"

        # ブラウザで開く（オプション）
        if [ "${OPEN_BROWSER:-false}" == "true" ]; then
            open "$DEPLOYMENT_URL"
        fi
    else
        log_error "デプロイに失敗しました"
        return 1
    fi
}

# プロジェクト状態確認
check_project_status() {
    log_info "プロジェクト状態を確認中..."

    # 最新のデプロイメント情報を取得
    vercel ls --token=$VERCEL_TOKEN 2>/dev/null | head -10 || true
}

# メイン処理
main() {
    log_info "🚀 Vercel 自動デプロイを開始"
    echo "================================"

    # Vercel CLI チェック
    check_vercel_cli

    # ログイン確認
    if ! check_login; then
        auto_login || exit 1
    fi

    # プロジェクトディレクトリに移動
    if [ -n "${PROJECT_DIR:-}" ]; then
        cd "$PROJECT_DIR"
    fi

    # プロジェクトリンク
    link_project

    # デプロイ実行
    deploy "${1:-production}" "${2:-Auto deploy}"

    # 状態確認
    check_project_status

    log_success "✨ デプロイ完了！"
}

# スクリプト実行
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
