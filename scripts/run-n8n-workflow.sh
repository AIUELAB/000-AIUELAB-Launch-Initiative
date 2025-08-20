#!/bin/bash

# 🤖 n8nワークフロー実行スクリプト
# 使い方: ./scripts/run-n8n-workflow.sh [workflow_name]

# 色の定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 環境変数の読み込み
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# n8n設定の読み込み
CONFIG_FILE="automation/n8n-workflows/n8n-config.json"

echo -e "${BLUE}🤖 n8nワークフロー実行${NC}"
echo "================================"

# 引数がない場合はメニューを表示
if [ -z "$1" ]; then
    echo "利用可能なワークフロー:"
    echo ""
    echo "1) 📦 Vercelへデプロイ"
    echo "2) 🔄 自動化を実行"
    echo "3) 🔀 GitHubと同期"
    echo "4) 📱 iOSアプリをテスト"
    echo "5) 💾 プロジェクトをバックアップ"
    echo ""
    read -p "番号を選択してください (1-5): " choice

    case $choice in
        1) WORKFLOW="deploy_to_vercel" ;;
        2) WORKFLOW="run_automation" ;;
        3) WORKFLOW="sync_with_github" ;;
        4) WORKFLOW="test_ios_app" ;;
        5) WORKFLOW="backup_project" ;;
        *) echo -e "${RED}❌ 無効な選択です${NC}"; exit 1 ;;
    esac
else
    WORKFLOW=$1
fi

# Webhook URLの取得（実際の実装では jq を使用）
case $WORKFLOW in
    "deploy_to_vercel")
        WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://your-n8n.app/webhook/deploy-vercel}"
        WORKFLOW_NAME="Vercelデプロイ"
        ;;
    "run_automation")
        WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://your-n8n.app/webhook/run-automation}"
        WORKFLOW_NAME="自動化実行"
        ;;
    "sync_with_github")
        WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://your-n8n.app/webhook/sync-github}"
        WORKFLOW_NAME="GitHub同期"
        ;;
    "test_ios_app")
        WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://your-n8n.app/webhook/test-ios}"
        WORKFLOW_NAME="iOSテスト"
        ;;
    "backup_project")
        WEBHOOK_URL="${N8N_WEBHOOK_URL:-https://your-n8n.app/webhook/backup}"
        WORKFLOW_NAME="バックアップ"
        ;;
    *)
        echo -e "${RED}❌ 不明なワークフロー: $WORKFLOW${NC}"
        exit 1
        ;;
esac

echo -e "${YELLOW}⏳ $WORKFLOW_NAME を実行中...${NC}"

# データの準備
DATA=$(cat <<EOF
{
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "project": "claude-code-template",
    "triggered_by": "manual",
    "environment": "$(uname -s)",
    "workflow": "$WORKFLOW"
}
EOF
)

# n8n Webhookを呼び出し
RESPONSE=$(curl -s -X POST \
    -H "Content-Type: application/json" \
    -H "X-API-Key: ${N8N_API_KEY}" \
    -d "$DATA" \
    "$WEBHOOK_URL")

# 結果の確認
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ $WORKFLOW_NAME が正常に実行されました！${NC}"
    echo ""
    echo "レスポンス:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
else
    echo -e "${RED}❌ エラーが発生しました${NC}"
    echo "Webhook URL: $WEBHOOK_URL"
    echo ""
    echo "トラブルシューティング:"
    echo "1. .envファイルにN8N_WEBHOOK_URLが設定されているか確認"
    echo "2. n8nが起動しているか確認"
    echo "3. Webhookノードが正しく設定されているか確認"
fi

echo ""
echo "================================"
echo -e "${BLUE}完了${NC}"
