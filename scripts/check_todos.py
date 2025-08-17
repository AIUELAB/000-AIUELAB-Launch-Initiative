#!/usr/bin/env python3
"""
TODO/FIXME/HACKコメントを検出して報告するスクリプト
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
from collections import defaultdict


# チェックするタグ
TODO_TAGS = ['TODO', 'FIXME', 'HACK', 'XXX', 'BUG', 'OPTIMIZE', 'REFACTOR']

# チェック対象の拡張子
FILE_EXTENSIONS = [
    '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.c', '.cpp', '.h', '.hpp',
    '.cs', '.go', '.rs', '.swift', '.kt', '.rb', '.php', '.sh', '.bash',
    '.yaml', '.yml', '.json', '.md', '.txt', '.sql', '.dockerfile', '.makefile'
]

# 除外するパス
EXCLUDE_PATHS = [
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    'node_modules',
    '.pytest_cache',
    '.mypy_cache',
    'dist',
    'build',
    'coverage',
    'htmlcov',
    '.sessions',
]


def should_check_file(file_path: Path) -> bool:
    """ファイルをチェックすべきか判定"""
    # 除外パスのチェック
    path_str = str(file_path)
    for exclude in EXCLUDE_PATHS:
        if exclude in path_str:
            return False
    
    # 拡張子のチェック
    if file_path.suffix.lower() not in FILE_EXTENSIONS:
        # 拡張子なしのファイルでも、実行可能ファイルはチェック
        if not file_path.suffix and file_path.is_file():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline()
                    if first_line.startswith('#!'):
                        return True
            except:
                pass
        return False
    
    return True


def extract_todos(file_path: Path) -> List[Tuple[int, str, str, str]]:
    """ファイルからTODOコメントを抽出"""
    todos = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError):
        return todos
    
    # 各タグのパターンを作成
    patterns = []
    for tag in TODO_TAGS:
        # タグの後にコロンやスペースが続くパターン
        patterns.append((tag, re.compile(
            rf'\b{tag}\b[:\s]*(.*)$',
            re.IGNORECASE
        )))
    
    for line_no, line in enumerate(lines, 1):
        for tag, pattern in patterns:
            match = pattern.search(line)
            if match:
                # TODOの内容を抽出
                content = match.group(1).strip()
                
                # 優先度を判定
                priority = 'normal'
                if '!' in content[:5] or 'urgent' in content.lower() or 'critical' in content.lower():
                    priority = 'high'
                elif '?' in content[:5] or 'maybe' in content.lower() or 'consider' in content.lower():
                    priority = 'low'
                
                todos.append((line_no, tag.upper(), priority, content))
    
    return todos


def format_todo_report(todos_by_file: dict) -> List[str]:
    """TODO報告をフォーマット"""
    report = []
    
    # 統計情報
    total_todos = sum(len(todos) for todos in todos_by_file.values())
    tag_counts = defaultdict(int)
    priority_counts = defaultdict(int)
    
    for todos in todos_by_file.values():
        for _, tag, priority, _ in todos:
            tag_counts[tag] += 1
            priority_counts[priority] += 1
    
    # サマリー
    report.append(f"📊 TODO Summary:")
    report.append(f"  Total: {total_todos} items in {len(todos_by_file)} files")
    
    if tag_counts:
        report.append(f"\n  By Tag:")
        for tag in TODO_TAGS:
            if tag in tag_counts:
                report.append(f"    {tag}: {tag_counts[tag]}")
    
    if priority_counts:
        report.append(f"\n  By Priority:")
        for priority in ['high', 'normal', 'low']:
            if priority in priority_counts:
                emoji = '🔴' if priority == 'high' else '🟡' if priority == 'normal' else '🟢'
                report.append(f"    {emoji} {priority}: {priority_counts[priority]}")
    
    # 詳細
    if todos_by_file:
        report.append(f"\n📝 Details:")
        
        # 優先度順にソート
        sorted_files = sorted(todos_by_file.items(), 
                            key=lambda x: max((1 if t[2] == 'high' else 2 if t[2] == 'normal' else 3 
                                             for t in x[1]), default=3))
        
        for file_path, todos in sorted_files:
            report.append(f"\n  {file_path}:")
            for line_no, tag, priority, content in todos:
                priority_emoji = '🔴' if priority == 'high' else '🟡' if priority == 'normal' else '🟢'
                report.append(f"    Line {line_no}: {priority_emoji} [{tag}] {content[:80]}{'...' if len(content) > 80 else ''}")
    
    return report


def main():
    """メインエントリーポイント"""
    project_root = Path.cwd()
    todos_by_file = {}
    
    # ファイルを走査
    for file_path in project_root.rglob('*'):
        if not file_path.is_file():
            continue
        
        if not should_check_file(file_path):
            continue
        
        todos = extract_todos(file_path)
        if todos:
            relative_path = file_path.relative_to(project_root)
            todos_by_file[str(relative_path)] = todos
    
    # レポート生成
    report = format_todo_report(todos_by_file)
    
    # 出力
    print("\n🔍 TODO/FIXME Check Report")
    print("=" * 60)
    for line in report:
        print(line)
    
    # 高優先度のTODOがある場合は警告
    has_high_priority = any(
        any(todo[2] == 'high' for todo in todos)
        for todos in todos_by_file.values()
    )
    
    if has_high_priority:
        print("\n⚠️  Warning: High priority TODOs found!")
        print("Please consider addressing them before committing.")
    
    # 終了コード（TODOの数に応じて）
    total_todos = sum(len(todos) for todos in todos_by_file.values())
    if total_todos > 50:
        print(f"\n⚠️  Too many TODOs ({total_todos})! Consider cleaning them up.")
        sys.exit(1)
    elif total_todos > 0:
        print(f"\n💡 {total_todos} TODO(s) found. Remember to address them.")
        sys.exit(0)
    else:
        print("\n✅ No TODOs found!")
        sys.exit(0)


if __name__ == "__main__":
    main()