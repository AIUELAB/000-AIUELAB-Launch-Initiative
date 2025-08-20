#!/bin/bash

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Open in Cursor
# @raycast.mode silent
# @raycast.icon 📝
# @raycast.description Cursorでプロジェクトを開く
# @raycast.packageName Claude Code Tools
# @raycast.author Your Name

# プロジェクトのパス
PROJECT_PATH="/Users/admin/Documents/Cursor/claude-code-template-mcp"

# Cursorで開く
code "$PROJECT_PATH"

# 通知
echo "📝 Cursorでプロジェクトを開きました"
