#!/usr/bin/env bash
# shellcheck shell=bash

# 安全設定
set -euo pipefail
IFS=$'\n\t'

# ヘルプ
usage() {
	cat <<'EOF'
Usage: scripts/setup-n8n.sh [options]

Options:
  -n, --name NAME         PROJECT_NAME を指定（未指定時はディレクトリ名）
  -p, --port PORT         N8N_PORT を指定（未指定時は自動割当 5678+）
      --user USER         N8N_USER を指定（既定: admin）
      --password PASS     N8N_PASSWORD を指定（既定: password）
      --non-interactive   完全自動（入力なし）
      --force             既存 .env.n8n を上書き/更新（キー単位）
  -h, --help              このヘルプを表示

本スクリプトは以下を行います：
- 未使用ポートの自動検出（5678 から順に）
- ルート直下の .env.n8n を作成/更新（PROJECT_NAME, N8N_PORT など）
- Raycast の設定は変更しないため、出力の baseUrl を Raycast に手動反映してください
EOF
}

# ルート検出
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_PATH="${ROOT_DIR}/.env.n8n"

# 依存コマンド存在確認
command_exists() { command -v "$1" >/dev/null 2>&1; }

# ポート使用確認（macOS 対応）
is_port_in_use() {
	local port="$1"
	if command_exists nc; then
		# macOS の nc は -G でタイムアウト指定可能
		if nc -z -G 1 localhost "$port" >/dev/null 2>&1; then
			return 0
		else
			return 1
		fi
	elif command_exists lsof; then
		if lsof -iTCP -sTCP:LISTEN -n -P | grep -q ":${port} "; then
			return 0
		else
			return 1
		fi
	else
		# 確認不可の場合は未使用扱い（保守的に継続）
		return 1
	fi
}

find_free_port() {
	local start_port="${1:-5678}"
	local max_port=$((start_port + 200))
	local p
	for ((p=start_port; p<=max_port; p++)); do
		if ! is_port_in_use "$p"; then
			echo "$p"
			return 0
		fi
	done
	echo "" # 見つからない場合は空
	return 1
}

# sed インライン置換（mac/GNU 両対応）
sed_inplace() {
	local pattern="$1" file="$2"
	if sed --version >/dev/null 2>&1; then
		# GNU sed
		sed -i -e "$pattern" "$file"
	else
		# BSD/macOS sed
		sed -i '' -e "$pattern" "$file"
	fi
}

# .env 行の upsert
upsert_env_var() {
	local key="$1" value="$2" file="$3"
	if [ -f "$file" ] && grep -q "^${key}=" "$file"; then
		# 既存キーを置換
		sed_inplace "s|^${key}=.*|${key}=${value}|" "$file"
	else
		# 末尾に追記（ファイルが無ければ先に作成）
		if [ ! -f "$file" ]; then
			touch "$file"
		fi
		printf '%s\n' "${key}=${value}" >>"$file"
	fi
}

# デフォルト値
PROJECT_NAME_DEFAULT="$(basename "$ROOT_DIR")"
N8N_USER_DEFAULT="admin"
N8N_PASSWORD_DEFAULT="password"
START_PORT_DEFAULT=5678

# 引数処理
PROJECT_NAME="$PROJECT_NAME_DEFAULT"
N8N_PORT=""
N8N_USER="$N8N_USER_DEFAULT"
N8N_PASSWORD="$N8N_PASSWORD_DEFAULT"
NON_INTERACTIVE=false
FORCE=false

while [ $# -gt 0 ]; do
	case "$1" in
		-n|--name)
			PROJECT_NAME="$2"; shift 2;;
		-p|--port)
			N8N_PORT="$2"; shift 2;;
		--user)
			N8N_USER="$2"; shift 2;;
		--password)
			N8N_PASSWORD="$2"; shift 2;;
		--non-interactive)
			NON_INTERACTIVE=true; shift;;
		--force)
			FORCE=true; shift;;
		-h|--help)
			usage; exit 0;;
		*)
			echo "Unknown option: $1" >&2
			usage; exit 1;;
	esac
done

# PORT 自動割当
if [ -z "${N8N_PORT}" ]; then
	N8N_PORT="$(find_free_port "$START_PORT_DEFAULT" || true)"
	if [ -z "$N8N_PORT" ]; then
		echo "未使用ポートが見つかりませんでした。--port で指定してください" >&2
		exit 1
	fi
fi

# .env.n8n の生成/更新
if [ ! -f "$ENV_PATH" ]; then
	printf '%s\n' "Creating $ENV_PATH"
	touch "$ENV_PATH"
fi

# FORCE 指定なしでもキー単位で上書き（使い回し時の衝突回避のため）
upsert_env_var "PROJECT_NAME" "$PROJECT_NAME" "$ENV_PATH"
upsert_env_var "N8N_PORT" "$N8N_PORT" "$ENV_PATH"
upsert_env_var "N8N_USER" "$N8N_USER" "$ENV_PATH"
upsert_env_var "N8N_PASSWORD" "$N8N_PASSWORD" "$ENV_PATH"
upsert_env_var "DB_SQLITE_POOL_SIZE" "5" "$ENV_PATH"
upsert_env_var "N8N_RUNNERS_ENABLED" "true" "$ENV_PATH"
upsert_env_var "N8N_ENFORCE_SETTINGS_FILE_PERMISSIONS" "true" "$ENV_PATH"

# 結果表示
cat <<EOF

✅ .env.n8n を更新しました:
- PROJECT_NAME=${PROJECT_NAME}
- N8N_PORT=${N8N_PORT}
- N8N_USER=${N8N_USER}
- N8N_PASSWORD=(hidden)
- OPTIONS: non_interactive=${NON_INTERACTIVE}, force=${FORCE}

次の手順:
1) 起動:   npm run n8n:start
2) Raycast: 拡張の Preferences で baseUrl を http://localhost:${N8N_PORT} に設定
3) 実行:   Raycast から Webhook を実行して確認

ヒント:
- スクリプトコマンド利用時は N8N_BASE_URL を環境に設定可能:
    export N8N_BASE_URL="http://localhost:${N8N_PORT}"
- 秘密鍵/認証情報は /Users/admin/Documents/key を利用（推奨、リポジトリ外）

EOF

exit 0
