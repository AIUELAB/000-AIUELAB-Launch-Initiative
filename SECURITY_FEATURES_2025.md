# 🔒 2025年セキュリティ機能実装ガイド

このドキュメントは、Claude Code MCP テンプレートに追加された2025年最新の無料セキュリティツールと開発環境改善機能の完全ガイドです。

## 📋 実装済み機能一覧

### 1. 🛡️ OpenSSF Scorecard
**ファイル**: `.github/workflows/scorecard.yml`
- **目的**: プロジェクトのセキュリティスコア自動評価
- **実行タイミング**: 週次、mainブランチへのpush時
- **特徴**:
  - 18のセキュリティベストプラクティスを自動評価
  - 結果をGitHub Security Dashboardに表示
  - SARIFフォーマットでの結果出力

### 2. 🔍 CodeQL セマンティック分析
**ファイル**: `.github/workflows/codeql.yml`
- **目的**: 高度な静的コード分析による脆弱性検出
- **対応言語**: Python（拡張可能）
- **特徴**:
  - security-extendedクエリセット使用
  - 自動修正提案機能
  - GitHub Security Dashboardとの統合

### 3. 🔑 Gitleaks シークレット検出
**ファイル**: `.github/workflows/gitleaks.yml`, `.gitleaks.toml`
- **目的**: ハードコードされたAPIキーや認証情報の検出
- **カスタムルール**:
  - Anthropic API Key検出
  - OpenAI API Key検出
  - GitHub PAT/OAuth検出
  - Brave Search API Key検出
  - Firecrawl API Key検出
  - MCP関連キー検出
- **除外設定**: テストファイル、ドキュメント、例示ファイル

### 4. 📦 SBOM生成と脆弱性スキャン
**ファイル**: `.github/workflows/sbom.yml`
- **ツール**:
  - Syft: SBOM生成（SPDX/CycloneDX形式）
  - Grype: 脆弱性スキャン
  - Microsoft SBOM Tool: エンタープライズ向けSBOM
- **特徴**:
  - 3つの異なるツールで冗長性確保
  - リリース時の自動SBOM添付
  - 依存関係レビューの自動化

### 5. 🔄 Renovate 依存関係自動更新
**ファイル**: `renovate.json`
- **機能**:
  - 90以上のパッケージマネージャーサポート
  - マイナー/パッチ更新の自動マージ
  - セキュリティ更新の優先処理
- **グループ化設定**:
  - Python依存関係
  - JavaScript依存関係
  - テストツール（pytest）
  - リンティングツール（ruff, black, mypy）
  - 型チェックツール
  - クラウドSDK
  - MCP関連パッケージ

### 6. 🐳 Dev Container環境
**ファイル**: `.devcontainer/`
- **Dockerfile**: 完全な開発環境イメージ
  - Python 3.11 + Node.js 18
  - セキュリティツール（Gitleaks, Syft, Grype）
  - MCPサーバー事前インストール
  - Smithery/Context7統合
  - Oh-My-Zsh設定
- **post-create.sh**: 環境自動セットアップスクリプト
  - 仮想環境作成
  - 依存関係インストール
  - MCPサーバー設定
  - 環境変数設定
  - セキュリティチェック実行

### 7. ✅ Pre-commit Hooks
**ファイル**: `.pre-commit-config.yaml`
- **統合ツール**:
  - Black/Ruff: コードフォーマット
  - mypy: 型チェック
  - bandit: セキュリティ脆弱性検出
  - Gitleaks: シークレット検出
  - shellcheck: シェルスクリプト検証
  - hadolint: Dockerfile検証
  - markdownlint: ドキュメント品質
- **pre-commit.ci統合**: PRでの自動修正

### 8. 📊 セキュリティバッジ
**ファイル**: `README.md`
- OpenSSF Scorecard バッジ
- CodeQL ステータスバッジ
- Gitleaks ステータスバッジ
- SBOM ワークフローバッジ
- Renovate 有効化バッジ
- pre-commit.ci ステータスバッジ
- ライセンスバッジ

