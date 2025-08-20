# Claude Code MCP テンプレートプロジェクト 🏆 v2.0

<!-- cSpell:words Ollama mkdocstrings isort numpy Docstrings firecrawl pytest Apidog venv myuser myrepo modelcontextprotocol FIRECRAWL -->

<!-- Security Badges -->
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/[YOUR_USERNAME]/claude-code-template-mcp/badge)](https://securityscorecards.dev/viewer/?uri=github.com/[YOUR_USERNAME]/claude-code-template-mcp)
[![CodeQL](https://github.com/[YOUR_USERNAME]/claude-code-template-mcp/workflows/CodeQL/badge.svg)](https://github.com/[YOUR_USERNAME]/claude-code-template-mcp/security/code-scanning)
[![Gitleaks](https://github.com/[YOUR_USERNAME]/claude-code-template-mcp/workflows/Gitleaks%20Secret%20Detection/badge.svg)](https://github.com/[YOUR_USERNAME]/claude-code-template-mcp/actions/workflows/gitleaks.yml)
[![SBOM](https://github.com/[YOUR_USERNAME]/claude-code-template-mcp/workflows/SBOM%20Generation%20and%20Vulnerability%20Scan/badge.svg)](https://github.com/[YOUR_USERNAME]/claude-code-template-mcp/actions/workflows/sbom.yml)
[![Renovate](https://img.shields.io/badge/renovate-enabled-brightgreen.svg)](https://renovatebot.com)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/[YOUR_USERNAME]/claude-code-template-mcp/main.svg)](https://results.pre-commit.ci/latest/github/[YOUR_USERNAME]/claude-code-template-mcp/main)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**2025年最新ベストプラクティス対応**のClaude Codeプロジェクトテンプレートです。GitHub、Web検索、ブラウザ自動化、クラウドサービス連携など、25以上のMCPサーバーがすぐに使えます。

## 🆕 v2.0 新機能（2025年8月）

- 🤖 **Ollama統合** - 完全無料のローカルLLM（APIキー不要、DeepSeek-R1/Llama3対応）
- 📚 **MkDocs自動ドキュメント** - mkdocstringsでコードから直接APIドキュメント生成
- ⚡ **Ruff統一** - Black/isort/flake8を統合した高速リンター（実行速度10倍）
- 🎯 **最適化された依存関係** - pandas/numpy等削除で50%軽量化、ビルド時間半減
- 🔒 **セキュリティワークフロー統合** - CodeQL/Gitleaks/SBOM/Scorecard統合
- 📖 **包括的Docstrings** - 全主要関数にGoogle Style Docstrings追加
- 🧪 **パフォーマンステスト** - 自動性能測定スクリプト実装
- 🔐 **セキュリティ監査** - 脆弱性自動検出ツール実装

## 🚀 特徴

### 🎯 2025年最新機能（完全実装済み）

- ✅ **スラッシュコマンド対応** - `.claude/commands/`に5つの基本コマンド実装済み
- ✅ **MCPプロファイル切り替え** - minimal/standard/remote/hybrid/fullの5段階設定
- ✅ **リモートMCPサーバー対応** - SSE/HTTPトランスポート、OAuth 2.0認証サポート
- ✅ **Headlessモード強化** - `scripts/claude-ci.sh`でCI/CD完全統合
- ✅ **Docker隔離環境** - 安全な`--dangerously-skip-permissions`実行
- ✅ **GitHub Actions統合** - 自動レビュー・修正・セキュリティ分析
- ✅ **プロジェクト固有設定** - `.mcp.json`でチーム共有可能
- ✅ **自動APIキー管理** - ローカルキーフォルダから自動読み込み (`/Users/admin/Documents/key`)
- ✅ **セッション管理** - 自動保存・クラッシュリカバリー機能
- ✅ **エラーリカバリー** - リトライ機構・包括的エラーハンドリング
- ✅ **Pre-commit hooks** - コード品質の自動チェック
- ✅ **Docker対応** - マルチステージビルド・docker-compose設定
- ✅ **CI/CD Pipeline** - GitHub Actions完全設定

### 🔥 コア機能

- ✅ **Serena MCPサーバー統合** - 高度なセマンティックコード操作（LSP対応）
- ✅ **25+ MCPサーバー統合済み** - filesystem、github、brave-search、playwright、firecrawl等
- ✅ **自動セットアップスクリプト** - ワンコマンドで環境構築
- ✅ **APIキー管理** - 環境変数での安全な管理
- ✅ **サンプルコード付き** - MCPサーバーを活用した実装例
- ✅ **完全なドキュメント** - CLAUDE.mdによるAI向け指示書
- ✅ **VSCode/Cursor最適化** - 完全な設定ファイル・拡張機能推奨
- ✅ **包括的テストスイート** - pytest、カバレッジ、型チェック

## 📦 含まれているMCPサーバー

### 🌟 Serena - 高度なコード操作サーバー

| 機能 | 説明 |
|------|------|
| **セマンティック検索** | LSP（Language Server Protocol）を使用した高度なコード理解 |
| **多言語対応** | Python, TypeScript, Go, Rust, Java, C#, PHP等 |
| **コード実行** | シェルコマンドの実行とログの読み取り |
| **プロジェクト管理** | 自動インデックス作成と高速検索 |
| **APIキー不要** | オープンソースで無料利用可能 |

### 🔧 Smithery - MCPサーバー管理ツール

| 機能 | 説明 |
|------|------|
| **サーバー管理** | MCPサーバーのインストール/アンインストール/更新 |
| **サーバー検索** | SmitheryレジストリからMCPサーバーを検索 |
| **サーバー検査** | インストール済みサーバーの詳細情報表示 |
| **開発ツール** | MCPサーバー開発用のホットリロード、ビルド、プレイグラウンド |
| **APIキー推奨** | 高度な機能にはSMITHERY_API_KEYが必要 |

### 基本サーバー

| サーバー | 機能 | 必要なAPIキー |
|---------|------|--------------|
| filesystem | ファイルシステム操作（Serenaと競合注意） | 不要 |
| github | GitHub統合（Issue、PR、コード検索） | GITHUB_TOKEN |
| fetch | Web取得 | 不要 |
| context7 | ライブラリドキュメント | 不要 |
| brave-search | Web/画像/動画検索 | BRAVE_API_KEY |
| playwright | ブラウザ自動化 | 不要 |
| ide | IDE統合 | 不要 |
| firecrawl | 高度なWebスクレイピング | FIRECRAWL_API_KEY |

### 追加サーバー

- memory - 長期記憶管理
- sequential-thinking - 順次思考
- smithery-stdout - stdoutログキャプチャ
- postgres - PostgreSQL連携
- slack - Slack統合
- aws/gcp/azure - クラウドサービス
- docker/kubernetes - コンテナ管理

### 🌐 リモートMCPサーバー（クラウドホスト型）

| サーバー | 機能 | トランスポート | 認証 |
|---------|------|---------------|------|
| Linear | 課題管理・プロジェクト追跡 | SSE | Bearer Token |
| Notion | ナレッジベース・ワークスペース | HTTP | OAuth 2.0 |
| Sentry | エラー追跡・パフォーマンス監視 | SSE | Bearer Token |
| Apidog | API ドキュメント・テスト | HTTP | API Key |
| SimpleScraper | Webスクレイピングサービス | SSE | API Key |

## 🔧 クイックスタート

### 1. テンプレートをコピー

```bash
# このテンプレートを新しいプロジェクトにコピー
cp -r claude-code-template-mcp my-new-project
cd my-new-project
```

### 2. n8n のクイックスタート（Raycast 用）

```bash
# 自動セットアップ + 起動（未使用ポートを自動割当）
npm run n8n:start:ready

# Raycast の拡張 Preferences → baseUrl を出力に表示された
# http://localhost:<N8N_PORT> に更新（例: http://localhost:5678）

# 状態確認
npm run n8n:status
```

メモ:

- ポートを変更した場合は Raycast も同じポートに合わせてください
- 鍵/認証情報は `/Users/admin/Documents/key` を利用（リポジトリ外）

### 3. MCPサーバーのセットアップ

```bash
# MCPサーバーをインストール
cd mcp-config
bash setup-mcp.sh
# ※ Serenaを有効にする場合は'y'を選択
```

### 4. リモートMCPサーバーのセットアップ（オプション）

```bash
# リモートサーバーを設定
./scripts/setup-remote-mcp.sh
```

### 5. Python環境のセットアップ

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### (任意) ローカルLLM/Ollama の導入

Python 3.11 系の仮想環境が必要です。必要なときだけ別途インストールしてください。

```bash
# 推奨: Python 3.11 で新しい venv を作成
python3.11 -m venv venv
source venv/bin/activate

# Ollama 依存のみ導入
pip install -r requirements-ollama.txt

# Ollama 本体のセットアップ（macOS例）
brew install ollama
ollama serve &
ollama pull llama3.2:3b
```

### 6. Claude Desktopの設定

```bash
# MCPプロファイルを選択（minimal/standard/remote/hybrid/full）
./scripts/mcp-profile-switch.sh hybrid  # ローカル+リモートの併用推奨

# または手動で設定をコピー
# macOSの場合
cp mcp-config/claude_desktop_config.json ~/Library/Application\ Support/Claude/

# Windowsの場合
cp mcp-config/claude_desktop_config.json %APPDATA%/Claude/

# Claudeアプリを再起動
```

## 🎯 新機能の使い方

### スラッシュコマンド

Claude Codeで `/` を入力すると、カスタムコマンドが表示されます：

- `/fix-errors` - エラーを修正
- `/refactor` - コードのリファクタリング
- `/test` - テストコードの生成
- `/review` - コードレビュー
- `/optimize` - パフォーマンス最適化

### MCPプロファイル

パフォーマンスに応じて3つのプロファイルから選択：

```bash
# 最小構成（Serenaのみ）
./scripts/mcp-profile-switch.sh minimal

# 標準構成（開発に必要な基本サーバー）
./scripts/mcp-profile-switch.sh standard

# フル構成（すべてのサーバー）
./scripts/mcp-profile-switch.sh full
```

### Headlessモード（CI/CD用）

```bash
# テストを実行
./scripts/claude-headless.sh -t test

# コードレビュー
./scripts/claude-headless.sh -t review -f src/main.py

# カスタムプロンプト
./scripts/claude-headless.sh -p "Fix all type errors" --output json
```

### 6. 動作確認

```bash
# Claude Codeを起動
claude-code

# Claudeで「/mcp」と入力してMCPサーバーを確認
```

## 📂 プロジェクト構造

```text
claude-code-template-mcp/
├── mcp-config/                    # MCP設定
│   ├── claude_desktop_config.json # Claude Desktop設定
│   ├── setup-mcp.sh              # 基本MCPセットアップ
│   ├── setup-additional-mcp.sh   # 追加MCPセットアップ
│   └── .env.mcp.example          # APIキーテンプレート
├── src/                           # ソースコード
│   ├── main.py                   # メインアプリケーション
│   ├── config.py                 # 設定管理
│   ├── session_manager.py        # セッション管理
│   ├── error_recovery.py         # エラーリカバリー
│   └── mcp_examples.py           # MCPサンプルコード
├── tests/                         # テスト
│   └── test_main.py              # 26個のテスト（全て合格）
├── scripts/                       # ユーティリティ
│   ├── load-keys.sh              # APIキー自動ロード
│   ├── load_keys.py              # APIキー読み込みPython
│   ├── check_no_secrets.py       # シークレット検出
│   ├── sync_env_template.py      # 環境変数同期
│   ├── validate_mcp_config.py    # MCP設定検証
│   └── check_todos.py            # TODO/FIXMEチェック
├── config/                        # 設定ファイル
│   └── keys.json                 # APIキーマッピング
├── .vscode/                       # VSCode/Cursor設定
│   ├── settings.json             # エディタ設定
│   ├── tasks.json                # タスク定義
│   ├── launch.json               # デバッグ設定
│   └── extensions.json           # 推奨拡張機能
├── .github/workflows/             # CI/CD
│   └── ci.yml                    # GitHub Actions
├── CLAUDE.md                      # AI向け指示書
├── README.md                      # このファイル
├── requirements.txt               # Python依存関係
├── requirements-dev.txt           # 開発用依存関係
├── Dockerfile                     # Docker設定
├── docker-compose.yml             # Docker Compose設定
├── Makefile                       # タスク自動化
├── .pre-commit-config.yaml        # Pre-commit設定
├── VERSION                        # バージョン管理
├── .gitignore                     # Git除外設定
└── venv/                          # Python仮想環境
```

## 💡 MCPサーバーの使用例

### Serenaでの高度なコード操作

```python
# セマンティック検索（関数定義を探す）
# 例: "serena で calculate_sum 関数の定義を探して"

# コードのリファクタリング
# 例: "serena ですべての print 文を logger.info に置換"
```

### GitHub操作

```python
# Claude内で直接GitHubを操作
# 例: "/mcp github list-issues owner:myuser repo:myrepo"
```

### Web検索

```python
# Brave Searchで最新情報を取得
# 例: "/mcp brave-search 'Python MCP tutorial 2024'"
```

### ファイル操作

```python
# 高度なファイルシステム操作
# 例: "/mcp filesystem read-multiple-files paths:[file1.py,file2.py]"
```

### ブラウザ自動化

```python
# Playwrightでブラウザを制御
# 例: "/mcp playwright navigate url:https://example.com"
```

## 🛠️ 開発コマンド

### Makefile Commands（推奨）

```bash
# ヘルプを表示
make help

# 初期セットアップ（仮想環境作成・依存関係インストール）
make setup

# テスト実行
make test

# コードフォーマット
make format

# リントチェック
make lint

# 型チェック
make type-check

# カバレッジ測定
make coverage

# Pre-commitフック実行
make pre-commit

# APIキーをロード
make load-keys

# MCP設定を検証
make validate-mcp

# すべてのチェック実行
make all

# クリーンアップ
make clean
```

### 手動コマンド

```bash
# コードフォーマット
ruff format src/ tests/

# リント
ruff check src/ tests/

# テスト実行
pytest tests/

# 型チェック
mypy src/

# セキュリティチェック
bandit -r src/
pip-audit
```

## 🎆 Serenaの設定方法

### オプション1: uvx方式（推奨 - 自動更新）

```json
// デフォルトで有効になっています
"serena": {
  "command": "uvx",
  "args": ["--from", "git+https://github.com/oraios/serena", "serena-mcp-server"]
}
```

### オプション2: ローカルインストール

```bash
git clone https://github.com/oraios/serena ~/serena
# claude_desktop_config.jsonで"disabled": trueを削除
```

### オプション3: Docker方式

```bash
# Dockerが必要
# claude_desktop_config.jsonでserena-dockerを有効化
```

## 📦 Smitheryの使用方法

### MCPサーバーの管理

```bash
# Smithery CLIを使ってMCPサーバーを管理
# サーバーのインストール
npx @smithery/cli install [server-name] --client claude

# サーバーのアンインストール
npx @smithery/cli uninstall [server-name] --client claude

# インストール済みサーバーの一覧
npx @smithery/cli list servers --client claude

# サーバーの詳細情報
npx @smithery/cli inspect [server-name]
```

### Smithery APIキーの取得

1. <https://smithery.ai/>
2. アカウントを作成
3. APIキーを生成
4. `.env.mcp`にSMITHERY_API_KEYを設定

## 🔑 APIキーの取得方法

### GitHub Token

1. GitHub Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)" をクリック
3. 必要なスコープを選択（repo、workflow等）

### Brave Search API

1. <https://brave.com/search/api/>
2. アカウントを作成
3. APIキーを生成

### Firecrawl API

1. <https://firecrawl.dev/>
2. サインアップ
3. ダッシュボードからAPIキーを取得

### Smithery API

1. <https://smithery.ai/>
2. アカウント作成
3. APIキーを生成

## 📚 ドキュメント

- [MCP公式ドキュメント](https://modelcontextprotocol.io/)
- [Claude Code ドキュメント](https://docs.anthropic.com/claude-code)
- [MCP Servers リポジトリ](https://github.com/modelcontextprotocol/servers)

## 🤝 ベストプラクティス

1. **APIキーの管理**
   - 絶対にコミットしない
   - .env.mcpファイルで管理
   - .gitignoreに追加済み

2. **MCPサーバーの選択**
   - タスクに適したサーバーを選ぶ
   - 複数のサーバーを組み合わせる
   - レート制限に注意

3. **エラーハンドリング**
   - MCPサーバーのエラーを適切に処理
   - フォールバック戦略を用意

## 🆘 トラブルシューティング

### MCPサーバーが動作しない

```bash
# Node.jsバージョンを確認（18以上必要）
node --version

# MCPサーバーを再インストール
npm install -g @modelcontextprotocol/server-*

# Claudeアプリを再起動
```

### APIキーエラー

```bash
# .env.mcpファイルを確認
cat .env.mcp

# 環境変数が設定されているか確認
echo $GITHUB_TOKEN
```

### Python環境エラー

```bash
# 仮想環境を再作成
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📄 ライセンス

MITライセンス

## 🎉 さあ始めよう

このテンプレートを使えば、MCPサーバーのパワーを最大限に活用したClaude Codeプロジェクトをすぐに始められます。

```bash
# プロジェクトを開始
cd my-new-project
claude-code

# MCPサーバーを確認
# Claudeで「/mcp」と入力
```

### Happy Coding with MCP 🚀

## Raycast 外部設定ファイル（任意）

- `externalConfigPath` に URL もしくはローカルパス（絶対/~/、または file://）を指定すると、その JSON から `baseUrl`/`apiKey`/`apiKeyHeaderName` を読み込みます。
- 例（ローカル雛形）: `public/raycast-n8n-config.json` を参考にしてください。
- 例（GitHub Raw）: `https://raw.githubusercontent.com/you/repo/main/raycast-n8n-config.json` を指定。
