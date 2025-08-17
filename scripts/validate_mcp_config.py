#!/usr/bin/env python3
"""
MCP設定ファイルの検証スクリプト
claude_desktop_config.jsonの構文と設定をチェック
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List


def validate_json_syntax(file_path: Path) -> tuple[bool, str]:
    """JSON構文の検証"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json.load(f)
        return True, "Valid JSON syntax"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON syntax: {e}"
    except FileNotFoundError:
        return False, f"File not found: {file_path}"
    except Exception as e:
        return False, f"Error reading file: {e}"


def validate_mcp_server(server_name: str, server_config: Dict[str, Any]) -> List[str]:
    """個別のMCPサーバー設定を検証"""
    errors = []
    warnings = []
    
    # 必須フィールドのチェック
    if 'command' not in server_config:
        errors.append(f"  ❌ {server_name}: Missing 'command' field")
    
    # コマンドの検証
    if 'command' in server_config:
        command = server_config['command']
        
        if not command:
            errors.append(f"  ❌ {server_name}: Empty command")
        elif isinstance(command, str):
            # 単一コマンドの場合
            if not Path(command).name:
                errors.append(f"  ❌ {server_name}: Invalid command: {command}")
        elif isinstance(command, list):
            # コマンド配列の場合
            if len(command) == 0:
                errors.append(f"  ❌ {server_name}: Empty command array")
            else:
                cmd_executable = command[0]
                # 実行可能ファイルの存在チェック（一般的なコマンドのみ）
                common_commands = ['node', 'python', 'python3', 'npx', 'uvx', 'docker']
                if cmd_executable in common_commands:
                    if os.system(f"which {cmd_executable} > /dev/null 2>&1") != 0:
                        warnings.append(f"  ⚠️  {server_name}: Command '{cmd_executable}' not found in PATH")
    
    # 引数の検証
    if 'args' in server_config:
        args = server_config['args']
        if not isinstance(args, list):
            errors.append(f"  ❌ {server_name}: 'args' must be a list")
        elif isinstance(command, str):
            warnings.append(f"  ⚠️  {server_name}: 'args' is ignored when 'command' is a string")
    
    # 環境変数の検証
    if 'env' in server_config:
        env = server_config['env']
        if not isinstance(env, dict):
            errors.append(f"  ❌ {server_name}: 'env' must be a dictionary")
        else:
            for key, value in env.items():
                if not isinstance(key, str):
                    errors.append(f"  ❌ {server_name}: Environment variable key must be a string: {key}")
                if value is not None and not isinstance(value, str):
                    errors.append(f"  ❌ {server_name}: Environment variable value must be a string: {key}={value}")
                
                # 環境変数が設定されているかチェック
                if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                    env_var = value[2:-1]
                    if not os.getenv(env_var):
                        warnings.append(f"  ⚠️  {server_name}: Environment variable not set: {env_var}")
    
    # Node.jsパッケージの存在チェック
    if isinstance(server_config.get('command'), list):
        command = server_config['command']
        if len(command) > 0 and command[0] in ['node', 'npx']:
            if len(command) > 1:
                package_path = command[1]
                if package_path.startswith('/') or package_path.startswith('./'):
                    # ローカルパスの場合
                    if not Path(package_path).exists():
                        errors.append(f"  ❌ {server_name}: Package not found: {package_path}")
                elif '@' in package_path:
                    # npmパッケージの場合
                    package_name = package_path.split('/')[-1]
                    # パッケージの存在確認（簡易チェック）
                    node_modules = Path('node_modules')
                    if node_modules.exists():
                        if not any(node_modules.glob(f"**/{package_name}*")):
                            warnings.append(f"  ⚠️  {server_name}: Package may not be installed: {package_path}")
    
    return errors + warnings


def validate_mcp_config(config_path: Path) -> tuple[bool, List[str]]:
    """MCP設定全体を検証"""
    messages = []
    
    # JSON構文チェック
    is_valid, message = validate_json_syntax(config_path)
    if not is_valid:
        messages.append(f"❌ {message}")
        return False, messages
    
    messages.append(f"✅ Valid JSON syntax")
    
    # 設定内容の読み込み
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # mcpServersセクションの存在チェック
    if 'mcpServers' not in config:
        messages.append("❌ Missing 'mcpServers' section")
        return False, messages
    
    mcp_servers = config['mcpServers']
    if not isinstance(mcp_servers, dict):
        messages.append("❌ 'mcpServers' must be a dictionary")
        return False, messages
    
    if not mcp_servers:
        messages.append("⚠️  No MCP servers configured")
        return True, messages
    
    messages.append(f"📦 Found {len(mcp_servers)} MCP server(s)")
    
    # 各サーバーの検証
    has_errors = False
    for server_name, server_config in mcp_servers.items():
        if not isinstance(server_config, dict):
            messages.append(f"  ❌ {server_name}: Invalid configuration (must be a dictionary)")
            has_errors = True
            continue
        
        server_messages = validate_mcp_server(server_name, server_config)
        if server_messages:
            messages.extend(server_messages)
            if any('❌' in msg for msg in server_messages):
                has_errors = True
        else:
            messages.append(f"  ✅ {server_name}: Valid configuration")
    
    return not has_errors, messages


def check_required_env_vars() -> List[str]:
    """必要な環境変数のチェック"""
    messages = []
    
    # 一般的に必要な環境変数
    required_vars = {
        'GITHUB_TOKEN': 'GitHub MCP server',
        'OPENAI_API_KEY': 'OpenAI integration',
        'ANTHROPIC_API_KEY': 'Anthropic integration',
        'BRAVE_API_KEY': 'Brave Search',
    }
    
    missing_vars = []
    for var, usage in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"  - {var} (for {usage})")
    
    if missing_vars:
        messages.append("\n⚠️  Missing environment variables:")
        messages.extend(missing_vars)
        messages.append("  💡 Tip: Copy .env.mcp.example to .env.mcp and fill in your values")
    
    return messages


def main():
    """メインエントリーポイント"""
    project_root = Path.cwd()
    config_path = project_root / 'mcp-config' / 'claude_desktop_config.json'
    
    print("🔍 Validating MCP configuration...")
    print(f"📄 Config file: {config_path}")
    print()
    
    # 設定ファイルの検証
    is_valid, messages = validate_mcp_config(config_path)
    
    for message in messages:
        print(message)
    
    # 環境変数のチェック
    env_messages = check_required_env_vars()
    if env_messages:
        print()
        for message in env_messages:
            print(message)
    
    print()
    if is_valid:
        print("✅ MCP configuration validation passed!")
        sys.exit(0)
    else:
        print("❌ MCP configuration validation failed!")
        print("Please fix the errors above before proceeding.")
        sys.exit(1)


if __name__ == "__main__":
    main()