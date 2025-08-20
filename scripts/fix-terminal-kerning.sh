#!/bin/bash

# Terminal Kerning/Character Spacing Fix Script
# This script automatically fixes character spacing issues in terminal display

echo "🔧 Fixing terminal character spacing and kerning issues..."

# Set proper encoding environment variables
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export TERM="xterm-256color"
export PYTHONIOENCODING="utf-8"

# Function to update VSCode/Cursor settings
update_vscode_settings() {
    local settings_file="$1"

    if [ -f "$settings_file" ]; then
        echo "📝 Updating VSCode/Cursor settings..."

        # Backup original settings
        cp "$settings_file" "${settings_file}.backup.$(date +%Y%m%d_%H%M%S)"

        # Use Python to update JSON settings
        python3 << EOF
import json
import os

settings_path = "$settings_file"

# Read existing settings
with open(settings_path, 'r', encoding='utf-8') as f:
    settings = json.load(f)

# Update terminal font settings for better kerning
updated_settings = {
    # Better monospace fonts with proper kerning
    "terminal.integrated.fontFamily": "JetBrains Mono, SF Mono, Menlo, Monaco, 'Courier New', monospace",
    "terminal.integrated.fontSize": 14,
    "terminal.integrated.lineHeight": 1.4,  # Better line spacing
    "terminal.integrated.letterSpacing": 0.5,  # Add letter spacing

    # Editor font settings
    "editor.fontFamily": "JetBrains Mono, Fira Code, SF Mono, Menlo, Monaco, Consolas, 'Courier New', monospace",
    "editor.fontSize": 14,
    "editor.lineHeight": 22,
    "editor.letterSpacing": 0.3,
    "editor.fontLigatures": true,

    # Terminal rendering optimization
    "terminal.integrated.gpuAcceleration": "on",
    "terminal.integrated.rendererType": "canvas",  # Better rendering
    "terminal.integrated.unicodeVersion": "11",
    "terminal.integrated.minimumContrastRatio": 4.5,

    # Environment variables for proper encoding
    "terminal.integrated.env.osx": {
        "PYTHONPATH": "\${workspaceFolder}",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "TERM": "xterm-256color",
        "CLICOLOR": "1",
        "PYTHONIOENCODING": "utf-8"
    },
    "terminal.integrated.env.linux": {
        "PYTHONPATH": "\${workspaceFolder}",
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
        "TERM": "xterm-256color",
        "PYTHONIOENCODING": "utf-8"
    }
}

# Update settings
for key, value in updated_settings.items():
    settings[key] = value

# Write updated settings
with open(settings_path, 'w', encoding='utf-8') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print("✅ Settings updated successfully!")
EOF
    else
        echo "⚠️  Settings file not found: $settings_file"
    fi
}

# Function to install recommended fonts
install_fonts() {
    echo "📦 Checking for recommended fonts..."

    # Check OS type
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo "⚠️  Homebrew not found. Please install Homebrew first."
            echo "   Visit: https://brew.sh"
        else
            # Install JetBrains Mono font (best for programming)
            if ! brew list --cask | grep -q "font-jetbrains-mono"; then
                echo "Installing JetBrains Mono font..."
                brew install --cask font-jetbrains-mono
            else
                echo "✅ JetBrains Mono already installed"
            fi

            # Install Fira Code font (alternative with ligatures)
            if ! brew list --cask | grep -q "font-fira-code"; then
                echo "Installing Fira Code font..."
                brew install --cask font-fira-code
            else
                echo "✅ Fira Code already installed"
            fi
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            # Debian/Ubuntu
            echo "Installing fonts on Linux..."
            sudo apt-get update
            sudo apt-get install -y fonts-jetbrains-mono fonts-firacode
        elif command -v dnf &> /dev/null; then
            # Fedora
            sudo dnf install -y jetbrains-mono-fonts fira-code-fonts
        fi
    fi
}

# Function to create terminal test file
create_test_file() {
    cat > terminal_kerning_test.txt << 'EOF'
Terminal Kerning Test
=====================

Regular Text:
/help for help, /status for your current setup

Monospace Characters:
0123456789
ABCDEFGHIJ
abcdefghij
!@#$%^&*()

Code Sample:
def calculate_sum(a, b):
    """Calculate the sum of two numbers."""
    return a + b

Special Characters:
→ ← ↑ ↓ ⌘ ⌥ ⇧ ⌃ ⌫ ⏎

Unicode Box Drawing:
┌─────────────────┐
│ Box Drawing     │
├─────────────────┤
│ Test Content    │
└─────────────────┘

Letter Spacing Test:
i i i i i i i i i i
l l l l l l l l l l
| | | | | | | | | |
1 1 1 1 1 1 1 1 1 1

If the above text appears properly spaced and readable,
the kerning fix has been successfully applied.
EOF
    echo "📄 Test file created: terminal_kerning_test.txt"
}

# Main execution
main() {
    echo "=================================="
    echo "Terminal Kerning Fix Script"
    echo "=================================="
    echo ""

    # Detect workspace directory
    WORKSPACE_DIR=$(pwd)

    # Check for .vscode/settings.json
    VSCODE_SETTINGS="$WORKSPACE_DIR/.vscode/settings.json"
    if [ -f "$VSCODE_SETTINGS" ]; then
        update_vscode_settings "$VSCODE_SETTINGS"
    fi

    # Check for global VSCode settings (macOS)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        GLOBAL_VSCODE="$HOME/Library/Application Support/Code/User/settings.json"
        GLOBAL_CURSOR="$HOME/Library/Application Support/Cursor/User/settings.json"

        if [ -f "$GLOBAL_CURSOR" ]; then
            echo "Found Cursor global settings"
            read -p "Update global Cursor settings? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                update_vscode_settings "$GLOBAL_CURSOR"
            fi
        elif [ -f "$GLOBAL_VSCODE" ]; then
            echo "Found VSCode global settings"
            read -p "Update global VSCode settings? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                update_vscode_settings "$GLOBAL_VSCODE"
            fi
        fi
    fi

    # Offer to install fonts
    read -p "Install recommended fonts? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_fonts
    fi

    # Create test file
    create_test_file

    echo ""
    echo "✅ Terminal kerning fix complete!"
    echo ""
    echo "🔄 Please restart your terminal/editor for changes to take effect."
    echo ""
    echo "📝 To test the changes:"
    echo "   1. Restart your terminal/editor"
    echo "   2. Run: cat terminal_kerning_test.txt"
    echo "   3. Check if text spacing looks correct"
    echo ""
    echo "💡 If issues persist, try:"
    echo "   - Changing terminal.integrated.letterSpacing value (0.3 to 1.0)"
    echo "   - Using a different font from the list"
    echo "   - Adjusting terminal.integrated.lineHeight (1.2 to 1.6)"
}

# Run main function
main
