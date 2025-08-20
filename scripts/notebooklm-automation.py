#!/usr/bin/env python3
"""
NotebookLM 自動化スクリプト
Google OAuth2.0とPlaywrightを使用した自動アクセス
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

# Google Auth関連
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# ブラウザ自動化
try:
    from playwright.sync_api import sync_playwright, Page
except ImportError:
    print("Playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install chromium")

# 設定
SCOPES = ['https://www.googleapis.com/auth/userinfo.email']
TOKEN_FILE = Path.home() / '.notebooklm' / 'token.json'
CREDENTIALS_FILE = Path.home() / '.notebooklm' / 'credentials.json'
NOTEBOOK_URL = "https://notebooklm.google.com/notebook/ce4eebd7-38da-4b35-8205-8b31f9125827"


class NotebookLMAutomation:
    """NotebookLM自動化クラス"""

    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self.page: Optional[Page] = None
        self.browser = None
        self.context = None
        self.playwright = None

    def setup_google_auth(self) -> bool:
        """Google認証のセットアップ"""
        try:
            # トークンファイルが存在する場合は読み込み
            if TOKEN_FILE.exists():
                self.credentials = Credentials.from_authorized_user_file(
                    str(TOKEN_FILE), SCOPES
                )

            # 認証が無効または存在しない場合
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # トークンをリフレッシュ
                    self.credentials.refresh(Request())
                else:
                    # 新規認証フロー
                    if not CREDENTIALS_FILE.exists():
                        print(f"❌ 認証ファイルが見つかりません: {CREDENTIALS_FILE}")
                        print("Google Cloud Consoleで認証情報を作成してください")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(CREDENTIALS_FILE), SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)

                # トークンを保存
                TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
                with open(TOKEN_FILE, 'w') as token:
                    token.write(self.credentials.to_json())

            print("✅ Google認証成功")
            return True

        except Exception as e:
            print(f"❌ 認証エラー: {e}")
            return False

    def start_browser_with_auth(self) -> bool:
        """認証済みブラウザを起動"""
        try:
            self.playwright = sync_playwright().start()

            # Chromeプロファイルを使用（ログイン状態を保持）
            user_data_dir = Path.home() / '.notebooklm' / 'browser_profile'
            user_data_dir.mkdir(parents=True, exist_ok=True)

            self.browser = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(user_data_dir),
                headless=False,  # GUIで確認する場合はFalse
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ],
                viewport={'width': 1280, 'height': 800}
            )

            self.page = self.browser.new_page()

            # Googleにログイン済みかチェック
            self.page.goto("https://accounts.google.com")
            time.sleep(2)

            # ログイン済みならNotebookLMに直接アクセス
            if "myaccount.google.com" in self.page.url or "accounts.google.com/ServiceLogin" not in self.page.url:
                print("✅ Google既にログイン済み")
                return True
            else:
                print("⚠️  Googleログインが必要です")
                # 手動ログインを促す
                print("ブラウザでGoogleにログインしてください...")
                input("ログイン完了後、Enterキーを押してください...")
                return True

        except Exception as e:
            print(f"❌ ブラウザ起動エラー: {e}")
            return False

    def access_notebook(self) -> bool:
        """NotebookLMにアクセス"""
        try:
            print(f"📚 NotebookLMにアクセス中...")
            self.page.goto(NOTEBOOK_URL, wait_until='networkidle')
            time.sleep(3)

            # アクセス成功をチェック
            if "notebooklm.google.com" in self.page.url:
                print(f"✅ NotebookLMアクセス成功")
                print(f"URL: {self.page.url}")
                return True
            else:
                print(f"❌ NotebookLMアクセス失敗")
                return False

        except Exception as e:
            print(f"❌ アクセスエラー: {e}")
            return False

    def add_source(self, source_type: str, source_data: str) -> bool:
        """ソースを追加"""
        try:
            # ソース追加ボタンをクリック
            self.page.click('button:has-text("Add source")', timeout=5000)
            time.sleep(1)

            if source_type == "text":
                # テキストソースを追加
                self.page.fill('textarea', source_data)
                self.page.click('button:has-text("Add")')
            elif source_type == "url":
                # URLソースを追加
                self.page.fill('input[type="url"]', source_data)
                self.page.click('button:has-text("Add")')

            print(f"✅ ソース追加成功: {source_type}")
            return True

        except Exception as e:
            print(f"❌ ソース追加エラー: {e}")
            return False

    def chat_with_notebook(self, query: str) -> Optional[str]:
        """NotebookLMとチャット"""
        try:
            # チャット入力欄を探す
            chat_input = self.page.locator('textarea[placeholder*="Ask"]').first
            chat_input.fill(query)
            chat_input.press("Enter")

            # レスポンスを待つ
            time.sleep(5)

            # 最新のレスポンスを取得
            responses = self.page.locator('.response-message').all()
            if responses:
                latest_response = responses[-1].text_content()
                return latest_response

            return None

        except Exception as e:
            print(f"❌ チャットエラー: {e}")
            return None

    def cleanup(self):
        """リソースのクリーンアップ"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


