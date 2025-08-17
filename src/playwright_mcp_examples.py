#!/usr/bin/env python3
"""
Playwright MCP サーバー活用例

このファイルはPlaywright MCPサーバーを使用した
ブラウザ自動化のサンプルコードを提供します。

注意: これらの例はClaude CodeなどのMCP対応クライアント
から実行されることを想定しています。
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, List

from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


@dataclass
class BrowserAction:
    """ブラウザアクションの定義"""

    action_type: str
    description: str
    mcp_tool: str
    parameters: Dict[str, Any]


class PlaywrightMCPExamples:
    """Playwright MCPの使用例を示すクラス"""

    def __init__(self):
        """初期化"""
        self.actions_log: List[BrowserAction] = []
        logger.info("Playwright MCP Examples initialized")

    def show_available_tools(self) -> None:
        """利用可能なPlaywright MCPツールを表示"""
        table = Table(title="Playwright MCP Tools", show_header=True)
        table.add_column("Tool Name", style="cyan", width=30)
        table.add_column("Description", style="green")
        table.add_column("Category", style="yellow")

        tools = [
            # Core automation
            ("browser_navigate", "URLへ移動", "Core"),
            ("browser_snapshot", "ページ構造を取得", "Core"),
            ("browser_click", "要素をクリック", "Core"),
            ("browser_type", "テキスト入力", "Core"),
            ("browser_press_key", "キー押下", "Core"),
            ("browser_select_option", "ドロップダウン選択", "Core"),
            ("browser_drag", "ドラッグ&ドロップ", "Core"),
            ("browser_hover", "ホバー", "Core"),
            ("browser_evaluate", "JavaScript実行", "Core"),
            ("browser_wait_for", "待機", "Core"),
            # Navigation
            ("browser_navigate_back", "前のページへ", "Navigation"),
            ("browser_navigate_forward", "次のページへ", "Navigation"),
            # Screenshot & Recording
            ("browser_take_screenshot", "スクリーンショット", "Screenshot"),
            ("browser_pdf_save", "PDF保存", "PDF"),
            # Tab management
            ("browser_tab_list", "タブ一覧", "Tab"),
            ("browser_tab_new", "新規タブ", "Tab"),
            ("browser_tab_select", "タブ選択", "Tab"),
            ("browser_tab_close", "タブを閉じる", "Tab"),
            # Network & Console
            ("browser_network_requests", "ネットワークリクエスト", "Debug"),
            ("browser_console_messages", "コンソールメッセージ", "Debug"),
            # Dialog handling
            ("browser_handle_dialog", "ダイアログ処理", "Dialog"),
            # File upload
            ("browser_file_upload", "ファイルアップロード", "File"),
            # Browser control
            ("browser_resize", "ウィンドウサイズ変更", "Browser"),
            ("browser_close", "ブラウザを閉じる", "Browser"),
        ]

        for tool_name, description, category in tools:
            table.add_row(tool_name, description, category)

        console.print(table)

    def example_basic_navigation(self) -> Dict[str, Any]:
        """基本的なナビゲーションの例"""
        console.print(Panel.fit("🌐 基本的なナビゲーションの例", style="bold blue"))

        actions = [
            BrowserAction(
                action_type="navigate",
                description="Googleへ移動",
                mcp_tool="browser_navigate",
                parameters={"url": "https://www.google.com"},
            ),
            BrowserAction(
                action_type="snapshot",
                description="ページ構造を取得",
                mcp_tool="browser_snapshot",
                parameters={},
            ),
            BrowserAction(
                action_type="screenshot",
                description="スクリーンショット取得",
                mcp_tool="browser_take_screenshot",
                parameters={"filename": "google-homepage.png"},
            ),
        ]

        self._display_actions(actions)
        return {"example": "basic_navigation", "actions": len(actions)}

    def example_form_interaction(self) -> Dict[str, Any]:
        """フォーム操作の例"""
        console.print(Panel.fit("📝 フォーム操作の例", style="bold green"))

        actions = [
            BrowserAction(
                action_type="navigate",
                description="フォームページへ移動",
                mcp_tool="browser_navigate",
                parameters={"url": "https://example.com/form"},
            ),
            BrowserAction(
                action_type="type",
                description="名前フィールドに入力",
                mcp_tool="browser_type",
                parameters={"element": "Name input field", "ref": "#name", "text": "John Doe"},
            ),
            BrowserAction(
                action_type="type",
                description="メールフィールドに入力",
                mcp_tool="browser_type",
                parameters={
                    "element": "Email input field",
                    "ref": "#email",
                    "text": "john@example.com",
                },
            ),
            BrowserAction(
                action_type="select",
                description="国を選択",
                mcp_tool="browser_select_option",
                parameters={"element": "Country dropdown", "ref": "#country", "values": ["Japan"]},
            ),
            BrowserAction(
                action_type="click",
                description="送信ボタンをクリック",
                mcp_tool="browser_click",
                parameters={"element": "Submit button", "ref": "#submit"},
            ),
            BrowserAction(
                action_type="wait",
                description="3秒待機",
                mcp_tool="browser_wait_for",
                parameters={"time": 3},
            ),
        ]

        self._display_actions(actions)
        return {"example": "form_interaction", "actions": len(actions)}

    def example_web_scraping(self) -> Dict[str, Any]:
        """Webスクレイピングの例"""
        console.print(Panel.fit("🔍 Webスクレイピングの例", style="bold yellow"))

        actions = [
            BrowserAction(
                action_type="navigate",
                description="ニュースサイトへ移動",
                mcp_tool="browser_navigate",
                parameters={"url": "https://news.ycombinator.com"},
            ),
            BrowserAction(
                action_type="snapshot",
                description="ページ構造を取得",
                mcp_tool="browser_snapshot",
                parameters={},
            ),
            BrowserAction(
                action_type="evaluate",
                description="記事タイトルを抽出",
                mcp_tool="browser_evaluate",
                parameters={
                    "function": """() => {
                        const titles = document.querySelectorAll('.titleline > a');
                        return Array.from(titles).map(t => ({
                            title: t.textContent,
                            url: t.href
                        })).slice(0, 10);
                    }"""
                },
            ),
            BrowserAction(
                action_type="screenshot",
                description="ページ全体のスクリーンショット",
                mcp_tool="browser_take_screenshot",
                parameters={"filename": "news-page.png", "fullPage": True},
            ),
        ]

        self._display_actions(actions)
        return {"example": "web_scraping", "actions": len(actions)}

    def example_multi_tab_operation(self) -> Dict[str, Any]:
        """マルチタブ操作の例"""
        console.print(Panel.fit("🗂️ マルチタブ操作の例", style="bold magenta"))

        actions = [
            BrowserAction(
                action_type="navigate",
                description="最初のページを開く",
                mcp_tool="browser_navigate",
                parameters={"url": "https://www.google.com"},
            ),
            BrowserAction(
                action_type="new_tab",
                description="新しいタブを開く",
                mcp_tool="browser_tab_new",
                parameters={"url": "https://www.github.com"},
            ),
            BrowserAction(
                action_type="list_tabs",
                description="タブ一覧を取得",
                mcp_tool="browser_tab_list",
                parameters={},
            ),
            BrowserAction(
                action_type="select_tab",
                description="最初のタブに切り替え",
                mcp_tool="browser_tab_select",
                parameters={"index": 0},
            ),
            BrowserAction(
                action_type="type",
                description="検索ボックスに入力",
                mcp_tool="browser_type",
                parameters={
                    "element": "Search box",
                    "ref": "input[name='q']",
                    "text": "Playwright MCP",
                },
            ),
            BrowserAction(
                action_type="close_tab",
                description="2番目のタブを閉じる",
                mcp_tool="browser_tab_close",
                parameters={"index": 1},
            ),
        ]

        self._display_actions(actions)
        return {"example": "multi_tab", "actions": len(actions)}

    def example_advanced_interaction(self) -> Dict[str, Any]:
        """高度なインタラクションの例"""
        console.print(Panel.fit("⚡ 高度なインタラクションの例", style="bold red"))

        actions = [
            BrowserAction(
                action_type="navigate",
                description="インタラクティブなページへ",
                mcp_tool="browser_navigate",
                parameters={"url": "https://example.com/interactive"},
            ),
            BrowserAction(
                action_type="hover",
                description="メニューにホバー",
                mcp_tool="browser_hover",
                parameters={"element": "Dropdown menu", "ref": "#menu"},
            ),
            BrowserAction(
                action_type="wait",
                description="メニューが表示されるまで待機",
                mcp_tool="browser_wait_for",
                parameters={"text": "Menu Item"},
            ),
            BrowserAction(
                action_type="drag",
                description="要素をドラッグ&ドロップ",
                mcp_tool="browser_drag",
                parameters={
                    "startElement": "Draggable item",
                    "startRef": "#drag-source",
                    "endElement": "Drop target",
                    "endRef": "#drop-target",
                },
            ),
            BrowserAction(
                action_type="dialog",
                description="確認ダイアログを承認",
                mcp_tool="browser_handle_dialog",
                parameters={"accept": True, "promptText": "Confirmed"},
            ),
            BrowserAction(
                action_type="network",
                description="ネットワークリクエストを確認",
                mcp_tool="browser_network_requests",
                parameters={},
            ),
            BrowserAction(
                action_type="console",
                description="コンソールメッセージを取得",
                mcp_tool="browser_console_messages",
                parameters={},
            ),
        ]

        self._display_actions(actions)
        return {"example": "advanced_interaction", "actions": len(actions)}

    def _display_actions(self, actions: List[BrowserAction]) -> None:
        """アクションリストを表示"""
        for i, action in enumerate(actions, 1):
            console.print(f"\n{i}. [cyan]{action.description}[/cyan]")
            console.print(f"   Tool: [yellow]{action.mcp_tool}[/yellow]")
            if action.parameters:
                console.print(f"   Parameters: {json.dumps(action.parameters, indent=2)}")

            self.actions_log.append(action)

    def show_usage_instructions(self) -> None:
        """使用方法を表示"""
        instructions = """
        🚀 Playwright MCP サーバーの使用方法:

        1. セットアップ:
           bash scripts/setup-playwright-mcp.sh

        2. MCPクライアント（Claude Desktop等）で設定:
           mcp-config.json の内容を設定に追加

        3. 基本的な使い方:
           - "browser_navigate でGoogleを開いて"
           - "browser_snapshot でページ構造を見せて"
           - "browser_click で検索ボタンをクリック"
           - "browser_type で検索ボックスにテキストを入力"

        4. 高度な機能:
           - JavaScript実行: browser_evaluate
           - マルチタブ操作: browser_tab_*
           - ファイルアップロード: browser_file_upload
           - PDF生成: browser_pdf_save（要 --caps=pdf）

        5. デバッグ:
           - ネットワーク監視: browser_network_requests
           - コンソール監視: browser_console_messages
        """

        console.print(Panel(instructions, title="📚 使用方法", style="blue"))


def main():
    """メイン関数"""
    examples = PlaywrightMCPExamples()

    console.print(Panel.fit("🎭 Playwright MCP Server Examples", style="bold cyan"))

    # 利用可能なツールを表示
    examples.show_available_tools()
    console.print()

    # 各種例を実行
    examples.example_basic_navigation()
    console.print()

    examples.example_form_interaction()
    console.print()

    examples.example_web_scraping()
    console.print()

    examples.example_multi_tab_operation()
    console.print()

    examples.example_advanced_interaction()
    console.print()

    # 使用方法を表示
    examples.show_usage_instructions()

    # サマリー表示
    console.print(
        Panel.fit(
            f"✅ 合計 {len(examples.actions_log)} アクションの例を表示しました", style="green"
        )
    )


if __name__ == "__main__":
    main()
