#!/bin/zsh
set -euo pipefail

# ===== Session Status Automation for zsh =====
# - Collects per-session commands via preexec hook
# - On shell exit, appends a session summary to PROJECT_STATUS.md
# - Optional draft helpers: session_task/session_done/session_todo/session_decision/session_approach

# Guard: install only once per shell
if [ -n "${__CC_SESSION_STATUS_INSTALLED-}" ]; then
	return 0
fi
export __CC_SESSION_STATUS_INSTALLED=1

__cc_now_iso() {
	date -Is 2>/dev/null || date "+%Y-%m-%dT%H:%M:%S%z"
}

__cc_find_repo_root() {
	local top
	if top=$(git rev-parse --show-toplevel 2>/dev/null); then
		print -r -- "$top"
		return 0
	fi
	# Fallback: search upward for PROJECT_STATUS.md
	local dir="$PWD"
	while [ "$dir" != "/" ]; do
		if [ -f "$dir/PROJECT_STATUS.md" ]; then
			print -r -- "$dir"
			return 0
		fi
		dir=$(dirname "$dir")
	done
	# Default to template repo if present
	if [ -d "/Users/admin/Documents/Cursor/claude-code-template" ]; then
		print -r -- "/Users/admin/Documents/Cursor/claude-code-template"
		return 0
	fi
	print -r -- "$PWD"
}

__cc_init_session_vars() {
	export CC_SESSION_START_TS="${CC_SESSION_START_TS-$(__cc_now_iso)}"
	export CC_SESSION_ID="${CC_SESSION_ID-$$}"
	export CC_REPO_ROOT="${CC_REPO_ROOT-$(__cc_find_repo_root)}"
	export CC_SESSION_DIR="${CC_SESSION_DIR-"$CC_REPO_ROOT/.session"}"
	mkdir -p "$CC_SESSION_DIR"
	export CC_SESSION_CMD_LOG="${CC_SESSION_CMD_LOG-"$CC_SESSION_DIR/cmds.$CC_SESSION_ID.log"}"
	: >| "$CC_SESSION_CMD_LOG"
}

__cc_init_session_vars

# -------- Helpers to manage draft fields during the session --------
session_task() {
	# usage: session_task "説明"
	print -r -- "$*" >| "$CC_SESSION_DIR/task.$CC_SESSION_ID.txt"
}
session_done() {
	# usage: session_done "完了項目"
	print -r -- "- $*" >> "$CC_SESSION_DIR/done.$CC_SESSION_ID.txt"
}
session_todo() {
	# usage: session_todo "未完了項目"
	print -r -- "- $*" >> "$CC_SESSION_DIR/todo.$CC_SESSION_ID.txt"
}
session_decision() {
	# usage: session_decision "決定/仕様"
	print -r -- "- $*" >> "$CC_SESSION_DIR/decisions.$CC_SESSION_ID.txt"
}
session_approach() {
	# usage: session_approach "アプローチ/戦略"
	print -r -- "- $*" >> "$CC_SESSION_DIR/approach.$CC_SESSION_ID.txt"
}

# -------- MCP Status Check --------
mcp_status() {
	echo "🔍 MCP Server Status Check"
	echo "========================="
	
	# Check if MCP servers are configured
	local mcp_config="${CC_REPO_ROOT}/mcp-config/claude_desktop_config.json"
	if [ -f "$mcp_config" ]; then
		echo "✅ MCP設定ファイル: 存在"
	else
		echo "❌ MCP設定ファイル: 不明"
	fi
	
	# Check GitHub MCP
	local github_mcp="${CC_REPO_ROOT}/bin/github-mcp"
	if [ -f "$github_mcp" ]; then
		echo "✅ GitHub MCP: インストール済み"
	else
		echo "❌ GitHub MCP: 未インストール"
	fi
	
	# Check Node.js MCP servers
	echo -e "\n📦 MCPサーバー (npm global):"
	npm list -g --depth=0 2>/dev/null | grep -E "@modelcontextprotocol|@mcp" || echo "  なし"
	
	# Check environment variables
	echo -e "\n🔑 環境変数:"
	[ -n "${GITHUB_PAT-}" ] && echo "  ✅ GITHUB_PAT: 設定済み" || echo "  ⚠️  GITHUB_PAT: 未設定"
	[ -n "${OPENAI_API_KEY-}" ] && echo "  ✅ OPENAI_API_KEY: 設定済み" || echo "  ⚠️  OPENAI_API_KEY: 未設定"
	[ -n "${ANTHROPIC_API_KEY-}" ] && echo "  ✅ ANTHROPIC_API_KEY: 設定済み" || echo "  ⚠️  ANTHROPIC_API_KEY: 未設定"
}

# -------- Project Status Check --------
project_status() {
	echo "📊 Project Status"
	echo "================"
	
	# Python environment
	echo -e "\n🐍 Python環境:"
	python --version 2>&1 | head -1
	echo "  仮想環境: ${VIRTUAL_ENV:-未アクティブ}"
	
	# Git status
	echo -e "\n📝 Git状態:"
	git status --short 2>/dev/null | head -5 || echo "  Gitリポジトリではありません"
	
	# Test coverage
	if [ -f "${CC_REPO_ROOT}/.coverage" ]; then
		echo -e "\n✅ テストカバレッジ:"
		python -m coverage report --skip-covered 2>/dev/null | tail -3 || echo "  カバレッジ情報なし"
	fi
}

