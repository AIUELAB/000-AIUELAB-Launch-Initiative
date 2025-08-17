#!/usr/bin/env python3
"""
Security check script to detect secrets in codebase.
Prevents accidental commits of sensitive information.
"""

import os
import re
import sys
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any

# Patterns for detecting secrets
SECRET_PATTERNS = [
    # API Keys
    (r'["\']?api[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}["\']', 'API Key'),
    (r'["\']?apikey["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-]{20,}["\']', 'API Key'),
    
    # AWS
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key'),
    (r'["\']?aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\'][a-zA-Z0-9/+=]{40}["\']', 'AWS Secret Key'),
    
    # GitHub
    (r'ghp_[a-zA-Z0-9]{36}', 'GitHub Personal Access Token'),
    (r'gho_[a-zA-Z0-9]{36}', 'GitHub OAuth Token'),
    (r'ghu_[a-zA-Z0-9]{36}', 'GitHub User Token'),
    (r'ghs_[a-zA-Z0-9]{36}', 'GitHub Server Token'),
    (r'ghr_[a-zA-Z0-9]{36}', 'GitHub Refresh Token'),
    
    # Private Keys
    (r'-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----', 'Private Key'),
    (r'-----BEGIN PRIVATE KEY-----', 'Private Key'),
    
    # Generic Secrets
    (r'["\']?password["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', 'Password'),
    (r'["\']?secret["\']?\s*[:=]\s*["\'][^"\']{8,}["\']', 'Secret'),
    (r'["\']?token["\']?\s*[:=]\s*["\'][a-zA-Z0-9_\-\.]{20,}["\']', 'Token'),
    
    # Database URLs with credentials
    (r'(mysql|postgresql|mongodb)://[^:]+:[^@]+@[^/]+', 'Database URL with credentials'),
    
    # JWT
    (r'eyJ[a-zA-Z0-9_\-]+\.eyJ[a-zA-Z0-9_\-]+\.[a-zA-Z0-9_\-]+', 'JWT Token'),
    
    # Slack
    (r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,34}', 'Slack Token'),
    
    # Google
    (r'AIza[0-9A-Za-z_\-]{35}', 'Google API Key'),
    
    # Stripe
    (r'sk_live_[0-9a-zA-Z]{24,}', 'Stripe Secret Key'),
    (r'rk_live_[0-9a-zA-Z]{24,}', 'Stripe Restricted Key'),
]

# Files/directories to skip
SKIP_PATHS = {
    '.git',
    '.env.example',
    '.env.mcp.example',
    'node_modules',
    'venv',
    '__pycache__',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    'dist',
    'build',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.DS_Store',
    'Thumbs.db',
}

# Files that are allowed to contain example secrets
ALLOWED_FILES = {
    '.env.example',
    '.env.mcp.example',
    'test_*.py',
    '*_test.py',
    'check_no_secrets.py',  # This file itself
    'example*.py',
    'sample*.py',
}


def should_skip_file(file_path: Path) -> bool:
    """Check if file should be skipped."""
    # Skip if in skip paths
    for skip in SKIP_PATHS:
        if skip in str(file_path):
            return True
    
    # Skip if in allowed files
    for allowed in ALLOWED_FILES:
        if allowed in file_path.name or file_path.match(allowed):
            return True
    
    # Skip binary files
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1)
    except (UnicodeDecodeError, PermissionError):
        return True
    
    return False


def scan_file(file_path: Path) -> List[Tuple[int, str, str]]:
    """Scan a file for secrets."""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.splitlines()
    except Exception:
        return findings
    
    # Check each pattern
    for pattern, secret_type in SECRET_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE):
            # Find line number
            line_num = content[:match.start()].count('\n') + 1
            line_content = lines[line_num - 1].strip()
            
            # Skip if it's a variable reference like ${API_KEY}
            if '${' in match.group(0) or 'process.env' in line_content:
                continue
            
            # Skip if it's clearly a placeholder
            if any(placeholder in match.group(0).lower() for placeholder in 
                   ['your_', 'example', 'placeholder', 'xxx', '...', '<', '>']):
                continue
            
            findings.append((line_num, secret_type, line_content[:100]))
    
    return findings


def scan_directory(root_dir: Path) -> Dict[str, List[Tuple[int, str, str]]]:
    """Scan directory for secrets."""
    all_findings = {}
    
    for file_path in root_dir.rglob('*'):
        if file_path.is_file() and not should_skip_file(file_path):
            findings = scan_file(file_path)
            if findings:
                relative_path = file_path.relative_to(root_dir)
                all_findings[str(relative_path)] = findings
    
    return all_findings


def generate_report(findings: Dict[str, List[Tuple[int, str, str]]]) -> str:
    """Generate security report."""
    if not findings:
        return "✅ No secrets detected in the codebase."
    
    report = ["🚨 SECURITY WARNING: Potential secrets detected!\n"]
    total_issues = sum(len(f) for f in findings.values())
    
    report.append(f"Found {total_issues} potential secret(s) in {len(findings)} file(s):\n")
    
    for file_path, file_findings in findings.items():
        report.append(f"\n📄 {file_path}:")
        for line_num, secret_type, line_content in file_findings:
            report.append(f"  Line {line_num}: [{secret_type}] {line_content}")
    
    report.append("\n⚠️  Please remove these secrets before committing!")
    report.append("💡 Use environment variables or a secrets manager instead.")
    
    return "\n".join(report)


def main():
    """Main function."""
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    print("🔍 Scanning for secrets in codebase...")
    print(f"📁 Project root: {project_root}")
    
    # Scan for secrets
    findings = scan_directory(project_root)
    
    # Generate report
    report = generate_report(findings)
    print("\n" + report)
    
    # Exit with error if secrets found
    if findings:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()