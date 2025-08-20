# 🤖 AI Tools & Integrations (2025)

このプロジェクトには最新の無料AIツールとセキュリティ機能が統合されています。

## 🎯 無料AIコーディングツール

### Aider - AIペアプログラミング
```bash
# インストール
./scripts/setup-ai-tools.sh

# 使用方法
aider <file>  # ファイルを指定してAIペアプログラミング
aider         # 対話モードで開始
```

### code2prompt - コードをLLMプロンプトに変換
```bash
code2prompt --path ./src --output prompt.md
```

### LLM CLI - コマンドラインLLMツール
```bash
llm "Explain this Python code" < main.py
```

## 🔒 セキュリティツール（無料）

### GitHub Advanced Security
- **CodeQL** - セマンティックコード分析
- **Dependabot** - 依存関係の自動更新
- **Secret scanning** - 秘密情報の検出

パブリックリポジトリでは完全無料で利用可能。

### セキュリティスキャン
```bash
# Bandit (Python SAST)
bandit -r src/

# Semgrep (多言語SAST)
semgrep --config=auto src/

# Gitleaks (秘密検出)
gitleaks detect --source . --verbose

# Safety (依存関係チェック)
safety check

# pip-audit (Pythonパッケージ監査)
pip-audit
```

### SonarQube Community Edition
```bash
# 起動
docker-compose -f docker-compose.sonarqube.yml up -d

# アクセス
# http://localhost:9000
# デフォルト: admin/admin
```

## 🚀 GitHub Actions統合

### 自動セキュリティスキャン
- 毎週月曜日に自動実行
- Push/PRごとに実行
- CodeQL分析
- 依存関係チェック
- 脆弱性スキャン

### ワークフロー
```yaml
.github/workflows/
├── security-scan.yml    # セキュリティスキャン
├── codeql.yml           # CodeQL分析
├── gitleaks.yml         # 秘密情報検出
└── sbom.yml            # SBOM生成
```

## 💡 ベストプラクティス

### AIツール使用時
1. APIキーは環境変数で管理
2. `.env`ファイルに保存（gitignoreに追加済み）
3. コミット前に秘密情報チェック

### セキュリティ
1. 定期的な依存関係更新（Dependabot）
2. PRごとのセキュリティチェック
3. 週次の包括的スキャン

## 🔧 設定

### 環境変数（.env）
```bash
# AI Tools
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Security Tools
SNYK_TOKEN=your-snyk-token
DEEPSOURCE_DSN=your-deepsource-dsn
```

### Aider設定（.aider.conf.yml）
```yaml
model: gpt-4-turbo-preview
auto-commits: false
show-diffs: true
```

## 📊 コード品質ツール

### 静的解析
- **Ruff** - 高速Pythonリンター
- **Black** - コードフォーマッター
- **mypy** - 型チェック

### 動的解析
- **pytest** - テストフレームワーク
- **coverage** - カバレッジ測定

## 🌐 クラウドネイティブツール

### Container Security
```bash
# Trivy (コンテナスキャン)
trivy image your-image:tag

# Grype (脆弱性スキャン)
grype dir:./

# Syft (SBOM生成)
syft dir:./
```

## 📈 メトリクス & モニタリング

### コード品質メトリクス
- 複雑度分析
- 重複コード検出
- テストカバレッジ
- セキュリティスコア

## 🔄 CI/CD統合

すべてのツールはGitHub Actionsと完全統合：
- 自動実行
- PRコメント
- ステータスチェック
- アーティファクト保存

## 📚 リソース

- [Aider Documentation](https://aider.chat/)
- [GitHub Advanced Security](https://docs.github.com/en/code-security)
- [SonarQube Docs](https://docs.sonarqube.org/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 🎉 今すぐ始める

```bash
# AIツールのセットアップ
./scripts/setup-ai-tools.sh

# セキュリティチェック実行
make security

# AIペアプログラミング開始
aider src/main.py
```
