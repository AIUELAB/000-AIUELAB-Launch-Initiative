#!/usr/bin/env python3
"""
Check for secrets and sensitive information in the codebase
"""

import re
import sys
from pathlib import Path

# Patterns to detect secrets
SECRET_PATTERNS = [
    # API Keys
    (r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9_\-]{20,}["\']', "API Key"),
    (r'apikey\s*=\s*["\'][a-zA-Z0-9_\-]{20,}["\']', "API Key"),
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key"),
    (r'aws[_-]?secret[_-]?access[_-]?key\s*=\s*["\'][a-zA-Z0-9/+=]{40}["\']', "AWS Secret Key"),
    # GitHub
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"ghu_[a-zA-Z0-9]{36}", "GitHub User Token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub Server Token"),
    (r"ghr_[a-zA-Z0-9]{36}", "GitHub Refresh Token"),
    # Generic Secrets
    (r'["\']sk-[a-zA-Z0-9]{48}["\']', "OpenAI API Key"),
    (r'["\']sk-ant-[a-zA-Z0-9]{40,}["\']', "Anthropic API Key"),
    (r'password\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Password"),
    (r'secret\s*=\s*["\'][^"\']{8,}["\']', "Hardcoded Secret"),
    # Private Keys
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH |)PRIVATE KEY-----", "Private Key"),
    (r"-----BEGIN PGP PRIVATE KEY BLOCK-----", "PGP Private Key"),
    # Tokens
    # Require quoted pattern to avoid matching constant names like BEARER = "bearer"
    (r'["\']Bearer\s+[A-Za-z0-9._\-]+=*["\']', "Bearer Token"),
    (r'["\']xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}["\']', "Slack Bot Token"),
    (r'["\']xoxp-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}["\']', "Slack User Token"),
]

# Files and directories to skip
SKIP_PATTERNS = [
    "venv/",
    ".venv/",
    "node_modules/",
    ".git/",
    "__pycache__/",
    "*.pyc",
    ".env.example",
    ".env.mcp.example",
    "requirements*.txt",
    "*.lock",
    "*.log",
    "docs/",
    "tests/",
    ".claude/",
    "scripts/check_no_secrets.py",
]


def should_skip(file_path: Path) -> bool:
    """Check if file should be skipped."""
    str_path = str(file_path)

    for pattern in SKIP_PATTERNS:
        if pattern.endswith("/"):
            if pattern[:-1] in str_path:
                return True
        elif pattern.startswith("*"):
            if str_path.endswith(pattern[1:]):
                return True
        elif pattern in str_path:
            return True

    return False


def check_file_for_secrets(file_path: Path) -> list[tuple[int, str, str]]:
    """Check a single file for secrets."""
    findings = []

    try:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                # Skip comments and empty lines
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or stripped.startswith("//"):
                    continue

                # Check against patterns
                for pattern, secret_type in SECRET_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's an example or placeholder
                        if any(
                            placeholder in line.lower()
                            for placeholder in [
                                "example",
                                "placeholder",
                                "your_",
                                "xxx",
                                "...",
                                "dummy",
                            ]
                        ):
                            continue

                        findings.append((line_num, secret_type, line.strip()[:100]))

    except Exception as e:
        print(f"Error reading {file_path}: {e}")

    return findings


def _iter_files(base_dir: Path, patterns: list[str]) -> list[Path]:
    """Return files under base_dir matching any of the glob patterns, excluding skip list.

    This helper centralizes the traversal to keep the control flow in main() simple.
    """
    files: list[Path] = []
    for pattern in patterns:
        for file_path in base_dir.rglob(pattern):
            if should_skip(file_path):
                continue
            files.append(file_path)
    return files


def _scan_group(base_dir: Path, patterns: list[str]) -> tuple[list[tuple[Path, list[tuple[int, str, str]]]], int]:
    """Scan a group of patterns and return (findings, files_checked)."""
    findings_list: list[tuple[Path, list[tuple[int, str, str]]]] = []
    files_checked = 0

    for file_path in _iter_files(base_dir, patterns):
        files_checked += 1
        findings = check_file_for_secrets(file_path)
        if findings:
            findings_list.append((file_path, findings))

    return findings_list, files_checked


def main():
    """Main function to check for secrets."""
    print("🔍 Checking for secrets and sensitive information...")

    base_dir = Path(__file__).parent.parent
    all_findings: list[tuple[Path, list[tuple[int, str, str]]]] = []
    files_checked = 0

    scan_groups: list[list[str]] = [
        ["*.py"],
        ["*.js", "*.ts", "*.jsx", "*.tsx"],
        ["*.json", "*.yml", "*.yaml", "*.toml", "*.ini"],
        ["*.sh"],
    ]

    for patterns in scan_groups:
        group_findings, count = _scan_group(base_dir, patterns)
        all_findings.extend(group_findings)
        files_checked += count

    # Report findings
    print(f"✅ Checked {files_checked} files")

    if all_findings:
        print("\n❌ Found potential secrets:")
        for file_path, findings in all_findings:
            rel_path = file_path.relative_to(base_dir)
            print(f"\n📄 {rel_path}:")
            for line_num, secret_type, content in findings:
                print(f"  Line {line_num}: {secret_type}")
                print(f"    {content}")

        print(
            f"\n❌ Found {sum(len(f) for _, f in all_findings)} potential secrets in {len(all_findings)} files!"
        )
        print("\n⚠️  Please review these findings and ensure no real secrets are committed.")
        sys.exit(1)
    else:
        print("✅ No secrets detected!")
        sys.exit(0)


if __name__ == "__main__":
    main()
