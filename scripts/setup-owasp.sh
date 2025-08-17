#!/bin/bash
# OWASP Dependency-Check Setup Script
# CVE脆弱性スキャン設定

set -e

echo "🔐 OWASP Dependency-Check Setup"
echo "================================"

# Define version
OWASP_VERSION="9.0.8"
INSTALL_DIR="$HOME/.owasp"

# Check if already installed
if [ -d "$INSTALL_DIR/dependency-check" ]; then
    echo "✅ OWASP Dependency-Check is already installed"
    echo "   Location: $INSTALL_DIR/dependency-check"
else
    echo "📦 Installing OWASP Dependency-Check v${OWASP_VERSION}..."

    # Create installation directory
    mkdir -p "$INSTALL_DIR"

    # Download OWASP Dependency-Check
    echo "⬇️  Downloading..."
    curl -L "https://github.com/jeremylong/DependencyCheck/releases/download/v${OWASP_VERSION}/dependency-check-${OWASP_VERSION}-release.zip" \
         -o "/tmp/dependency-check.zip"

    # Extract
    echo "📂 Extracting..."
    unzip -q "/tmp/dependency-check.zip" -d "$INSTALL_DIR"
    rm "/tmp/dependency-check.zip"

    # Make executable
    chmod +x "$INSTALL_DIR/dependency-check/bin/dependency-check.sh"

    echo "✅ OWASP Dependency-Check installed successfully"
fi

# Create project configuration
echo ""
echo "📝 Creating OWASP configuration file..."
cat > owasp-config.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<suppressions xmlns="https://jeremylong.github.io/DependencyCheck/dependency-suppression.1.3.xsd">
    <!-- Suppress false positives here -->
    <!-- Example:
    <suppress>
        <notes>False positive - this is a test library</notes>
        <packageUrl regex="true">^pkg:pypi/pytest@.*$</packageUrl>
        <cpe>cpe:/a:pytest:pytest</cpe>
    </suppress>
    -->
</suppressions>
EOF

# Create scan script
echo ""
echo "📜 Creating scan script..."
cat > scripts/scan-dependencies.sh << 'EOF'
#!/bin/bash
# Dependency vulnerability scanning script

echo "🔍 Scanning dependencies for vulnerabilities..."
echo "=============================================="

INSTALL_DIR="$HOME/.owasp"
SCAN_PATH="${1:-.}"
OUTPUT_DIR="security-reports"
REPORT_FORMAT="${2:-HTML}"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Run dependency check
"$INSTALL_DIR/dependency-check/bin/dependency-check.sh" \
    --scan "$SCAN_PATH" \
    --format "$REPORT_FORMAT" \
    --format JSON \
    --project "claude-code-template-mcp" \
    --out "$OUTPUT_DIR" \
    --suppression owasp-config.xml \
    --enableExperimental \
    --nvdApiKey "${NVD_API_KEY:-}" \
    2>&1 | tee "$OUTPUT_DIR/scan.log"

# Check results
if [ -f "$OUTPUT_DIR/dependency-check-report.json" ]; then
    echo ""
    echo "📊 Scan Results:"
    python3 -c "
import json
import sys

with open('$OUTPUT_DIR/dependency-check-report.json', 'r') as f:
    report = json.load(f)

vulnerabilities = []
for dep in report.get('dependencies', []):
    if dep.get('vulnerabilities'):
        vulnerabilities.extend(dep['vulnerabilities'])

if vulnerabilities:
    print(f'⚠️  Found {len(vulnerabilities)} vulnerabilities:')

    # Group by severity
    severity_counts = {}
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'UNKNOWN')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

    for severity, count in sorted(severity_counts.items()):
        emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(severity, '⚪')
        print(f'  {emoji} {severity}: {count}')
else:
    print('✅ No vulnerabilities found!')
"
    echo ""
    echo "📁 Full reports available in: $OUTPUT_DIR/"
else
    echo "❌ Scan failed. Check $OUTPUT_DIR/scan.log for details."
    exit 1
fi
EOF

chmod +x scripts/scan-dependencies.sh

# Create GitHub Actions workflow for security scanning
echo ""
echo "🔧 Creating GitHub Actions workflow..."
mkdir -p .github/workflows

cat > .github/workflows/security-scan.yml << 'EOF'
name: Security Scan

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run weekly on Sunday at 2 AM
    - cron: '0 2 * * 0'
  workflow_dispatch:

jobs:
  dependency-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run OWASP Dependency-Check
      uses: dependency-check/Dependency-Check_Action@main
      with:
        project: 'claude-code-template-mcp'
        path: '.'
        format: 'HTML,JSON'
        args: >
          --enableRetired
          --enableExperimental
      env:
        JAVA_HOME: /opt/jdk

    - name: Upload results
      uses: actions/upload-artifact@v4
      if: always()
      with:
        name: dependency-check-report
        path: reports/

    - name: Check for vulnerabilities
      run: |
        python -c "
        import json
        import sys

        with open('reports/dependency-check-report.json', 'r') as f:
            report = json.load(f)

        critical = 0
        high = 0

        for dep in report.get('dependencies', []):
            for vuln in dep.get('vulnerabilities', []):
                severity = vuln.get('severity', '')
                if severity == 'CRITICAL':
                    critical += 1
                elif severity == 'HIGH':
                    high += 1

        if critical > 0:
            print(f'❌ Found {critical} CRITICAL vulnerabilities')
            sys.exit(1)
        elif high > 5:
            print(f'⚠️  Found {high} HIGH vulnerabilities (threshold: 5)')
            sys.exit(1)
        else:
            print('✅ Vulnerability check passed')
        "

  pip-audit:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install pip-audit
      run: pip install pip-audit

    - name: Run pip-audit
      run: pip-audit -r requirements.txt --desc

  safety-check:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install safety
      run: pip install safety

    - name: Run safety check
      run: safety check -r requirements.txt --json
EOF

echo ""
echo "✅ OWASP Dependency-Check setup complete!"
echo ""
echo "Usage:"
echo "  Run scan: ./scripts/scan-dependencies.sh"
echo "  Scan specific path: ./scripts/scan-dependencies.sh /path/to/scan"
echo "  Different format: ./scripts/scan-dependencies.sh . XML"
echo ""
echo "Note: For faster scans, get a free NVD API key from:"
echo "  https://nvd.nist.gov/developers/request-an-api-key"
echo "  Then set: export NVD_API_KEY=your-key"
