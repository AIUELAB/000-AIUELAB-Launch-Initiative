# 設定ガイド

## 環境変数

### 基本設定

`.env`ファイルで基本的なアプリケーション設定を管理：

```bash
# アプリケーション設定
APP_NAME="Claude Code MCP Template"
APP_VERSION="1.0.0"
ENVIRONMENT="development"  # development/staging/production
DEBUG="False"  # True でデバッグモード有効
LOG_LEVEL="INFO"  # DEBUG/INFO/WARNING/ERROR
```

### MCP API キー設定

`.env.mcp`ファイルでMCPサーバーのAPIキーを管理：

```bash
# 必須
GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxx"
BRAVE_API_KEY="BSA_xxxxxxxxxxxxxxxxxxxx"

# オプショナル
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"
ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxxxxxx"
FIRECRAWL_API_KEY="fc_xxxxxxxxxxxxxxxxxxxx"
SLACK_BOT_TOKEN="xoxb-xxxxxxxxxxxxxxxxxxxx"
GITLAB_TOKEN="glpat-xxxxxxxxxxxxxxxxxxxx"

# クラウドプロバイダー
AWS_ACCESS_KEY_ID="AKIA_xxxxxxxxxxxxxxxxxxxx"
AWS_SECRET_ACCESS_KEY="xxxxxxxxxxxxxxxxxxxx"
GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
AZURE_SUBSCRIPTION_ID="xxxxxxxxxxxxxxxxxxxx"
```

## Ollama設定

### 基本設定

`.ollama.yml`ファイルでOllamaの詳細設定：

```yaml
# デフォルトモデル設定
models:
  chat: llama3.2:3b        # チャット用
  code: codellama:7b        # コード生成・レビュー用
  analysis: mistral:7b      # 高度な分析用
  fast: deepseek-r1:1.5b    # 高速レスポンス用

# パラメータ設定
parameters:
  temperature: 0.7          # 創造性 (0.0-2.0)
  top_p: 0.9               # トークン選択の多様性
  top_k: 40                # 候補トークン数
  max_tokens: 2048         # 最大生成トークン数
  seed: 42                 # 再現性のためのシード値
  num_predict: -1          # 予測トークン数 (-1で無制限)

# パフォーマンス設定
performance:
  num_threads: 8           # CPUスレッド数
  num_gpu: 1              # GPU使用数 (0で無効)
  batch_size: 512         # バッチサイズ
  context_size: 4096      # コンテキストウィンドウサイズ

# メモリ設定
memory:
  max_memory: "8GB"       # 最大メモリ使用量
  cache_enabled: true     # キャッシュ有効化
  cache_size: "2GB"       # キャッシュサイズ

# ネットワーク設定
network:
  host: "127.0.0.1"       # Ollamaサーバーホスト
  port: 11434             # Ollamaサーバーポート
  timeout: 120            # タイムアウト（秒）
```

### モデル別設定

用途に応じたモデル選択：

| 用途 | 推奨モデル | メモリ要件 | 特徴 |
|------|------------|------------|------|
| 軽量タスク | deepseek-r1:1.5b | 4GB | 高速、省メモリ |
| 汎用チャット | llama3.2:3b | 8GB | バランス型 |
| コード生成 | codellama:7b | 16GB | コード特化 |
| 高度な分析 | mistral:7b | 16GB | 高精度 |
| 数学・論理 | qwen2.5:7b | 16GB | 数学特化 |

## MCPプロファイル

### プロファイル選択

`mcp-config/profiles/`ディレクトリから選択：

```bash
# 最小構成（最速）
./scripts/apply-mcp-profile.sh minimal

# 標準構成（推奨）
./scripts/apply-mcp-profile.sh standard

# リモートのみ
./scripts/apply-mcp-profile.sh remote

# ハイブリッド（ローカル＋リモート）
./scripts/apply-mcp-profile.sh hybrid

# フル機能
./scripts/apply-mcp-profile.sh full
```

### カスタムプロファイル作成

`mcp-config/profiles/custom.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/admin"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    // 必要なサーバーのみ追加
  }
}
```

## Python環境設定

### 仮想環境

```bash
# venv作成
python -m venv venv

# 有効化
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate      # Windows

# 依存関係インストール
pip install -r requirements.txt
```

### uv使用（高速）

```bash
# uvインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# 依存関係インストール
uv pip sync requirements.txt

# 新しいパッケージ追加
uv pip install package_name
uv pip compile requirements.in -o requirements.txt
```

## IDE設定

### VSCode/Cursor

`.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": false,
  "ruff.enable": true,
  "ruff.lint.enable": true,
  "ruff.format.enable": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.ruff": "explicit",
      "source.organizeImports.ruff": "explicit"
    }
  }
}
```

## CI/CD設定

### GitHub Actions

`.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ --cov=src
      - name: Lint with Ruff
        run: ruff check src tests
```

## セキュリティ設定

### Git hooks (pre-commit)

`.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.14.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

### シークレット管理

```bash
# .gitignore に追加
.env
.env.mcp
*.key
*.pem
credentials.json

# Git-secretsインストール
brew install git-secrets  # macOS
git secrets --install
git secrets --register-aws
```

## トラブルシューティング

### よくある問題

#### Ollamaが起動しない

```bash
# サービス再起動
ollama serve

# ポート確認
lsof -i :11434
```

#### MCPサーバーが動作しない

```bash
# Node.jsバージョン確認
node --version  # v18以上必要

# 再インストール
cd mcp-config && bash setup-mcp.sh
```

#### 環境変数が読み込まれない

```bash
# 確認
python src/main.py check-env

# 再読み込み
source venv/bin/activate
python -c "from dotenv import load_dotenv; load_dotenv('.env.mcp'); import os; print(os.getenv('GITHUB_TOKEN'))"
```

## 次のステップ

- [最初のプロジェクト](first-project.md) - サンプルプロジェクト作成
- [MCPサーバーガイド](../features/mcp-servers.md) - 各MCPサーバーの詳細
