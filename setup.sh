#!/bin/bash

# 🚀 Claude Code テンプレート - 初期セットアップスクリプト
# このスクリプトは1回だけ実行すればOKです

echo "========================================="
echo "📦 Claude Code テンプレートのセットアップ"
echo "========================================="
echo ""

# 色の定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 必要なツールの確認
echo "1️⃣  必要なツールを確認中..."

# Node.jsの確認
if command -v node &> /dev/null; then
    echo -e "${GREEN}✅ Node.js がインストールされています${NC}"
else
    echo -e "${YELLOW}⚠️  Node.js がインストールされていません${NC}"
    echo "   👉 https://nodejs.org/ からインストールしてください"
fi

# Pythonの確認
if command -v python3 &> /dev/null; then
    echo -e "${GREEN}✅ Python3 がインストールされています${NC}"
else
    echo -e "${YELLOW}⚠️  Python3 がインストールされていません${NC}"
    echo "   👉 https://www.python.org/ からインストールしてください"
fi

# Gitの確認
if command -v git &> /dev/null; then
    echo -e "${GREEN}✅ Git がインストールされています${NC}"
else
    echo -e "${YELLOW}⚠️  Git がインストールされていません${NC}"
    echo "   👉 https://git-scm.com/ からインストールしてください"
fi

echo ""
echo "2️⃣  Python仮想環境を作成中..."

# Python仮想環境の作成
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Python仮想環境を作成しました${NC}"
else
    echo -e "${YELLOW}ℹ️  Python仮想環境は既に存在します${NC}"
fi

# 仮想環境の有効化
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

echo ""
echo "3️⃣  必要なパッケージをインストール中..."

# requirements.txtが存在する場合はインストール
if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt
    echo -e "${GREEN}✅ Pythonパッケージをインストールしました${NC}"
fi

# package.jsonが存在する場合はインストール
if [ -f "package.json" ]; then
    npm install --silent
    echo -e "${GREEN}✅ Node.jsパッケージをインストールしました${NC}"
fi

echo ""
echo "4️⃣  環境変数ファイルを作成中..."

# .envファイルの作成（存在しない場合）
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# 🔐 環境変数設定ファイル
# 各サービスのAPIキーをここに設定してください

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic (Claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# GitHub
GITHUB_TOKEN=your_github_token_here

# n8n
N8N_WEBHOOK_URL=https://your-n8n-instance.app/webhook/xxx
N8N_API_KEY=your_n8n_api_key_here

# Supabase
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here

# Firebase
FIREBASE_API_KEY=your_firebase_api_key_here
FIREBASE_PROJECT_ID=your_firebase_project_id_here

# Vercel
VERCEL_TOKEN=your_vercel_token_here

# Brave Search
BRAVE_API_KEY=your_brave_api_key_here

# Firecrawl
FIRECRAWL_API_KEY=your_firecrawl_api_key_here
EOF
    echo -e "${GREEN}✅ .envファイルを作成しました${NC}"
    echo -e "${YELLOW}   👉 .envファイルを開いて、必要なAPIキーを設定してください${NC}"
else
    echo -e "${YELLOW}ℹ️  .envファイルは既に存在します${NC}"
fi

# .env.mcpファイルの作成（存在しない場合）
if [ ! -f ".env.mcp" ]; then
    cp .env .env.mcp
    echo -e "${GREEN}✅ .env.mcpファイルを作成しました${NC}"
else
    echo -e "${YELLOW}ℹ️  .env.mcpファイルは既に存在します${NC}"
fi

echo ""
echo "5️⃣  スクリプトに実行権限を付与中..."

# スクリプトに実行権限を付与
chmod +x scripts/raycast/*.sh 2>/dev/null
chmod +x scripts/*.sh 2>/dev/null
echo -e "${GREEN}✅ スクリプトに実行権限を付与しました${NC}"

echo ""
echo "6️⃣  Gitの初期設定..."

# Gitリポジトリの初期化（まだの場合）
if [ ! -d ".git" ]; then
    git init
    echo -e "${GREEN}✅ Gitリポジトリを初期化しました${NC}"
else
    echo -e "${YELLOW}ℹ️  Gitリポジトリは既に初期化されています${NC}"
fi

# .gitignoreの確認
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# 環境変数
.env
.env.mcp
.env.local

# Python
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.egg-info/

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# ビルドファイル
dist/
build/
*.log

# 一時ファイル
tmp/
temp/
EOF
    echo -e "${GREEN}✅ .gitignoreファイルを作成しました${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}🎉 セットアップが完了しました！${NC}"
echo "========================================="
echo ""
echo "📝 次のステップ:"
echo "1. .envファイルを開いて必要なAPIキーを設定"
echo "2. Cursorでプロジェクトを開く: code ."
echo "3. docs/README_初めに.md を読む"
echo ""
echo "💡 ヒント:"
echo "- わからないことがあったら Claude (Cmd+L) に聞いてください"
echo "- examples/ フォルダにサンプルコードがあります"
echo ""
echo "頑張ってください！🚀"
