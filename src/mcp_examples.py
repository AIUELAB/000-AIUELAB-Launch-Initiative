#!/usr/bin/env python3
"""
MCP（Model Context Protocol）サーバーを活用するサンプルコード

このファイルは、MCPサーバーと連携する際の実装例を示します。
実際のMCP呼び出しはClaude内で行われますが、
このコードはMCPサーバーから取得したデータを処理する方法を示しています。
"""

import asyncio
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table

# 環境変数の読み込み
load_dotenv()
load_dotenv(".env.mcp")

console = Console()


@dataclass
class GitHubIssue:
    """GitHubのIssue情報を格納するデータクラス"""

    number: int
    title: str
    state: str
    created_at: datetime
    author: str
    labels: List[str]
    body: Optional[str] = None


@dataclass
class SearchResult:
    """検索結果を格納するデータクラス"""

    title: str
    url: str
    snippet: str
    source: str


class MCPDataProcessor:
    """MCPサーバーから取得したデータを処理するクラス"""

    def __init__(self):
        """初期化"""
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.brave_api_key = os.getenv("BRAVE_API_KEY")
        logger.info("MCP Data Processor initialized")

    def process_github_issues(self, issues_data: List[Dict[str, Any]]) -> List[GitHubIssue]:
        """
        GitHubのIssueデータを処理

        Args:
            issues_data: MCPのgithubサーバーから取得したIssueデータ

        Returns:
            処理されたIssueのリスト
        """
        processed_issues = []

        for issue in issues_data:
            processed_issue = GitHubIssue(
                number=issue.get("number"),
                title=issue.get("title"),
                state=issue.get("state"),
                created_at=datetime.fromisoformat(
                    issue.get("created_at", "").replace("Z", "+00:00")
                ),
                author=issue.get("user", {}).get("login", "unknown"),
                labels=[label.get("name") for label in issue.get("labels", [])],
                body=issue.get("body"),
            )
            processed_issues.append(processed_issue)

        return processed_issues

    def display_github_issues(self, issues: List[GitHubIssue]) -> None:
        """
        GitHubのIssueを表形式で表示

        Args:
            issues: 表示するIssueのリスト
        """
        table = Table(title="GitHub Issues")
        table.add_column("Number", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta")
        table.add_column("State", style="green")
        table.add_column("Author", style="yellow")
        table.add_column("Labels", style="blue")

        for issue in issues:
            labels_str = ", ".join(issue.labels) if issue.labels else "No labels"
            table.add_row(
                str(issue.number),
                issue.title[:50] + "..." if len(issue.title) > 50 else issue.title,
                issue.state,
                issue.author,
                labels_str,
            )

        console.print(table)

    def process_search_results(self, search_data: Dict[str, Any]) -> List[SearchResult]:
        """
        Brave SearchやFirecrawlの検索結果を処理

        Args:
            search_data: MCPの検索サーバーから取得したデータ

        Returns:
            処理された検索結果のリスト
        """
        results = []

        # Brave Searchの結果形式
        if "web" in search_data and "results" in search_data["web"]:
            for item in search_data["web"]["results"]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("description", ""),
                    source="Brave Search",
                )
                results.append(result)

        # Firecrawlの結果形式
        elif "data" in search_data:
            for item in search_data["data"]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("content", "")[:200],
                    source="Firecrawl",
                )
                results.append(result)

        return results

    def display_search_results(self, results: List[SearchResult]) -> None:
        """
        検索結果を表示

        Args:
            results: 表示する検索結果のリスト
        """
        for i, result in enumerate(results, 1):
            console.print(f"\n[bold cyan]{i}. {result.title}[/bold cyan]")
            console.print(f"   [link]{result.url}[/link]")
            console.print(f"   [dim]{result.snippet}[/dim]")
            console.print(f"   [yellow]Source: {result.source}[/yellow]")

    async def process_file_operations(self, file_paths: List[str]) -> Dict[str, str]:
        """
        ファイルシステム操作の結果を処理（非同期）

        Args:
            file_paths: 処理するファイルパスのリスト

        Returns:
            ファイルパスと内容のマッピング
        """
        file_contents = {}

        for path in file_paths:
            file_path = Path(path)
            if file_path.exists():
                try:
                    with open(file_path, encoding="utf-8") as f:
                        file_contents[path] = f.read()
                    logger.info(f"Successfully read file: {path}")
                except Exception as e:
                    logger.error(f"Error reading file {path}: {e}")
                    file_contents[path] = f"Error: {str(e)}"
            else:
                file_contents[path] = "File not found"

        return file_contents

    def generate_markdown_report(self, data: Dict[str, Any]) -> str:
        """
        MCPサーバーから取得したデータをMarkdownレポートに変換

        Args:
            data: レポート化するデータ

        Returns:
            Markdownフォーマットのレポート
        """
        report = []
        report.append("# MCP Data Analysis Report")
        report.append(f"\n## Generated at {datetime.now().isoformat()}")

        if "github_issues" in data:
            report.append("\n## GitHub Issues Summary")
            issues = data["github_issues"]
            report.append(f"- Total Issues: {len(issues)}")
            open_issues = [i for i in issues if i.state == "open"]
            report.append(f"- Open Issues: {len(open_issues)}")
            report.append(f"- Closed Issues: {len(issues) - len(open_issues)}")

        if "search_results" in data:
            report.append("\n## Search Results Summary")
            results = data["search_results"]
            report.append(f"- Total Results: {len(results)}")
            by_source = {}
            for r in results:
                by_source[r.source] = by_source.get(r.source, 0) + 1
            for source, count in by_source.items():
                report.append(f"- {source}: {count} results")

        if "files_processed" in data:
            report.append("\n## Files Processed")
            for file_path in data["files_processed"]:
                report.append(f"- `{file_path}`")

        return "\n".join(report)


