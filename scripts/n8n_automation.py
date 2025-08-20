#!/usr/bin/env python3
"""
n8n Automation Helper
作業工程の中で自動的にn8nワークフローをトリガーするヘルパースクリプト
"""

import json
import requests
from typing import Dict, Any, Optional, List
import subprocess
import os
from datetime import datetime
from pathlib import Path

N8N_NOT_RUNNING = "n8n not running"


class N8NAutomation:
    """n8n自動化ヘルパークラス"""

    def __init__(self, base_url: str = "http://localhost:5679"):
        self.base_url = base_url
        self.webhook_base = f"{base_url}/webhook"

    def trigger_webhook(self, path: str, data: Dict[str, Any] = None, method: str = "GET") -> Dict[str, Any]:
        """Webhookをトリガー"""
        url = f"{self.webhook_base}/{path}"

        try:
            if method.upper() == "GET":
                response = requests.get(url, params=data, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)

            response.raise_for_status()
            return {"success": True, "data": response.text, "status": response.status_code}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_health(self) -> bool:
        """n8nサーバーの健全性チェック"""
        try:
            response = requests.get(f"{self.base_url}/healthz", timeout=2)
            return response.status_code == 200
        except Exception:
            return False


class WorkflowTriggers:
    """特定の作業に応じたワークフロートリガー"""

    def __init__(self):
        self.n8n = N8NAutomation()

    def on_git_commit(self, message: str, files: List[str]) -> Dict[str, Any]:
        """Git コミット時にn8nワークフローをトリガー"""
        if not self.n8n.check_health():
            return {"skipped": True, "reason": N8N_NOT_RUNNING}

        # 特定のファイルパターンでワークフローをトリガー
        if any(f.endswith('.test.py') for f in files):
            return self.n8n.trigger_webhook("run-tests", {
                "commit_message": message,
                "test_files": [f for f in files if f.endswith('.test.py')],
                "timestamp": datetime.now().isoformat()
            })

        return {"skipped": True, "reason": "No matching trigger"}

    def on_error_detection(self, error_type: str, error_message: str, file_path: str) -> Dict[str, Any]:
        """エラー検出時にn8nワークフローをトリガー"""
        if not self.n8n.check_health():
            return {"skipped": True, "reason": N8N_NOT_RUNNING}

        # エラー通知ワークフローをトリガー
        return self.n8n.trigger_webhook("error-handler", {
            "error_type": error_type,
            "message": error_message,
            "file": file_path,
            "timestamp": datetime.now().isoformat()
        })

    def on_build_complete(self, success: bool, duration: float, output: str) -> Dict[str, Any]:
        """ビルド完了時にn8nワークフローをトリガー"""
        if not self.n8n.check_health():
            return {"skipped": True, "reason": N8N_NOT_RUNNING}

        return self.n8n.trigger_webhook("build-notification", {
            "success": success,
            "duration": duration,
            "output": output[:1000],  # 最初の1000文字のみ
            "timestamp": datetime.now().isoformat()
        })

    def on_deploy_request(self, environment: str, version: str) -> Dict[str, Any]:
        """デプロイリクエスト時にn8nワークフローをトリガー"""
        if not self.n8n.check_health():
            return {"skipped": True, "reason": N8N_NOT_RUNNING}

        return self.n8n.trigger_webhook("deploy", {
            "environment": environment,
            "version": version,
            "timestamp": datetime.now().isoformat()
        })


def auto_trigger_n8n(event_type: str, **kwargs) -> Dict[str, Any]:
    """
    イベントタイプに基づいて自動的にn8nワークフローをトリガー

    使用例:
        auto_trigger_n8n("git_commit", message="Fix bug", files=["main.py"])
        auto_trigger_n8n("error", error_type="SyntaxError", error_message="...", file_path="test.py")
    """
    triggers = WorkflowTriggers()

    event_handlers = {
        "git_commit": lambda: triggers.on_git_commit(
            kwargs.get("message", ""),
            kwargs.get("files", [])
        ),
        "error": lambda: triggers.on_error_detection(
            kwargs.get("error_type", "Unknown"),
            kwargs.get("error_message", ""),
            kwargs.get("file_path", "")
        ),
        "build": lambda: triggers.on_build_complete(
            kwargs.get("success", False),
            kwargs.get("duration", 0),
            kwargs.get("output", "")
        ),
        "deploy": lambda: triggers.on_deploy_request(
            kwargs.get("environment", "staging"),
            kwargs.get("version", "latest")
        )
    }

    handler = event_handlers.get(event_type)
    if handler:
        return handler()

    return {"error": f"Unknown event type: {event_type}"}


def integrate_with_shell():
    """シェルコマンドと統合"""
    script_content = '''#!/bin/bash
# n8n自動化フック for Bash

# Git pre-commit hook
n8n_git_hook() {
    files=$(git diff --cached --name-only)
    message=$(git log -1 --pretty=%B 2>/dev/null || echo "No commit message")
    python3 -c "
from scripts.n8n_automation import auto_trigger_n8n
import sys
result = auto_trigger_n8n('git_commit', message='$message', files='$files'.split())
sys.exit(0 if result.get('success', False) else 1)
"
}

# エラーハンドリングフック
n8n_error_hook() {
    error_type=$1
    error_msg=$2
    file_path=$3
    python3 -c "
from scripts.n8n_automation import auto_trigger_n8n
auto_trigger_n8n('error', error_type='$error_type', error_message='$error_msg', file_path='$file_path')
"
}

# ビルドフック
n8n_build_hook() {
    success=$1
    duration=$2
    output=$3
    python3 -c "
from scripts.n8n_automation import auto_trigger_n8n
auto_trigger_n8n('build', success=$success, duration=$duration, output='$output')
"
}
'''

    with open("scripts/n8n_hooks.sh", "w", encoding="utf-8") as f:
        f.write(script_content)

    os.chmod("scripts/n8n_hooks.sh", 0o700)
    print("Bash integration script created at scripts/n8n_hooks.sh")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            n8n = N8NAutomation()
            if n8n.check_health():
                print("✅ n8n is running and healthy")
                result = n8n.trigger_webhook("test", {"source": "automation_script"})
                print(f"Test webhook result: {result}")
            else:
                print("❌ n8n is not running")

        elif command == "integrate":
            integrate_with_shell()
            print("✅ Shell integration completed")

        elif command == "trigger":
            if len(sys.argv) > 2:
                event_type = sys.argv[2]
                kwargs: Dict[str, Any] = {}
                for arg in sys.argv[3:]:
                    if "=" in arg:
                        key, value = arg.split("=", 1)
                        kwargs[key] = value

                result = auto_trigger_n8n(event_type, **kwargs)
                print(json.dumps(result, indent=2))
            else:
                print("Usage: python n8n_automation.py trigger <event_type> [key=value ...]")

        else:
            print("Usage: python n8n_automation.py [test|integrate|trigger]")
    else:
        n8n = N8NAutomation()
        print(f"n8n health check: {n8n.check_health()}")
