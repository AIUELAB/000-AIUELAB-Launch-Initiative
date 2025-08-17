#!/usr/bin/env python3
"""
メインアプリケーションモジュール（MCP対応版）

このファイルはアプリケーションのエントリーポイントです。
MCPサーバーとの連携機能を含んでいます。
"""

import asyncio
import os
import re
import sys
from dataclasses import dataclass
from typing import Any, Dict, List

import click
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table

# 環境変数の読み込み
load_dotenv()
load_dotenv(".env.mcp")  # プロジェクトルートの.env.mcp
load_dotenv("mcp-config/.env.mcp")  # mcp-configディレクトリの.env.mcp（後方互換性）

# Richコンソールの初期化
console = Console()

# ロガーの設定
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=os.getenv("LOG_LEVEL", "INFO"),
)


@dataclass
class AppConfig:
    """アプリケーション設定"""

    app_name: str
    version: str
    debug: bool
    environment: str
    mcp_enabled: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        """環境変数から設定を読み込む"""
        return cls(
            app_name=os.getenv("APP_NAME", "Claude Code MCP Template"),
            version=os.getenv("APP_VERSION", "1.0.0"),
            debug=os.getenv("DEBUG", "False").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "development"),
            mcp_enabled=bool(os.getenv("GITHUB_TOKEN") or os.getenv("BRAVE_API_KEY")),
        )


