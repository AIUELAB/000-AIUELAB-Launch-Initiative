#!/usr/bin/env python3
"""
Test script for GitHub MCP Integration

This script tests the basic functionality of the GitHub MCP integration.
Run this to verify your setup is working correctly.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Add src to path
sys.path.append(str(Path(__file__).parent))

console = Console()


def check_environment():
    """Check if all required environment variables are set."""
    load_dotenv()

    # Keep diagnostics only
    required_vars = {
        "GITHUB_PAT": "GitHub Personal Access Token",
        "OPENAI_API_KEY": "OpenAI API Key (optional if using Anthropic)",
        "ANTHROPIC_API_KEY": "Anthropic API Key (optional if using OpenAI)",
    }

    console.print(Panel.fit("🔍 Checking Environment Variables", border_style="blue"))

    table = Table(title="Environment Check")
    table.add_column("Variable", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Status", style="green")

    has_github_pat = False
    has_llm_key = False

    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == "GITHUB_PAT":
                has_github_pat = True
                status = "✅ Set"
            elif var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                has_llm_key = True
                status = "✅ Set"
            else:
                status = "✅ Set"
        else:
            if var == "GITHUB_PAT":
                status = "❌ Missing"
            elif var in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY"]:
                status = "⚠️ Not set"
            else:
                status = "❌ Missing"

        table.add_row(var, description, status)

    console.print(table)

    if not has_github_pat:
        console.print("\n[red]❌ GITHUB_PAT is required. Please add it to your .env file.[/red]")
        console.print("   Get a token at: https://github.com/settings/personal-access-tokens/new")
        return False

    if not has_llm_key:
        console.print(
            "\n[yellow]⚠️ No LLM API key found. You need either OPENAI_API_KEY or ANTHROPIC_API_KEY.[/yellow]"
        )
        return False

    return True


def check_config_file():
    """Check if GitHub MCP configuration file exists."""
    console.print("\n")
    console.print(Panel.fit("📁 Checking Configuration File", border_style="blue"))

    config_path = Path("github_mcp_config.json")

    if config_path.exists():
        console.print(f"✅ Configuration file found: {config_path}")

        try:
            with open(config_path) as f:
                config = json.load(f)
            console.print("✅ Configuration file is valid JSON")

            if "mcpServers" in config and "github" in config["mcpServers"]:
                console.print("✅ GitHub server configuration found")
                return True
            else:
                console.print("[red]❌ GitHub server configuration not found in config file[/red]")
                return False
        except json.JSONDecodeError as e:
            console.print(f"[red]❌ Invalid JSON in configuration file: {e}[/red]")
            return False
    else:
        console.print(f"[red]❌ Configuration file not found: {config_path}[/red]")
        return False


async def test_mcp_connection():
    """Test the MCP connection to GitHub."""
    console.print("\n")
    console.print(Panel.fit("🔌 Testing MCP Connection", border_style="blue"))

    try:
        from src.github_mcp_integration import GitHubMCPIntegration

        # Determine which LLM provider to use
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
            console.print("Using OpenAI as LLM provider")
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
            console.print("Using Anthropic as LLM provider")
        else:
            console.print("[red]❌ No LLM provider API key found[/red]")
            return False

        # Create integration instance
        github = GitHubMCPIntegration(llm_provider=provider)

        # Try to setup
        console.print("Setting up GitHub MCP integration...")
        await github.setup(max_steps=10)
        console.print("✅ GitHub MCP integration initialized successfully")

        # Try a simple query
        console.print("\n🧪 Running test query...")
        result = await github.run_custom_query(
            "Search for the repository 'github/github-mcp-server' and show its description and star count"
        )

        if result:
            console.print("✅ Test query executed successfully")
            console.print(
                Panel(
                    result[:500] + "..." if len(result) > 500 else result,
                    title="Query Result (truncated)",
                    border_style="green",
                )
            )
        else:
            console.print("[yellow]⚠️ Query returned empty result[/yellow]")

        # Cleanup
        await github.cleanup()
        return True

    except ImportError as e:
        console.print(f"[red]❌ Import error: {e}[/red]")
        console.print("   Make sure to run: pip install -r requirements.txt")
        return False
    except Exception as e:
        console.print(f"[red]❌ Error during testing: {e}[/red]")
        return False


async def main():
    """Main test function."""
    console.print(
        Panel.fit(
            "🧪 GitHub MCP Integration Test Suite",
            subtitle="Testing your GitHub MCP setup",
            border_style="bold cyan",
        )
    )

    all_passed = True

    # Check environment variables
    if not check_environment():
        all_passed = False

    # Check configuration file
    if not check_config_file():
        all_passed = False

    # If basic checks pass, test the connection
    if all_passed:
        if not await test_mcp_connection():
            all_passed = False

    # Final result
    console.print("\n" + "=" * 50)
    if all_passed:
        console.print(
            Panel.fit(
                "✅ All tests passed! Your GitHub MCP integration is ready to use.",
                border_style="bold green",
            )
        )
        console.print("\nNext steps:")
        console.print("1. Run the integration: python src/github_mcp_integration.py")
        console.print("2. Try interactive workflows: python examples/github_workflows.py")
    else:
        console.print(
            Panel.fit(
                "❌ Some tests failed. Please fix the issues above and try again.",
                border_style="bold red",
            )
        )
        console.print("\nTroubleshooting:")
        console.print("1. Make sure your .env file contains GITHUB_PAT")
        console.print("2. Ensure you have either OPENAI_API_KEY or ANTHROPIC_API_KEY set")
        console.print("3. Run: pip install -r requirements.txt")
        console.print("4. Check that Docker is installed and running (if using Docker)")


if __name__ == "__main__":
    asyncio.run(main())
