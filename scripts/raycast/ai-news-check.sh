#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Check AI/MCP News
# @raycast.mode fullOutput
# @raycast.icon 🤖
# @raycast.description 最新のAI/MCP情報をチェック
# @raycast.packageName AI News Monitor
# @raycast.author Your Name
# @raycast.interval 30m

# プロジェクトディレクトリ
PROJECT_PATH="/Users/admin/Documents/Cursor/claude-code-template-mcp"
COLLECTOR_PATH="$PROJECT_PATH/automation/ai-news-collector"

# ディレクトリ移動
cd "$COLLECTOR_PATH"

# Python仮想環境を有効化
source "$PROJECT_PATH/venv/bin/activate" 2>/dev/null

echo "🤖 AI/MCP最新情報チェック"
echo "================================"
echo ""

# 最新のダイジェストファイルを確認
TODAY=$(date +%Y%m%d)
DIGEST_FILE="collected_data/digest_${TODAY}.md"

if [ -f "$DIGEST_FILE" ]; then
    # 今日のダイジェストがある場合は表示
    cat "$DIGEST_FILE"
else
    # ない場合は収集を実行
    echo "📡 最新情報を収集中..."
    python3 -c "
import asyncio
from collector import AINewsCollector

async def quick_check():
    collector = AINewsCollector('config.json')
    articles = await collector.collect_from_all_sources()

    if articles:
        print(collector.format_for_display(articles[:5]))
        collector.save_daily_digest(articles)
    else:
        print('📭 新しい情報はありません')

asyncio.run(quick_check())
"
fi

echo ""
echo "================================"
echo "💡 詳細: $COLLECTOR_PATH/collected_data/"
