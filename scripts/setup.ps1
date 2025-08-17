# Claude Code MCP Template Setup Script for Windows
# PowerShell version of the setup script

# Colors for output
$colors = @{
    Red = "Red"
    Green = "Green" 
    Yellow = "Yellow"
    Blue = "Blue"
    Cyan = "Cyan"
}

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Info { Write-ColorOutput "[INFO] $args" -Color $colors.Blue }
function Write-Success { Write-ColorOutput "[SUCCESS] $args" -Color $colors.Green }
function Write-Warning { Write-ColorOutput "[WARNING] $args" -Color $colors.Yellow }
function Write-Error { Write-ColorOutput "[ERROR] $args" -Color $colors.Red }

# Banner
Write-Host ""
Write-ColorOutput "============================================" -Color $colors.Cyan
Write-ColorOutput "   Claude Code MCP Template Setup Script   " -Color $colors.Cyan
Write-ColorOutput "============================================" -Color $colors.Cyan
Write-Host ""

# Get project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
Set-Location $ProjectRoot

Write-Info "Project directory: $ProjectRoot"

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Info "Python version: $pythonVersion"
} catch {
    Write-Error "Python is not installed. Please install Python 3.11 or later."
    exit 1
}

# Check Node.js installation (for MCP)
try {
    $nodeVersion = node --version 2>&1
    Write-Info "Node.js version: $nodeVersion"
} catch {
    Write-Warning "Node.js is not found. MCP servers require Node.js 18 or later."
}

# Virtual environment setup
$venvPath = Join-Path $ProjectRoot "venv"

if (Test-Path $venvPath) {
    $response = Read-Host "Existing virtual environment found. Delete and recreate? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        Write-Info "Removing existing virtual environment..."
        Remove-Item -Recurse -Force $venvPath
    } else {
        Write-Info "Using existing virtual environment."
    }
}

if (-not (Test-Path $venvPath)) {
    Write-Info "Creating Python virtual environment..."
    python -m venv venv
    Write-Success "Virtual environment created"
}

# Activate virtual environment
Write-Info "Activating virtual environment..."
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Error "Could not find activation script"
    exit 1
}

# Upgrade pip
Write-Info "Upgrading pip..."
python -m pip install --upgrade pip | Out-Null

# Install dependencies
$requirementsFile = Join-Path $ProjectRoot "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Info "Installing Python dependencies..."
    pip install -r requirements.txt
    Write-Success "All Python dependencies installed"
} else {
    Write-Warning "requirements.txt not found"
}

# Create .env file
$envFile = Join-Path $ProjectRoot ".env"
$envExample = Join-Path $ProjectRoot ".env.example"

if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
    Write-Info "Creating .env file from .env.example..."
    Copy-Item $envExample $envFile
    Write-Success ".env file created"
    Write-Warning "Edit .env file to set required environment variables"
} elseif (Test-Path $envFile) {
    Write-Info ".env file already exists"
}

# Create MCP .env file
$mcpEnvFile = Join-Path $ProjectRoot "mcp-config\.env.mcp"
$mcpEnvExample = Join-Path $ProjectRoot "mcp-config\.env.mcp.example"

if (-not (Test-Path $mcpEnvFile) -and (Test-Path $mcpEnvExample)) {
    Write-Info "Creating .env.mcp file from .env.mcp.example..."
    Copy-Item $mcpEnvExample $mcpEnvFile
    Write-Success ".env.mcp file created"
    Write-Warning "Edit mcp-config\.env.mcp file to set required API keys"
} elseif (Test-Path $mcpEnvFile) {
    Write-Info ".env.mcp file already exists"
}

# MCP Server setup
Write-Host ""
$response = Read-Host "Setup MCP servers? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    $mcpSetupScript = Join-Path $ProjectRoot "mcp-config\setup-mcp.sh"
    if (Test-Path $mcpSetupScript) {
        Write-Info "Setting up MCP servers..."
        # For Windows, we'll run npm install commands directly
        Write-Info "Installing MCP servers via npm..."
        npm install -g @modelcontextprotocol/server-filesystem `
                      @modelcontextprotocol/server-github `
                      @modelcontextprotocol/server-brave-search `
                      @context7/mcp-server `
                      @playwright/mcp `
                      @win32user/mcp-ide 2>$null
        Write-Success "MCP servers installed"
    } else {
        Write-Warning "mcp-config\setup-mcp.sh not found"
    }
}

# Check directory structure
Write-Info "Checking project structure..."
$directories = @("src", "tests", "scripts", "mcp-config")
foreach ($dir in $directories) {
    $dirPath = Join-Path $ProjectRoot $dir
    if (Test-Path $dirPath) {
        Write-ColorOutput "  ✓ $dir\" -Color $colors.Green
    } else {
        Write-ColorOutput "  ✗ $dir\ (not found)" -Color $colors.Red
        New-Item -ItemType Directory -Path $dirPath | Out-Null
        Write-Info "$dir\ directory created"
    }
}

# Git repository initialization
$gitPath = Join-Path $ProjectRoot ".git"
if (-not (Test-Path $gitPath)) {
    $response = Read-Host "Initialize Git repository? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        git init
        Write-Success "Git repository initialized"
        
        $response = Read-Host "Create initial commit? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            git add .
            git commit -m "Initial commit: Claude Code MCP template"
            Write-Success "Initial commit created"
        }
    }
} else {
    Write-Info "Git repository already initialized"
}

# Run tests
$response = Read-Host "Run tests? (y/N)"
if ($response -eq "y" -or $response -eq "Y") {
    Write-Info "Running tests..."
    $testDir = Join-Path $ProjectRoot "tests"
    if (Test-Path $testDir) {
        pytest tests -v
        if ($LASTEXITCODE -eq 0) {
            Write-Success "All tests passed"
        } else {
            Write-Warning "Some tests failed"
        }
    } else {
        Write-Warning "No test files found"
    }
}

# Complete
Write-Host ""
Write-ColorOutput "============================================" -Color $colors.Green
Write-ColorOutput "       Setup completed successfully!        " -Color $colors.Green
Write-ColorOutput "============================================" -Color $colors.Green
Write-Host ""
Write-ColorOutput "Next steps:" -Color $colors.Cyan
Write-Host "1. Activate virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "2. Edit .env file to set environment variables"
Write-Host "3. Edit mcp-config\.env.mcp file to set API keys"
Write-Host "4. Run application: python src\main.py"
Write-Host "5. Run MCP examples: python src\mcp_examples.py"
Write-Host "6. Start Claude Code: claude-code"
Write-Host ""
Write-ColorOutput "MCP Server Usage:" -Color $colors.Yellow
Write-Host "• Type '/mcp' in Claude to check MCP servers"
Write-Host "• mcp__github__ for GitHub operations"
Write-Host "• mcp__brave-search__ for web search"
Write-Host "• mcp__filesystem__ for file operations"
Write-Host ""
Write-ColorOutput "Happy Coding with Claude Code & MCP! 🚀" -Color $colors.Green

# Optional: Open VS Code
if (Get-Command code -ErrorAction SilentlyContinue) {
    $response = Read-Host "Open project in VS Code? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        code .
    }
}