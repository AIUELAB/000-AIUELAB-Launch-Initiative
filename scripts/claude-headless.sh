#!/bin/bash

# Claude Code Headless Mode Script
# Run Claude Code in non-interactive mode for CI/CD and automation

set -e

# Colors for output
# shellcheck disable=SC2034
GREEN='\033[0;32m'
# shellcheck disable=SC2034
BLUE='\033[0;34m'
# shellcheck disable=SC2034
YELLOW='\033[1;33m'
# shellcheck disable=SC2034
RED='\033[0;31m'
# shellcheck disable=SC2034
NC='\033[0m'

# Default values
OUTPUT_FORMAT="text"
TIMEOUT=300
VERBOSE=false
PROMPT=""
TASK=""

# Function to display usage
usage() {
    echo -e "${BLUE}Claude Code Headless Mode${NC}"
    echo -e "Usage: $0 [OPTIONS]"
    echo -e "\nOptions:"
    echo -e "  -p, --prompt TEXT      Prompt to send to Claude"
    echo -e "  -t, --task TASK        Predefined task (test|lint|review|docs)"
    echo -e "  -o, --output FORMAT    Output format (text|json|stream-json)"
    echo -e "  -f, --file FILE        Input file to process"
    echo -e "  --timeout SECONDS      Maximum execution time (default: 300)"
    echo -e "  -v, --verbose          Verbose output"
    echo -e "  -h, --help             Show this help message"
    echo -e "\nExamples:"
    echo -e "  $0 -t test              # Run tests"
    echo -e "  $0 -t lint              # Run linting"
    echo -e "  $0 -t review -f app.py  # Review specific file"
    echo -e "  $0 -p 'Fix type errors' # Custom prompt"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--prompt)
            PROMPT="$2"
            shift 2
            ;;
        -t|--task)
            TASK="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -f|--file)
            INPUT_FILE="$2"
            shift 2
            ;;
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            usage
            ;;
    esac
done

# Function to log messages
log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
    fi
}

# Function to run predefined tasks
run_task() {
    local task=$1

    case "$task" in
        test)
            PROMPT="Run all tests and report any failures. Use pytest for Python code."
            ;;
        lint)
            PROMPT="Run linting and code quality checks. Fix any issues found."
            ;;
        review)
            if [ -n "$INPUT_FILE" ]; then
                PROMPT="Review the code in $INPUT_FILE and provide feedback on quality, security, and best practices."
            else
                PROMPT="Review recent changes and provide feedback on code quality."
            fi
            ;;
        docs)
            PROMPT="Generate or update documentation for the codebase."
            ;;
        security)
            PROMPT="Run security audit and identify potential vulnerabilities."
            ;;
        optimize)
            PROMPT="Analyze code for performance issues and suggest optimizations."
            ;;
        *)
            echo -e "${RED}Unknown task: $task${NC}"
            echo -e "Available tasks: test, lint, review, docs, security, optimize"
            exit 1
            ;;
    esac
}

# Main execution
if [ -z "$PROMPT" ] && [ -z "$TASK" ]; then
    echo -e "${RED}Error: Either --prompt or --task must be specified${NC}"
    usage
fi

# Process task if specified
if [ -n "$TASK" ]; then
    run_task "$TASK"
fi

# Add file context if specified
if [ -n "$INPUT_FILE" ]; then
    if [ ! -f "$INPUT_FILE" ]; then
        echo -e "${RED}Error: File '$INPUT_FILE' not found${NC}"
        exit 1
    fi
    PROMPT="$PROMPT\n\nFile to process: $INPUT_FILE"
fi

# Prepare the Claude Code command
CLAUDE_CMD="claude-code"

# Add headless mode flag
CLAUDE_CMD="$CLAUDE_CMD -p \"$PROMPT\""

# Add output format
if [ "$OUTPUT_FORMAT" = "json" ] || [ "$OUTPUT_FORMAT" = "stream-json" ]; then
    CLAUDE_CMD="$CLAUDE_CMD --output-format $OUTPUT_FORMAT"
fi

# Add timeout
CLAUDE_CMD="timeout $TIMEOUT $CLAUDE_CMD"

# Log the command if verbose
log "Executing: $CLAUDE_CMD"

# Execute Claude Code in headless mode
echo -e "${BLUE}Running Claude Code in headless mode...${NC}"

# Create temporary file for output
OUTPUT_FILE=$(mktemp)

# Run the command and capture output
if eval "$CLAUDE_CMD" > "$OUTPUT_FILE" 2>&1; then
    echo -e "${GREEN}✓ Task completed successfully${NC}"

    # Process output based on format
    if [ "$OUTPUT_FORMAT" = "json" ] || [ "$OUTPUT_FORMAT" = "stream-json" ]; then
        # For JSON output, pretty-print if jq is available
        if command -v jq &> /dev/null; then
            cat "$OUTPUT_FILE" | jq '.'
        else
            cat "$OUTPUT_FILE"
        fi
    else
        # For text output, display as-is
        cat "$OUTPUT_FILE"
    fi

    # Clean up
    rm -f "$OUTPUT_FILE"
    exit 0
else
    EXIT_CODE=$?
    echo -e "${RED}✗ Task failed with exit code: $EXIT_CODE${NC}"

    # Show error output
    if [ -f "$OUTPUT_FILE" ]; then
        echo -e "${RED}Error output:${NC}"
        cat "$OUTPUT_FILE"
        rm -f "$OUTPUT_FILE"
    fi

    exit $EXIT_CODE
fi
