#!/bin/bash
# Semgrep SAST Scanner
# Advanced Static Application Security Testing

set -e

echo "🔍 Semgrep Security Analysis"
echo "============================"

# Parse arguments
SCAN_TYPE="${1:-full}"
TARGET="${2:-.}"
OUTPUT_FORMAT="${3:-text}"

# Colors for output
# shellcheck disable=SC2034
RED='\033[0;31m'
# shellcheck disable=SC2034
GREEN='\033[0;32m'
# shellcheck disable=SC2034
YELLOW='\033[1;33m'
# shellcheck disable=SC2034
BLUE='\033[0;34m'
# shellcheck disable=SC2034
NC='\033[0m' # No Color

# Function to run basic security scan
run_security_scan() {
    echo -e "${BLUE}🛡️  Running Security Scan...${NC}"
    echo "------------------------"

    semgrep \
        --config=auto \
        --config=.semgrep.yml \
        --severity=ERROR \
        --severity=WARNING \
        --json \
        "$TARGET" 2>/dev/null | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)

    if 'errors' in data and data['errors']:
        print('❌ Scan errors:')
        for error in data['errors'][:3]:
            print(f'  - {error.get(\"message\", \"Unknown error\")}')

    results = data.get('results', [])

    if not results:
        print('✅ No security issues found!')
    else:
        # Group by severity
        severity_counts = {}
        for result in results:
            severity = result['extra'].get('severity', 'INFO')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        print(f'⚠️  Found {len(results)} issues:')
        for severity in ['ERROR', 'WARNING', 'INFO']:
            if severity in severity_counts:
                emoji = {'ERROR': '🔴', 'WARNING': '🟠', 'INFO': '🔵'}.get(severity, '⚪')
                print(f'  {emoji} {severity}: {severity_counts[severity]}')

        # Show first few issues
        print('\\nTop issues:')
        for result in results[:5]:
            file = result['path']
            line = result['start']['line']
            message = result['extra']['message']
            rule = result['check_id']
            print(f'  • {file}:{line} - {message} [{rule}]')

except Exception as e:
    print(f'Error parsing results: {e}')
    sys.exit(1)
"
}

# Function to run OWASP security scan
run_owasp_scan() {
    echo -e "${BLUE}🔐 Running OWASP Top 10 Scan...${NC}"
    echo "------------------------"

    semgrep \
        --config=https://semgrep.dev/p/owasp-top-ten \
        --json \
        "$TARGET" 2>/dev/null | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    results = data.get('results', [])

    if not results:
        print('✅ No OWASP Top 10 issues found!')
    else:
        print(f'⚠️  Found {len(results)} OWASP issues')

        # Group by OWASP category
        categories = {}
        for result in results:
            metadata = result['extra'].get('metadata', {})
            category = metadata.get('owasp', 'Unknown')
            categories[category] = categories.get(category, 0) + 1

        for cat, count in sorted(categories.items()):
            print(f'  • {cat}: {count}')

except Exception as e:
    print(f'Error: {e}')
"
}

# Function to run supply chain scan
run_supply_chain_scan() {
    echo -e "${BLUE}📦 Running Supply Chain Scan...${NC}"
    echo "------------------------"

    semgrep \
        --config=https://semgrep.dev/p/supply-chain \
        --json \
        "$TARGET" 2>/dev/null | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    results = data.get('results', [])

    if not results:
        print('✅ No supply chain issues found!')
    else:
        print(f'⚠️  Found {len(results)} supply chain risks')
        for result in results[:5]:
            print(f'  • {result[\"path\"]}:{result[\"start\"][\"line\"]} - {result[\"extra\"][\"message\"]}')

except Exception as e:
    print(f'Error: {e}')
"
}