class Application:
    """メインアプリケーションクラス"""

    def __init__(self, config: AppConfig):
        """
        アプリケーションの初期化

        Args:
            config: アプリケーション設定
        """
        self.config = config
        logger.info(f"Initializing {config.app_name} v{config.version}")

        if config.mcp_enabled:
            logger.info("MCP servers are configured and ready")
        else:
            logger.warning("MCP servers not configured (missing API keys)")

    def run(self) -> None:
        """アプリケーションのメイン処理を実行"""
        logger.info("Application started")

        # サンプル処理
        self.display_info()
        self.check_mcp_status()
        self.process_data()

        logger.info("Application finished")

    def display_info(self) -> None:
        """アプリケーション情報を表示"""
        table = Table(title=f"{self.config.app_name} Information")
        table.add_column("Property", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")

        table.add_row("App Name", self.config.app_name)
        table.add_row("Version", self.config.version)
        table.add_row("Environment", self.config.environment)
        table.add_row("Debug Mode", str(self.config.debug))
        table.add_row("MCP Enabled", "✓" if self.config.mcp_enabled else "✗")

        console.print(table)

    def check_mcp_status(self) -> None:
        """MCPサーバーの状態をチェック"""
        console.print("\n[bold cyan]MCP Server Status:[/bold cyan]")

        mcp_servers = {
            "GitHub": bool(os.getenv("GITHUB_TOKEN")),
            "Brave Search": bool(os.getenv("BRAVE_API_KEY")),
            "Firecrawl": bool(os.getenv("FIRECRAWL_API_KEY")),
            "Slack": bool(os.getenv("SLACK_BOT_TOKEN")),
            "GitLab": bool(os.getenv("GITLAB_TOKEN")),
            "AWS": bool(os.getenv("AWS_ACCESS_KEY_ID")),
            "GCP": bool(os.getenv("GOOGLE_APPLICATION_CREDENTIALS")),
            "Azure": bool(os.getenv("AZURE_SUBSCRIPTION_ID")),
        }

        table = Table(show_header=False)
        table.add_column("Server", style="yellow")
        table.add_column("Status", style="green")

        for server, configured in mcp_servers.items():
            status = "[green]✓ Configured[/green]" if configured else "[dim]Not configured[/dim]"
            table.add_row(f"  {server}", status)

        console.print(table)

        # 基本MCPサーバー（設定不要）
        console.print("\n[bold cyan]Always Available:[/bold cyan]")
        console.print("  • filesystem - File system operations")
        console.print("  • fetch - Web fetching")
        console.print("  • context7 - Library documentation")
        console.print("  • playwright - Browser automation")
        console.print("  • ide - IDE integration")
        console.print("  • memory - Memory management")

    def process_data(self) -> Dict[str, Any]:
        """
        データ処理のサンプル

        Returns:
            処理結果の辞書
        """
        logger.debug("Processing data...")

        result = {
            "status": "success",
            "items_processed": 42,
            "message": "Data processing completed successfully",
            "mcp_ready": self.config.mcp_enabled,
        }

        console.print(f"\n[green]✓[/green] {result['message']}")
        console.print(f"  Items processed: {result['items_processed']}")

        if result["mcp_ready"]:
            console.print("  [cyan]MCP servers are ready for use in Claude[/cyan]")

        return result


def calculate_sum(numbers: List[float]) -> float:
    """
    数値のリストの合計を計算する

    Args:
        numbers: 合計する数値のリスト

    Returns:
        数値の合計
    """
    return sum(numbers)


def validate_email(email: str) -> bool:
    """
    メールアドレスの形式を検証する

    Args:
        email: 検証するメールアドレス

    Returns:
        有効な形式の場合True、そうでない場合False
    """
    if not email:
        return False

    # 簡単なメールアドレスの正規表現パターン
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


async def demonstrate_mcp_usage():
    """MCPサーバーの使用方法をデモンストレーション"""
    console.print("\n[bold yellow]MCP Server Usage Examples:[/bold yellow]\n")

    examples = [
        (
            "GitHub",
            "Get repository issues",
            "mcp__github__list_issues owner:octocat repo:hello-world",
        ),
        (
            "Brave Search",
            "Search the web",
            "mcp__brave-search__brave_web_search query:'Python MCP tutorial'",
        ),
        (
            "Filesystem",
            "Read multiple files",
            "mcp__filesystem__read_multiple_files paths:[README.md,setup.py]",
        ),
        (
            "Playwright",
            "Navigate to URL",
            "mcp__playwright__browser_navigate url:https://example.com",
        ),
        ("Firecrawl", "Scrape website", "mcp__firecrawl__firecrawl_scrape url:https://example.com"),
    ]

    for service, description, command in examples:
        console.print(f"[cyan]{service}:[/cyan] {description}")
        console.print(f"  [dim]Command: {command}[/dim]\n")


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Claude Code MCP Template CLI"""
    pass


@cli.command()
@click.option("--debug", is_flag=True, help="Enable debug mode")
def run(debug: bool):
    """Run the application"""
    config = AppConfig.from_env()
    if debug:
        config.debug = True
        logger.remove()
        logger.add(sys.stderr, level="DEBUG")

    app = Application(config)
    try:
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@cli.command()
def info():
    """Display application and MCP information"""
    config = AppConfig.from_env()
    app = Application(config)
    app.display_info()
    app.check_mcp_status()


@cli.command()
def mcp_demo():
    """Show MCP server usage examples"""
    asyncio.run(demonstrate_mcp_usage())


@cli.command(name='sum')
@click.argument('numbers', nargs=-1, type=float)
def sum_command(numbers):
    """Calculate the sum of numbers"""
    if not numbers:
        console.print("[yellow]No numbers provided[/yellow]")
        return

    result = calculate_sum(list(numbers))
    console.print(f"[green]Sum: {result}[/green]")


@cli.command()
@click.argument('email')
def validate(email):
    """Validate an email address"""
    if validate_email(email):
        console.print(f"[green]✓[/green] {email} is valid")
    else:
        console.print(f"[red]✗[/red] {email} is invalid")


@cli.command()
def check_env():
    """Check environment variables and API keys"""
    console.print("[bold cyan]Environment Check:[/bold cyan]\n")

    required_vars = {
        "GITHUB_TOKEN": "GitHub Personal Access Token",
        "BRAVE_API_KEY": "Brave Search API Key",
    }

    optional_vars = {
        "FIRECRAWL_API_KEY": "Firecrawl API Key",
        "SLACK_BOT_TOKEN": "Slack Bot Token",
        "GITLAB_TOKEN": "GitLab Access Token",
        "AWS_ACCESS_KEY_ID": "AWS Access Key",
        "OPENAI_API_KEY": "OpenAI API Key",
        "ANTHROPIC_API_KEY": "Anthropic API Key",
    }

    # 必須環境変数のチェック
    console.print("[yellow]Required:[/yellow]")
    all_required_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            console.print(f"  [green]✓[/green] {var}: {description} (set)")
        else:
            console.print(f"  [red]✗[/red] {var}: {description} (missing)")
            all_required_set = False

    # オプショナル環境変数のチェック
    console.print("\n[yellow]Optional:[/yellow]")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            console.print(f"  [green]✓[/green] {var}: {description} (set)")
        else:
            console.print(f"  [dim]○[/dim] {var}: {description} (not set)")

    if all_required_set:
        console.print("\n[green]✓ All required environment variables are set![/green]")
    else:
        console.print("\n[red]✗ Some required environment variables are missing.[/red]")
        console.print("  Edit mcp-config/.env.mcp to add your API keys.")


if __name__ == "__main__":
    cli()
