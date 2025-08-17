#!/usr/bin/env python3
"""
Playwright MCP サーバー動作確認スクリプト

このスクリプトはPlaywright MCPの導入が成功したかを確認します。
実際のMCP操作はClaude CodeなどのMCPクライアントから実行してください。
"""

import json
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def check_nodejs():
    """Node.jsのバージョンを確認"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        console.print(f"✅ Node.js {version} が見つかりました", style="green")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("❌ Node.jsが見つかりません", style="red")
        return False


def check_npm():
    """npmのバージョンを確認"""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, check=True)
        version = result.stdout.strip()
        console.print(f"✅ npm {version} が見つかりました", style="green")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        console.print("❌ npmが見つかりません", style="red")
        return False


def check_playwright_mcp():
    """Playwright MCPサーバーのインストール状態を確認"""
    try:
        # グローバルインストールの確認
        result = subprocess.run(
            ["npm", "list", "-g", "@playwright/mcp"], capture_output=True, text=True
        )
        if "@playwright/mcp" in result.stdout:
            console.print(
                "✅ Playwright MCPサーバーがグローバルにインストールされています", style="green"
            )
            return True

        # npxでの利用可能性を確認
        result = subprocess.run(
            ["npx", "@playwright/mcp@latest", "--help"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            console.print("✅ Playwright MCPサーバーがnpx経由で利用可能です", style="green")
            return True

        console.print("⚠️  Playwright MCPサーバーがインストールされていません", style="yellow")
        return False
    except Exception as e:
        console.print(f"⚠️  Playwright MCPサーバーの確認中にエラー: {e}", style="yellow")
        return False


def check_mcp_config():
    """MCP設定ファイルの存在を確認"""
    config_path = Path("mcp-config.json")
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = json.load(f)

            if "mcpServers" in config and "playwright" in config["mcpServers"]:
                console.print("✅ mcp-config.json にPlaywright設定が見つかりました", style="green")
                return True
            else:
                console.print("⚠️  mcp-config.json にPlaywright設定がありません", style="yellow")
                return False
        except json.JSONDecodeError:
            console.print("❌ mcp-config.json の解析に失敗しました", style="red")
            return False
    else:
        console.print("⚠️  mcp-config.json が見つかりません", style="yellow")
        return False


def check_playwright_browsers():
    """Playwrightブラウザのインストール状態を確認"""
    try:
        result = subprocess.run(
            ["npx", "playwright", "--version"], capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            console.print(f"✅ Playwright {result.stdout.strip()} が利用可能です", style="green")

            # ブラウザの確認
            browsers = ["chromium", "firefox", "webkit"]
            for browser in browsers:
                console.print(f"   - {browser.capitalize()} ブラウザ", style="cyan")
            return True
        else:
            console.print("⚠️  Playwrightブラウザが未インストールの可能性があります", style="yellow")
            return False
    except Exception as e:
        console.print(f"⚠️  Playwrightブラウザの確認中にエラー: {e}", style="yellow")
        return False


def display_mcp_tools():
    """利用可能なMCPツールを表示"""
    table = Table(title="利用可能なPlaywright MCPツール", show_header=True)
    table.add_column("カテゴリ", style="cyan", width=15)
    table.add_column("ツール数", style="green", width=10)
    table.add_column("主なツール", style="yellow")

    tools_categories = [
        ("コア自動化", 11, "navigate, click, type, snapshot"),
        ("ナビゲーション", 2, "back, forward"),
        ("スクリーンショット", 2, "screenshot, pdf"),
        ("タブ管理", 4, "new, list, select, close"),
        ("デバッグ", 2, "network, console"),
        ("その他", 4, "dialog, upload, resize, close"),
    ]

    for category, count, tools in tools_categories:
        table.add_row(category, str(count), tools)

    console.print(table)


def main():
    """メイン処理"""
    console.print(Panel.fit("🎭 Playwright MCP Server 動作確認", style="bold cyan"))
    console.print()

    checks = [
        ("Node.js", check_nodejs),
        ("npm", check_npm),
        ("Playwright MCP", check_playwright_mcp),
        ("MCP設定ファイル", check_mcp_config),
        ("Playwrightブラウザ", check_playwright_browsers),
    ]

    results = []
    for name, check_func in checks:
        console.print(f"\n📋 {name}の確認中...")
        results.append(check_func())

    console.print("\n" + "=" * 50 + "\n")

    # 結果サマリー
    passed = sum(results)
    total = len(results)

    if passed == total:
        console.print(
            Panel.fit(f"✅ すべてのチェックに合格しました ({passed}/{total})", style="bold green")
        )
        console.print("\n🎉 Playwright MCPサーバーを使用する準備が整いました！")

        # 利用可能なツールを表示
        console.print()
        display_mcp_tools()

        # 使用方法を表示
        console.print("\n📚 使用方法:")
        console.print("1. Claude DesktopやVS Codeの設定にmcp-config.jsonの内容を追加")
        console.print("2. MCPクライアントを再起動")
        console.print("3. 'browser_navigate でGoogleを開いて' などのコマンドを実行")

    elif passed > 0:
        console.print(
            Panel.fit(f"⚠️  一部のチェックに問題があります ({passed}/{total})", style="bold yellow")
        )
        console.print("\n💡 セットアップを完了するには:")
        console.print("bash scripts/setup-playwright-mcp.sh")
    else:
        console.print(Panel.fit(f"❌ セットアップが必要です ({passed}/{total})", style="bold red"))
        console.print("\n🔧 セットアップ手順:")
        console.print("1. Node.js 18以上をインストール")
        console.print("2. bash scripts/setup-playwright-mcp.sh を実行")

    console.print("\n📖 詳細はPLAYWRIGHT_MCP_README.mdを参照してください")


if __name__ == "__main__":
    main()
