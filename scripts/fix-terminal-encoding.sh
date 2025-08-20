#!/bin/bash

# 文字化け・色化け修正スクリプト
# Terminal encoding and color fix script

set -e

echo "========================================="
echo "Terminal Encoding & Color Fix Script"
echo "========================================="
echo ""

# 1. エンコーディング設定
echo "📝 Setting up UTF-8 encoding..."

# UTF-8 環境変数の設定
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
export LANGUAGE="en_US.UTF-8"

# Python環境のUTF-8設定
export PYTHONIOENCODING="utf-8"
export PYTHONLEGACYWINDOWSSTDIO="utf-8"

# 2. ターミナル設定
echo "🖥️  Configuring terminal settings..."

# TERMの設定（256色対応）
if [[ "$TERM" != *"256color"* ]]; then
    export TERM="xterm-256color"
fi

# カラー出力の有効化
export CLICOLOR=1
export LSCOLORS=ExFxBxDxCxegedabagacad
export LS_COLORS='di=1;34:ln=1;35:so=1;31:pi=1;33:ex=1;32:bd=34;46:cd=34;43:su=30;41:sg=30;46:tw=30;42:ow=30;43'

# Less コマンドでのカラー表示
export LESS='-R'
export LESSCHARSET='utf-8'

# 3. シェル設定ファイルの更新
echo "📄 Updating shell configuration..."

# シェルの判定
SHELL_CONFIG=""
if [[ "$SHELL" == *"zsh"* ]]; then
    SHELL_CONFIG="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

# 設定を永続化
if [ -n "$SHELL_CONFIG" ]; then
    echo ""
    echo "Adding encoding settings to $SHELL_CONFIG..."

    # バックアップ作成
    cp "$SHELL_CONFIG" "${SHELL_CONFIG}.backup.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true

    # 既存の設定をチェックして追加
    if ! grep -q "# Terminal Encoding Fix" "$SHELL_CONFIG" 2>/dev/null; then
        cat >> "$SHELL_CONFIG" << 'EOF'

# Terminal Encoding Fix
export LANG="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
export LANGUAGE="en_US.UTF-8"
export PYTHONIOENCODING="utf-8"
export TERM="xterm-256color"
export CLICOLOR=1
export LESS='-R'
export LESSCHARSET='utf-8'
EOF
        echo "✅ Settings added to $SHELL_CONFIG"
    else
        echo "⚠️  Settings already exist in $SHELL_CONFIG"
    fi
fi

# 4. Git設定のUTF-8対応
echo ""
echo "🔧 Configuring Git for UTF-8..."
git config --global core.quotepath false 2>/dev/null || true
git config --global gui.encoding utf-8 2>/dev/null || true
git config --global i18n.commit.encoding utf-8 2>/dev/null || true
git config --global i18n.logoutputencoding utf-8 2>/dev/null || true

# 5. 現在の設定確認
echo ""
echo "========================================="
echo "Current Settings:"
echo "========================================="
echo "LANG: $LANG"
echo "LC_ALL: $LC_ALL"
echo "TERM: $TERM"
echo "PYTHONIOENCODING: $PYTHONIOENCODING"
echo ""

# 6. テスト表示
echo "========================================="
echo "Test Display:"
echo "========================================="
echo ""

# 色のテスト
echo "Color Test:"
echo -e "\033[0;30mBlack\033[0m  \033[1;30mBright Black\033[0m"
echo -e "\033[0;31mRed\033[0m    \033[1;31mBright Red\033[0m"
echo -e "\033[0;32mGreen\033[0m  \033[1;32mBright Green\033[0m"
echo -e "\033[0;33mYellow\033[0m \033[1;33mBright Yellow\033[0m"
echo -e "\033[0;34mBlue\033[0m   \033[1;34mBright Blue\033[0m"
echo -e "\033[0;35mMagenta\033[0m \033[1;35mBright Magenta\033[0m"
echo -e "\033[0;36mCyan\033[0m   \033[1;36mBright Cyan\033[0m"
echo -e "\033[0;37mWhite\033[0m  \033[1;37mBright White\033[0m"
echo ""

# 日本語文字のテスト
echo "UTF-8 Character Test:"
echo "English: Hello, World!"
echo "Japanese: こんにちは、世界！"
echo "Emoji: 🚀 🎉 ✨ 💻 📝"
echo "Special: © ® ™ € £ ¥"
echo ""

# 7. 推奨事項
echo "========================================="
echo "Recommendations:"
echo "========================================="
echo ""
echo "1. Terminal Application Settings:"
echo "   - Font: Use a monospace font with good Unicode support"
echo "   - Recommended: SF Mono, JetBrains Mono, Fira Code"
echo "   - Font Size: 12-14pt for optimal readability"
echo ""
echo "2. Terminal Size:"
echo "   - Width: 120+ characters"
echo "   - Height: 40+ lines"
echo ""
echo "3. Apply Changes:"
echo "   - Run: source $SHELL_CONFIG"
echo "   - Or restart your terminal"
echo ""
echo "✅ Terminal encoding fix completed!"
echo ""
echo "If you still see issues:"
echo "1. Check your terminal app preferences"
echo "2. Ensure your font supports Unicode"
echo "3. Try: export LANG=C.UTF-8 (alternative)"
echo ""
