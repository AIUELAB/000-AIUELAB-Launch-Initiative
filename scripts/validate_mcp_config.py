#!/usr/bin/env python3
"""
Validate MCP (Model Context Protocol) configuration files.
Ensures all MCP server configurations are valid and properly formatted.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class MCPConfigValidator:
    """Validator for MCP configuration files."""
    
    REQUIRED_FIELDS = {
        'command': str,  # Required for local servers
    }
    
    OPTIONAL_FIELDS = {
        'args': list,
        'env': dict,
        'disabled': bool,
        'description': str,
        'transport': str,  # For remote servers
        'url': str,  # For remote servers
        'headers': dict,  # For remote servers
        'oauth': dict,  # For OAuth-enabled servers
        'tlsVerify': bool,
        'timeout': int,
    }
    
    VALID_TRANSPORTS = ['stdio', 'sse', 'http']
    
    KNOWN_SERVERS = {
        'serena', 'filesystem', 'github', 'fetch', 'context7',
        'brave-search', 'playwright', 'ide', 'firecrawl',
        'memory', 'sequential-thinking', 'puppeteer', 'postgres',
        'slack', 'gitlab', 'google-maps', 'aws', 'gcp', 'azure',
        'docker', 'kubernetes', 'smithery-cli', 'smithery-stdout',
        'linear-remote', 'notion-remote', 'sentry-remote',
        'apidog-remote', 'simplescraper-remote'
    }
    
    def __init__(self, config_dir: Path):
        """Initialize validator with config directory."""
        self.config_dir = config_dir
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate a single MCP config file."""
        if not file_path.exists():
            self.errors.append(f"Config file not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'r') as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in {file_path}: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")
            return False
        
        # Check for mcpServers key
        if 'mcpServers' not in config:
            self.errors.append(f"Missing 'mcpServers' key in {file_path}")
            return False
        
        servers = config['mcpServers']
        if not isinstance(servers, dict):
            self.errors.append(f"'mcpServers' must be a dictionary in {file_path}")
            return False
        
        # Validate each server
        for server_name, server_config in servers.items():
            # Skip comment entries
            if server_name.startswith('//'):
                continue
            
            self._validate_server(server_name, server_config, file_path)
        
        return len(self.errors) == 0
    
    def _validate_server(self, name: str, config: Dict[str, Any], file_path: Path) -> None:
        """Validate individual server configuration."""
        # Check if it's a remote server
        is_remote = 'transport' in config
        
        if is_remote:
            self._validate_remote_server(name, config, file_path)
        else:
            self._validate_local_server(name, config, file_path)
        
        # Warn about unknown servers
        base_name = name.replace('-remote', '').replace('-hybrid', '')
        if base_name not in self.KNOWN_SERVERS and not name.startswith('custom'):
            self.warnings.append(f"Unknown server '{name}' in {file_path.name}")
    
    def _validate_local_server(self, name: str, config: Dict[str, Any], file_path: Path) -> None:
        """Validate local server configuration."""
        # Check for hybrid configuration
        if 'primary' in config and 'fallback' in config:
            # Hybrid server
            self._validate_local_server(f"{name}-primary", config.get('primary', {}), file_path)
            if 'transport' in config.get('fallback', {}):
                self._validate_remote_server(f"{name}-fallback", config.get('fallback', {}), file_path)
            return
        
        # Check required fields
        if 'command' not in config:
            self.errors.append(f"Server '{name}' missing required 'command' field in {file_path.name}")
            return
        
        # Validate command
        command = config['command']
        if not isinstance(command, str):
            self.errors.append(f"Server '{name}' has invalid 'command' type in {file_path.name}")
        
        # Validate args
        if 'args' in config:
            if not isinstance(config['args'], list):
                self.errors.append(f"Server '{name}' has invalid 'args' type in {file_path.name}")
            else:
                for arg in config['args']:
                    if not isinstance(arg, str):
                        self.errors.append(f"Server '{name}' has non-string arg in {file_path.name}")
        
        # Validate env
        if 'env' in config:
            if not isinstance(config['env'], dict):
                self.errors.append(f"Server '{name}' has invalid 'env' type in {file_path.name}")
            else:
                for key, value in config['env'].items():
                    if not isinstance(key, str) or not isinstance(value, str):
                        self.errors.append(f"Server '{name}' has invalid env var in {file_path.name}")
    
    def _validate_remote_server(self, name: str, config: Dict[str, Any], file_path: Path) -> None:
        """Validate remote server configuration."""
        # Check transport
        transport = config.get('transport')
        if not transport:
            self.errors.append(f"Remote server '{name}' missing 'transport' in {file_path.name}")
            return
        
        if transport not in self.VALID_TRANSPORTS:
            self.errors.append(f"Server '{name}' has invalid transport '{transport}' in {file_path.name}")
        
        # Check URL
        if 'url' not in config:
            self.errors.append(f"Remote server '{name}' missing 'url' in {file_path.name}")
        elif not isinstance(config['url'], str):
            self.errors.append(f"Server '{name}' has invalid 'url' type in {file_path.name}")
        
        # Validate headers
        if 'headers' in config:
            if not isinstance(config['headers'], dict):
                self.errors.append(f"Server '{name}' has invalid 'headers' type in {file_path.name}")
        
        # Validate OAuth config
        if 'oauth' in config:
            oauth = config['oauth']
            if not isinstance(oauth, dict):
                self.errors.append(f"Server '{name}' has invalid 'oauth' type in {file_path.name}")
            else:
                # Check OAuth fields
                oauth_fields = ['clientId', 'clientSecret', 'scope', 'authorizationUrl', 'tokenEndpoint']
                for field in ['clientId']:  # Only clientId is truly required
                    if field not in oauth:
                        self.warnings.append(f"Server '{name}' OAuth missing '{field}' in {file_path.name}")
    
    def validate_env_file(self, env_file: Path) -> bool:
        """Validate environment file has required variables."""
        if not env_file.exists():
            self.warnings.append(f"Environment file not found: {env_file}")
            return True  # Not an error, just a warning
        
        required_vars = {
            'GITHUB_TOKEN': 'GitHub integration',
            'BRAVE_API_KEY': 'Web search',
        }
        
        try:
            with open(env_file, 'r') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Error reading {env_file}: {e}")
            return False
        
        for var, purpose in required_vars.items():
            if var not in content:
                self.warnings.append(f"Missing {var} in {env_file.name} (needed for {purpose})")
        
        return True
    
    def validate_all(self) -> bool:
        """Validate all MCP configuration files."""
        valid = True
        
        # Main config file
        main_config = self.config_dir / 'claude_desktop_config.json'
        if main_config.exists():
            print(f"✓ Validating {main_config.name}...")
            valid = self.validate_file(main_config) and valid
        
        # Remote config file
        remote_config = self.config_dir / 'claude_desktop_config_remote.json'
        if remote_config.exists():
            print(f"✓ Validating {remote_config.name}...")
            valid = self.validate_file(remote_config) and valid
        
        # Profile files
        profiles_dir = self.config_dir / 'profiles'
        if profiles_dir.exists():
            for profile_file in profiles_dir.glob('*.json'):
                print(f"✓ Validating profile: {profile_file.name}...")
                valid = self.validate_file(profile_file) and valid
        
        # Remote servers config
        remote_servers = self.config_dir / 'remote-servers.json'
        if remote_servers.exists():
            print(f"✓ Validating {remote_servers.name}...")
            # This file has different structure, skip detailed validation
            try:
                with open(remote_servers, 'r') as f:
                    json.load(f)
            except Exception as e:
                self.errors.append(f"Invalid JSON in {remote_servers.name}: {e}")
                valid = False
        
        # Check environment files
        env_file = self.config_dir.parent / '.env.mcp'
        env_example = self.config_dir.parent / '.env.mcp.example'
        
        if env_example.exists():
            print(f"✓ Checking environment template...")
            self.validate_env_file(env_example)
        
        if env_file.exists():
            print(f"✓ Checking environment variables...")
            self.validate_env_file(env_file)
        
        return valid
    
    def print_report(self) -> None:
        """Print validation report."""
        print("\n" + "="*60)
        print("MCP Configuration Validation Report")
        print("="*60)
        
        if not self.errors and not self.warnings:
            print("✅ All MCP configurations are valid!")
        else:
            if self.errors:
                print(f"\n❌ Errors ({len(self.errors)}):")
                for error in self.errors:
                    print(f"  • {error}")
            
            if self.warnings:
                print(f"\n⚠️  Warnings ({len(self.warnings)}):")
                for warning in self.warnings:
                    print(f"  • {warning}")
        
        print("="*60)


def main():
    """Main function."""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_dir = project_root / 'mcp-config'
    
    print("🔍 Validating MCP configuration files...")
    print(f"📁 Config directory: {config_dir}")
    
    # Create validator
    validator = MCPConfigValidator(config_dir)
    
    # Validate all configs
    is_valid = validator.validate_all()
    
    # Print report
    validator.print_report()
    
    # Exit with appropriate code
    if not is_valid or validator.errors:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()