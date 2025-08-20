#!/bin/bash

# n8n自動トリガースクリプト
# 作業工程で特定の条件を検出したら自動的にn8nワークフローをトリガー

N8N_URL="http://localhost:5679"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# n8nの健全性チェック
check_n8n() {
    curl -s "${N8N_URL}/healthz" > /dev/null 2>&1
    return $?
}

# Pythonスクリプトのエラーを検出してn8nに送信
detect_python_errors() {
    local file=$1
    python3 "$file" 2>&1 | while IFS= read -r line; do
        if [[ $line == *"Error"* ]] || [[ $line == *"Exception"* ]]; then
            echo "🔴 Error detected: $line"
            # n8nにエラー通知を送信
            curl -s "${N8N_URL}/webhook/error-notify" \
                -G --data-urlencode "error=$line" \
                --data-urlencode "file=$file" \
                --data-urlencode "time=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        fi
    done
}

# テスト実行と結果をn8nに送信
run_tests_with_n8n() {
    echo "🧪 Running tests with n8n integration..."
    
    start_time=$(date +%s)
    test_output=$(pytest tests/ -v 2>&1)
    exit_code=$?
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if [ $exit_code -eq 0 ]; then
        echo "✅ Tests passed"
        status="success"
    else
        echo "❌ Tests failed"
        status="failed"
    fi
    
    # n8nに結果を送信
    if check_n8n; then
        curl -s "${N8N_URL}/webhook/test-results" \
            -G --data-urlencode "status=$status" \
            --data-urlencode "duration=$duration" \
            --data-urlencode "summary=${test_output: -500}"
    fi
    
    echo "$test_output"
    return $exit_code
}

# ビルド実行とn8n通知
build_with_n8n() {
    echo "🔨 Building with n8n integration..."
    
    start_time=$(date +%s)
    build_output=$(npm run build 2>&1)
    exit_code=$?
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    if check_n8n; then
        curl -s "${N8N_URL}/webhook/build-complete" \
            -G --data-urlencode "success=$([[ $exit_code -eq 0 ]] && echo 'true' || echo 'false')" \
            --data-urlencode "duration=$duration"
    fi
    
    echo "$build_output"
    return $exit_code
}

# Gitフックとn8n統合
setup_git_hooks() {
    echo "📎 Setting up Git hooks with n8n..."
    
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# n8n統合付きpre-commitフック

# n8nが動作している場合、コミット情報を送信
if curl -s "http://localhost:5679/healthz" > /dev/null 2>&1; then
    files=$(git diff --cached --name-only | tr '\n' ',')
    curl -s "http://localhost:5679/webhook/pre-commit" \
        -G --data-urlencode "files=$files" \
        --data-urlencode "branch=$(git branch --show-current)"
fi

# 通常のpre-commitチェックを続行
exit 0
EOF
    
    chmod +x .git/hooks/pre-commit
    echo "✅ Git hooks installed"
}

# メイン処理
case "$1" in
    "test")
        python3 "${SCRIPT_DIR}/n8n_automation.py" test
        ;;
    "integrate")
        python3 "${SCRIPT_DIR}/n8n_automation.py" integrate
        setup_git_hooks
        ;;
    "run-tests")
        run_tests_with_n8n
        ;;
    "build")
        build_with_n8n
        ;;
    "check-errors")
        if [ -z "$2" ]; then
            echo "Usage: $0 check-errors <python_file>"
            exit 1
        fi
        detect_python_errors "$2"
        ;;
    "trigger")
        shift
        python3 "${SCRIPT_DIR}/n8n_automation.py" trigger "$@"
        ;;
    *)
        echo "n8n自動化ツール"
        echo ""
        echo "使用方法:"
        echo "  $0 test          - n8n接続テスト"
        echo "  $0 integrate     - Git/Shell統合セットアップ"
        echo "  $0 run-tests     - テスト実行とn8n通知"
        echo "  $0 build         - ビルド実行とn8n通知"
        echo "  $0 check-errors <file> - Pythonエラー検出"
        echo "  $0 trigger <event> [args] - カスタムイベントトリガー"
        echo ""
        echo "例:"
        echo "  $0 trigger git_commit message='Fix bug' files='main.py,test.py'"
        echo "  $0 trigger error error_type=SyntaxError file_path=app.py"
        exit 0
        ;;
esac