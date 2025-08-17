#!/bin/bash

# Claude Code CI/CD Integration Script
# Provides headless mode automation for continuous integration

set -e

# Color output definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
COMMAND=""
OUTPUT_FORMAT="text"
SKIP_PERMISSIONS=false
TIMEOUT=300
DOCKER_MODE=false
VERBOSE=false

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS] -c COMMAND"
    echo ""
    echo "Claude Code CI/CD automation script for headless operations"
    echo ""
    echo "Options:"
    echo "  -c, --command COMMAND    Command to execute (required)"
    echo "  -o, --output FORMAT      Output format: text, json, stream-json (default: text)"
    echo "  -s, --skip-permissions   Skip all permission prompts (use with caution)"
    echo "  -d, --docker            Run in Docker isolation mode"
    echo "  -t, --timeout SECONDS   Timeout in seconds (default: 300)"
    echo "  -v, --verbose           Enable verbose output"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  # Fix linting errors"
    echo "  $0 -c 'fix all linting errors' -s"
    echo ""
    echo "  # Run tests with JSON output"
    echo "  $0 -c 'run all tests and report results' -o json"
    echo ""
    echo "  # Generate code with Docker isolation"
    echo "  $0 -c 'generate REST API endpoints' -d -s"
    echo ""
    echo "  # CI pipeline integration"
    echo "  $0 -c 'check code quality and fix issues' -o stream-json -t 600"
    exit 0
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--command)
            COMMAND="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -s|--skip-permissions)
            SKIP_PERMISSIONS=true
            shift
            ;;
        -d|--docker)
            DOCKER_MODE=true
            shift
            ;;
        -t|--timeout)
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

# Validate required arguments
if [ -z "$COMMAND" ]; then
    echo -e "${RED}Error: Command is required${NC}"
    usage
fi

# Function to log messages
log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${BLUE}[INFO]${NC} $1"
    fi
}

# Function to run Claude in Docker
run_in_docker() {
    log "Setting up Docker environment..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    # Build Docker command
    DOCKER_CMD="docker run --rm"
    DOCKER_CMD="$DOCKER_CMD -v $(pwd):/workspace"
    DOCKER_CMD="$DOCKER_CMD -w /workspace"
    DOCKER_CMD="$DOCKER_CMD -e CLAUDE_API_KEY"
    
    # Add environment variables from .env.mcp if exists
    if [ -f ".env.mcp" ]; then
        DOCKER_CMD="$DOCKER_CMD --env-file .env.mcp"
    fi
    
    # Use official Claude Code Docker image (hypothetical)
    DOCKER_CMD="$DOCKER_CMD anthropic/claude-code:latest"
    
    # Add Claude command
    DOCKER_CMD="$DOCKER_CMD claude"
    DOCKER_CMD="$DOCKER_CMD -p \"$COMMAND\""
    DOCKER_CMD="$DOCKER_CMD --output-format $OUTPUT_FORMAT"
    
    if [ "$SKIP_PERMISSIONS" = true ]; then
        DOCKER_CMD="$DOCKER_CMD --dangerously-skip-permissions"
    fi
    
    log "Executing: $DOCKER_CMD"
    
    # Execute with timeout
    timeout $TIMEOUT bash -c "$DOCKER_CMD"
    return $?
}

# Function to run Claude directly
run_direct() {
    log "Running Claude Code in headless mode..."
    
    # Check if claude is installed
    if ! command -v claude &> /dev/null; then
        echo -e "${RED}Error: Claude Code is not installed${NC}"
        echo "Install with: npm install -g @anthropic/claude-cli"
        exit 1
    fi
    
    # Build Claude command
    CLAUDE_CMD="claude"
    CLAUDE_CMD="$CLAUDE_CMD -p \"$COMMAND\""
    CLAUDE_CMD="$CLAUDE_CMD --output-format $OUTPUT_FORMAT"
    
    if [ "$SKIP_PERMISSIONS" = true ]; then
        CLAUDE_CMD="$CLAUDE_CMD --dangerously-skip-permissions"
    fi
    
    log "Executing: $CLAUDE_CMD"
    
    # Execute with timeout
    timeout $TIMEOUT bash -c "$CLAUDE_CMD"
    return $?
}

# Main execution
echo -e "${GREEN}Claude Code CI/CD Automation${NC}"
echo -e "${BLUE}Command:${NC} $COMMAND"
echo -e "${BLUE}Output Format:${NC} $OUTPUT_FORMAT"
echo -e "${BLUE}Timeout:${NC} ${TIMEOUT}s"

if [ "$DOCKER_MODE" = true ]; then
    echo -e "${BLUE}Mode:${NC} Docker Isolation"
    run_in_docker
    EXIT_CODE=$?
else
    echo -e "${BLUE}Mode:${NC} Direct Execution"
    if [ "$SKIP_PERMISSIONS" = true ]; then
        echo -e "${YELLOW}Warning: Running with --dangerously-skip-permissions${NC}"
    fi
    run_direct
    EXIT_CODE=$?
fi

# Handle exit codes
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Command completed successfully${NC}"
elif [ $EXIT_CODE -eq 124 ]; then
    echo -e "${RED}❌ Command timed out after ${TIMEOUT}s${NC}"
    exit 1
else
    echo -e "${RED}❌ Command failed with exit code: $EXIT_CODE${NC}"
    exit $EXIT_CODE
fi