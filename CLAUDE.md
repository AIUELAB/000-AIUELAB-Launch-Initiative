# Claude Code プロジェクト指示書（MCP対応版）🏆

## プロジェクト概要
このプロジェクトは**2025年最新ベストプラクティス**に対応したMCP（Model Context Protocol）サーバーが完全統合されたClaude Codeテンプレートです。

## 🎯 2025年最新機能

### スラッシュコマンド
`.claude/commands/`ディレクトリにカスタムコマンドが定義されています：
- `/fix-errors` - エラー修正
- `/refactor` - リファクタリング
- `/test` - テスト作成
- `/review` - コードレビュー
- `/optimize` - パフォーマンス最適化

### MCPプロファイル
パフォーマンスに応じて選択可能：
- `minimal` - Serenaのみ（最高速）
- `standard` - 基本開発セット
- `full` - 全機能有効

### Headlessモード
CI/CDでの自動実行に対応：
```bash
./scripts/claude-headless.sh -t test
```

## 🎯 利用可能なMCPサーバー

### 🌟 Serena - 高度なコード操作サーバー（推奨）
- **セマンティックコード検索** - LSPを使用した高度なコード理解
- **多言語対応** - Python, TypeScript, Go, Rust, Java, C#, PHP等
- **コード実行** - シェルコマンドの実行とログ読み取り
- **プロジェクト管理** - 自動インデックス作成と高速検索
- **filesystemの上位互換** - より高度なファイル操作が可能

### 🔧 Smithery - MCPサーバー管理ツール
- **サーバー管理** - MCPサーバーのインストール/アンインストール/更新
- **サーバー検索** - SmitheryレジストリからMCPサーバーを探す
- **サーバー検査** - インストール済みサーバーの詳細情報
- **開発ツール** - MCPサーバー開発用のホットリロード、ビルド、プレイグラウンド

### 基本MCPサーバー
- **filesystem** - ファイルシステム操作（Serena使用時は無効推奨）
- **github** - GitHub統合（Issue、PR、コード検索）
- **fetch** - Web取得とスクレイピング
- **context7** - ライブラリドキュメント取得
- **brave-search** - Web、画像、ニュース、動画検索
- **playwright** - ブラウザ自動化とテスト
- **ide** - IDE統合（診断、コード実行）
- **firecrawl** - 高度なWebスクレイピング

### 追加MCPサーバー
- **memory** - 長期記憶管理
- **sequential-thinking** - 順次思考処理
- **puppeteer** - ブラウザ自動化（代替）
- **smithery-stdout** - stdoutログのキャプチャと管理
- **postgres/slack/gitlab** - 各種サービス統合
- **aws/gcp/azure** - クラウドサービス統合
- **docker/kubernetes** - コンテナ管理

## 開発環境
- Python 3.11+
- Node.js 18+
- 仮想環境: `venv`
- パッケージ管理: pip, npm

## 重要なコマンド

### MCPセットアップ
```bash
# MCPサーバーのインストール
cd mcp-config
bash setup-mcp.sh

# 環境変数の設定
cp .env.mcp.example .env.mcp
# .env.mcpファイルを編集してAPIキーを設定
```

### 環境セットアップ
```bash
# 仮想環境の作成と有効化
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows

# 依存関係のインストール
pip install -r requirements.txt
npm install  # package.jsonがある場合
```

### 開発コマンド
```bash
# コードフォーマット
black src/ tests/

# リント
pylint src/ tests/

# テスト実行
pytest tests/

# 型チェック
mypy src/
```

## MCPサーバーの活用例

### Serenaでの高度なコード操作
```python
# セマンティック検索
# "Serenaで calculate_sum 関数の定義を探して"
# "Serenaで TODO コメントがあるすべての場所を表示"

# コードリファクタリング
# "Serenaですべての print 文を logger.info に置換"
# "Serenaで変数名 foo を bar にリネーム"

# コード実行
# "Serenaで pytest を実行して結果を確認"
# "Serenaで npm run build を実行"
```

### ファイル操作
```python
# MCPのfilesystemサーバーを使って、ファイルを読み書き
# /mcp コマンドでMCPツールを確認
```

### GitHub統合
```python
# GitHubのIssueやPRを直接操作
# コード検索や自動レビューも可能
```

### Web検索とスクレイピング
```python
# Brave SearchやFirecrawlを使った情報収集
# Playwrightでブラウザ自動化
```

## プロジェクト構造
```
.
├── mcp-config/         # MCP設定とスクリプト
│   ├── claude_desktop_config.json
│   └── setup-mcp.sh
├── src/                # ソースコード
├── tests/              # テストコード
├── scripts/            # ユーティリティスクリプト
└── venv/               # Python仮想環境
```