class MCPOrchestrator:
    """複数のMCPサーバーを組み合わせて使用するオーケストレーター"""

    def __init__(self):
        """初期化"""
        self.processor = MCPDataProcessor()
        logger.info("MCP Orchestrator initialized")

    async def analyze_github_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        GitHubリポジトリを分析（MCPサーバーとの連携をシミュレート）

        Args:
            owner: リポジトリオーナー
            repo: リポジトリ名

        Returns:
            分析結果
        """
        logger.info(f"Analyzing GitHub repository: {owner}/{repo}")

        # 実際のMCP呼び出しはClaude内で行われます
        # ここではデータ処理の例を示します

        analysis = {
            "repository": f"{owner}/{repo}",
            "timestamp": datetime.now().isoformat(),
            "stats": {"issues": 0, "pull_requests": 0, "contributors": 0},
            "recommendations": [],
        }

        # 分析結果に基づく推奨事項
        analysis["recommendations"].append("Consider adding more documentation")
        analysis["recommendations"].append("Review open issues regularly")

        return analysis

    async def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        トピックについてリサーチ（複数のMCPサーバーを活用）

        Args:
            topic: リサーチするトピック

        Returns:
            リサーチ結果
        """
        logger.info(f"Researching topic: {topic}")

        research = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "summary": "",
            "key_points": [],
        }

        # MCPサーバーを組み合わせた処理例
        # 1. Brave Searchで検索
        # 2. Firecrawlで詳細情報取得
        # 3. filesystemで結果を保存

        research["sources"].append({"type": "web_search", "query": topic, "results_count": 10})

        research["key_points"] = [
            f"Important finding about {topic} #1",
            f"Important finding about {topic} #2",
            f"Important finding about {topic} #3",
        ]

        research["summary"] = (
            f"Research on '{topic}' completed successfully with data from multiple sources."
        )

        return research

    def display_analysis(self, analysis: Dict[str, Any]) -> None:
        """
        分析結果を表示

        Args:
            analysis: 表示する分析結果
        """
        console.print("\n[bold green]Analysis Results[/bold green]")
        console.print(json.dumps(analysis, indent=2, default=str))


async def main():
    """メイン処理"""
    console.print("[bold cyan]MCP Examples - Demonstrating MCP Server Integration[/bold cyan]\n")

    # MCPデータプロセッサーの初期化
    processor = MCPDataProcessor()
    orchestrator = MCPOrchestrator()

    # サンプルデータ（実際はMCPサーバーから取得）
    sample_issues = [
        {
            "number": 1,
            "title": "Add MCP integration",
            "state": "open",
            "created_at": "2024-01-01T00:00:00Z",
            "user": {"login": "developer1"},
            "labels": [{"name": "enhancement"}, {"name": "mcp"}],
            "body": "We need to add MCP server integration",
        },
        {
            "number": 2,
            "title": "Fix bug in search",
            "state": "closed",
            "created_at": "2024-01-02T00:00:00Z",
            "user": {"login": "developer2"},
            "labels": [{"name": "bug"}],
            "body": "Search feature has a bug",
        },
    ]

    # GitHubのIssueを処理して表示
    console.print("\n[yellow]Processing GitHub Issues...[/yellow]")
    issues = processor.process_github_issues(sample_issues)
    processor.display_github_issues(issues)

    # リポジトリ分析の実行
    console.print("\n[yellow]Analyzing Repository...[/yellow]")
    analysis = await orchestrator.analyze_github_repository("example", "repo")
    orchestrator.display_analysis(analysis)

    # トピックリサーチの実行
    console.print("\n[yellow]Researching Topic...[/yellow]")
    research = await orchestrator.research_topic("MCP Server Integration")
    orchestrator.display_analysis(research)

    # レポート生成
    console.print("\n[yellow]Generating Report...[/yellow]")
    report_data = {
        "github_issues": issues,
        "search_results": [],
        "files_processed": ["src/main.py", "tests/test_main.py"],
    }
    report = processor.generate_markdown_report(report_data)
    console.print(Markdown(report))

    console.print("\n[bold green]✓ MCP Examples completed successfully![/bold green]")


if __name__ == "__main__":
    # 非同期処理の実行
    asyncio.run(main())
