#!/bin/bash

# =====================================================
# Playwright MCP Server Setup Script
# =====================================================

set -e  # エラーが発生したら停止

# カラー定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ヘッダー表示
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}   Playwright MCP Server セットアップスクリプト   ${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Node.jsの確認
echo -e "${YELLOW}📦 Node.jsの確認...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.jsがインストールされていません。${NC}"
    echo "Node.js 18以上をインストールしてください。"
    echo "https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}❌ Node.jsのバージョンが古いです。${NC}"
    echo "Node.js 18以上が必要です。"
    exit 1
fi
echo -e "${GREEN}✅ Node.js $(node -v) が見つかりました${NC}"

# npmの確認
echo -e "${YELLOW}📦 npmの確認...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npmがインストールされていません。${NC}"
    exit 1
fi
echo -e "${GREEN}✅ npm $(npm -v) が見つかりました${NC}"

# Playwright MCPサーバーのインストール
echo ""
echo -e "${YELLOW}🎭 Playwright MCPサーバーのインストール...${NC}"

# グローバルインストール（推奨）
echo -e "${BLUE}グローバルインストールを実行します...${NC}"
npm install -g @playwright/mcp@latest

# 成功確認
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Playwright MCPサーバーが正常にインストールされました${NC}"
else
    echo -e "${RED}❌ インストールに失敗しました${NC}"
    exit 1
fi

# Playwrightブラウザのインストール
echo ""
echo -e "${YELLOW}🌐 Playwrightブラウザのインストール...${NC}"
echo -e "${BLUE}Chromium、Firefox、WebKitをインストールします...${NC}"
npx playwright install

# 設定ファイルの確認
echo ""
echo -e "${YELLOW}⚙️  MCP設定ファイルの確認...${NC}"

if [ -f "mcp-config.json" ]; then
    echo -e "${GREEN}✅ mcp-config.json が見つかりました${NC}"
else
    echo -e "${YELLOW}⚠️  mcp-config.json が見つかりません${NC}"
    echo "mcp-config.json.example から作成します..."

    if [ -f "mcp-config.json.example" ]; then
        cp mcp-config.json.example mcp-config.json
        echo -e "${GREEN}✅ mcp-config.json を作成しました${NC}"
    else
        echo -e "${BLUE}ℹ️  標準的なmcp-config.jsonを作成します${NC}"
        cat > mcp-config.json << 'EOF'
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest"
      ]
    }
  }
}
EOF
        echo -e "${GREEN}✅ mcp-config.json を作成しました${NC}"
    fi
fi

# 出力ディレクトリの作成
echo ""
echo -e "${YELLOW}📁 出力ディレクトリの作成...${NC}"
mkdir -p playwright-output
echo -e "${GREEN}✅ playwright-output ディレクトリを作成しました${NC}"

# 使用方法の表示
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${GREEN}🎉 セットアップが完了しました！${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}📝 使用方法:${NC}"
echo ""
echo "1. Claude DesktopまたはVS Codeの設定で、以下のMCPサーバーを追加:"
echo -e "${BLUE}   mcp-config.json の内容を参照${NC}"
echo ""
echo "2. 基本的な使用例:"
echo "   - browser_navigate: URLへ移動"
echo "   - browser_snapshot: ページの構造を取得"
echo "   - browser_click: 要素をクリック"
echo "   - browser_type: テキスト入力"
echo "   - browser_take_screenshot: スクリーンショット取得"
echo ""
echo "3. 高度な設定オプション:"
echo "   --headless: ヘッドレスモード"
echo "   --browser=chrome: ブラウザ指定"
echo "   --caps=vision,pdf: 追加機能有効化"
echo "   --output-dir=./path: 出力ディレクトリ指定"
echo ""
echo -e "${YELLOW}📚 詳細なドキュメント:${NC}"
echo "   https://github.com/microsoft/playwright-mcp"
echo ""
echo -e "${GREEN}✨ Happy Testing with Playwright MCP! ✨${NC}"
