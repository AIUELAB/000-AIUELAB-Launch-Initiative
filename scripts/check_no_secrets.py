#!/usr/bin/env python3
"""
APIキーやシークレットが誤ってコミットされないようチェックするスクリプト
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# チェックするパターン
SECRET_PATTERNS = [
    # APIキー
    (r'(api[_-]?key|apikey)\s*=\s*["\']([^"\']+)["\']', "API Key"),
    (r'(secret[_-]?key|secretkey)\s*=\s*["\']([^"\']+)["\']', "Secret Key"),
    (r'(access[_-]?token|accesstoken)\s*=\s*["\']([^"\']+)["\']', "Access Token"),
    (r'(private[_-]?key|privatekey)\s*=\s*["\']([^"\']+)["\']', "Private Key"),
    
    # 一般的なAPIキーパターン
    (r'sk-[a-zA-Z0-9]{48}', "OpenAI API Key"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub Personal Access Token"),
    (r'ghs_[a-zA-Z0-9]{36}', "GitHub Secret"),
    (r'github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59}', "GitHub Fine-grained PAT"),
    
    # AWSクレデンシャル
    (r'AKIA[0-9A-Z]{16}', "AWS Access Key ID"),
    (r'aws_secret_access_key\s*=\s*["\']([^"\']+)["\']', "AWS Secret Key"),
    
    # データベース認証情報
    (r'(password|passwd|pwd)\s*=\s*["\']([^"\']+)["\']', "Password"),
    (r'(database_url|db_url)\s*=\s*["\']([^"\']+)["\']', "Database URL"),
    
    # その他
    (r'Bearer\s+[a-zA-Z0-9\-\._~\+\/]+', "Bearer Token"),
    (r'Basic\s+[a-zA-Z0-9=]+', "Basic Auth"),
]

# 除外するファイル/ディレクトリ
EXCLUDE_PATHS = [
    '.git',
    '.venv',
    'venv',
    '__pycache__',
    'node_modules',
    '.env.example',
    '.env.mcp.example',
    '*.example',
    'test_*',
    '*_test.py',
]

# 許可するダミー値
ALLOWED_DUMMY_VALUES = [
    'your-api-key-here',
    'your_api_key_here',
    'YOUR_API_KEY_HERE',
    'xxx',
    'XXX',
    'placeholder',
    'example',
    'test',
    'dummy',
    'fake',
    '<your-key>',
    '${API_KEY}',
    '$(API_KEY)',
    'sk-...', 
    'ghp_...',
    'your_github_token',
    'your_openai_key',
]


def should_skip_file(file_path: Path) -> bool:
    """ファイルをスキップすべきか判定"""
    path_str = str(file_path)
    
    for exclude in EXCLUDE_PATHS:
        if exclude in path_str:
            return True
        if file_path.match(exclude):
            return True
    
    # バイナリファイルはスキップ
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            f.read(1)
    except (UnicodeDecodeError, PermissionError):
        return True
    
    return False


def is_allowed_value(value: str) -> bool:
    """許可されたダミー値かチェック"""
    value_lower = value.lower()
    
    for allowed in ALLOWED_DUMMY_VALUES:
        if allowed.lower() in value_lower:
            return True
    
    # 環境変数参照の場合は許可
    if value.startswith('$') or value.startswith('${'):
        return True
    
    # 空文字や短すぎる値は無視
    if len(value) < 5:
        return True
    
    return False


def check_file_for_secrets(file_path: Path) -> List[Tuple[int, str, str]]:
    """ファイル内のシークレットをチェック"""
    findings = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception:
        return findings
    
    for line_no, line in enumerate(lines, 1):
        # コメント行はスキップ
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//'):
            continue
        
        for pattern, secret_type in SECRET_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                # マッチした値を取得
                if match.groups():
                    value = match.group(len(match.groups()))
                else:
                    value = match.group(0)
                
                # 許可された値でなければ報告
                if not is_allowed_value(value):
                    findings.append((line_no, secret_type, value[:20] + '...'))
    
    return findings


def main():
    """メインエントリーポイント"""
    project_root = Path.cwd()
    
    # チェック対象のファイルを収集
    files_to_check = []
    for ext in ['*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.json', '*.yaml', '*.yml', 
                '*.toml', '*.ini', '*.cfg', '*.conf', '*.sh', '*.bash', '*.env*']:
        files_to_check.extend(project_root.rglob(ext))
    
    has_secrets = False
    
    for file_path in files_to_check:
        if should_skip_file(file_path):
            continue
        
        findings = check_file_for_secrets(file_path)
        
        if findings:
            has_secrets = True
            print(f"\n⚠️  Potential secrets found in {file_path.relative_to(project_root)}:")
            for line_no, secret_type, preview in findings:
                print(f"  Line {line_no}: {secret_type} - {preview}")
    
    if has_secrets:
        print("\n❌ Secrets detected! Please remove them before committing.")
        print("💡 Tip: Use environment variables or .env files (added to .gitignore) instead.")
        sys.exit(1)
    else:
        print("✅ No secrets detected in the codebase.")
        sys.exit(0)


if __name__ == "__main__":
    main()