## コーディング規約
- PEP 8に準拠
- Blackでフォーマット
- 型ヒントを積極的に使用
- docstringは必須（Google Style）
- MCPサーバーを活用した効率的な開発

## 注意事項
- コミット前に必ずテストを実行
- 環境変数は`.env`と`.env.mcp`ファイルで管理
- センシティブな情報はコミットしない
- MCPサーバーのAPIキーは適切に管理

## よくある作業

### 新機能の追加
1. `src/`に新しいモジュールを作成
2. 対応するテストを`tests/`に作成
3. MCPサーバーを活用して外部サービスと連携
4. テストを実行して確認
5. コードをフォーマット・リント

### MCPサーバーの活用
```python
# GitHubから情報取得
# mcp__github__get_issue でIssue情報を取得

# Webから情報収集
# mcp__brave-search__brave_web_search で検索

# ファイル操作
# mcp__filesystem__read_file でファイル読み込み
```

### デバッグ
```python
import pdb; pdb.set_trace()  # ブレークポイント
```

## トラブルシューティング

### MCPサーバー関連
- MCPサーバーが動作しない場合は`npm install -g @modelcontextprotocol/server-*`を実行
- APIキーが設定されているか`.env.mcp`を確認
- Claudeアプリケーションを再起動

### Python環境
- 仮想環境が有効でない場合は`source venv/bin/activate`を実行
- パッケージが見つからない場合は`pip install -r requirements.txt`を再実行

## Smitheryの使い方

### MCPサーバーの管理
```bash
# Smitheryを使って新しいMCPサーバーをインストール
"Smitheryで obsidian MCPサーバーをインストールして"

# インストール済みサーバーの確認
"Smitheryでインストール済みのMCPサーバーを一覧表示"

# サーバーの詳細情報
"Smitheryで github MCPサーバーの詳細を表示"
```

### 開発ツール
```bash
# MCPサーバーの開発
"Smitheryで開発サーバーを起動（ホットリロード付き）"
"Smitheryでサーバーをビルド"
"Smitheryでプレイグラウンドを開く"
```

## Serenaの詳細な使い方

### プロジェクトのアクティベート
```bash
# 特定のプロジェクトをアクティベート
# "Serenaで /path/to/project をアクティベート"
```

### LSP機能の活用
- **定義にジャンプ**: 関数やクラスの定義元を探す
- **参照検索**: 特定の関数が使われている場所をすべて探す
- **シンボル検索**: プロジェクト全体からシンボルを検索
- **エラー診断**: コードのエラーをリアルタイムで検出

### Serena vs filesystem
- Serena使用時はfilesystemサーバーを無効にすることを推奨
- Serenaはより高度なコード理解と操作が可能
- シンプルなファイル読み書きのみの場合はfilesystemでも十分

## MCPサーバー使用時のベストプラクティス

1. **適切なサーバーの選択**
   - コード操作: Serena（推奨）
   - ファイル操作: filesystem
   - GitHub操作: github
   - Web検索: brave-search
   - スクレイピング: firecrawl/playwright

2. **エラーハンドリング**
   - MCPサーバーのレスポンスを適切に処理
   - APIレート制限に注意

3. **セキュリティ**
   - APIキーは環境変数で管理
   - 認証情報をハードコードしない

## リソース
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [GitHub MCP Server](https://github.com/modelcontextprotocol/servers)

## 開発コマンド（Makefile使用推奨）

```bash
# コードフォーマット（Ruff/Black互換）
make format  # または ruff format src tests

# リント（Ruff推奨）
make lint    # または ruff check src tests

# 型チェック
make type    # または mypy src

# テスト実行（カバレッジ）
make coverage  # または pytest tests --cov=src

# すべてのチェック
make pre-commit
```

## 依存関係の更新（uv推奨）

```bash
uv pip compile requirements.in -o requirements.txt
uv pip sync requirements.txt
```

## GitHub MCP Integration（ネイティブ版）

```bash
# ネイティブバイナリのインストール（Docker不要）
./setup_github_mcp.sh

# 環境変数（.env もしくは .env.mcp）
# どちらの変数名でも可：GITHUB_TOKEN / GITHUB_PAT
GITHUB_TOKEN=your_github_token
# LLMプロバイダ
OPENAI_API_KEY=your_openai_key  # または ANTHROPIC_API_KEY

# 動作確認
python test_github_mcp.py
python src/github_mcp_integration.py
```
