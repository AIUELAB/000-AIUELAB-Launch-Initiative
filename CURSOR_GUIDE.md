# 🎯 Cursor × Claude Code 完全ガイド

## 📋 プロジェクト概要

**このプロジェクトはCursorでClaude Codeを使用するための最上位テンプレートです。**

- **統合済みMCPサーバー**: 25以上のMCPサーバーがすぐに利用可能
- **Python開発環境**: 仮想環境とツールチェーン完備
- **自動化**: Makefile、Pre-commit hooks、CI/CD設定済み
- **2025年ベストプラクティス**: 最新のClaude Code機能に対応

## 🚀 クイックスタート（Cursor向け）

### 1. Cursorでプロジェクトを開く

```bash
# Cursorでプロジェクトを開く
cursor .
```

### 2. 環境変数の設定

```bash
# 環境変数ファイルをコピー
cp .env.mcp.example .env.mcp

# .env.mcpを編集してAPIキーを設定
# 最低限必要：
# - GITHUB_TOKEN
# - BRAVE_API_KEY
```

### 3. Claude Codeセッション開始

```bash
# Claude Codeを起動
claude

# MCPサーバーの確認
/mcp
```

## 💡 Cursor固有の使い方

### AI機能の活用

1. **Cmd+K**: AIによるコード生成
2. **Cmd+L**: AIチャット開始
3. **Cmd+Shift+L**: コンテキスト付きチャット

### Claude CodeとCursorの連携

```bash
# CursorのターミナルでClaude Codeを起動
claude

# MCPサーバーを使った開発例
"Serenaでcalculate_sum関数の定義を探して"
"GitHubで最新のPRをレビューして"
"Brave Searchで最新のPython MCPチュートリアルを検索"
```

### 推奨ワークフロー

1. **コード探索**: Serena MCPで高度なコード検索
2. **変更実装**: CursorのAI機能でコード生成
3. **テスト実行**: `make test`でテスト
4. **品質チェック**: `make pre-commit`で品質確認
5. **コミット**: GitHubと連携して自動コミット

## 🛠️ よく使うコマンド

### Makefile タスク

```bash
# プロジェクトセットアップ
make setup

# コードフォーマット
make format

# テスト実行
make test

# 全チェック実行
make all

# APIキー読み込み
make load-keys
```

### MCP操作

```bash
# MCPサーバー一覧
/mcp

# Serenaでコード検索
"Serenaで[関数名]の定義を探して"

# GitHub操作
"GitHubでissue #123の詳細を表示"

# Web検索
"Brave Searchで[検索語]を検索"
```

## 📂 プロジェクト構造

```
claude-code-template-mcp/
├── .vscode/               # Cursor/VSCode設定
│   ├── settings.json      # エディタ設定（Cursor最適化済み）
│   ├── tasks.json         # タスク定義
│   └── extensions.json    # 推奨拡張機能
├── mcp-config/            # MCP設定
│   ├── profiles/          # 3段階のプロファイル
│   │   ├── minimal.json   # 最小構成
│   │   ├── standard.json  # 標準構成
│   │   └── full.json      # フル構成
│   └── setup-mcp.sh       # セットアップスクリプト
├── src/                   # ソースコード
├── tests/                 # テストコード
├── scripts/               # ユーティリティ
├── CLAUDE.md              # Claude向け指示書
├── CURSOR_GUIDE.md        # このファイル
└── Makefile               # タスク自動化
```

## 🎨 Cursor設定のカスタマイズ

### 推奨設定（.vscode/settings.json）

- **自動保存**: 1秒後に自動保存
- **フォーマット**: 保存時に自動フォーマット
- **Python**: Ruffによる高速リント
- **Git**: スマートコミット有効
- **ターミナル**: GPU加速有効

### キーボードショートカット

| コマンド | 説明 |
|---------|------|
| `Cmd+K` | AI生成 |
| `Cmd+L` | AIチャット |
| `Cmd+Shift+P` | コマンドパレット |
| `Cmd+P` | ファイル検索 |
| `Cmd+Shift+F` | プロジェクト内検索 |

## 🔧 トラブルシューティング

### Claude Codeが起動しない

```bash
# Node.jsバージョン確認（18以上必要）
node --version

# Claude Codeの再インストール
npm install -g @anthropic/claude-cli
```

### MCPサーバーが動作しない

```bash
# MCP設定の検証
make validate-mcp

# MCPサーバーの再セットアップ
cd mcp-config && bash setup-mcp.sh
```

### Python環境エラー

```bash
# 仮想環境の再作成
rm -rf venv
make setup
```

## 📚 参考リンク

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Cursor Documentation](https://cursor.sh/docs)

## 🎯 次のステップ

1. **APIキーの設定**: `.env.mcp`にAPIキーを設定
2. **MCPプロファイル選択**: minimal/standard/fullから選択
3. **コード実装開始**: CursorとClaude Codeを活用した開発
4. **CI/CD設定**: GitHub Actionsでの自動化

## 💪 ベストプラクティス

1. **CLAUDE.mdを常に最新に**: プロジェクト固有の指示を記載
2. **PROJECT_STATUS.mdで進捗管理**: セッション間の継続性確保
3. **Makefileを活用**: 反復タスクの自動化
4. **MCPサーバーを適切に選択**: タスクに応じた最適なサーバー使用
5. **定期的なテスト実行**: `make test`で品質維持

---

**Happy Coding with Cursor × Claude Code! 🚀**