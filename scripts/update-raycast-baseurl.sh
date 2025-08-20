#!/usr/bin/env bash
# shellcheck shell=bash
set -euo pipefail
IFS=$'\n\t'

# このスクリプトは Raycast 設定の拡張プリファレンスにある baseUrl と apiKey を書き換える補助です。
# Raycast の内部ストレージ仕様に依存するため、将来変更で失敗する可能性があります。

EXTENSION_NAME="raycast-n8n-runner"
NEW_BASE_URL="${1:-}"
TARGET_JSON="${2:-}"
KEY_FILE="/Users/admin/Documents/key/n8n-key.txt"

if [ -z "${NEW_BASE_URL}" ]; then
  echo "Usage: scripts/update-raycast-baseurl.sh http://localhost:5678 [path/to/preferences.json]" >&2
  exit 1
fi

# shellcheck disable=SC2034
: "${EXTENSION_NAME}" # keep variable referenced for shellcheck

API_KEY=""
if [ -f "$KEY_FILE" ]; then
  API_KEY="$(cat "$KEY_FILE" | tr -d '\r\n')"
fi

update_file() {
  local file="$1"
  local updated=0
  # baseUrl を更新
  if grep -q '"baseUrl"' "$file" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      local tmp="${file}.tmp"
      jq --arg url "$NEW_BASE_URL" '(.preferences // {}) as $p | ($p.baseUrl? | length) as $has | if $has then .preferences.baseUrl = $url else . end' "$file" >"$tmp" && mv "$tmp" "$file"
    else
      sed -i '' -e "s|\(\"baseUrl\"[[:space:]]*:[[:space:]]*\)\"[^\"]*\"|\1\"${NEW_BASE_URL//\//\/}\"|" "$file" || true
    fi
    updated=$((updated+1))
  fi
  # apiKey を更新（存在する場合）
  if [ -n "$API_KEY" ] && grep -q '"apiKey"' "$file" 2>/dev/null; then
    if command -v jq >/dev/null 2>&1; then
      local tmp="${file}.tmp"
      jq --arg key "$API_KEY" '(.preferences // {}) as $p | ($p.apiKey? | length) as $has | if $has then .preferences.apiKey = $key else . end' "$file" >"$tmp" && mv "$tmp" "$file"
    else
      sed -i '' -e "s|\(\"apiKey\"[[:space:]]*:[[:space:]]*\)\"[^\"]*\"|\1\"${API_KEY//\//\/}\"|" "$file" || true
    fi
    updated=$((updated+1))
  fi
  echo "$updated"
}

if [ -n "$TARGET_JSON" ] && [ -f "$TARGET_JSON" ]; then
  count=$(update_file "$TARGET_JSON")
  if [ "$count" -eq 0 ]; then
    echo "No matching keys in: $TARGET_JSON (baseUrl/apiKey not found)." >&2
  else
    echo "✅ Updated Raycast preferences file: $TARGET_JSON ($count change(s))"
  fi
  exit 0
fi

# 候補の Raycast 設定ディレクトリ（macOS）
CANDIDATES=(
  "$HOME/Library/Application Support/Raycast"
  "$HOME/Library/Containers/com.raycast.macos/Data/Library/Application Support/Raycast"
  "/Users/admin/Documents/Raycast"
)

PREF_ROOT=""
for d in "${CANDIDATES[@]}"; do
  if [ -d "$d" ]; then
    PREF_ROOT="$d"
    break
  fi
done

if [ -z "$PREF_ROOT" ]; then
  echo "Raycast preference dir not found. Tried:" >&2
  for d in "${CANDIDATES[@]}"; do echo " - $d" >&2; done
  exit 0
fi

UPDATED=0
while IFS= read -r -d '' file; do
  if grep -q '"baseUrl"\|"apiKey"' "$file" 2>/dev/null; then
    c=$(update_file "$file")
    UPDATED=$((UPDATED + c))
  fi
done < <(find "$PREF_ROOT" -type f -name "*.json" -print0)

if [ "$UPDATED" -eq 0 ]; then
  echo "No matching Raycast preferences found in: $PREF_ROOT. Please update in Raycast Preferences manually." >&2
else
  echo "✅ Updated Raycast preferences in $UPDATED place(s). ($PREF_ROOT)"
fi

exit 0
