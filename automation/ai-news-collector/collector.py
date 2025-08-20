"""
🤖 AI/MCP最新情報自動収集システム
常に最新のAI技術とMCP関連情報を収集し、有益な情報をユーザーに提示
"""

import json
import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from pathlib import Path
import feedparser
import re
from typing import List, Dict, Any
import hashlib

class AINewsCollector:
    """AI/MCP関連ニュースの自動収集クラス"""

    def __init__(self, config_path="config.json"):
        """初期化"""
        self.config = self.load_config(config_path)
        self.collected_news = []
        self.seen_urls = self.load_seen_urls()
        self.output_dir = Path("collected_data")
        self.output_dir.mkdir(exist_ok=True)

    def load_config(self, config_path):
        """設定ファイルを読み込む"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_seen_urls(self):
        """既に収集済みのURLを読み込む"""
        seen_file = self.output_dir / "seen_urls.json"
        if seen_file.exists():
            with open(seen_file, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        return set()

    def save_seen_urls(self):
        """収集済みURLを保存"""
        seen_file = self.output_dir / "seen_urls.json"
        with open(seen_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.seen_urls), f)

    async def fetch_rss_feed(self, url: str) -> List[Dict]:
        """RSSフィードから記事を取得"""
        try:
            feed = feedparser.parse(url)
            articles = []

            for entry in feed.entries[:10]:  # 最新10件
                if entry.link not in self.seen_urls:
                    article = {
                        "title": entry.get("title", ""),
                        "url": entry.get("link", ""),
                        "summary": entry.get("summary", ""),
                        "published": entry.get("published", ""),
                        "source": feed.feed.get("title", "Unknown"),
                        "collected_at": datetime.now().isoformat()
                    }
                    articles.append(article)

            return articles
        except Exception as e:
            print(f"❌ RSS取得エラー ({url}): {e}")
            return []

    async def fetch_web_content(self, session: aiohttp.ClientSession, url: str) -> str:
        """Webページの内容を取得"""
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.text()
        except Exception as e:
            print(f"❌ Web取得エラー ({url}): {e}")
        return ""

    def calculate_relevance_score(self, article: Dict) -> float:
        """記事の関連性スコアを計算"""
        score = 0.0
        text = f"{article.get('title', '')} {article.get('summary', '')}".lower()

        # 重要キーワードをチェック
        importance_keywords = self.config["filters"]["importance_keywords"]
        for keyword in importance_keywords:
            if keyword.lower() in text:
                score += 0.2

        # AI/MCP関連キーワード
        ai_keywords = ["ai", "gpt", "claude", "llm", "mcp", "model context protocol",
                       "machine learning", "深層学習", "人工知能", "生成ai"]
        for keyword in ai_keywords:
            if keyword in text:
                score += 0.15

        # 除外キーワードがある場合はスコアを下げる
        exclude_keywords = self.config["filters"]["exclude_keywords"]
        for keyword in exclude_keywords:
            if keyword.lower() in text:
                score -= 0.3

        # 最新性によるボーナス
        if "published" in article:
            try:
                pub_date = datetime.fromisoformat(article["published"])
                days_old = (datetime.now() - pub_date).days
                if days_old <= 1:
                    score += 0.3
                elif days_old <= 3:
                    score += 0.2
                elif days_old <= 7:
                    score += 0.1
            except:
                pass

        return min(1.0, max(0.0, score))

    def categorize_priority(self, score: float) -> str:
        """スコアに基づいて優先度を決定"""
        if score >= 0.9:
            return "critical"
        elif score >= 0.7:
            return "high"
        elif score >= 0.5:
            return "medium"
        else:
            return "low"

    async def collect_from_all_sources(self):
        """全ソースから情報を収集"""
        print("🔍 AI/MCP最新情報を収集中...")

        all_articles = []

        # AI ニュースソース
        for source in self.config["sources"]["ai_news"]:
            if source["type"] == "blog" and source["url"].endswith("feed"):
                articles = await self.fetch_rss_feed(source["url"])
                all_articles.extend(articles)

        # MCP関連ソース
        async with aiohttp.ClientSession() as session:
            for source in self.config["sources"]["mcp_sources"]:
                if source["type"] == "github":
                    # GitHub APIを使って最新リリースを確認
                    api_url = "https://api.github.com/repos/modelcontextprotocol/servers/releases/latest"
                    content = await self.fetch_web_content(session, api_url)
                    if content:
                        try:
                            release = json.loads(content)
                            if release["html_url"] not in self.seen_urls:
                                article = {
                                    "title": f"MCP: {release['name']}",
                                    "url": release["html_url"],
                                    "summary": release.get("body", "")[:500],
                                    "published": release["published_at"],
                                    "source": "GitHub - MCP",
                                    "collected_at": datetime.now().isoformat()
                                }
                                all_articles.append(article)
                        except:
                            pass

        # 関連性スコアを計算して優先度を設定
        for article in all_articles:
            article["relevance_score"] = self.calculate_relevance_score(article)
            article["priority"] = self.categorize_priority(article["relevance_score"])

            # 閾値以上のスコアのみ保存
            if article["relevance_score"] >= self.config["filters"]["min_relevance_score"]:
                self.collected_news.append(article)
                self.seen_urls.add(article["url"])

        # スコアでソート
        self.collected_news.sort(key=lambda x: x["relevance_score"], reverse=True)

        return self.collected_news

    def format_for_display(self, articles: List[Dict], max_items: int = 5) -> str:
        """表示用にフォーマット"""
        if not articles:
            return "📭 新しい情報はありません"

        output = ["🎯 **AI/MCP 最新情報**\n"]
        output.append(f"_収集日時: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")

        # 優先度別に分類
        critical = [a for a in articles if a["priority"] == "critical"]
        high = [a for a in articles if a["priority"] == "high"]
        medium = [a for a in articles if a["priority"] == "medium"]

        if critical:
            output.append("\n🚨 **重要なアップデート**")
            for article in critical[:3]:
                output.append(f"• [{article['title']}]({article['url']})")
                if article.get('summary'):
                    summary = article['summary'][:100] + "..."
                    output.append(f"  _{summary}_")

        if high:
            output.append("\n📢 **注目ニュース**")
            for article in high[:max_items]:
                output.append(f"• [{article['title']}]({article['url']})")

        if medium and len(output) < 15:
            output.append("\n📰 **その他の情報**")
            for article in medium[:3]:
                output.append(f"• {article['title']}")

        # 統計情報
        output.append(f"\n📊 _本日の収集: {len(articles)}件_")

        return "\n".join(output)

    def save_daily_digest(self, articles: List[Dict]):
        """日次ダイジェストを保存"""
        date_str = datetime.now().strftime("%Y%m%d")
        digest_file = self.output_dir / f"digest_{date_str}.json"

        digest = {
            "date": datetime.now().isoformat(),
            "total_articles": len(articles),
            "critical": len([a for a in articles if a["priority"] == "critical"]),
            "high": len([a for a in articles if a["priority"] == "high"]),
            "articles": articles
        }

        with open(digest_file, 'w', encoding='utf-8') as f:
            json.dump(digest, f, ensure_ascii=False, indent=2)

        # Markdown形式でも保存
        md_file = self.output_dir / f"digest_{date_str}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(self.format_for_display(articles, max_items=10))

        print(f"💾 ダイジェスト保存: {digest_file}")
        return digest_file

    async def run_collection_cycle(self):
        """収集サイクルを実行"""
        # 情報収集
        articles = await self.collect_from_all_sources()

        if articles:
            # 表示
            print("\n" + "="*60)
            print(self.format_for_display(articles))
            print("="*60 + "\n")

            # 保存
            self.save_daily_digest(articles)
            self.save_seen_urls()

            # 重要な情報があれば通知
            critical = [a for a in articles if a["priority"] == "critical"]
            if critical:
                await self.send_notification(critical[0])

        return articles

    async def send_notification(self, article: Dict):
        """重要な情報を通知"""
        print(f"\n🔔 **重要な更新を検出！**")
        print(f"📌 {article['title']}")
        print(f"🔗 {article['url']}")
        print(f"📝 {article.get('summary', '')[:200]}")

        # n8n webhookに送信（設定されている場合）
        if self.config["notification"]["channels"]["n8n_webhook"]:
            # ここにn8n webhook送信ロジックを追加
            pass

# ========================================
# 定期実行用スクリプト
# ========================================
async def main():
    """メイン処理"""
    collector = AINewsCollector("config.json")

    print("🤖 AI/MCP情報収集システム起動")
    print("="*60)

    while True:
        try:
            # 収集実行
            await collector.run_collection_cycle()

            # 次回実行まで待機（30分）
            print(f"⏰ 次回収集: {(datetime.now() + timedelta(minutes=30)).strftime('%H:%M')}")
            await asyncio.sleep(1800)  # 30分

        except KeyboardInterrupt:
            print("\n👋 収集を終了します")
            break
        except Exception as e:
            print(f"❌ エラー: {e}")
            await asyncio.sleep(60)  # エラー時は1分後に再試行

if __name__ == "__main__":
    asyncio.run(main())
