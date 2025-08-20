#!/usr/bin/env python3
"""
Security audit script for the application
"""

import json
import subprocess
import sys
from pathlib import Path


class SecurityAuditor:
    """Security audit utilities."""

    def __init__(self):
        self.issues = []
        self.base_dir = Path(__file__).parent.parent

    def add_issue(self, severity: str, category: str, message: str, file: str = None):
        """Add a security issue."""
        self.issues.append(
            {"severity": severity, "category": category, "message": message, "file": file}
        )

    def check_dependencies(self):
        """Check for known vulnerabilities in dependencies."""
        print("🔍 Checking dependencies for vulnerabilities...")

        try:
            # Run pip-audit
            result = subprocess.run(
                ["pip-audit", "--format", "json"],
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                check=False,
            )

            if result.returncode == 0:
                audit_data = json.loads(result.stdout)
                if audit_data:
                    for vuln in audit_data:
                        self.add_issue(
                            "HIGH",
                            "Dependency",
                            f"{vuln['name']} {vuln['version']} has known vulnerability: {vuln.get('description', 'N/A')}",
                        )
                else:
                    print("   ✅ No vulnerabilities found in dependencies")
            else:
                print(f"   ⚠️ pip-audit failed: {result.stderr}")
        except FileNotFoundError:
            print("   ⚠️ pip-audit not installed")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    def check_permissions(self):
        """Check file permissions."""
        print("🔍 Checking file permissions...")

        sensitive_files = [".env", ".env.mcp", "*.key", "*.pem", "credentials.json"]

        for pattern in sensitive_files:
            for file_path in self.base_dir.rglob(pattern):
                if file_path.is_file():
                    stat = file_path.stat()
                    mode = oct(stat.st_mode)[-3:]

                    if mode != "600":
                        self.add_issue(
                            "MEDIUM",
                            "Permissions",
                            f"Sensitive file {file_path.name} has permissions {mode} (should be 600)",
                            str(file_path),
                        )

        print("   ✅ File permissions checked")

    def check_hardcoded_secrets(self):
        """Check for hardcoded secrets."""
        print("🔍 Checking for hardcoded secrets...")

        # Run the check_no_secrets script
        try:
            result = subprocess.run(
                [sys.executable, "scripts/check_no_secrets.py"],
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                check=False,
            )

            if result.returncode != 0:
                self.add_issue("CRITICAL", "Secrets", "Potential secrets found in codebase")
                print("   ⚠️ Potential secrets detected")
            else:
                print("   ✅ No secrets detected")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    def check_imports(self):
        """Check for dangerous imports."""
        print("🔍 Checking for dangerous imports...")

        dangerous_imports = ["pickle", "marshal", "eval", "exec", "__import__", "compile"]

        python_files = list(self.base_dir.rglob("*.py"))

        for file_path in python_files:
            if "venv" in str(file_path) or ".venv" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                for dangerous in dangerous_imports:
                    if dangerous in content:
                        # Check if it's actually being used
                        if (
                            f"import {dangerous}" in content
                            or f"from {dangerous}" in content
                            or f"{dangerous}(" in content
                        ):
                            self.add_issue(
                                "MEDIUM",
                                "Imports",
                                f"Potentially dangerous import/function '{dangerous}' used",
                                str(file_path),
                            )
            except Exception:
                pass

        if not any(i["category"] == "Imports" for i in self.issues):
            print("   ✅ No dangerous imports found")

    def check_ssl_verification(self):
        """Check for disabled SSL verification."""
        print("🔍 Checking SSL verification...")

        patterns = ["verify=False", "ssl_verify=False", "VERIFY_SSL=False", "check_hostname=False"]

        for file_path in self.base_dir.rglob("*.py"):
            if "venv" in str(file_path) or ".venv" in str(file_path):
                continue

            try:
                content = file_path.read_text()
                for pattern in patterns:
                    if pattern in content:
                        self.add_issue(
                            "HIGH",
                            "SSL",
                            f"SSL verification might be disabled: {pattern}",
                            str(file_path),
                        )
            except Exception:
                pass

        if not any(i["category"] == "SSL" for i in self.issues):
            print("   ✅ SSL verification properly configured")

    def check_environment_variables(self):
        """Check environment variable usage."""
        print("🔍 Checking environment variables...")

        env_files = [".env", ".env.mcp"]

        for env_file in env_files:
            env_path = self.base_dir / env_file
            if env_path.exists():
                self.add_issue(
                    "HIGH",
                    "Environment",
                    f"Environment file {env_file} exists in repository (should be in .gitignore)",
                    str(env_path),
                )

        # Check .gitignore
        gitignore_path = self.base_dir / ".gitignore"
        if gitignore_path.exists():
            gitignore_content = gitignore_path.read_text()
            for env_file in env_files:
                if env_file not in gitignore_content:
                    self.add_issue("HIGH", "Environment", f"{env_file} not in .gitignore")

        print("   ✅ Environment variables checked")

    def run_bandit(self):
        """Run bandit security scanner."""
        print("🔍 Running Bandit security scanner...")

        try:
            result = subprocess.run(
                ["bandit", "-r", "src", "-f", "json", "-ll"],
                capture_output=True,
                text=True,
                cwd=self.base_dir,
                check=False,
            )

            if result.stdout:
                bandit_results = json.loads(result.stdout)
                for issue in bandit_results.get("results", []):
                    self.add_issue(
                        issue["issue_severity"].upper(),
                        "Bandit",
                        f"{issue['issue_text']} (CWE-{issue.get('issue_cwe', {}).get('id', 'N/A')})",
                        issue["filename"],
                    )

            print("   ✅ Bandit scan completed")
        except FileNotFoundError:
            print("   ⚠️ Bandit not installed")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    def generate_report(self):
        """Generate security audit report."""
        print("\n" + "=" * 50)
        print("🔒 Security Audit Report")
        print("=" * 50)

        if not self.issues:
            print("\n✅ No security issues found! Great job! 🎉")
            return 0

        # Group by severity
        critical = [i for i in self.issues if i["severity"] == "CRITICAL"]
        high = [i for i in self.issues if i["severity"] == "HIGH"]
        medium = [i for i in self.issues if i["severity"] == "MEDIUM"]
        low = [i for i in self.issues if i["severity"] == "LOW"]

        # Print issues
        if critical:
            print(f"\n🔴 CRITICAL ({len(critical)} issues):")
            for issue in critical:
                print(f"   • [{issue['category']}] {issue['message']}")
                if issue["file"]:
                    print(f"     File: {issue['file']}")

        if high:
            print(f"\n🟠 HIGH ({len(high)} issues):")
            for issue in high:
                print(f"   • [{issue['category']}] {issue['message']}")
                if issue["file"]:
                    print(f"     File: {issue['file']}")

        if medium:
            print(f"\n🟡 MEDIUM ({len(medium)} issues):")
            for issue in medium:
                print(f"   • [{issue['category']}] {issue['message']}")
                if issue["file"]:
                    print(f"     File: {issue['file']}")

        if low:
            print(f"\n🟢 LOW ({len(low)} issues):")
            for issue in low:
                print(f"   • [{issue['category']}] {issue['message']}")
                if issue["file"]:
                    print(f"     File: {issue['file']}")

        # Summary
        total = len(self.issues)
        print(f"\n📊 Summary: {total} issues found")
        print(f"   Critical: {len(critical)}")
        print(f"   High: {len(high)}")
        print(f"   Medium: {len(medium)}")
        print(f"   Low: {len(low)}")

        # Security score
        score = 100
        score -= len(critical) * 25
        score -= len(high) * 15
        score -= len(medium) * 5
        score -= len(low) * 2
        score = max(0, score)

        if score >= 90:
            grade = "A 🏆"
        elif score >= 80:
            grade = "B 🎯"
        elif score >= 70:
            grade = "C ✅"
        elif score >= 60:
            grade = "D ⚠️"
        else:
            grade = "F ❌"

        print(f"\n🎓 Security Score: {score}/100 (Grade: {grade})")

        # Recommendations
        print("\n💡 Recommendations:")
        if critical or high:
            print("   🚨 Fix critical and high severity issues immediately")
        if any(i["category"] == "Dependency" for i in self.issues):
            print("   📦 Update vulnerable dependencies")
        if any(i["category"] == "Secrets" for i in self.issues):
            print("   🔑 Remove all hardcoded secrets and use environment variables")
        if any(i["category"] == "Permissions" for i in self.issues):
            print("   🔒 Fix file permissions for sensitive files")

        return 1 if critical or high else 0


def main():
    """Run security audit."""
    print("🔒 Security Audit Suite")
    print("=" * 50)

    auditor = SecurityAuditor()

    # Run all checks
    auditor.check_dependencies()
    auditor.check_permissions()
    auditor.check_hardcoded_secrets()
    auditor.check_imports()
    auditor.check_ssl_verification()
    auditor.check_environment_variables()
    auditor.run_bandit()

    # Generate report
    return auditor.generate_report()


if __name__ == "__main__":
    sys.exit(main())
