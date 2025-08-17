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
