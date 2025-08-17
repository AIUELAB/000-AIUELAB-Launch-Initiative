#!/bin/bash

# APIキー読み込みスクリプト
# キーフォルダから自動的にAPIキーを読み込んで.env.mcpを生成

set -e

# カラー出力の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# プロジェクトルートを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# ログ関数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# ヘッダー表示
echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}      APIキー自動読み込みスクリプト         ${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# Pythonの確認
if ! command -v python3 &> /dev/null; then
    log_error "Python3が見つかりません"
    exit 1
fi

# 引数の処理
AUTO_MODE=false
OUTPUT_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --output|-o)
            OUTPUT_PATH="$2"
            shift 2
            ;;
        --help|-h)
            echo "使用方法: $0 [オプション]"
            echo ""
            echo "オプション:"
            echo "  -a, --auto        自動モード（確認なしで実行）"
            echo "  -o, --output PATH 出力先のパスを指定"
            echo "  -h, --help        このヘルプを表示"
            exit 0
            ;;
        *)
            log_error "不明なオプション: $1"
            exit 1
            ;;
    esac
done

# 自動モードの場合
if [ "$AUTO_MODE" = true ]; then
    log_info "自動モードで実行します"
    
    # デフォルトの出力先
    if [ -z "$OUTPUT_PATH" ]; then
        OUTPUT_PATH="$PROJECT_ROOT/.env.mcp"
    fi
    
    # Pythonスクリプトを自動実行
    echo "1" | python3 "$SCRIPT_DIR/load_keys.py" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        log_success ".env.mcpファイルを生成しました: $OUTPUT_PATH"
    else
        log_error "キーの読み込みに失敗しました"
        exit 1
    fi
else
    # 対話モード
    python3 "$SCRIPT_DIR/load_keys.py"
fi

# 生成されたファイルの確認
if [ -f "$PROJECT_ROOT/.env.mcp" ]; then
    echo ""
    log_success "環境変数ファイルが正常に生成されました"
    echo ""
    echo -e "${CYAN}次のステップ:${NC}"
    echo "  1. 生成されたファイルを確認:"
    echo "     cat $PROJECT_ROOT/.env.mcp"
    echo ""
    echo "  2. アプリケーションを実行:"
    echo "     python src/main.py info"
    echo ""
    echo "  3. MCPサーバーの状態を確認:"
    echo "     python src/main.py check-env"
fi

echo ""
log_info "完了しました！"