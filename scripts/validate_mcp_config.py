#!/usr/bin/env python3
"""
Validate MCP configuration files for CI/CD
"""

import json
import sys
from pathlib import Path
from typing import Any


def validate_json_file(file_path: Path) -> tuple[bool, str]:
    """Validate JSON file format."""
    try:
        with open(file_path) as f:
            json.load(f)
        return True, "OK"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {e}"
    except FileNotFoundError:
        return False, "File not found"


def validate_mcp_server_config(config: dict[str, Any]) -> list[str]:
    """Validate MCP server configuration."""
    errors = []

    if "mcpServers" not in config:
        errors.append("Missing 'mcpServers' key")
        return errors

    servers = config["mcpServers"]
    for server_name, server_config in servers.items():
        # Check required fields
        if "command" not in server_config:
            errors.append(f"{server_name}: Missing 'command' field")

        if "args" in server_config and not isinstance(server_config["args"], list):
            errors.append(f"{server_name}: 'args' must be a list")

        # Check environment variables
        if "env" in server_config:
            for env_key, env_value in server_config["env"].items():
                if "${" in str(env_value) and "}" in str(env_value):
                    # Check if it's a valid env var reference
                    var_name = str(env_value).replace("${", "").replace("}", "")
                    if not var_name.isupper():
                        errors.append(f"{server_name}: Invalid env var reference: {env_value}")

    return errors


def main():
    """Main validation function."""
    print("🔍 Validating MCP Configuration...")

    # Find config files
    base_dir = Path(__file__).parent.parent
    config_dir = base_dir / "mcp-config"

    has_errors = False

    # Check main config
    main_config = config_dir / "claude_desktop_config.json"
    if main_config.exists():
        valid, msg = validate_json_file(main_config)
        if valid:
            print(f"✅ {main_config.name}: Valid JSON")

            # Validate content
            with open(main_config) as f:
                config = json.load(f)

            errors = validate_mcp_server_config(config)
            if errors:
                print(f"❌ {main_config.name}: Configuration errors:")
                for error in errors:
                    print(f"   - {error}")
                has_errors = True
            else:
                print(f"✅ {main_config.name}: Valid configuration")
        else:
            print(f"❌ {main_config.name}: {msg}")
            has_errors = True
    else:
        print(f"⚠️  {main_config.name}: Not found")

    # Check profile configs
    profiles_dir = config_dir / "profiles"
    if profiles_dir.exists():
        for profile_file in profiles_dir.glob("*.json"):
            valid, msg = validate_json_file(profile_file)
            if valid:
                print(f"✅ Profile {profile_file.name}: Valid JSON")

                # Validate content
                with open(profile_file) as f:
                    config = json.load(f)

                errors = validate_mcp_server_config(config)
                if errors:
                    print(f"❌ Profile {profile_file.name}: Configuration errors:")
                    for error in errors:
                        print(f"   - {error}")
                    has_errors = True
                else:
                    print(f"✅ Profile {profile_file.name}: Valid configuration")
            else:
                print(f"❌ Profile {profile_file.name}: {msg}")
                has_errors = True

    # Check .ollama.yml exists
    ollama_config = base_dir / ".ollama.yml"
    if ollama_config.exists():
        print("✅ .ollama.yml: Found")
    else:
        print("⚠️  .ollama.yml: Not found (optional)")

    # Check environment files
    env_files = [".env.example", ".env.mcp.example"]
    for env_file in env_files:
        env_path = base_dir / env_file
        if env_path.exists():
            print(f"✅ {env_file}: Found")
        else:
            print(f"⚠️  {env_file}: Not found")

    # Final result
    if has_errors:
        print("\n❌ Validation failed!")
        sys.exit(1)
    else:
        print("\n✅ All MCP configurations are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