# -------- Hooks --------
__cc_preexec() {
	local cmd_ts; cmd_ts=$(date "+%Y-%m-%d %H:%M:%S")
	print -r -- "[$cmd_ts] $1" >> "$CC_SESSION_CMD_LOG"
}

__cc_zshexit() {
	set +e
	local repo_root="$(__cc_find_repo_root)"
	local status_md="$repo_root/PROJECT_STATUS.md"
	local now_dh; now_dh=$(date "+%Y-%m-%d %H:%M:%S")
	local today; today=$(date "+%Y-%m-%d")

	# Read drafts if exist
	local task_file="$CC_SESSION_DIR/task.$CC_SESSION_ID.txt"
	local done_file="$CC_SESSION_DIR/done.$CC_SESSION_ID.txt"
	local todo_file="$CC_SESSION_DIR/todo.$CC_SESSION_ID.txt"
	local decisions_file="$CC_SESSION_DIR/decisions.$CC_SESSION_ID.txt"
	local approach_file="$CC_SESSION_DIR/approach.$CC_SESSION_ID.txt"

	local task_desc="未記載"
	[ -s "$task_file" ] && task_desc=$(cat "$task_file")

	# Optional interactive prompts if enabled and attached to a TTY
	if [ "${CC_STATUS_INTERACTIVE-0}" = "1" ] && [ -t 0 ]; then
		if [ ! -s "$task_file" ]; then
			print -n -- "現在のタスク内容を入力（空でスキップ）: "
			read -r _in || true
			if [ -n "${_in}" ]; then
				print -r -- "${_in}" >| "$task_file"; task_desc="$__in"
			fi
		fi
		if [ ! -s "$done_file" ]; then
			print -n -- "完了した作業（箇条書き可、空でスキップ）: "
			read -r _in || true
			[ -n "${_in}" ] && print -r -- "- ${_in}" >| "$done_file"
		fi
		if [ ! -s "$todo_file" ]; then
			print -n -- "未完了の作業（箇条書き可、空でスキップ）: "
			read -r _in || true
			[ -n "${_in}" ] && print -r -- "- ${_in}" >| "$todo_file"
		fi
		if [ ! -s "$decisions_file" ]; then
			print -n -- "重要な決定事項/仕様（箇条書き可、空でスキップ）: "
			read -r _in || true
			[ -n "${_in}" ] && print -r -- "- ${_in}" >| "$decisions_file"
		fi
		if [ ! -s "$approach_file" ]; then
			print -n -- "使用したアプローチ/戦略（箇条書き可、空でスキップ）: "
			read -r _in || true
			[ -n "${_in}" ] && print -r -- "- ${_in}" >| "$approach_file"
		fi
		[ -s "$task_file" ] && task_desc=$(cat "$task_file")
	fi

	# Ensure header exists
	if [ ! -f "$status_md" ]; then
		cat > "$status_md" <<'HDR'
# プロジェクト状態管理ファイル

## 📋 プロジェクト概要
（必要に応じて記載）

## 📅 セッション記録
HDR
	else
		# add section header if missing
		if ! grep -q "^## 📅 セッション記録" "$status_md"; then
			echo "
## 📅 セッション記録" >> "$status_md"
		fi
	fi

	{
		print -r -- "\n### ${today} セッション (自動保存)"
		print -r -- "- **作業内容**: ${task_desc}"
		print -r -- "- **成果（完了）**:"
		if [ -s "$done_file" ]; then
			cat "$done_file"
		else
			print -r -- "  - 未記載"
		fi
		print -r -- "- **未完了**:"
		if [ -s "$todo_file" ]; then
			cat "$todo_file"
		else
			print -r -- "  - 未記載"
		fi
		print -r -- "- **重要な決定事項・仕様**:"
		if [ -s "$decisions_file" ]; then
			cat "$decisions_file"
		else
			print -r -- "  - 未記載"
		fi
		print -r -- "- **使用した主なコマンド/アプローチ**:"
		if [ -s "$approach_file" ]; then
			cat "$approach_file"
		fi
		# Commands (last 30 unique-ish)
		if [ -s "$CC_SESSION_CMD_LOG" ]; then
			print -r -- "\n```bash"
			# filter trivial sourcing of this script and duplicates
			sed 's/^\[[^]]*\] //g' "$CC_SESSION_CMD_LOG" \
				| grep -v "session-status.zsh" \
				| awk '!(seen[$0]++)' \
				| tail -n 30
			print -r -- "```"
		fi
		print -r -- "\n(自動保存: ${now_dh})"
	} >> "$status_md"

	# Cleanup drafts for this session
	rm -f "$task_file" "$done_file" "$todo_file" "$decisions_file" "$approach_file" 2>/dev/null || true
}

# Install hooks
if typeset -f add-zsh-hook >/dev/null 2>&1; then
	add-zsh-hook preexec __cc_preexec
	add-zsh-hook zshexit __cc_zshexit
else
	# Fallback to function names
	preexec() { __cc_preexec "$@"; }
	TRAPEXIT() { __cc_zshexit; }
fi

# Quiet
:


