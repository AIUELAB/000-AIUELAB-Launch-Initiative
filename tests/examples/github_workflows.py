"""
GitHub MCP Workflow Examples

This module demonstrates various GitHub workflows using the MCP integration.
These examples show how to automate common GitHub tasks.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from collections.abc import Awaitable, Callable

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table

from src.github_mcp_integration import GitHubMCPIntegration

console = Console()

OWNER_PROMPT = "Enter repository owner"
REPO_PROMPT = "Enter repository name"


class GitHubWorkflowExamples:
    """Examples of common GitHub workflows using MCP."""

    def __init__(self):
        self.github = GitHubMCPIntegration()

    async def setup(self):
        """Initialize the GitHub MCP integration."""
        await asyncio.to_thread(self.github.setup, max_steps=50)

    async def workflow_repository_analysis(self):
        """
        Workflow: Analyze a repository comprehensively.
        """
        console.print(Panel.fit("📊 Repository Analysis Workflow", border_style="cyan"))

        owner = Prompt.ask(OWNER_PROMPT, default="microsoft")
        repo = Prompt.ask(REPO_PROMPT, default="vscode")

        # Get repository overview
        console.print("\n[bold]Getting repository overview...[/bold]")
        result = await self.github.run_custom_query(
            f"""Analyze the GitHub repository {owner}/{repo} and provide:
            1. Basic statistics (stars, forks, issues, PRs)
            2. Primary programming languages used
            3. Recent commit activity (last 5 commits)
            4. Top 3 contributors
            5. Open issues by label
            6. Latest release information
            """
        )
        console.print(result)

    async def workflow_issue_triage(self):
        """
        Workflow: Triage and categorize issues in a repository.
        """
        console.print(Panel.fit("🏷️ Issue Triage Workflow", border_style="cyan"))

        owner = Prompt.ask(OWNER_PROMPT, default="facebook")
        repo = Prompt.ask(REPO_PROMPT, default="react")

        console.print("\n[bold]Analyzing issues for triage...[/bold]")
        result = await self.github.run_custom_query(
            f"""For the repository {owner}/{repo}:
            1. List the 10 most recent open issues
            2. Categorize them by:
               - Bug reports
               - Feature requests
               - Documentation
               - Questions
            3. Identify issues without labels
            4. Find issues that are over 30 days old without any comments
            5. Suggest priority levels based on issue content and engagement
            """
        )
        console.print(result)

    async def workflow_pr_review_helper(self):
        """
        Workflow: Help with pull request reviews.
        """
        console.print(Panel.fit("👁️ Pull Request Review Helper", border_style="cyan"))

        owner = Prompt.ask(OWNER_PROMPT, default="pytorch")
        repo = Prompt.ask(REPO_PROMPT, default="pytorch")

        console.print("\n[bold]Analyzing pull requests...[/bold]")
        result = await self.github.run_custom_query(
            f"""For the repository {owner}/{repo}:
            1. List open pull requests that:
               - Have been open for more than 7 days
               - Have no reviews yet
               - Have failing checks
            2. For each PR, show:
               - Title and author
               - Files changed count
               - Lines added/removed
               - Review status
            3. Prioritize which PRs should be reviewed first based on:
               - Age of PR
               - Size of changes
               - Author's contribution history
            """
        )
        console.print(result)

    async def workflow_find_good_first_issues(self):
        """
        Workflow: Find good first issues for new contributors.
        """
        console.print(Panel.fit("🌟 Find Good First Issues", border_style="cyan"))

        language = Prompt.ask("Enter programming language", default="python")
        topic = Prompt.ask("Enter topic/area of interest", default="machine-learning")

        console.print("\n[bold]Searching for beginner-friendly issues...[/bold]")
        result = await self.github.run_custom_query(
            f"""Find good first issues for new contributors:
            1. Search for repositories with:
               - Language: {language}
               - Topic: {topic}
               - More than 100 stars
            2. In those repositories, find issues labeled as:
               - "good first issue"
               - "beginner friendly"
               - "help wanted"
               - "easy"
            3. For each issue, show:
               - Repository name and stars
               - Issue title and description summary
               - Required skills
               - Link to the issue
            4. Sort by repository popularity and issue age
            """
        )
        console.print(result)

    async def workflow_dependency_security_check(self):
        """
        Workflow: Check repository for security issues and dependencies.
        """
        console.print(Panel.fit("🔒 Security & Dependency Check", border_style="cyan"))

        owner = Prompt.ask(OWNER_PROMPT)
        repo = Prompt.ask(REPO_PROMPT)

        console.print("\n[bold]Running security analysis...[/bold]")
        result = await self.github.run_custom_query(
            f"""Perform a security and dependency check for {owner}/{repo}:
            1. Check for any Dependabot alerts
            2. Look for security vulnerabilities in dependencies
            3. Find outdated dependencies
            4. Check for exposed secrets or API keys in recent commits
            5. Review security policy (SECURITY.md) if it exists
            6. List any code scanning alerts if available
            7. Provide recommendations for improving security
            """
        )
        console.print(result)

    async def workflow_release_notes_generator(self):
        """
        Workflow: Generate release notes from commits and PRs.
        """
        console.print(Panel.fit("📝 Release Notes Generator", border_style="cyan"))

        owner = Prompt.ask(OWNER_PROMPT)
        repo = Prompt.ask(REPO_PROMPT)
        since_tag = Prompt.ask("Since which tag/release? (leave empty for latest)", default="")

        query = f"""Generate release notes for {owner}/{repo}"""
        if since_tag:
            query += f" since tag {since_tag}"
        else:
            query += " since the last release"

        query += """:
        1. List all merged pull requests
        2. Categorize changes as:
           - Features
           - Bug Fixes
           - Performance Improvements
           - Documentation
           - Breaking Changes
        3. List contributors
        4. Include commit statistics
        5. Format as markdown suitable for GitHub releases
        """

        console.print("\n[bold]Generating release notes...[/bold]")
        result = await self.github.run_custom_query(query)
        console.print(result)

    async def workflow_project_discovery(self):
        """
        Workflow: Discover interesting projects based on criteria.
        """
        console.print(Panel.fit("🔍 Project Discovery", border_style="cyan"))

        # Create options table
        table = Table(title="Search Criteria")
        table.add_column("Option", style="cyan")
        table.add_column("Description")

        table.add_row("1", "Trending repositories this week")
        table.add_row("2", "New AI/ML tools")
        table.add_row("3", "Active projects needing contributors")
        table.add_row("4", "Projects by specific organization")
        table.add_row("5", "Custom search")

        console.print(table)

        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            query = """Find trending GitHub repositories from the past week:
            1. Show top 10 repositories by stars gained
            2. Include various programming languages
            3. Show description, language, and star count
            4. Include topics/tags
            """
        elif choice == "2":
            query = """Discover new AI/ML tools on GitHub:
            1. Find repositories created in the last month
            2. Topics: machine-learning, artificial-intelligence, deep-learning
            3. More than 50 stars
            4. Has documentation (README with more than 500 words)
            5. Active development (commits in last week)
            """
        elif choice == "3":
            query = """Find active projects looking for contributors:
            1. Repositories with "help wanted" issues
            2. More than 500 stars
            3. Active in last month
            4. Has CONTRIBUTING.md file
            5. Good documentation
            6. Variety of programming languages
            """
        elif choice == "4":
            org = Prompt.ask("Enter organization name", default="google")
            query = f"""Explore projects by {org}:
            1. List their most popular repositories
            2. Recently updated projects (last month)
            3. Projects with most contributors
            4. Categorize by purpose/domain
            5. Highlight interesting or lesser-known projects
            """
        else:
            query = Prompt.ask("Enter your custom discovery query")

        console.print("\n[bold]Discovering projects...[/bold]")
        result = await self.github.run_custom_query(query)
        console.print(result)

    async def workflow_contribution_opportunities(self):
        """
        Workflow: Find contribution opportunities matching skills.
        """
        console.print(Panel.fit("💡 Contribution Opportunities", border_style="cyan"))

        skills = Prompt.ask(
            "Enter your skills (comma-separated)", default="python,javascript,react"
        )
        difficulty = Prompt.ask(
            "Difficulty level", choices=["beginner", "intermediate", "advanced"], default="beginner"
        )

        console.print("\n[bold]Finding contribution opportunities...[/bold]")
        result = await self.github.run_custom_query(
            f"""Find contribution opportunities for someone with skills in {skills} at {difficulty} level:
            1. Search for issues in popular repositories (>1000 stars)
            2. Look for issues labeled:
               - For {difficulty}: good-first-issue, easy, beginner-friendly
               - Or: help-wanted, contributions-welcome
            3. Match repositories using these technologies
            4. Prioritize:
               - Well-documented projects
               - Active maintainer response
               - Clear contribution guidelines
            5. For each opportunity show:
               - Repository and issue details
               - Required skills
               - Estimated effort
               - How to get started
            """
        )
        console.print(result)

    async def cleanup(self):
        """Clean up resources."""
        await self.github.cleanup()


async def interactive_menu():
    """Run an interactive menu for workflow examples."""
    examples = GitHubWorkflowExamples()

    try:
        await examples.setup()

        def build_workflows_table() -> Table:
            table = Table(title="Available Workflows")
            table.add_column("Option", style="cyan", width=8)
            table.add_column("Workflow", style="white")
            table.add_column("Description", style="dim")

            table.add_row(
                "1", "Repository Analysis", "Comprehensive repository statistics and insights"
            )
            table.add_row("2", "Issue Triage", "Categorize and prioritize repository issues")
            table.add_row("3", "PR Review Helper", "Find PRs that need review")
            table.add_row("4", "Good First Issues", "Find beginner-friendly issues")
            table.add_row("5", "Security Check", "Check dependencies and security issues")
            table.add_row("6", "Release Notes", "Generate release notes from commits")
            table.add_row("7", "Project Discovery", "Discover interesting projects")
            table.add_row("8", "Contribution Finder", "Find ways to contribute")
            table.add_row("0", "Exit", "Exit the program")
            return table

        def get_actions() -> dict[str, Callable[[], Awaitable[None]]]:
            return {
                "1": examples.workflow_repository_analysis,
                "2": examples.workflow_issue_triage,
                "3": examples.workflow_pr_review_helper,
                "4": examples.workflow_find_good_first_issues,
                "5": examples.workflow_dependency_security_check,
                "6": examples.workflow_release_notes_generator,
                "7": examples.workflow_project_discovery,
                "8": examples.workflow_contribution_opportunities,
            }

        while True:
            console.print("\n" + "=" * 50)
            console.print(Panel.fit("🌟 GitHub MCP Workflow Examples", border_style="bold green"))

            console.print(build_workflows_table())

            choice = Prompt.ask(
                "\nSelect a workflow", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8"]
            )

            if choice == "0":
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
            else:
                action_map = get_actions()
                action = action_map.get(choice)
                if action is not None:
                    await action()
                else:
                    console.print("[red]Invalid choice. Please try again.[/red]")

            if not Confirm.ask("\n[cyan]Run another workflow?[/cyan]", default=True):
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        logger.error(f"Workflow error: {e}")
    finally:
        await examples.cleanup()


if __name__ == "__main__":
    asyncio.run(interactive_menu())
