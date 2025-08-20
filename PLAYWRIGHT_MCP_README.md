# 🎭 Playwright MCP Server 導入ガイド

## 概要

Playwright MCPサーバーは、ブラウザ自動化機能を提供するModel Context Protocol（MCP）サーバーです。このサーバーを使用すると、Claude CodeなどのLLMがWebページと直接対話できるようになります。

### 主な特徴

- **高速で軽量**: スクリーンショットではなく、Playwrightのアクセシビリティツリーを使用
- **LLMフレンドリー**: ビジョンモデル不要、構造化データのみで動作
- **確実なツール適用**: スクリーンショットベースのアプローチにありがちな曖昧さを回避

## 📋 要件

- Node.js 18以上
- VS Code、Cursor、Claude Desktop、または他のMCPクライアント

## 🚀 クイックスタート

### 1. セットアップスクリプトの実行

```bash
# セットアップスクリプトを実行
bash scripts/setup-playwright-mcp.sh
```

このスクリプトは以下を実行します：

- Node.jsとnpmの確認
- Playwright MCPサーバーのインストール
- Playwrightブラウザ（Chromium、Firefox、WebKit）のインストール
- 出力ディレクトリの作成

### 2. MCPクライアントの設定

#### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` に以下を追加：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

#### VS Code / Cursor

設定から MCP → 新しいMCPサーバーを追加：

- 名前: `playwright`
- コマンド: `npx @playwright/mcp@latest`

#### Claude Code CLI

```bash
claude mcp add playwright npx @playwright/mcp@latest
```

## 📚 使用例

### 基本的なナビゲーション

```python
# URLへ移動
"browser_navigate でhttps://www.google.comを開いて"

# ページ構造を取得
"browser_snapshot でページの構造を見せて"

# スクリーンショット取得
"browser_take_screenshot でスクリーンショットを撮って"
```

### フォーム操作

```python
# テキスト入力
"browser_type で検索ボックスに'Playwright MCP'と入力"

# ボタンクリック
"browser_click で送信ボタンをクリック"

# ドロップダウン選択
"browser_select_option で国のドロップダウンから'Japan'を選択"
```

### 高度な操作

```python
# JavaScript実行
"browser_evaluate で全ての記事タイトルを取得"

# マルチタブ操作
"browser_tab_new で新しいタブを開く"
"browser_tab_list でタブ一覧を表示"
"browser_tab_select でインデックス0のタブに切り替え"

# ファイルアップロード
"browser_file_upload で/path/to/file.pdfをアップロード"

# PDF生成（要 --caps=pdf）
"browser_pdf_save でページをPDFとして保存"
```

## 🛠️ 設定オプション

### 基本設定（mcp-config.json）

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

### ヘッドレスモード

```json
{
  "mcpServers": {
    "playwright-headless": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--headless"
      ]
    }
  }
}
```

### 高度な設定

```json
{
  "mcpServers": {
    "playwright-advanced": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--browser=chrome",
        "--headless",
        "--caps=vision,pdf",
        "--output-dir=./playwright-output",
        "--viewport-size=1920,1080"
      ]
    }
  }
}
```

## 📋 利用可能なツール

### コア自動化ツール

- `browser_navigate` - URLへ移動
- `browser_snapshot` - ページ構造を取得（アクセシビリティツリー）
- `browser_click` - 要素をクリック
- `browser_type` - テキスト入力
- `browser_press_key` - キー押下
- `browser_select_option` - ドロップダウン選択
- `browser_drag` - ドラッグ&ドロップ
- `browser_hover` - ホバー
- `browser_evaluate` - JavaScript実行
- `browser_wait_for` - 待機

### ナビゲーション

- `browser_navigate_back` - 前のページへ
- `browser_navigate_forward` - 次のページへ

### スクリーンショット & 記録

- `browser_take_screenshot` - スクリーンショット取得
- `browser_pdf_save` - PDF保存（要 --caps=pdf）

### タブ管理

- `browser_tab_list` - タブ一覧
- `browser_tab_new` - 新規タブ
- `browser_tab_select` - タブ選択
- `browser_tab_close` - タブを閉じる

### デバッグ

- `browser_network_requests` - ネットワークリクエスト一覧
- `browser_console_messages` - コンソールメッセージ取得

### その他

- `browser_handle_dialog` - ダイアログ処理
- `browser_file_upload` - ファイルアップロード
- `browser_resize` - ウィンドウサイズ変更
- `browser_close` - ブラウザを閉じる

## 🔍 サンプルコードの実行

```bash
# Python仮想環境の有効化
source venv/bin/activate

# サンプルコードの実行
python src/playwright_mcp_examples.py
```

このサンプルコードには以下の例が含まれています：

- 基本的なナビゲーション
- フォーム操作
- Webスクレイピング
- マルチタブ操作
- 高度なインタラクション

## 🐛 トラブルシューティング

### ブラウザがインストールされていない

```bash
npx playwright install
```

### MCPサーバーが見つからない

```bash
npm install -g @playwright/mcp@latest
```

### ヘッドレスモードで動作しない

一部のサイトはヘッドレスモードを検出してブロックすることがあります。その場合は通常モードを使用してください。

### スクリーンショットが保存されない

`--output-dir` パラメータで出力ディレクトリを指定してください：

```json
"args": [
  "@playwright/mcp@latest",
  "--output-dir=./playwright-output"
]
```

## 📖 参考資料

- [Playwright MCP GitHub](https://github.com/microsoft/playwright-mcp)
- [Playwright Documentation](https://playwright.dev)
- [Model Context Protocol](https://modelcontextprotocol.io)

## 💡 Tips

1. **アクセシビリティツリーの活用**: `browser_snapshot`を使用してページ構造を理解し、適切な要素を特定
2. **待機の重要性**: 動的コンテンツには`browser_wait_for`を使用
3. **エラーハンドリング**: `browser_console_messages`でJavaScriptエラーを確認
4. **ネットワーク監視**: `browser_network_requests`でAPIコールを追跡
5. **マルチタブの活用**: 複数のページを並行して操作する際は`browser_tab_*`ツールを使用

## 🎉 さあ、始めましょう

Playwright MCPサーバーを使って、Webの自動化とテストを始めましょう。質問や問題がある場合は、GitHubのIssueを作成してください。
