#!/bin/bash

# GitHub AIUELAB 自動化スクリプト
# アカウント: https://github.com/AIUELAB

set -euo pipefail

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# GitHub設定
GITHUB_USER="AIUELAB"
GITHUB_EMAIL="aiuelab.official@gmail.com"
GITHUB_ORG="AIUELAB"

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

# GitHub CLI チェック
check_github_cli() {
    if ! command -v gh &> /dev/null; then
        log_error "GitHub CLI がインストールされていません"
        log_info "インストール中..."
        brew install gh
    else
        log_success "GitHub CLI が検出されました: $(gh --version | head -1)"
    fi
}

# ログイン状態確認
check_login() {
    log_info "GitHub ログイン状態を確認中..."

    if gh auth status &> /dev/null; then
        USER=$(gh api user --jq .login)
        log_success "ログイン済み: $USER"

        if [ "$USER" != "$GITHUB_USER" ]; then
            log_warning "期待するユーザー ($GITHUB_USER) と異なります"
            return 1
        fi
        return 0
    else
        log_warning "ログインが必要です"
        return 1
    fi
}

# 自動ログイン
auto_login() {
    # 環境変数からトークンを取得
    if [ -f ".env.github" ]; then
        source .env.github
    fi

    if [ -z "${GITHUB_TOKEN:-}" ]; then
        log_error "GITHUB_TOKEN が設定されていません"
        log_info "以下の手順でトークンを取得してください："
        echo "1. https://github.com/settings/tokens/new にアクセス"
        echo "2. 必要なスコープを選択（repo, workflow, admin:org）"
        echo "3. トークンを生成"
        echo "4. .env.github ファイルに追加: GITHUB_TOKEN=your_token"
        return 1
    fi

    # トークンでログイン
    echo "$GITHUB_TOKEN" | gh auth login --with-token
    log_success "GitHub にログインしました"
}

# リポジトリ作成
create_repository() {
    local REPO_NAME="$1"
    local DESCRIPTION="${2:-}"
    local PRIVATE="${3:-false}"

    log_info "リポジトリを作成中: $REPO_NAME"

    if [ "$PRIVATE" = "true" ]; then
        gh repo create "$GITHUB_USER/$REPO_NAME" --private --description "$DESCRIPTION"
    else
        gh repo create "$GITHUB_USER/$REPO_NAME" --public --description "$DESCRIPTION"
    fi

    log_success "リポジトリ作成完了: https://github.com/$GITHUB_USER/$REPO_NAME"
}

# iOS アプリテンプレートリポジトリ作成
create_ios_template() {
    local APP_NAME="$1"

    log_info "iOSアプリテンプレートを作成中: $APP_NAME"

    # リポジトリ作成
    create_repository "$APP_NAME" "iOS App - $APP_NAME" true

    # クローン
    gh repo clone "$GITHUB_USER/$APP_NAME" "/tmp/$APP_NAME"
    cd "/tmp/$APP_NAME"

    # 基本構造作成
    cat > README.md << EOF
# $APP_NAME

iOS Application developed by AIUELAB

## Overview
- **Developer**: AIUELAB
- **Website**: https://aiuelab.com
- **Platform**: iOS
- **Language**: Swift

## Features
- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3

## Requirements
- iOS 15.0+
- Xcode 14.0+
- Swift 5.7+

## Installation
\`\`\`bash
git clone https://github.com/$GITHUB_USER/$APP_NAME.git
cd $APP_NAME
open $APP_NAME.xcodeproj
\`\`\`

## License
Copyright © 2025 AIUELAB. All rights reserved.
EOF

    # .gitignore 作成
    cat > .gitignore << 'EOF'
# Xcode
build/
*.pbxuser
!default.pbxuser
*.mode1v3
!default.mode1v3
*.mode2v3
!default.mode2v3
*.perspectivev3
!default.perspectivev3
xcuserdata/
*.xccheckout
*.moved-aside
DerivedData/
*.hmap
*.ipa
*.dSYM.zip
*.dSYM

# CocoaPods
Pods/
*.xcworkspace

# Swift Package Manager
.build/
.swiftpm/

# fastlane
fastlane/report.xml
fastlane/Preview.html
fastlane/screenshots/**/*.png
fastlane/test_output

# Code Injection
iOSInjectionProject/
EOF

    # GitHub Actions ワークフロー
    mkdir -p .github/workflows
    cat > .github/workflows/ios.yml << 'EOF'
name: iOS CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    name: Build and Test
    runs-on: macos-latest

    steps:
    - uses: actions/checkout@v3

    - name: Select Xcode
      run: sudo xcode-select -switch /Applications/Xcode.app

    - name: Build
      run: |
        xcodebuild clean build \
          -project ${{ github.event.repository.name }}.xcodeproj \
          -scheme ${{ github.event.repository.name }} \
          -sdk iphonesimulator \
          -destination 'platform=iOS Simulator,name=iPhone 14'

    - name: Test
      run: |
        xcodebuild test \
          -project ${{ github.event.repository.name }}.xcodeproj \
          -scheme ${{ github.event.repository.name }} \
          -sdk iphonesimulator \
          -destination 'platform=iOS Simulator,name=iPhone 14'
EOF

    # コミット＆プッシュ
    git add .
    git commit -m "Initial iOS app template setup"
    git push origin main

    log_success "iOSアプリテンプレート作成完了"
    cd -
}

# 統計情報表示
show_stats() {
    log_info "GitHub AIUELAB 統計情報"
    echo "================================"

    # ユーザー情報
    gh api user --jq '
        "👤 ユーザー: " + .login,
        "📧 メール: " + .email,
        "🌍 場所: " + .location,
        "🔗 ウェブ: " + .blog,
        "📝 Bio: " + .bio,
        "",
        "📊 統計:",
        "  • パブリックリポジトリ: " + (.public_repos | tostring),
        "  • フォロワー: " + (.followers | tostring),
        "  • フォロー中: " + (.following | tostring),
        "  • 作成日: " + .created_at
    '

    echo ""
    log_info "最近のアクティビティ"
    gh api "users/$GITHUB_USER/events" --jq '
        .[:5] | .[] |
        "  • " + .type + " - " + .repo.name + " (" + .created_at + ")"
    '
}

# メイン処理
main() {
    log_info "🚀 GitHub AIUELAB 自動化"
    echo "================================"

    # GitHub CLI チェック
    check_github_cli

    # ログイン確認
    if ! check_login; then
        auto_login || exit 1
    fi

    # コマンド処理
    case "${1:-}" in
        create-repo)
            create_repository "${2:-new-repo}" "${3:-}" "${4:-false}"
            ;;
        create-ios)
            create_ios_template "${2:-NewApp}"
            ;;
        stats)
            show_stats
            ;;
        *)
            echo "使用方法:"
            echo "  $0 create-repo <name> [description] [private]"
            echo "  $0 create-ios <app-name>"
            echo "  $0 stats"
            ;;
    esac
}

# スクリプト実行
if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi
