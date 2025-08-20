# 最初のプロジェクト

このガイドでは、Claude Code MCP Templateを使った最初のプロジェクトを作成します。

## プロジェクト: GitHub Issue自動分析ツール

GitHubリポジトリのIssueを取得し、Ollamaで分析するツールを作成します。

### Step 1: プロジェクトセットアップ

```bash
# プロジェクトディレクトリ作成
mkdir my_issue_analyzer
cd my_issue_analyzer

# 仮想環境作成
python -m venv venv
source venv/bin/activate

# テンプレートからファイルをコピー
cp ../claude-code-template-mcp/requirements.txt .
cp ../claude-code-template-mcp/.env.mcp.example .env.mcp
cp ../claude-code-template-mcp/.ollama.yml .
```

### Step 2: Issue分析スクリプト作成

`issue_analyzer.py`:

```python
#!/usr/bin/env python3
"""
GitHub Issue Analyzer with Ollama
MCPサーバーとOllamaを使用したIssue自動分析ツール
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

from dotenv import load_dotenv
from github import Github
from rich.console import Console
from rich.table import Table
from rich.progress import track

# Ollamaインポート（テンプレートから）
import sys
sys.path.append('../claude-code-template-mcp')
from src.ollama_integration import OllamaManager

# 環境変数読み込み
load_dotenv('.env.mcp')

console = Console()


class IssueAnalyzer:
    """GitHub Issue分析クラス"""

    def __init__(self, repo_name: str):
        """
        初期化

        Args:
            repo_name: 分析対象のリポジトリ (owner/repo形式)
        """
        self.repo_name = repo_name
        self.github = Github(os.getenv('GITHUB_TOKEN'))
        self.repo = self.github.get_repo(repo_name)
        self.ollama = OllamaManager(model="llama3.2:3b")

    def fetch_issues(self, state: str = "open", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Issueを取得

        Args:
            state: Issue状態 (open/closed/all)
            limit: 取得数上限

        Returns:
            Issue情報のリスト
        """
        console.print(f"[cyan]Fetching {state} issues from {self.repo_name}...[/cyan]")

        issues = []
        for issue in track(
            self.repo.get_issues(state=state)[:limit],
            description="Loading issues..."
        ):
            issues.append({
                'number': issue.number,
                'title': issue.title,
                'body': issue.body or "",
                'labels': [label.name for label in issue.labels],
                'created_at': issue.created_at,
                'updated_at': issue.updated_at,
                'comments': issue.comments,
                'state': issue.state,
                'url': issue.html_url
            })

        return issues

    def analyze_issue(self, issue: Dict[str, Any]) -> Dict[str, str]:
        """
        個別のIssueを分析

        Args:
            issue: Issue情報

        Returns:
            分析結果
        """
        # 分析プロンプト構築
        prompt = f"""
        Analyze this GitHub issue and provide:
        1. Summary (1-2 sentences)
        2. Priority (High/Medium/Low)
        3. Category (Bug/Feature/Documentation/Question)
        4. Estimated effort (Hours)
        5. Suggested labels

        Issue #{issue['number']}: {issue['title']}

        Description:
        {issue['body'][:500]}

        Current labels: {', '.join(issue['labels'])}
        Comments: {issue['comments']}
        Created: {issue['created_at']}
        """

        # Ollamaで分析
        response = self.ollama.chat(
            prompt,
            system="You are a GitHub issue analyst. Provide concise, actionable insights."
        )

        # 結果をパース
        return {
            'issue_number': issue['number'],
            'title': issue['title'],
            'analysis': response,
            'url': issue['url']
        }

    def batch_analyze(self, issues: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        複数のIssueを一括分析

        Args:
            issues: Issue情報リスト

        Returns:
            分析結果リスト
        """
        console.print("\n[yellow]Analyzing issues with Ollama...[/yellow]")

        results = []
        for issue in track(issues, description="Analyzing..."):
            try:
                analysis = self.analyze_issue(issue)
                results.append(analysis)
            except Exception as e:
                console.print(f"[red]Error analyzing issue #{issue['number']}: {e}[/red]")

        return results

    def generate_report(self, analyses: List[Dict[str, str]]) -> str:
        """
        分析レポート生成

        Args:
            analyses: 分析結果リスト

        Returns:
            マークダウン形式のレポート
        """
        report = f"""# GitHub Issue Analysis Report

**Repository:** {self.repo_name}  
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}  
**Issues Analyzed:** {len(analyses)}

## Summary

"""

        # 各Issueの分析結果を追加
        for analysis in analyses:
            report += f"""
### Issue #{analysis['issue_number']}: {analysis['title']}

**URL:** {analysis['url']}

**Analysis:**
{analysis['analysis']}

---
"""

        # 統計サマリー生成
        summary_prompt = f"""
        Based on these {len(analyses)} issue analyses, provide:
        1. Overall repository health assessment
        2. Top 3 priority areas
        3. Recommended next actions

        Keep it concise and actionable.
        """

        overall_summary = self.ollama.chat(summary_prompt)
        report += f"\n## Overall Assessment\n\n{overall_summary}\n"

        return report

    def display_results(self, analyses: List[Dict[str, str]]):
        """
        結果を表示

        Args:
            analyses: 分析結果リスト
        """
        table = Table(title=f"Issue Analysis for {self.repo_name}")
        table.add_column("Issue #", style="cyan")
        table.add_column("Title", style="yellow")
        table.add_column("Analysis Summary", style="green")

        for analysis in analyses:
            # 分析の最初の行のみ表示
            summary = analysis['analysis'].split('\n')[0][:100] + "..."
            table.add_row(
                str(analysis['issue_number']),
                analysis['title'][:50],
                summary
            )

        console.print(table)


def main():
    """メイン実行関数"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze GitHub Issues with Ollama')
    parser.add_argument('repo', help='Repository name (owner/repo)')
    parser.add_argument('--state', default='open', choices=['open', 'closed', 'all'])
    parser.add_argument('--limit', type=int, default=5, help='Number of issues to analyze')
    parser.add_argument('--output', help='Output file for report (markdown)')

    args = parser.parse_args()

    try:
        # 分析実行
        analyzer = IssueAnalyzer(args.repo)

        # Issue取得
        issues = analyzer.fetch_issues(state=args.state, limit=args.limit)
        console.print(f"[green]✓ Fetched {len(issues)} issues[/green]\n")

        # 分析実行
        analyses = analyzer.batch_analyze(issues)

        # 結果表示
        analyzer.display_results(analyses)

        # レポート生成
        if args.output:
            report = analyzer.generate_report(analyses)
            with open(args.output, 'w') as f:
                f.write(report)
            console.print(f"\n[green]✓ Report saved to {args.output}[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
```

### Step 3: 実行

```bash
# 環境変数設定
export GITHUB_TOKEN="your_github_token"

# Ollamaサービス起動
ollama serve &

# スクリプト実行
python issue_analyzer.py facebook/react --limit 5 --output report.md
```

### Step 4: 拡張機能追加

`advanced_features.py`:

```python
"""高度な機能追加"""

from typing import List, Dict
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud


class IssueVisualizer:
    """Issue分析の可視化"""

    @staticmethod
    def create_priority_chart(analyses: List[Dict]):
        """優先度チャート生成"""
        # 優先度をカウント
        priorities = {'High': 0, 'Medium': 0, 'Low': 0}
        for analysis in analyses:
            # 分析テキストから優先度を抽出
            text = analysis['analysis'].lower()
            if 'high' in text:
                priorities['High'] += 1
            elif 'medium' in text:
                priorities['Medium'] += 1
            else:
                priorities['Low'] += 1

        # 円グラフ生成
        plt.figure(figsize=(8, 6))
        plt.pie(priorities.values(), labels=priorities.keys(), autopct='%1.1f%%')
        plt.title('Issue Priority Distribution')
        plt.savefig('priority_chart.png')

    @staticmethod
    def create_word_cloud(analyses: List[Dict]):
        """ワードクラウド生成"""
        # 全テキスト結合
        all_text = ' '.join([a['analysis'] for a in analyses])

        # ワードクラウド生成
        wordcloud = WordCloud(width=800, height=400).generate(all_text)

        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('Issue Analysis Word Cloud')
        plt.savefig('wordcloud.png')


class IssuePrioritizer:
    """自動優先順位付け"""

    def __init__(self, ollama_manager):
        self.ollama = ollama_manager

    def calculate_priority_score(self, issue: Dict) -> float:
        """優先度スコア計算"""
        score = 0.0

        # コメント数による重み付け
        score += issue['comments'] * 2

        # ラベルによる重み付け
        critical_labels = ['bug', 'security', 'critical', 'urgent']
        for label in issue['labels']:
            if label.lower() in critical_labels:
                score += 10

        # 経過時間による重み付け
        from datetime import datetime, timezone
        age_days = (datetime.now(timezone.utc) - issue['created_at']).days
        if age_days > 30:
            score += 5

        return score

    def rank_issues(self, issues: List[Dict]) -> List[Dict]:
        """Issue優先順位付け"""
        for issue in issues:
            issue['priority_score'] = self.calculate_priority_score(issue)

        return sorted(issues, key=lambda x: x['priority_score'], reverse=True)


class IssueAutoLabeler:
    """自動ラベル提案"""

    def __init__(self, ollama_manager):
        self.ollama = ollama_manager

    def suggest_labels(self, issue: Dict) -> List[str]:
        """ラベル提案"""
        prompt = f"""
        Based on this issue, suggest appropriate GitHub labels:

        Title: {issue['title']}
        Body: {issue['body'][:300]}

        Return only a comma-separated list of labels.
        """

        response = self.ollama.chat(prompt)
        labels = [label.strip() for label in response.split(',')]

        return labels
```

