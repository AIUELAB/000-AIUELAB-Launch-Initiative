#!/usr/bin/env python3
"""
Enhanced Headless Mode for Claude Code
Provides non-interactive execution for CI/CD and automation

Features:
- Task orchestration with predefined workflows
- Real-time streaming output
- JSON/YAML output formats
- Parallel task execution
- Result caching
- Error recovery and retry logic
"""

import asyncio
import hashlib
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

import click
import yaml
from loguru import logger
from rich.console import Console
from rich.table import Table

# Local imports
from .error_recovery import ErrorRecovery
from .session_manager import SessionManager

console = Console()


class TaskType(Enum):
    """Predefined task types"""

    TEST = "test"
    LINT = "lint"
    FORMAT = "format"
    REVIEW = "review"
    DOCS = "docs"
    BUILD = "build"
    DEPLOY = "deploy"
    ANALYZE = "analyze"
    OPTIMIZE = "optimize"
    SECURITY = "security"


class OutputFormat(Enum):
    """Output format options"""

    TEXT = "text"
    JSON = "json"
    YAML = "yaml"
    STREAM_JSON = "stream-json"
    MARKDOWN = "markdown"
    HTML = "html"


@dataclass
class TaskResult:
    """Task execution result"""

    task_id: str
    task_type: TaskType
    status: str  # success, failure, skipped, timeout
    start_time: datetime
    end_time: datetime
    output: Any
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)

    @property
    def duration(self) -> float:
        """Calculate task duration in seconds"""
        return (self.end_time - self.start_time).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "status": self.status,
            "duration": self.duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "output": self.output,
            "errors": self.errors,
            "warnings": self.warnings,
            "metrics": self.metrics,
        }


