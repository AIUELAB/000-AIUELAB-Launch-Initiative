#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open NotebookLM
# @raycast.mode fullOutput
# @raycast.icon 📚
# @raycast.description AIUELABのNotebookLMを開く（自動ログイン）
# @raycast.packageName AIUELAB Tools
# @raycast.author Takashi Gunji

# 色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 設定
GOOGLE_ACCOUNT="aiuelab.official@gmail.com"
NOTEBOOK_ID="ce4eebd7-38da-4b35-8205-8b31f9125827"
NOTEBOOK_URL="https://notebooklm.google.com/notebook/${NOTEBOOK_ID}?authuser=1"

echo -e "${BLUE}📚 NotebookLM を開いています...${NC}"
echo "================================"
echo -e "アカウント: ${GREEN}${GOOGLE_ACCOUNT}${NC}"
echo -e "Notebook ID: ${NOTEBOOK_ID}"

# Chromeのプロファイルを使用してログイン状態を保持
# aiuelab.official@gmail.comでログイン済みのChromeを使用
open -a "Google Chrome" "${NOTEBOOK_URL}"

# 別の方法: デフォルトブラウザで開く
# open "${NOTEBOOK_URL}"

echo -e "\n${GREEN}✅ NotebookLMを開きました${NC}"
echo -e "${YELLOW}💡 ヒント:${NC}"
echo "• 初回アクセス時はGoogleログインが必要です"
echo "• ${GOOGLE_ACCOUNT} でログインしてください"
echo "• ログイン状態はChromeプロファイルに保存されます"