# Function to run custom rules scan
run_custom_scan() {
    echo -e "${BLUE}🎯 Running Custom Rules Scan...${NC}"
    echo "------------------------"

    if [ -f ".semgrep.yml" ]; then
        semgrep \
            --config=.semgrep.yml \
            --json \
            "$TARGET" 2>/dev/null | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    results = data.get('results', [])

    if not results:
        print('✅ No custom rule violations found!')
    else:
        print(f'⚠️  Found {len(results)} custom rule violations')

        # Group by rule
        rules = {}
        for result in results:
            rule_id = result['check_id']
            rules[rule_id] = rules.get(rule_id, 0) + 1

        for rule, count in sorted(rules.items(), key=lambda x: x[1], reverse=True):
            print(f'  • {rule}: {count}')

except Exception as e:
    print(f'Error: {e}')
"
    else
        echo "⚠️  No .semgrep.yml found"
    fi
}

# Function to generate report
generate_report() {
    echo -e "${BLUE}📊 Generating Report...${NC}"
    echo "------------------------"

    REPORT_DIR="security-reports"
    mkdir -p "$REPORT_DIR"

    # Generate different format reports
    case "$OUTPUT_FORMAT" in
        json)
            semgrep --config=auto --json "$TARGET" > "$REPORT_DIR/semgrep-report.json"
            echo "📁 JSON report: $REPORT_DIR/semgrep-report.json"
            ;;
        sarif)
            semgrep --config=auto --sarif "$TARGET" > "$REPORT_DIR/semgrep-report.sarif"
            echo "📁 SARIF report: $REPORT_DIR/semgrep-report.sarif"
            ;;
        gitlab)
            semgrep --config=auto --gitlab-sast "$TARGET" > "$REPORT_DIR/semgrep-gitlab.json"
            echo "📁 GitLab SAST report: $REPORT_DIR/semgrep-gitlab.json"
            ;;
        text|*)
            semgrep --config=auto "$TARGET" > "$REPORT_DIR/semgrep-report.txt"
            echo "📁 Text report: $REPORT_DIR/semgrep-report.txt"
            ;;
    esac
}

# Function to run full scan
run_full_scan() {
    run_security_scan
    echo ""
    run_owasp_scan
    echo ""
    run_supply_chain_scan
    echo ""
    run_custom_scan
    echo ""
    generate_report
}

# Function to run quick scan
run_quick_scan() {
    echo -e "${BLUE}⚡ Running Quick Scan...${NC}"
    echo "------------------------"

    semgrep \
        --config=auto \
        --severity=ERROR \
        --max-target-bytes=1000000 \
        "$TARGET"
}

# Function to run CI scan
run_ci_scan() {
    echo -e "${BLUE}🚀 Running CI Scan...${NC}"
    echo "------------------------"

    # Exit with error code if issues found
    semgrep \
        --config=auto \
        --config=.semgrep.yml \
        --severity=ERROR \
        --error \
        "$TARGET"

    if [ $? -eq 0 ]; then
        echo "✅ CI scan passed!"
        exit 0
    else
        echo "❌ CI scan failed!"
        exit 1
    fi
}

# Main execution
case "$SCAN_TYPE" in
    security)
        run_security_scan
        ;;
    owasp)
        run_owasp_scan
        ;;
    supply-chain)
        run_supply_chain_scan
        ;;
    custom)
        run_custom_scan
        ;;
    quick)
        run_quick_scan
        ;;
    ci)
        run_ci_scan
        ;;
    full)
        run_full_scan
        ;;
    *)
        echo "Usage: $0 [scan_type] [target] [output_format]"
        echo ""
        echo "Scan types:"
        echo "  security     - Security vulnerabilities"
        echo "  owasp        - OWASP Top 10"
        echo "  supply-chain - Supply chain risks"
        echo "  custom       - Custom rules from .semgrep.yml"
        echo "  quick        - Quick scan (errors only)"
        echo "  ci           - CI/CD scan (fails on errors)"
        echo "  full         - All scans (default)"
        echo ""
        echo "Output formats: text, json, sarif, gitlab"
        exit 1
        ;;
esac

echo ""
echo "✨ Semgrep scan complete!"
