#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail
IFS=$'\n\t'

# このスクリプトは Raycast 設定の拡張プリファレンスにある baseUrl を書き換える補助です。
# Raycast の内部ストレージ仕様に依存するため、将来変更で失敗する可能性があります。
# 失敗しても安全に終了するように実装しています。

EXTENSION_NAME="raycast-n8n-runner"
NEW_BASE_URL="${1:-}"

if [ -z "${NEW_BASE_URL}" ]; then
  echo "Usage: scripts/update-raycast-baseurl.sh http://localhost:5678" >&2
  exit 1
fi

echo "Target extension: ${EXTENSION_NAME}" >/dev/null

# Raycast のアプリサポートディレクトリ（macOS）
PREF_ROOT="$HOME/Library/Application Support/Raycast"

if [ ! -d "$PREF_ROOT" ]; then
  echo "Raycast preference dir not found: $PREF_ROOT" >&2
  exit 0
fi

# 候補ディレクトリを探索し、拡張の preferences.json を探す
UPDATED=0
while IFS= read -r -d '' file; do
  if grep -q '"baseUrl"' "$file" 2>/dev/null; then
    # JSON を単純置換（値部分のみ）。jq があれば厳密に更新
    if command -v jq >/dev/null 2>&1; then
      tmp="${file}.tmp"
      jq --arg url "$NEW_BASE_URL" '(.preferences // {}) as $p | ($p.baseUrl? | length) as $has | if $has then .preferences.baseUrl = $url else . end' "$file" >"$tmp" && mv "$tmp" "$file"
    else
      # 簡易: baseUrl の行を上書き（想定フォーマット依存）
      sed -i '' -e "s|\(\"baseUrl\"[[:space:]]*:[[:space:]]*\)\"[^\"]*\"|\1\"${NEW_BASE_URL//\//\/}\"|" "$file" || true
    fi
    echo "Updated: $file"
    UPDATED=$((UPDATED+1))
  fi
done < <(find "$PREF_ROOT" -type f -name "*.json" -print0)

if [ "$UPDATED" -eq 0 ]; then
  echo "No Raycast preferences containing baseUrl were found. Please update manually in Raycast Preferences." >&2
else
  echo "✅ Updated baseUrl in $UPDATED file(s)."
fi

exit 0
