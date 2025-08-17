# 📤 テンプレート共有ガイド

## このテンプレートを共有する方法

### 1. GitHub公開リポジトリとして

```bash
# GitHubで新規リポジトリ作成
# Repository name: claude-code-template-mcp
# Description: 2025 Best Practices Claude Code Template with MCP
# Public repository を選択

# ローカルからプッシュ
git remote add origin https://github.com/YOUR_USERNAME/claude-code-template-mcp.git
git branch -M main
git push -u origin main
```

### 2. GitHubテンプレートリポジトリとして設定

1. GitHubリポジトリ → Settings
2. General → Template repository にチェック
3. Save

これで他の人が「Use this template」ボタンで利用可能に

### 3. 共有用README追加情報

```markdown
## 🚀 Quick Start

### Use this template
1. Click "Use this template" button
2. Create your new repository
3. Clone and setup:

\```bash
git clone https://github.com/YOU/your-new-project.git
cd your-new-project
make setup
\```
```

### 4. タグとリリース

```bash
# バージョンタグ作成
git tag -a v1.0.0 -m "Initial release: 2025 features complete"
git push origin v1.0.0

# GitHubでリリース作成
# 1. Releases → Create a new release
# 2. Tag: v1.0.0
# 3. Title: Claude Code Template v1.0.0
# 4. Description: 以下を含める
```

### リリースノート例

```
## 🎉 Claude Code Template v1.0.0

### Features
- ✅ Slash commands (.claude/commands/)
- ✅ Headless CI/CD mode
- ✅ Docker isolation
- ✅ GitHub Actions workflows
- ✅ 25+ MCP servers configured

### Quick Start
1. Clone the template
2. Run `make setup`
3. Configure API keys in `.env.mcp`
4. Start with `claude`

### Requirements
- Python 3.11+
- Node.js 18+
- Cursor IDE (recommended)
```

### 5. ライセンス確認

現在のLICENSEファイル: MIT License
→ オープンソースとして共有可能

### 6. セキュリティ確認

共有前チェックリスト:
- [ ] `.env.mcp`が.gitignoreに含まれている ✅
- [ ] APIキーがコミットされていない ✅
- [ ] 個人情報が含まれていない ✅
- [ ] SECURITYポリシー記載済み ✅

### 7. コミュニティ共有

推奨共有先:
- GitHub Marketplace
- Awesome Claude リスト
- Dev.to / Medium 記事
- X (Twitter) #ClaudeCode #MCP
- Reddit r/ClaudeAI

### 8. バッジ追加

README.mdに追加:
```markdown
![Claude Code](https://img.shields.io/badge/Claude_Code-Ready-blue)
![MCP](https://img.shields.io/badge/MCP-25%2B_Servers-green)
![Tests](https://img.shields.io/badge/Tests-26_Passing-success)
![License](https://img.shields.io/badge/License-MIT-yellow)
```

## 共有コマンド

```bash
# すべてクリーンアップ
make clean

# 共有用アーカイブ作成
git archive --format=zip HEAD > claude-code-template-v1.0.0.zip

# ドキュメント生成
make summary > TEMPLATE_SUMMARY.txt
```

## 準備完了

このテンプレートは共有準備が整っています:
- ✅ 完全な機能実装
- ✅ ドキュメント完備
- ✅ テスト合格
- ✅ セキュリティ確認済み

**世界中の開発者と共有しましょう！**