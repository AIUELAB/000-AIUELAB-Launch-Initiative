#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Run n8n Automation
# @raycast.mode fullOutput
# @raycast.icon 🤖
# @raycast.description n8nワークフローを実行
# @raycast.packageName Claude Code Tools
# @raycast.author Your Name

# プロジェクトディレクトリ
PROJECT_PATH="/Users/admin/Documents/Cursor/claude-code-template-mcp"

# ディレクトリ移動
cd "$PROJECT_PATH"

# n8nワークフロー実行スクリプトを呼び出し
./scripts/run-n8n-workflow.sh
