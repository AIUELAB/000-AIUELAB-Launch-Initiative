# Claude Code Template MCP

## 概要

**Claude Code Template MCP**は、2025年最新のベストプラクティスに対応した開発テンプレートです。

## 主な特徴

### 🚀 完全無料のローカルLLM
- **Ollama統合** - APIキー不要で完全無料
- プライバシー保護とオフライン動作
- 最新モデル対応（DeepSeek-R1、Llama 3、GPT-OSS）

### 📚 自動ドキュメント生成
- **MkDocs + mkdocstrings** - コードから自動生成
- Material for MkDocsテーマ
- GitHub Pages対応

### 🛠️ 最適化された開発ツール
- **Ruff** - 高速な統一リンター/フォーマッター
- **uv** - 高速パッケージ管理
- **pre-commit** - 自動コード品質チェック

### 🔒 セキュリティファースト
- GitHub Advanced Security統合
- 自動脆弱性スキャン
- シークレット検出

## クイックスタート

```bash
# リポジトリのクローン
git clone https://github.com/your-username/claude-code-template-mcp.git
cd claude-code-template-mcp

# 環境セットアップ
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Ollama セットアップ
./scripts/setup-ollama.sh

# ドキュメント生成
mkdocs serve
```

## プロジェクト構造

```
.
├── src/                    # ソースコード
│   ├── main.py
│   └── ollama_integration.py
├── tests/                  # テストコード
├── docs/                   # ドキュメント
├── scripts/               # ユーティリティスクリプト
├── .github/workflows/     # GitHub Actions
├── mkdocs.yml            # MkDocs設定
├── pyproject.toml        # Python プロジェクト設定
└── requirements.txt      # 依存関係
```

## 主要コンポーネント

### Ollama統合

```python
from ollama_integration import OllamaManager

# LLMの初期化
manager = OllamaManager(model="llama3.2:3b")

# チャット
response = manager.chat("Pythonでフィボナッチ数列を実装して")
print(response)

# コードレビュー
review = code_review(your_code)
```

### MCP サーバー

利用可能なMCPサーバー：
- **Serena** - 高度なコード操作
- **filesystem** - ファイルシステム操作
- **github** - GitHub統合
- **brave-search** - Web検索

## 開発ワークフロー

1. **コード作成** - Ollama でAI支援
2. **フォーマット** - Ruff で自動整形
3. **テスト** - pytest で自動テスト
4. **ドキュメント** - MkDocs で自動生成
5. **デプロイ** - GitHub Actions でCI/CD

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)を参照してください。

## コントリビューション

プルリクエストを歓迎します！詳細は[CONTRIBUTING.md](CONTRIBUTING.md)を参照してください。

## サポート

- [Issues](https://github.com/your-username/claude-code-template-mcp/issues)
- [Discussions](https://github.com/your-username/claude-code-template-mcp/discussions)
