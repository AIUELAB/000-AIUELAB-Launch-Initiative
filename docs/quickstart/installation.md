# インストールガイド

## 必要要件

- Python 3.11以上
- Node.js 18以上
- Git
- macOS/Linux/Windows (WSL)

## クイックインストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/your-username/claude-code-template-mcp.git
cd claude-code-template-mcp
```

### 2. Python環境のセットアップ

```bash
# 仮想環境の作成
python -m venv venv

# 仮想環境の有効化
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

### 3. 依存関係のインストール

```bash
# Pythonパッケージ
pip install -r requirements.txt

# 開発用パッケージ（オプション）
pip install -e ".[dev]"
```

### 4. MCPサーバーのセットアップ

```bash
# 基本MCPサーバー
cd mcp-config
bash setup-mcp.sh

# 追加MCPサーバー（オプション）
bash setup-additional-mcp.sh
```

### 5. Ollama統合（ローカルLLM）

```bash
# Ollamaのインストールと設定
./scripts/setup-ollama.sh

# モデルのダウンロード
ollama pull llama3.2:3b
ollama pull codellama:7b
```

### 6. 環境変数の設定

```bash
# 環境変数ファイルのコピー
cp .env.example .env
cp .env.mcp.example .env.mcp

# APIキーの設定（.env.mcpを編集）
nano .env.mcp
```

必要なAPIキー：
- `GITHUB_TOKEN` - GitHub Personal Access Token
- `BRAVE_API_KEY` - Brave Search APIキー（オプション）
- `OPENAI_API_KEY` - OpenAI APIキー（オプション）
- `ANTHROPIC_API_KEY` - Anthropic APIキー（オプション）

### 7. 動作確認

```bash
# CLIの動作確認
python src/main.py --version

# 環境チェック
python src/main.py check-env

# Ollama統合テスト
python src/ollama_integration.py

# テスト実行
pytest tests/
```

## トラブルシューティング

### Ollamaが起動しない

```bash
# Ollamaサービスの起動
ollama serve

# 別ターミナルでモデル一覧確認
ollama list
```

### 依存関係のエラー

```bash
# pipのアップグレード
pip install --upgrade pip

# 依存関係の再インストール
pip install -r requirements.txt --force-reinstall
```

### MCPサーバーが動作しない

```bash
# Node.jsバージョン確認
node --version  # v18以上必要

# MCPサーバーの再インストール
npm install -g @modelcontextprotocol/server-filesystem
npm install -g @modelcontextprotocol/server-github
```

## 次のステップ

- [設定ガイド](configuration.md) - 詳細な設定方法
- [最初のプロジェクト](first-project.md) - サンプルプロジェクト作成
