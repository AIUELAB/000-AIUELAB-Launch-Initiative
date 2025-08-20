#!/usr/bin/env python3
"""
.envファイルと.env.exampleファイルの同期を保つスクリプト
新しい環境変数が追加されたら自動的にテンプレートファイルを更新
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set


def parse_env_file(file_path: Path) -> Dict[str, str]:
    """環境変数ファイルをパース"""
    env_vars = {}

    if not file_path.exists():
        return env_vars

    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # コメントや空行はスキップ
            if not line or line.startswith('#'):
                continue

            # KEY=value形式をパース
            match = re.match(r'^([A-Z_][A-Z0-9_]*)\s*=\s*(.*)$', line)
            if match:
                key = match.group(1)
                value = match.group(2).strip('"\'')
                env_vars[key] = value

    return env_vars


def create_template_value(key: str, value: str) -> str:
    """環境変数のテンプレート値を生成"""
    # キー名から適切なプレースホルダーを生成
    key_lower = key.lower()

    if 'api_key' in key_lower or 'apikey' in key_lower:
        return 'your-api-key-here'
    elif 'token' in key_lower:
        return 'your-token-here'
    elif 'secret' in key_lower:
        return 'your-secret-here'
    elif 'password' in key_lower or 'passwd' in key_lower:
        return 'your-password-here'
    elif 'url' in key_lower:
        if 'database' in key_lower or 'db' in key_lower:
            return 'postgresql://user:password@localhost:5432/dbname'
        else:
            return 'https://example.com'
    elif 'host' in key_lower:
        return 'localhost'
    elif 'port' in key_lower:
        return '8080'
    elif 'debug' in key_lower:
        return 'false'
    elif 'env' in key_lower or 'environment' in key_lower:
        return 'development'
    else:
        return f'your-{key.lower().replace("_", "-")}-here'


def update_template_file(template_path: Path, env_vars: Dict[str, str],
                        existing_template: Dict[str, str]) -> bool:
    """テンプレートファイルを更新"""
    updated = False

    # 新しい環境変数を検出
    new_vars = set(env_vars.keys()) - set(existing_template.keys())

    if new_vars:
        print(f"📝 Found {len(new_vars)} new environment variables:")
        for var in sorted(new_vars):
            print(f"  - {var}")

        # テンプレートファイルに追記
        with open(template_path, 'a', encoding='utf-8') as f:
            f.write("\n# Automatically added by sync_env_template.py\n")
            for var in sorted(new_vars):
                template_value = create_template_value(var, env_vars[var])
                f.write(f"{var}={template_value}\n")

        updated = True
        print(f"✅ Updated {template_path.name} with new variables")

    return updated


def main():
    """メインエントリーポイント"""
    project_root = Path.cwd()

    # チェックする環境変数ファイルのペア
    env_pairs = [
        ('.env', '.env.example'),
        ('.env.mcp', '.env.mcp.example'),
        ('.env.local', '.env.local.example'),
        ('.env.development', '.env.development.example'),
        ('.env.production', '.env.production.example'),
    ]

    has_updates = False

    for env_file, template_file in env_pairs:
        env_path = project_root / env_file
        template_path = project_root / template_file

        if not env_path.exists():
            continue

        # 環境変数ファイルをパース
        env_vars = parse_env_file(env_path)
        existing_template = parse_env_file(template_path)

        if not env_vars:
            continue

        # テンプレートファイルが存在しない場合は作成
        if not template_path.exists():
            print(f"📝 Creating new template file: {template_file}")
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(f"# Environment variables template for {env_file}\n")
                f.write("# Copy this file to " + env_file + " and fill in your values\n\n")

                for key in sorted(env_vars.keys()):
                    template_value = create_template_value(key, env_vars[key])
                    f.write(f"{key}={template_value}\n")

            has_updates = True
            print(f"✅ Created {template_file}")
        else:
            # 既存のテンプレートファイルを更新
            if update_template_file(template_path, env_vars, existing_template):
                has_updates = True

    # 削除された変数の警告
    for env_file, template_file in env_pairs:
        env_path = project_root / env_file
        template_path = project_root / template_file

        if env_path.exists() and template_path.exists():
            env_vars = parse_env_file(env_path)
            template_vars = parse_env_file(template_path)

            removed_vars = set(template_vars.keys()) - set(env_vars.keys())
            if removed_vars:
                print(f"\n⚠️  Warning: The following variables exist in {template_file} but not in {env_file}:")
                for var in sorted(removed_vars):
                    print(f"  - {var}")
                print("Consider removing them from the template if they're no longer needed.")

    if has_updates:
        print("\n✅ Environment templates synchronized successfully!")
        sys.exit(0)
    else:
        print("✅ Environment templates are already up to date.")
        sys.exit(0)


if __name__ == "__main__":
    main()
