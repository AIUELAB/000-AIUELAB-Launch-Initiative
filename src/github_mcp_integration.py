"""
GitHub MCP Integration Module

This module provides integration with GitHub's MCP Server using the mcp-use library.
It enables AI agents to interact with GitHub repositories, issues, pull requests, and more.
"""

import asyncio
import os
from typing import List, Optional

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from loguru import logger
from mcp_use import MCPAgent, MCPClient
from rich.console import Console
from rich.panel import Panel

# Initialize console for rich output
console = Console()

# Load environment variables
load_dotenv()


class GitHubMCPIntegration:
    """
    A class to handle GitHub operations through MCP Server.
    """

    def __init__(
        self,
        config_file: Optional[str] = None,
        llm_provider: str = "openai",
        use_native: bool = True,
    ):
        """
        Initialize GitHub MCP Integration.

        Args:
            config_file: Path to the MCP configuration file (auto-selects if None)
            llm_provider: LLM provider to use ('openai' or 'anthropic')
            use_native: Use native binary instead of Docker (default: True)
        """
        if config_file is None:
            # Auto-select configuration based on use_native flag
            config_file = (
                "github_mcp_config_native.json" if use_native else "github_mcp_config.json"
            )

        self.config_file = config_file
        self.llm_provider = llm_provider
        self.use_native = use_native
        self.client: Optional[MCPClient] = None
        self.agent: Optional[MCPAgent] = None
        self.llm = None

    async def setup(self, max_steps: int = 30):
        """
        Set up the MCP client and agent.

        Args:
            max_steps: Maximum steps for the agent to take
        """
        try:
            # Ensure GitHub PAT is available
            github_pat = os.getenv("GITHUB_PAT")
            if not github_pat:
                raise ValueError(
                    "GITHUB_PAT environment variable not set. Please add it to your .env file."
                )

            # Set the PAT as an environment variable for the MCP server
            os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"] = github_pat

            # Create MCP client from configuration
            self.client = MCPClient.from_config_file(self.config_file)

            # Create LLM based on provider
            if self.llm_provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set.")
                self.llm = ChatOpenAI(model="gpt-4o", api_key=api_key)
            elif self.llm_provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY environment variable not set.")
                # Allow overriding model via env var. Example for Opus 4.1: set ANTHROPIC_MODEL to the exact model ID
                # (e.g., "claude-opus-4.1" or the dated variant provided by Anthropic).
                anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
                self.llm = ChatAnthropic(model=anthropic_model, api_key=api_key)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")

            # Create agent with the client
            self.agent = MCPAgent(llm=self.llm, client=self.client, max_steps=max_steps)

            logger.info(
                f"GitHub MCP Integration initialized with {self.llm_provider} (Native: {self.use_native})"
            )
            console.print(
                Panel.fit(
                    f"✅ GitHub MCP Integration Ready\nProvider: {self.llm_provider}\nMode: {'Native Binary' if self.use_native else 'Docker'}\nMax Steps: {max_steps}",
                    title="Setup Complete",
                    border_style="green",
                )
            )

        except Exception as e:
            logger.error(f"Failed to setup GitHub MCP: {e}")
            console.print(
                Panel.fit(f"❌ Setup Failed: {str(e)}", title="Error", border_style="red")
            )
            raise

    async def search_repositories(self, query: str) -> str:
        """
        Search for GitHub repositories.

        Args:
            query: Search query for repositories

        Returns:
            Search results as a string
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        prompt = f"Search GitHub for repositories matching: {query}. Show the top 5 results with name, description, stars, and URL."

        console.print(f"\n🔍 Searching repositories: {query}")
        result = await self.agent.run(prompt)
        return str(result)

    async def get_repository_info(self, owner: str, repo: str) -> str:
        """
        Get detailed information about a specific repository.

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Repository information as a string
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        prompt = f"Get detailed information about the GitHub repository {owner}/{repo}, including description, languages, stars, issues count, and recent activity."

        console.print(f"\n📚 Getting info for: {owner}/{repo}")
        result = await self.agent.run(prompt)
        return str(result)

    async def list_issues(self, owner: str, repo: str, state: str = "open") -> str:
        """
        List issues for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            state: Issue state ('open', 'closed', or 'all')

        Returns:
            List of issues as a string
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        prompt = f"List {state} issues for the GitHub repository {owner}/{repo}. Show issue number, title, labels, and author."

        console.print(f"\n📋 Listing {state} issues for: {owner}/{repo}")
        result = await self.agent.run(prompt)
        return str(result)

    async def create_issue(
        self, owner: str, repo: str, title: str, body: str, labels: Optional[List[str]] = None
    ) -> str:
        """
        Create a new issue in a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            title: Issue title
            body: Issue body/description
            labels: Optional list of labels

        Returns:
            Created issue information
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        labels_str = f" with labels {', '.join(labels)}" if labels else ""
        prompt = f"""Create a new issue in the GitHub repository {owner}/{repo}:
        Title: {title}
        Body: {body}
        {labels_str}
        """

        console.print(f"\n➕ Creating issue in: {owner}/{repo}")
        result = await self.agent.run(prompt)
        return str(result)

    async def search_code(
        self, query: str, language: Optional[str] = None, org: Optional[str] = None
    ) -> str:
        """
        Search for code across GitHub.

        Args:
            query: Code search query
            language: Optional programming language filter
            org: Optional organization filter

        Returns:
            Code search results
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        filters = []
        if language:
            filters.append(f"language:{language}")
        if org:
            filters.append(f"org:{org}")

        filter_str = " ".join(filters)
        full_query = f"{query} {filter_str}".strip()

        prompt = f"Search GitHub code for: {full_query}. Show the top 5 results with file path, repository, and a snippet of the matching code."

        console.print(f"\n🔎 Searching code: {full_query}")
        result = await self.agent.run(prompt)
        return str(result)

    async def get_pull_requests(self, owner: str, repo: str, state: str = "open") -> str:
        """
        List pull requests for a repository.

        Args:
            owner: Repository owner
            repo: Repository name
            state: PR state ('open', 'closed', or 'all')

        Returns:
            List of pull requests
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        prompt = f"List {state} pull requests for the GitHub repository {owner}/{repo}. Show PR number, title, author, and review status."

        console.print(f"\n🔀 Listing {state} pull requests for: {owner}/{repo}")
        result = await self.agent.run(prompt)
        return str(result)

    async def run_custom_query(self, query: str) -> str:
        """
        Run a custom query using the GitHub MCP agent.

        Args:
            query: Custom query to execute

        Returns:
            Query result
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call setup() first.")

        console.print(f"\n💡 Running custom query: {query}")
        result = await self.agent.run(query)
        return str(result)

    async def cleanup(self):
        """Clean up resources."""
        if self.client and self.client.sessions:
            await self.client.close_all_sessions()
            logger.info("Cleaned up MCP sessions")


async def main():
    """
    Example usage of GitHub MCP Integration.
    """
    # Create integration instance (defaults to native binary)
    github = GitHubMCPIntegration(llm_provider="openai", use_native=True)  # or "anthropic"

    try:
        # Setup the integration
        await github.setup()

        # Example: Search for repositories
        console.print(Panel.fit("Example 1: Search Repositories", border_style="blue"))
        search_results = await github.search_repositories("python machine learning stars:>1000")
        console.print(search_results)

        # Example: Get repository information
        console.print(Panel.fit("Example 2: Get Repository Info", border_style="blue"))
        repo_info = await github.get_repository_info("langchain-ai", "langchain")
        console.print(repo_info)

        # Example: List issues
        console.print(Panel.fit("Example 3: List Issues", border_style="blue"))
        issues = await github.list_issues("microsoft", "vscode", state="open")
        console.print(issues)

        # Example: Search code
        console.print(Panel.fit("Example 4: Search Code", border_style="blue"))
        code_results = await github.search_code("async def", language="python", org="python")
        console.print(code_results)

        # Example: Custom query
        console.print(Panel.fit("Example 5: Custom Query", border_style="blue"))
        custom_result = await github.run_custom_query(
            "Find the most starred JavaScript frameworks on GitHub created in the last year"
        )
        console.print(custom_result)

    finally:
        # Always cleanup
        await github.cleanup()


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