## プロジェクト実行例

### 基本実行

```bash
# Facebook Reactリポジトリの分析
python issue_analyzer.py facebook/react --limit 10

# クローズドIssueの分析
python issue_analyzer.py microsoft/vscode --state closed --limit 5

# レポート出力付き
python issue_analyzer.py openai/gpt-3 --output analysis_report.md
```

### 結果の例

```
┌─────────────────────────────────────────────────────────────┐
│         Issue Analysis for facebook/react                   │
├────────┬──────────────────────────┬────────────────────────┤
│ Issue # │ Title                    │ Analysis Summary       │
├────────┼──────────────────────────┼────────────────────────┤
│ 12345  │ Bug: Component re-render │ Priority: High. This   │
│        │                          │ appears to be a...     │
│ 12346  │ Feature: Add dark mode   │ Priority: Medium...    │
└────────┴──────────────────────────┴────────────────────────┘
```

## 学習ポイント

このプロジェクトで学べること：

1. **MCPサーバー活用**
   - GitHub APIとの連携
   - 構造化データの取得

2. **Ollama統合**
   - ローカルLLMでの分析
   - プロンプトエンジニアリング

3. **実践的な応用**
   - Issue管理の自動化
   - レポート生成
   - データ可視化

## 次のステップ

1. **機能拡張**
   - PR分析機能追加
   - 自動ラベリング実装
   - Slack通知連携

2. **パフォーマンス改善**
   - 並列処理追加
   - キャッシング実装
   - バッチ処理最適化

3. **他のMCPサーバー活用**
   - Firecrawlでドキュメント取得
   - Brave Searchで関連情報検索
   - Slackで結果共有

## トラブルシューティング

### よくあるエラー

```bash
# GitHub API制限
# → GITHUB_TOKENが正しく設定されているか確認

# Ollama接続エラー
ollama serve  # サービス起動
ollama list   # モデル確認

# メモリ不足
# → より小さいモデル（deepseek-r1:1.5b）を使用
```

## 参考リンク

- [Ollama統合ガイド](../features/ollama.md)
- [MCPサーバーガイド](../features/mcp-servers.md)
- [GitHub API ドキュメント](https://docs.github.com/en/rest)
