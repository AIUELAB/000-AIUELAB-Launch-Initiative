#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail
IFS=$'\n\t'

# このスクリプトは Raycast 設定の拡張プリファレンスにある baseUrl と apiKey を書き換える補助です。
# Raycast の内部ストレージ仕様に依存するため、将来変更で失敗する可能性があります。

EXTENSION_NAME="raycast-n8n-runner"
NEW_BASE_URL="${1:-}"
KEY_FILE="/Users/admin/Documents/key/n8n-key.txt"

if [ -z "${NEW_BASE_URL}" ]; then
  echo "Usage: scripts/update-raycast-baseurl.sh http://localhost:5678" >&2
  exit 1
fi

API_KEY=""
if [ -f "$KEY_FILE" ]; then
  API_KEY="$(cat "$KEY_FILE" | tr -d '\r\n')"
fi

# Raycast のアプリサポートディレクトリ（macOS）
PREF_ROOT="$HOME/Library/Application Support/Raycast"

if [ ! -d "$PREF_ROOT" ]; then
  echo "Raycast preference dir not found: $PREF_ROOT" >&2
  exit 0
fi

UPDATED=0
while IFS= read -r -d '' file; do
  # baseUrl を更新
  if grep -q '"baseUrl"' "$file" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      tmp="${file}.tmp"
      jq --arg url "$NEW_BASE_URL" '(.preferences // {}) as $p | ($p.baseUrl? | length) as $has | if $has then .preferences.baseUrl = $url else . end' "$file" >"$tmp" && mv "$tmp" "$file"
    else
      sed -i '' -e "s|\(\"baseUrl\"[[:space:]]*:[[:space:]]*\)\"[^\"]*\"|\1\"${NEW_BASE_URL//\//\/}\"|" "$file" || true
    fi
    UPDATED=$((UPDATED+1))
  fi
  # apiKey を更新（存在する場合）
  if [ -n "$API_KEY" ] && grep -q '"apiKey"' "$file" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      tmp="${file}.tmp"
      jq --arg key "$API_KEY" '(.preferences // {}) as $p | ($p.apiKey? | length) as $has | if $has then .preferences.apiKey = $key else . end' "$file" >"$tmp" && mv "$tmp" "$file"
    else
      sed -i '' -e "s|\(\"apiKey\"[[:space:]]*:[[:space:]]*\)\"[^\"]*\"|\1\"${API_KEY//\//\/}\"|" "$file" || true
    fi
    UPDATED=$((UPDATED+1))
  fi
done < <(find "$PREF_ROOT" -type f -name "*.json" -print0)

if [ "$UPDATED" -eq 0 ]; then
  echo "No matching Raycast preferences found. Please update in Raycast Preferences manually." >&2
else
  echo "✅ Updated Raycast preferences in $UPDATED place(s)."
fi

exit 0
