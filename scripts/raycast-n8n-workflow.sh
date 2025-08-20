#!/usr/bin/env bash
set -euo pipefail

# Required parameters:
# @raycast.schemaVersion 1
# @raycast.title Run n8n Workflow
# @raycast.mode silent

# Optional parameters:
# @raycast.packageName n8n
# @raycast.icon 🧩

# Arguments
# @raycast.argument1 {"type": "text", "placeholder": "Webhook URL or path", "percentEncoded": true}
# @raycast.argument2 {"type": "text", "placeholder": "JSON payload (optional)", "optional": true}

# This Script Command triggers an n8n workflow via Webhook.
# Usage from Raycast:
#   - Argument1: Full Webhook URL (recommended) or Webhook path (e.g. my/raycast)
#   - Argument2: Optional JSON payload

REPO_ROOT="/Users/admin/Documents/Cursor/claude-code-template-mcp"
ENV_FILE="$REPO_ROOT/.env.n8n"

# Defaults (can be overridden by .env.n8n)
N8N_PORT="${N8N_PORT:-5678}"

if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck source=/dev/null
  . "$ENV_FILE"
  set +a
fi

INPUT_PATH_OR_URL="${1:?Missing first argument: Webhook URL or path}"
PAYLOAD="${2:-}"

if [[ "$INPUT_PATH_OR_URL" =~ ^https?:// ]]; then
  URL="$INPUT_PATH_OR_URL"
else
  # Trim leading slash then compose local URL
  TRIMMED="${INPUT_PATH_OR_URL#/}"
  URL="http://localhost:${N8N_PORT}/webhook/${TRIMMED}"
fi

FLAGS=(-sS -X POST)
# Prevent Raycast UI freeze on slow endpoints
CURL_MAX_TIME="${CURL_MAX_TIME:-10}"
FLAGS+=(--max-time "$CURL_MAX_TIME" --connect-timeout 5)
if [ -n "$PAYLOAD" ]; then
  FLAGS+=(-H "Content-Type: application/json" --data "$PAYLOAD")
fi

TMP_BODY_FILE="$(mktemp -t raycast-n8n-body.XXXXXX)"
HTTP_STATUS="$(curl -o "$TMP_BODY_FILE" -w "%{http_code}" "${FLAGS[@]}" "$URL" || true)"

if [[ "$HTTP_STATUS" =~ ^2 ]]; then
  echo "✅ Triggered: $URL"
  # Limit output size to keep Raycast UI snappy
  head -c 5000 "$TMP_BODY_FILE" || true
  rm -f "$TMP_BODY_FILE"
  exit 0
else
  echo "❌ Failed ($HTTP_STATUS) => $URL" >&2
  cat "$TMP_BODY_FILE" >&2 || true
  rm -f "$TMP_BODY_FILE"
  exit 1
fi