class NotebookLMCLI:
    """コマンドラインインターフェース"""

    @staticmethod
    def setup_oauth():
        """OAuth設定ガイド"""
        print("""
📋 NotebookLM OAuth設定手順:

1. Google Cloud Consoleにアクセス
   https://console.cloud.google.com/

2. 新規プロジェクトを作成または既存プロジェクトを選択

3. APIとサービス → 認証情報 → 作成
   - OAuth 2.0 クライアントID を選択
   - アプリケーションタイプ: デスクトップ

4. 認証情報をダウンロード
   - JSONファイルをダウンロード
   - ~/.notebooklm/credentials.json として保存

5. このスクリプトを再実行
        """)

    @staticmethod
    def create_config():
        """設定ファイル作成"""
        config = {
            "notebook_id": "ce4eebd7-38da-4b35-8205-8b31f9125827",
            "auto_login": True,
            "headless": False,
            "sync_interval": 3600,
            "sources": {
                "auto_add": True,
                "watch_folders": [
                    "/Users/admin/Documents/AIUELAB/000-AIUELAB-Launch-Initiative/docs"
                ]
            }
        }

        config_path = Path.home() / '.notebooklm' / 'config.json'
        config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        print(f"✅ 設定ファイル作成: {config_path}")
        return config_path


def main():
    """メイン処理"""
    print("🚀 NotebookLM 自動化ツール")
    print("=" * 40)

    # 設定ファイルチェック
    if not CREDENTIALS_FILE.exists():
        NotebookLMCLI.setup_oauth()
        return

    # 自動化インスタンス作成
    automation = NotebookLMAutomation()

    try:
        # Google認証
        if not automation.setup_google_auth():
            print("認証に失敗しました")
            return

        # ブラウザ起動
        if not automation.start_browser_with_auth():
            print("ブラウザ起動に失敗しました")
            return

        # NotebookLMアクセス
        if not automation.access_notebook():
            print("NotebookLMアクセスに失敗しました")
            return

        print("\n✨ NotebookLM自動アクセス成功!")
        print("ブラウザを操作してください。終了するにはCtrl+Cを押してください。")

        # 対話モード
        while True:
            try:
                command = input("\nコマンド (chat/add/quit): ").strip()

                if command == "quit":
                    break
                elif command == "chat":
                    query = input("質問: ")
                    response = automation.chat_with_notebook(query)
                    if response:
                        print(f"回答: {response}")
                elif command == "add":
                    source_type = input("ソースタイプ (text/url): ")
                    source_data = input("ソースデータ: ")
                    automation.add_source(source_type, source_data)

            except KeyboardInterrupt:
                break

    finally:
        automation.cleanup()
        print("\n👋 終了しました")


if __name__ == "__main__":
    main()
