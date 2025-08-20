#!/bin/bash
# Advanced Type Checking with Pyright and Basedpyright
# 2025年最新の型チェックツール

set -e

echo "🔍 Advanced Type Checking"
echo "========================="

# Parse arguments
CHECK_TYPE="${1:-both}"
TARGET_PATH="${2:-src}"

# Colors for output
RED='\033[0;31m'
# shellcheck disable=SC2034
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to run Pyright
run_pyright() {
    echo -e "${BLUE}📘 Running Pyright...${NC}"
    echo "------------------------"

    if command -v pyright &> /dev/null; then
        pyright "$TARGET_PATH" --outputjson 2>/dev/null | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)

    error_count = data['summary']['errorCount']
    warning_count = data['summary']['warningCount']
    info_count = data['summary']['informationCount']

    if error_count > 0:
        print(f'❌ Errors: {error_count}')
    if warning_count > 0:
        print(f'⚠️  Warnings: {warning_count}')
    if info_count > 0:
        print(f'ℹ️  Information: {info_count}')

    if error_count == 0 and warning_count == 0:
        print('✅ No type errors found!')

    # Print first 5 errors
    if 'diagnostics' in data and data['diagnostics']:
        print('\\nFirst issues:')
        for i, diag in enumerate(data['diagnostics'][:5]):
            file = diag['file']
            line = diag['range']['start']['line'] + 1
            message = diag['message']
            severity = diag['severity']
            print(f'  {severity}: {file}:{line} - {message}')

except Exception as e:
    print(f'Error parsing results: {e}')
    sys.exit(1)
" || {
        echo -e "${YELLOW}⚠️  Pyright check completed with issues${NC}"
    }
    else
        echo -e "${RED}❌ Pyright not installed${NC}"
        echo "Install with: pip install pyright"
    fi
}

# Function to run Basedpyright
run_basedpyright() {
    echo -e "${BLUE}📙 Running Basedpyright...${NC}"
    echo "------------------------"

    if command -v basedpyright &> /dev/null; then
        basedpyright "$TARGET_PATH" --outputjson 2>/dev/null | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)

    error_count = data['summary']['errorCount']
    warning_count = data['summary']['warningCount']
    info_count = data['summary']['informationCount']

    if error_count > 0:
        print(f'❌ Errors: {error_count}')
    if warning_count > 0:
        print(f'⚠️  Warnings: {warning_count}')
    if info_count > 0:
        print(f'ℹ️  Information: {info_count}')

    if error_count == 0 and warning_count == 0:
        print('✅ No type errors found!')

    # Print first 5 errors
    if 'diagnostics' in data and data['diagnostics']:
        print('\\nFirst issues:')
        for i, diag in enumerate(data['diagnostics'][:5]):
            file = diag['file']
            line = diag['range']['start']['line'] + 1
            message = diag['message']
            severity = diag['severity']
            print(f'  {severity}: {file}:{line} - {message}')

except Exception as e:
    print(f'Error parsing results: {e}')
    sys.exit(1)
" || {
        echo -e "${YELLOW}⚠️  Basedpyright check completed with issues${NC}"
    }
    else
        echo -e "${RED}❌ Basedpyright not installed${NC}"
        echo "Install with: pip install basedpyright"
    fi
}

# Function to run mypy for comparison
run_mypy() {
    echo -e "${BLUE}📗 Running mypy (for comparison)...${NC}"
    echo "------------------------"

    if command -v mypy &> /dev/null; then
        mypy "$TARGET_PATH" --no-error-summary 2>&1 | head -10 || true
        echo "..."
    else
        echo -e "${YELLOW}⚠️  mypy not installed${NC}"
    fi
}

# Function to run all type checkers
run_all() {
    run_pyright
    echo ""
    run_basedpyright
    echo ""
    run_mypy
}

# Function to compare results
compare_results() {
    echo -e "${BLUE}📊 Comparing Type Checkers${NC}"
    echo "=========================="

    # Create temp files for results
    PYRIGHT_OUT=$(mktemp)
    BASED_OUT=$(mktemp)
    MYPY_OUT=$(mktemp)

    # Run each checker and save output
    pyright "$TARGET_PATH" --outputjson 2>/dev/null > "$PYRIGHT_OUT" || true
    basedpyright "$TARGET_PATH" --outputjson 2>/dev/null > "$BASED_OUT" || true
    mypy "$TARGET_PATH" --json 2>/dev/null > "$MYPY_OUT" || true

    # Compare results
    python3 -c "
import json
import sys

def load_json_safe(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except:
        return None

pyright_data = load_json_safe('$PYRIGHT_OUT')
based_data = load_json_safe('$BASED_OUT')

print('📈 Comparison Results:')
print('-' * 40)

if pyright_data and 'summary' in pyright_data:
    print(f'Pyright:')
    print(f'  Errors: {pyright_data[\"summary\"][\"errorCount\"]}')
    print(f'  Warnings: {pyright_data[\"summary\"][\"warningCount\"]}')

if based_data and 'summary' in based_data:
    print(f'Basedpyright:')
    print(f'  Errors: {based_data[\"summary\"][\"errorCount\"]}')
    print(f'  Warnings: {based_data[\"summary\"][\"warningCount\"]}')

# Find unique errors
if pyright_data and based_data:
    pyright_msgs = set()
    based_msgs = set()

    for diag in pyright_data.get('diagnostics', []):
        pyright_msgs.add(diag['message'])

    for diag in based_data.get('diagnostics', []):
        based_msgs.add(diag['message'])

    unique_pyright = pyright_msgs - based_msgs
    unique_based = based_msgs - pyright_msgs

    if unique_pyright:
        print(f'\\n📘 Unique to Pyright: {len(unique_pyright)}')
        for msg in list(unique_pyright)[:3]:
            print(f'  - {msg[:80]}...')

    if unique_based:
        print(f'\\n📙 Unique to Basedpyright: {len(unique_based)}')
        for msg in list(unique_based)[:3]:
            print(f'  - {msg[:80]}...')
"

    # Cleanup
    rm -f "$PYRIGHT_OUT" "$BASED_OUT" "$MYPY_OUT"
}

# Main execution
case "$CHECK_TYPE" in
    pyright)
        run_pyright
        ;;
    basedpyright|based)
        run_basedpyright
        ;;
    mypy)
        run_mypy
        ;;
    compare)
        compare_results
        ;;
    both|all)
        run_all
        ;;
    *)
        echo "Usage: $0 [pyright|basedpyright|mypy|compare|both] [target_path]"
        echo "  pyright      - Run Pyright only"
        echo "  basedpyright - Run Basedpyright only"
        echo "  mypy         - Run mypy only"
        echo "  compare      - Compare all type checkers"
        echo "  both/all     - Run all type checkers"
        exit 1
        ;;
esac

echo ""
echo "✨ Type checking complete!"
