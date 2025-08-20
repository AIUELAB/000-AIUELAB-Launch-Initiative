#!/usr/bin/env python3
"""
TODO/FIXME/HACKコメントを検出して報告するスクリプト
"""

import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

# チェックするタグ
TODO_TAGS: List[str] = ["TODO", "FIXME", "HACK", "XXX", "BUG", "OPTIMIZE", "REFACTOR"]

# チェック対象の拡張子
FILE_EXTENSIONS: List[str] = [
    ".py",
    ".js",
    ".ts",
    ".jsx",
    ".tsx",
    ".java",
    ".c",
    ".cpp",
    ".h",
    ".hpp",
    ".cs",
    ".go",
    ".rs",
    ".swift",
    ".kt",
    ".rb",
    ".php",
    ".sh",
    ".bash",
    ".yaml",
    ".yml",
    ".json",
    ".md",
    ".txt",
    ".sql",
    ".dockerfile",
    ".makefile",
]

# 除外するパス
EXCLUDE_PATHS: List[str] = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    "dist",
    "build",
    "coverage",
    "htmlcov",
    ".sessions",
    "docs/",
    "tests/",
    ".claude/",
    ".vscode/",
    ".devcontainer/",
    "scripts/check_todos.py",
]


def should_check_file(file_path: Path) -> bool:
    """ファイルをチェックすべきか判定"""
    path_str = str(file_path)
    if any(exclude in path_str for exclude in EXCLUDE_PATHS):
        return False

    if file_path.suffix.lower() not in FILE_EXTENSIONS:
        # 拡張子なしの実行可能スクリプトのみ対象
        if not file_path.suffix and file_path.is_file():
            try:
                with open(file_path, encoding="utf-8") as f:
                    first_line = f.readline()
                    return first_line.startswith("#!")
            except (OSError, UnicodeDecodeError):
                return False
        return False

    return True


def extract_todos(file_path: Path) -> List[Tuple[int, str, str, str]]:
    """ファイルからTODOコメントを抽出"""
    todos: List[Tuple[int, str, str, str]] = []

    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError, OSError):
        return todos

    # 各タグのパターンを作成
    patterns = [(tag, re.compile(rf"\b{tag}\b[:\s]*(.*)$", re.IGNORECASE)) for tag in TODO_TAGS]

    for line_no, line in enumerate(lines, 1):
        for tag, pattern in patterns:
            match = pattern.search(line)
            if not match:
                continue

            content = match.group(1).strip()
            lower = content.lower()

            # 優先度を判定（ネストを浅く）
            if "!" in content[:5] or "urgent" in lower or "critical" in lower:
                priority = "high"
            elif "?" in content[:5] or "maybe" in lower or "consider" in lower:
                priority = "low"
            else:
                priority = "normal"

            todos.append((line_no, tag.upper(), priority, content))

    return todos


def format_todo_report(todos_by_file: Dict[str, List[Tuple[int, str, str, str]]]) -> List[str]:
    """TODO報告をフォーマット"""
    report: List[str] = []

    total_todos = sum(len(todos) for todos in todos_by_file.values())
    tag_counts: Dict[str, int] = defaultdict(int)
    priority_counts: Dict[str, int] = defaultdict(int)

    for todos in todos_by_file.values():
        for _, tag, priority, _ in todos:
            tag_counts[tag] += 1
            priority_counts[priority] += 1

    report.append("📊 TODO Summary:")
    report.append(f"  Total: {total_todos} items in {len(todos_by_file)} files")

    if tag_counts:
        report.append("\n  By Tag:")
        for tag in TODO_TAGS:
            if tag in tag_counts:
                report.append(f"    {tag}: {tag_counts[tag]}")

    if priority_counts:
        report.append("\n  By Priority:")
        for priority in ["high", "normal", "low"]:
            if priority in priority_counts:
                emoji = "🔴" if priority == "high" else "🟡" if priority == "normal" else "🟢"
                report.append(f"    {emoji} {priority}: {priority_counts[priority]}")

    if todos_by_file:
        report.append("\n📝 Details:")
        sorted_files = sorted(
            todos_by_file.items(),
            key=lambda x: max((1 if t[2] == "high" else 2 if t[2] == "normal" else 3 for t in x[1]), default=3),
        )
        for file_path, todos in sorted_files:
            report.append(f"\n  {file_path}:")
            for line_no, tag, priority, content in todos:
                priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "normal" else "🟢"
                report.append(
                    f"    Line {line_no}: {priority_emoji} [{tag}] {content[:80]}{'...' if len(content) > 80 else ''}"
                )

    return report


def main() -> None:
    """メインエントリーポイント"""
    project_root = Path.cwd()
    todos_by_file: Dict[str, List[Tuple[int, str, str, str]]] = {}

    for file_path in project_root.rglob("*"):
        if not file_path.is_file():
            continue
        if not should_check_file(file_path):
            continue
        todos = extract_todos(file_path)
        if todos:
            relative_path = file_path.relative_to(project_root)
            todos_by_file[str(relative_path)] = todos

    report = format_todo_report(todos_by_file)

    print("\n🔍 TODO/FIXME Check Report")
    print("=" * 60)
    for line in report:
        print(line)

    has_high = any(any(todo[2] == "high" for todo in todos) for todos in todos_by_file.values())
    if has_high:
        print("\n⚠️  Warning: High priority TODOs found!")
        print("Please consider addressing them before committing.")

    total_todos = sum(len(todos) for todos in todos_by_file.values())
    if total_todos > 50:
        print(f"\n⚠️  Too many TODOs ({total_todos})! Consider cleaning them up.")
        sys.exit(1)
    if total_todos > 0:
        print(f"\n💡 {total_todos} TODO(s) found. Remember to address them.")
        sys.exit(0)

    print("\n✅ No TODOs found!")
    sys.exit(0)


if __name__ == "__main__":
    main()
