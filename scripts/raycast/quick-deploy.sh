#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Quick Deploy to Vercel
# @raycast.mode fullOutput
# @raycast.icon 🚀
# @raycast.description Vercelに現在のプロジェクトをデプロイ
# @raycast.packageName Claude Code Tools
# @raycast.author Your Name

# 色の定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🚀 Vercelへのクイックデプロイ"
echo "================================"

# プロジェクトディレクトリに移動
cd /Users/admin/Documents/Cursor/claude-code-template-mcp

# 環境変数の読み込み
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Vercel CLIの確認
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}⚠️  Vercel CLIがインストールされていません${NC}"
    echo "インストール中..."
    npm install -g vercel
fi

# Gitの状態確認
echo -e "${BLUE}📊 Gitステータスを確認中...${NC}"
git status --short

# 変更をコミット
echo ""
read -p "変更をコミットしますか？ (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    read -p "コミットメッセージ: " commit_msg
    git commit -m "$commit_msg" || git commit -m "Update: $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${GREEN}✅ コミット完了${NC}"
fi

# Vercelにデプロイ
echo ""
echo -e "${YELLOW}⏳ Vercelにデプロイ中...${NC}"

# プロダクション or プレビュー
echo ""
echo "デプロイタイプを選択:"
echo "1) プレビュー（開発環境）"
echo "2) プロダクション（本番環境）"
read -p "選択 (1/2): " deploy_type

if [ "$deploy_type" = "2" ]; then
    vercel --prod --token=$VERCEL_TOKEN
else
    vercel --token=$VERCEL_TOKEN
fi

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ デプロイが完了しました！${NC}"
    echo ""
    echo "次のステップ:"
    echo "• Vercelダッシュボードで確認"
    echo "• デプロイURLを共有"
else
    echo -e "${RED}❌ デプロイに失敗しました${NC}"
    echo ""
    echo "トラブルシューティング:"
    echo "1. VERCEL_TOKENが.envに設定されているか確認"
    echo "2. vercel loginでログイン"
    echo "3. プロジェクトがVercelにリンクされているか確認"
fi

echo ""
echo "================================"
echo "完了"