class TaskCache:
    """Simple task result caching"""

    def __init__(self, cache_dir: Path = Path(".claude_cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=1)  # Default TTL

    def _get_cache_key(self, task_type: str, params: dict) -> str:
        """Generate cache key from task and parameters"""
        content = f"{task_type}:{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, task_type: str, params: dict) -> TaskResult | None:
        """Get cached result if available and not expired"""
        key = self._get_cache_key(task_type, params)
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            with cache_file.open(encoding="utf-8") as f:
                payload = json.load(f)
            # Parse timestamp and check expiry
            timestamp = datetime.fromisoformat(payload.get("timestamp"))
            if datetime.now() - timestamp > self.ttl:
                cache_file.unlink()
                return None

            data = payload.get("result", {})
            # Reconstruct TaskResult
            result = TaskResult(
                task_id=data.get("task_id", "unknown"),
                task_type=TaskType(data.get("task_type", TaskType.TEST.value)),
                status=data.get("status", "success"),
                start_time=datetime.fromisoformat(data.get("start_time")),
                end_time=datetime.fromisoformat(data.get("end_time")),
                output=data.get("output"),
                errors=list(data.get("errors", [])),
                warnings=list(data.get("warnings", [])),
                metrics=dict(data.get("metrics", {})),
            )
            return result
        except Exception as e:
            logger.warning(f"Failed to load cache: {e}")
            return None

    def set(self, task_type: str, params: dict, result: TaskResult):
        """Cache task result"""
        key = self._get_cache_key(task_type, params)
        cache_file = self.cache_dir / f"{key}.json"

        try:
            payload = {
                "result": result.to_dict(),
                "timestamp": datetime.now().isoformat(),
            }
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Failed to save cache: {e}")

    def clear(self):
        """Clear all cache"""
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()


class HeadlessExecutor:
    """Enhanced headless execution engine"""

    def __init__(
        self,
        output_format: OutputFormat = OutputFormat.TEXT,
        verbose: bool = False,
        timeout: int = 300,
        parallel: bool = False,
        use_cache: bool = True,
    ):
        self.output_format = output_format
        self.verbose = verbose
        self.timeout = timeout
        self.parallel = parallel
        self.cache = TaskCache() if use_cache else None
        self.error_recovery = ErrorRecovery()
        self.session_manager = SessionManager()
        self.executor = ThreadPoolExecutor(max_workers=4) if parallel else None

    async def execute_task(
        self, task_type: TaskType, params: dict | None = None, files: list[str] | None = None
    ) -> TaskResult:
        """Execute a single task"""
        task_id = f"{task_type.value}_{int(time.time())}"
        params = params or {}
        files = files or []

        # Check cache
        if self.cache:
            cached = self.cache.get(task_type.value, params)
            if cached:
                logger.info(f"Using cached result for {task_type.value}")
                return cached

        start_time = datetime.now()
        result = TaskResult(
            task_id=task_id,
            task_type=task_type,
            status="running",
            start_time=start_time,
            end_time=start_time,
            output=None,
        )

        try:
            # Execute task based on type
            if task_type == TaskType.TEST:
                result.output = await self._run_tests(params, files)
            elif task_type == TaskType.LINT:
                result.output = await self._run_lint(params, files)
            elif task_type == TaskType.FORMAT:
                result.output = await self._run_format(params, files)
            elif task_type == TaskType.REVIEW:
                result.output = await self._run_review(params, files)
            elif task_type == TaskType.DOCS:
                result.output = await self._generate_docs(params, files)
            elif task_type == TaskType.BUILD:
                result.output = await self._run_build(params)
            elif task_type == TaskType.ANALYZE:
                result.output = await self._run_analysis(params, files)
            elif task_type == TaskType.OPTIMIZE:
                result.output = await self._run_optimize(params, files)
            elif task_type == TaskType.SECURITY:
                result.output = await self._run_security_scan(params, files)
            else:
                raise ValueError(f"Unknown task type: {task_type}")

            result.status = "success"

        except TimeoutError:
            result.status = "timeout"
            result.errors.append(f"Task timed out after {self.timeout} seconds")
        except Exception as e:
            result.status = "failure"
            result.errors.append(str(e))
            logger.error(f"Task failed: {e}")

        result.end_time = datetime.now()

        # Cache result
        if self.cache and result.status == "success":
            self.cache.set(task_type.value, params, result)

        return result

    async def _run_tests(self, params: dict, files: list[str]) -> dict:
        """Run test suite"""
        cmd = ["pytest", "tests/", "-v", "--tb=short"]

        if files:
            cmd.extend(files)

        if params.get("coverage"):
            cmd.extend(["--cov=src", "--cov-report=term-missing"])

        if params.get("parallel"):
            cmd.extend(["-n", "auto"])

        result = await self._run_command(cmd)

        # Parse test results
        lines = result["stdout"].split("\n")
        passed = failed = skipped = 0

        for line in lines:
            if "passed" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        passed = int(parts[i - 1]) if i > 0 else 0
            if "failed" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "failed":
                        failed = int(parts[i - 1]) if i > 0 else 0

        return {
            "command": " ".join(cmd),
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "output": result["stdout"],
            "errors": result["stderr"],
            "exit_code": result["exit_code"],
        }

    async def _run_lint(self, params: dict, files: list[str]) -> dict:
        """Run linting tools"""
        results = {}

        # Ruff
        cmd = ["ruff", "check"]
        if files:
            cmd.extend(files)
        else:
            cmd.extend(["src/", "tests/"])

        if params.get("fix"):
            cmd.append("--fix")

        ruff_result = await self._run_command(cmd)
        results["ruff"] = ruff_result

        # Black check
        cmd = ["black", "--check"]
        if files:
            cmd.extend(files)
        else:
            cmd.extend(["src/", "tests/"])

        black_result = await self._run_command(cmd)
        results["black"] = black_result

        # mypy
        if params.get("type_check", True):
            cmd = ["mypy"]
            if files:
                cmd.extend(files)
            else:
                cmd.append("src/")

            mypy_result = await self._run_command(cmd)
            results["mypy"] = mypy_result

        return results

    async def _run_format(self, params: dict, files: list[str]) -> dict:
        """Run code formatters"""
        results = {}

        # Black
        cmd = ["black"]
        if files:
            cmd.extend(files)
        else:
            cmd.extend(["src/", "tests/"])

        black_result = await self._run_command(cmd)
        results["black"] = black_result

        # isort
        cmd = ["isort"]
        if files:
            cmd.extend(files)
        else:
            cmd.extend(["src/", "tests/"])

        isort_result = await self._run_command(cmd)
        results["isort"] = isort_result

        return results

    async def _run_review(self, params: dict, files: list[str]) -> dict:
        """Run code review checks"""
        results = {"complexity": [], "duplicates": [], "security": [], "todos": []}

        # Check complexity
        cmd = ["radon", "cc", "-s"] + (files or ["src/"])
        complexity = await self._run_command(cmd)
        results["complexity"] = complexity

        # Check TODOs
        cmd = ["python", "scripts/check_todos.py"]
        todos = await self._run_command(cmd)
        results["todos"] = todos

        # Security check
        cmd = ["bandit", "-r"] + (files or ["src/"])
        security = await self._run_command(cmd)
        results["security"] = security

        return results

    async def _generate_docs(self, params: dict, files: list[str]) -> dict:
        """Generate documentation"""
        results = {}

        # Generate API docs with pdoc
        cmd = ["pdoc", "--html", "--output-dir", "docs/api", "src"]
        api_docs = await self._run_command(cmd)
        results["api_docs"] = api_docs

        # Generate coverage report
        if params.get("coverage"):
            cmd = ["coverage", "html"]
            coverage = await self._run_command(cmd)
            results["coverage"] = coverage

        return results

    async def _run_build(self, params: dict) -> dict:
        """Run build process"""
        results = {}

        # Build Python package
        cmd = ["python", "-m", "build"]
        build = await self._run_command(cmd)
        results["build"] = build

        # Build Docker image if Dockerfile exists
        if Path("Dockerfile").exists():
            tag = params.get("tag", "latest")
            cmd = ["docker", "build", "-t", f"claude-code:{tag}", "."]
            docker = await self._run_command(cmd)
            results["docker"] = docker

        return results

    async def _run_analysis(self, params: dict, files: list[str]) -> dict:
        """Run code analysis"""
        results = {}

        # Cyclomatic complexity
        cmd = ["radon", "cc", "-s", "-a"] + (files or ["src/"])
        complexity = await self._run_command(cmd)
        results["complexity"] = complexity

        # Maintainability index
        cmd = ["radon", "mi", "-s"] + (files or ["src/"])
        maintainability = await self._run_command(cmd)
        results["maintainability"] = maintainability

        # Lines of code
        cmd = ["cloc", "--json"] + (files or ["src/", "tests/"])
        loc = await self._run_command(cmd)
        results["lines_of_code"] = loc

        return results

    async def _run_optimize(self, params: dict, files: list[str]) -> dict:
        """Run performance optimization checks"""
        results = {}

        # Profile with py-spy
        if params.get("profile"):
            cmd = [
                "py-spy",
                "record",
                "-o",
                "profile.svg",
                "--",
                "python",
                "-m",
                "pytest",
                "tests/",
            ]
            profile = await self._run_command(cmd)
            results["profile"] = profile

        # Memory profiling
        if params.get("memory"):
            cmd = ["python", "-m", "memory_profiler", "src/main.py"]
            memory = await self._run_command(cmd)
            results["memory"] = memory

        return results

    async def _run_security_scan(self, params: dict, files: list[str]) -> dict:
        """Run security scans"""
        results = {}

        # Bandit
        cmd = ["bandit", "-r", "-f", "json"] + (files or ["src/"])
        bandit = await self._run_command(cmd)
        results["bandit"] = bandit

        # Safety check
        cmd = ["safety", "check", "--json"]
        safety = await self._run_command(cmd)
        results["safety"] = safety

        # Check for secrets
        cmd = ["python", "scripts/check_no_secrets.py"]
        secrets = await self._run_command(cmd)
        results["secrets"] = secrets

        return results

    async def _run_command(self, cmd: list[str]) -> dict[str, Any]:
        """Run a shell command with timeout"""
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout)

            return {
                "command": " ".join(cmd),
                "stdout": stdout.decode("utf-8"),
                "stderr": stderr.decode("utf-8"),
                "exit_code": proc.returncode,
            }
        except TimeoutError:
            raise
        except Exception as e:
            return {"command": " ".join(cmd), "stdout": "", "stderr": str(e), "exit_code": -1}

    async def execute_workflow(
        self, tasks: list[TaskType], params: dict | None = None, files: list[str] | None = None
    ) -> list[TaskResult]:
        """Execute multiple tasks in sequence or parallel"""
        results = []

        if self.parallel and self.executor:
            # Run tasks in parallel
            futures = []
            for task in tasks:
                future = asyncio.create_task(self.execute_task(task, params, files))
                futures.append(future)

            results = await asyncio.gather(*futures)
        else:
            # Run tasks sequentially
            for task in tasks:
                result = await self.execute_task(task, params, files)
                results.append(result)

                # Stop on failure if requested
                if result.status == "failure" and not params.get("continue_on_error"):
                    break

        return results

    def format_output(self, results: list[TaskResult]) -> str:
        """Format results based on output format"""
        if self.output_format == OutputFormat.JSON:
            return json.dumps([r.to_dict() for r in results], indent=2)

        elif self.output_format == OutputFormat.YAML:
            return yaml.dump([r.to_dict() for r in results], default_flow_style=False)

        elif self.output_format == OutputFormat.STREAM_JSON:
            lines = []
            for r in results:
                lines.append(json.dumps(r.to_dict()))
            return "\n".join(lines)

        elif self.output_format == OutputFormat.MARKDOWN:
            md = "# Task Execution Results\n\n"
            for r in results:
                md += f"## {r.task_type.value.title()}\n\n"
                md += f"- **Status**: {r.status}\n"
                md += f"- **Duration**: {r.duration:.2f}s\n"
                if r.errors:
                    md += f"- **Errors**: {', '.join(r.errors)}\n"
                md += "\n"
            return md

        elif self.output_format == OutputFormat.HTML:
            html = "<html><body><h1>Task Results</h1>"
            for r in results:
                html += f"<h2>{r.task_type.value}</h2>"
                html += f"<p>Status: {r.status}</p>"
                html += f"<p>Duration: {r.duration:.2f}s</p>"
                if r.errors:
                    html += f"<p>Errors: {', '.join(r.errors)}</p>"
            html += "</body></html>"
            return html

        else:  # TEXT format
            table = Table(title="Task Execution Results")
            table.add_column("Task", style="cyan")
            table.add_column("Status", style="green")
            table.add_column("Duration", style="yellow")
            table.add_column("Errors", style="red")

            for r in results:
                status_icon = "✅" if r.status == "success" else "❌"
                table.add_row(
                    r.task_type.value,
                    f"{status_icon} {r.status}",
                    f"{r.duration:.2f}s",
                    ", ".join(r.errors[:50]) if r.errors else "-",
                )

            console = Console()
            with console.capture() as capture:
                console.print(table)

            return capture.get()

    def cleanup(self):
        """Cleanup resources"""
        if self.executor:
            self.executor.shutdown(wait=True)
        if self.cache:
            # Optionally clear old cache entries
            pass


@click.command()
@click.option(
    "-t",
    "--task",
    multiple=True,
    type=click.Choice([t.value for t in TaskType]),
    help="Task(s) to execute",
)
@click.option(
    "-o",
    "--output",
    type=click.Choice([f.value for f in OutputFormat]),
    default="text",
    help="Output format",
)
@click.option("-f", "--file", multiple=True, help="Files to process")
@click.option("--timeout", default=300, help="Execution timeout in seconds")
@click.option("-v", "--verbose", is_flag=True, help="Verbose output")
@click.option("--parallel", is_flag=True, help="Run tasks in parallel")
@click.option("--no-cache", is_flag=True, help="Disable result caching")
@click.option("--continue-on-error", is_flag=True, help="Continue on task failure")
def main(task, output, file, timeout, verbose, parallel, no_cache, continue_on_error):
    """Claude Code Headless Mode - Enhanced Edition"""

    # Setup logging
    if verbose:
        logger.add(sys.stderr, level="DEBUG")
    else:
        logger.add(sys.stderr, level="INFO")

    # Create executor
    output_format = OutputFormat(output)
    executor = HeadlessExecutor(
        output_format=output_format,
        verbose=verbose,
        timeout=timeout,
        parallel=parallel,
        use_cache=not no_cache,
    )

    # Convert task strings to TaskType
    tasks = [TaskType(t) for t in task]

    if not tasks:
        # Default workflow
        tasks = [TaskType.TEST, TaskType.LINT]

    # Prepare parameters
    params = {"continue_on_error": continue_on_error}

    # Run async tasks
    async def run():
        try:
            results = await executor.execute_workflow(tasks, params, list(file))
            output_str = executor.format_output(results)
            print(output_str)

            # Exit with error if any task failed
            if any(r.status == "failure" for r in results):
                sys.exit(1)

        except Exception as e:
            logger.error(f"Execution failed: {e}")
            sys.exit(1)
        finally:
            executor.cleanup()

    # Run the async function
    asyncio.run(run())


if __name__ == "__main__":
    main()
