#!/bin/bash

# Check terminal configuration for optimal display

# Get terminal dimensions
COLS=$(tput cols 2>/dev/null || echo 80)
ROWS=$(tput lines 2>/dev/null || echo 24)

# Check encoding
CURRENT_LANG=$LANG
# CURRENT_LC_ALL is intentionally read-only for display; suppress shellcheck unused warning
# shellcheck disable=SC2034
CURRENT_LC_ALL=$LC_ALL

echo "Terminal Configuration Check"
echo "============================"
echo ""

# Check width
if [ $COLS -lt 100 ]; then
    echo "[WARNING] Terminal width: $COLS chars"
    echo "          Recommended: 120+ chars"
    echo "          Some output may wrap incorrectly"
else
    echo "[OK] Terminal width: $COLS chars"
fi

# Check height
if [ $ROWS -lt 30 ]; then
    echo "[WARNING] Terminal height: $ROWS lines"
    echo "          Recommended: 30+ lines"
else
    echo "[OK] Terminal height: $ROWS lines"
fi

# Check encoding
if [[ "$CURRENT_LANG" == *"UTF-8"* ]] || [[ "$CURRENT_LANG" == *"utf8"* ]]; then
    echo "[OK] Character encoding: $CURRENT_LANG"
else
    echo "[WARNING] Character encoding: $CURRENT_LANG"
    echo "          Recommended: UTF-8"
    echo "          Run: export LANG=en_US.UTF-8"
fi

echo ""
echo "For optimal display:"
echo "- Resize terminal to 120x40 or larger"
echo "- Use monospace font (14pt recommended)"
echo "- See TERMINAL_SETUP.md for details"
echo ""