## 🚀 使用方法

### 初期セットアップ

1. **リポジトリの準備**
```bash
# READMEのバッジURLを更新
sed -i 's/\[YOUR_USERNAME\]/your-github-username/g' README.md
```

2. **環境変数の設定**
```bash
# .env.mcpファイルにAPIキーを設定
cp .env.mcp.example .env.mcp
# エディタで.env.mcpを編集してAPIキーを追加
```

3. **Pre-commitのインストール**
```bash
pip install pre-commit
pre-commit install
```

4. **Dev Containerの使用**（VSCode/Cursor）
- コマンドパレット: `Dev Containers: Reopen in Container`
- 自動でセットアップが実行される

### GitHub Actionsの有効化

1. **Settings > Actions > General**で有効化
2. **Settings > Security > Code scanning**でCodeQLを有効化
3. **Settings > Security > Secret scanning**でシークレットスキャンを有効化

### Renovateの設定

1. [Renovate GitHub App](https://github.com/apps/renovate)をインストール
2. リポジトリへのアクセスを許可
3. 自動的に`renovate.json`が認識される

### pre-commit.ciの設定

1. [pre-commit.ci](https://pre-commit.ci/)にサインアップ
2. リポジトリを追加
3. 自動的に`.pre-commit-config.yaml`が認識される

## 🔒 セキュリティベストプラクティス

### APIキー管理
- すべてのAPIキーは`.env.mcp`に保存
- `.env.mcp`は`.gitignore`に追加済み
- GitHub Secretsを使用してCI/CDで管理

### 依存関係管理
- Renovateによる自動更新
- セキュリティ更新の優先処理
- SBOM生成による透明性確保

### コード品質
- Pre-commitフックによる自動チェック
- CodeQLによる深層分析
- 型チェックとリンティングの強制

### シークレット保護
- Gitleaksによる事前検出
- カスタムルールでMCP特有のキーを検出
- プッシュ前の自動スキャン

## 📈 パフォーマンス影響

これらのツールは以下の影響があります：

- **ビルド時間**: +2-3分（初回のみ、キャッシュ後は+30秒）
- **ストレージ**: Dev Containerイメージ約2GB
- **CI実行時間**: PR毎に+3-5分

## 🆓 コスト

**すべて無料で利用可能**:
- OpenSSF Scorecard: 無料（オープンソース）
- CodeQL: 無料（パブリックリポジトリ）
- Gitleaks: 無料（オープンソース）
- Syft/Grype: 無料（オープンソース）
- Renovate: 無料（パブリックリポジトリ）
- pre-commit.ci: 無料（パブリックリポジトリ）
- Dev Containers: 無料（ローカル実行）

## 🔄 メンテナンス

### 週次タスク
- Renovateダッシュボードの確認
- セキュリティアラートの確認

### 月次タスク
- OpenSSF Scorecardスコアの確認
- 依存関係の手動レビュー

### 四半期タスク
- セキュリティポリシーの更新
- カスタムルールの見直し

## 📚 参考リンク

- [OpenSSF Scorecard](https://github.com/ossf/scorecard)
- [CodeQL Documentation](https://codeql.github.com/docs/)
- [Gitleaks](https://github.com/gitleaks/gitleaks)
- [Syft](https://github.com/anchore/syft)
- [Grype](https://github.com/anchore/grype)
- [Renovate](https://docs.renovatebot.com/)
- [pre-commit](https://pre-commit.com/)
- [Dev Containers](https://containers.dev/)

## 🎯 今後の拡張候補

1. **Semgrep**: カスタムルールベースのSAST
2. **Trivy**: コンテナスキャン
3. **OWASP Dependency Check**: 追加の依存関係スキャン
4. **Snyk**: 統合脆弱性管理（無料枠あり）
5. **GitHub Advanced Security**: エンタープライズ機能（有料）

---

**最終更新**: 2025年8月17日
**実装者**: Claude Code Assistant
**バージョン**: 1.0.0
