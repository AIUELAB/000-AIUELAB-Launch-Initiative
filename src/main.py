#!/usr/bin/env python3
"""Claude Code MCP Template のメインモジュール(MCP対応)。"""

import os
import re
import sys
from dataclasses import dataclass
from typing import Any

import click
from dotenv import load_dotenv
from loguru import logger
from rich.console import Console
from rich.table import Table

# 環境変数の読み込み
load_dotenv()
load_dotenv(".env.mcp")  # プロジェクトルートの.env.mcp
load_dotenv("mcp-config/.env.mcp")  # mcp-configディレクトリの.env.mcp(後方互換性)

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
    """Application configuration dataclass.

    Centralizes all application settings loaded from environment variables.
    Supports debug mode, environment selection, and MCP server detection.

    Attributes:
        app_name: Name of the application.
        version: Application version string.
        debug: Whether debug mode is enabled.
        environment: Current environment (development/staging/production).
        mcp_enabled: Whether MCP servers are configured with API keys.
    """

    app_name: str
    version: str
    debug: bool
    environment: str
    mcp_enabled: bool

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables.

        Reads from both .env and .env.mcp files to construct
        the application configuration.

        Returns:
            AppConfig instance with settings loaded from environment.

        Example:
            >>> config = AppConfig.from_env()
            >>> print(f"Running {config.app_name} v{config.version}")
        """
        return cls(
            app_name=os.getenv("APP_NAME", "Claude Code MCP Template"),
            version=os.getenv("APP_VERSION", "1.0.0"),
            debug=os.getenv("DEBUG", "False").lower() == "true",
            environment=os.getenv("ENVIRONMENT", "development"),
            mcp_enabled=bool(os.getenv("GITHUB_TOKEN") or os.getenv("BRAVE_API_KEY")),
        )


class Application:
    """Main application class for Claude Code MCP Template.

    Manages the application lifecycle, MCP server status checking,
    and core business logic execution.

    Attributes:
        config: Application configuration loaded from environment.
    """

    def __init__(self, config: AppConfig) -> None:
        """Initialize the application with configuration.

        Args:
            config: Application configuration object containing
                   settings loaded from environment variables.

        Note:
            Logs initialization status and MCP server availability.
        """
        self.config = config
        logger.info(f"Initializing {config.app_name} v{config.version}")

        if config.mcp_enabled:
            logger.info("MCP servers are configured and ready")
        else:
            logger.warning("MCP servers not configured (missing API keys)")

    def run(self) -> None:
        """Execute the main application workflow.

        Performs the following operations:
        1. Display application information
        2. Check MCP server status
        3. Process sample data

        This method demonstrates the typical application flow
        and MCP integration capabilities.
        """
        logger.info("Application started")

        # サンプル処理
        self.display_info()
        self.check_mcp_status()
        self.process_data()

        logger.info("Application finished")

    def display_info(self) -> None:
        """Display application information in a formatted table.

        Shows key application details including name, version,
        environment, debug status, and MCP availability using
        Rich console formatting.
        """
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
        """Check and display MCP server configuration status.

        Scans environment variables to determine which MCP servers
        are configured and displays their status in a formatted table.
        Also lists always-available MCP servers that don't require
        API keys.
        """
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

        # 基本MCPサーバー(設定不要)
        console.print("\n[bold cyan]Always Available:[/bold cyan]")
        console.print("  • filesystem - File system operations")
        console.print("  • fetch - Web fetching")
        console.print("  • context7 - Library documentation")
        console.print("  • playwright - Browser automation")
        console.print("  • ide - IDE integration")
        console.print("  • memory - Memory management")

    def process_data(self) -> dict[str, Any]:
        """Process sample data to demonstrate application functionality.

        Returns:
            Dictionary containing:
            - status: Processing status ("success" or "error")
            - items_processed: Number of items processed
            - message: Human-readable status message
            - mcp_ready: Whether MCP servers are available

        Example:
            >>> app = Application(config)
            >>> result = app.process_data()
            >>> print(f"Processed {result['items_processed']} items")
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


def calculate_sum(numbers: list[float]) -> float:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of numbers to sum. Can be integers or floats.

    Returns:
        The sum of all numbers in the list.

    Example:
        >>> calculate_sum([1.5, 2.5, 3.0])
        7.0
        >>> calculate_sum([])
        0.0
    """
    return sum(numbers)


def validate_email(email: str) -> bool:
    """Validate email address format using regex.

    Args:
        email: Email address string to validate.

    Returns:
        True if the email format is valid, False otherwise.

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False

    Note:
        Uses a simple regex pattern that covers most common
        email formats but may not handle all edge cases.
    """
    if not email:
        return False

    # 簡単なメールアドレスの正規表現パターン
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def demonstrate_mcp_usage() -> None:
    """Demonstrate MCP server usage with example commands.

    Displays example commands for various MCP servers including
    GitHub, Brave Search, Filesystem, Playwright, and Firecrawl.

    This function helps users understand how to interact with
    different MCP servers through Claude.
    """
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
def cli() -> None:
    """Claude Code MCP Template CLI.

    Main command group for the Claude Code MCP Template application.
    Provides subcommands for running the app, checking environment,
    validating data, and demonstrating MCP capabilities.

    Use --help with any subcommand for detailed information.
    """
    pass


@cli.command()
@click.option("--debug", is_flag=True, help="Enable debug mode")
def run(debug: bool) -> None:
    """Run the main application.

    Args:
        debug: Enable debug mode for verbose logging.

    Example:
        $ python src/main.py run
        $ python src/main.py run --debug
    """
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
def info() -> None:
    """Display application and MCP server information.

    Shows application configuration details and the status
    of all configured MCP servers.

    Example:
        $ python src/main.py info
    """
    config = AppConfig.from_env()
    app = Application(config)
    app.display_info()
    app.check_mcp_status()


@cli.command()
def mcp_demo() -> None:
    """Show MCP server usage examples.

    Displays example commands for interacting with various
    MCP servers to help users understand the available
    capabilities.

    Example:
        $ python src/main.py mcp-demo
    """
    demonstrate_mcp_usage()


@cli.command(name="sum")
@click.argument("numbers", nargs=-1, type=float)
def sum_command(numbers: tuple[float, ...]) -> None:
    """Calculate the sum of provided numbers.

    Args:
        numbers: Variable number of numeric arguments to sum.

    Example:
        $ python src/main.py sum 1.5 2.5 3.0
        Sum: 7.0
    """
    if not numbers:
        console.print("[yellow]No numbers provided[/yellow]")
        return

    result = calculate_sum(list(numbers))
    console.print(f"[green]Sum: {result}[/green]")


@cli.command()
@click.argument("email")
def validate(email: str) -> None:
    """Validate an email address format.

    Args:
        email: Email address to validate.

    Example:
        $ python src/main.py validate user@example.com
        ✓ user@example.com is valid
    """
    if validate_email(email):
        console.print(f"[green]✓[/green] {email} is valid")
    else:
        console.print(f"[red]✗[/red] {email} is invalid")


@cli.command()
def check_env() -> None:
    """Check environment variables and API keys.

    Verifies that all required and optional environment
    variables are properly configured. Helps diagnose
    MCP server configuration issues.

    Example:
        $ python src/main.py check-env
    """
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


def main() -> None:
    """Main entry point for the application.

    Initializes the CLI and handles command routing.
    This function is called when the script is executed directly.

    Example:
        $ python src/main.py --help
        $ python src/main.py run
    """
    cli()


if __name__ == "__main__":
    main()
