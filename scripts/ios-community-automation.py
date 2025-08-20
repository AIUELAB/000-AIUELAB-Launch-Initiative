#!/usr/bin/env python3
"""
iOS コミュニティイベント自動化スクリプト
iOS Discord Tokyo, Love Swift などのイベント情報を自動収集
"""

import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
from pathlib import Path
import schedule
import time

# Connpass API設定
CONNPASS_API_URL = "https://connpass.com/api/v1/event/"

# コミュニティ設定
COMMUNITIES = {
    "ios_discord": {
        "name": "iOS Discord Tokyo",
        "series_id": "14027",  # iOS Discord Tokyoのシリーズ ID
        "url": "https://iosdiscord.connpass.com/",
        "keywords": ["iOS", "Swift", "SwiftUI", "Discord"],
        "twitter": "@ios_discord_jp"
    },
    "love_swift": {
        "name": "Love Swift",
        "series_id": "12345",  # Love SwiftのシリーズID（要確認）
        "url": "https://love-swift.connpass.com/",
        "keywords": ["Swift", "iOS", "macOS", "watchOS", "tvOS"],
        "twitter": "@love_swift"
    },
    "try_swift": {
        "name": "try! Swift Tokyo",
        "keywords": ["try!", "Swift", "Conference"],
        "twitter": "@tryswiftconf"
    },
    "ios_dc": {
        "name": "iOSDC Japan",
        "keywords": ["iOSDC", "iOS", "Conference"],
        "twitter": "@iosdc_jp"
    }
}


class ConnpassEventFetcher:
    """Connpass イベント取得クラス"""

    def __init__(self):
        self.session = requests.Session()
        self.events_cache = []

    def fetch_events(self, keyword: str = None, series_id: str = None,
                     ym: str = None, ymd: str = None) -> List[Dict[str, Any]]:
        """イベント情報を取得"""
        params = {
            "order": 2,  # 更新日時順
            "count": 100
        }

        if keyword:
            params["keyword"] = keyword
        if series_id:
            params["series_id"] = series_id
        if ym:
            params["ym"] = ym  # YYYYMM形式
        if ymd:
            params["ymd"] = ymd  # YYYYMMDD形式

        try:
            response = self.session.get(CONNPASS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            return data.get("events", [])
        except Exception as e:
            print(f"❌ イベント取得エラー: {e}")
            return []

    def fetch_community_events(self, community_key: str) -> List[Dict[str, Any]]:
        """特定コミュニティのイベントを取得"""
        community = COMMUNITIES.get(community_key)
        if not community:
            return []

        events = []

        # シリーズIDで検索
        if "series_id" in community:
            events.extend(self.fetch_events(series_id=community["series_id"]))

        # キーワードで検索
        for keyword in community.get("keywords", []):
            keyword_events = self.fetch_events(keyword=keyword)
            # 重複を除去
            for event in keyword_events:
                if not any(e["event_id"] == event["event_id"] for e in events):
                    events.append(event)

        return events

    def fetch_upcoming_events(self) -> List[Dict[str, Any]]:
        """今後のイベントをすべて取得"""
        all_events = []

        # 各コミュニティのイベントを取得
        for community_key in COMMUNITIES.keys():
            events = self.fetch_community_events(community_key)
            for event in events:
                event["community"] = COMMUNITIES[community_key]["name"]
            all_events.extend(events)

        # 日付でソート
        all_events.sort(key=lambda x: x.get("started_at", ""))

        # 今後のイベントのみフィルタ
        now = datetime.now()
        upcoming = [
            e for e in all_events
            if datetime.fromisoformat(e["started_at"].replace("T", " ").replace("+09:00", "")) > now
        ]

        return upcoming


class EventNotifier:
    """イベント通知クラス"""

    def __init__(self):
        self.notified_events = self.load_notified_events()

    def load_notified_events(self) -> set:
        """通知済みイベントIDを読み込み"""
        cache_file = Path.home() / ".aiuelab" / "notified_events.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                return set(json.load(f))
        return set()

    def save_notified_events(self):
        """通知済みイベントIDを保存"""
        cache_file = Path.home() / ".aiuelab" / "notified_events.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, "w") as f:
            json.dump(list(self.notified_events), f)

    def format_event_message(self, event: Dict[str, Any]) -> str:
        """イベント情報をフォーマット"""
        start_time = datetime.fromisoformat(
            event["started_at"].replace("T", " ").replace("+09:00", "")
        )

        message = f"""
🎉 iOS イベント情報

**{event['title']}**
📅 {start_time.strftime('%Y年%m月%d日 %H:%M')}
📍 {event.get('address', 'オンライン') or 'オンライン'}
👥 {event.get('accepted', 0)}/{event.get('limit', '∞')} 人
🏢 {event.get('community', 'iOS Community')}

{event.get('catch', '')}

🔗 詳細・申込: {event['event_url']}
"""
        return message

    def notify_slack(self, event: Dict[str, Any]):
        """Slackに通知"""
        webhook_url = os.getenv("SLACK_WEBHOOK_URL")
        if not webhook_url:
            return

        message = self.format_event_message(event)

        payload = {
            "text": "新しいiOSイベントが公開されました！",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": message
                    }
                }
            ]
        }

        try:
            requests.post(webhook_url, json=payload)
            print(f"✅ Slack通知送信: {event['title']}")
        except Exception as e:
            print(f"❌ Slack通知エラー: {e}")

    def notify_twitter(self, event: Dict[str, Any]):
        """Twitterに投稿"""
        # Twitter APIを使用（別途設定必要）
        start_time = datetime.fromisoformat(
            event["started_at"].replace("T", " ").replace("+09:00", "")
        )

        tweet = f"""
🎉 iOS イベント情報

{event['title']}
📅 {start_time.strftime('%m/%d %H:%M')}
📍 {event.get('place', 'オンライン')[:20]}

詳細👇
{event['event_url']}

#iOS #Swift #iOSDev #東京
"""
        print(f"📱 Twitter投稿予定:\n{tweet}")

    def check_and_notify(self, events: List[Dict[str, Any]]):
        """新しいイベントをチェックして通知"""
        for event in events:
            event_id = str(event["event_id"])

            if event_id not in self.notified_events:
                print(f"🆕 新しいイベント: {event['title']}")

                # 各プラットフォームに通知
                self.notify_slack(event)
                self.notify_twitter(event)

                # 通知済みリストに追加
                self.notified_events.add(event_id)

        self.save_notified_events()


class EventCalendarGenerator:
    """イベントカレンダー生成クラス"""

    @staticmethod
    def generate_markdown_calendar(events: List[Dict[str, Any]]) -> str:
        """Markdownカレンダーを生成"""
        if not events:
            return "現在、予定されているイベントはありません。"

        markdown = """# 📅 iOS コミュニティイベントカレンダー

## 今後のイベント

| 日時 | イベント | 場所 | 参加者 | 申込 |
|------|----------|------|--------|------|
"""

        for event in events[:20]:  # 最大20件
            start_time = datetime.fromisoformat(
                event["started_at"].replace("T", " ").replace("+09:00", "")
            )

            date_str = start_time.strftime("%m/%d %H:%M")
            title = f"[{event['title'][:30]}]({event['event_url']})"
            place = event.get("place", "オンライン")[:20]
            participants = f"{event.get('accepted', 0)}/{event.get('limit', '∞')}"
            status = "🔵 受付中" if event.get("limit", 0) > event.get("accepted", 0) else "🔴 満席"

            markdown += f"| {date_str} | {title} | {place} | {participants} | {status} |\n"

        markdown += f"\n\n*最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}*"

        return markdown

    @staticmethod
    def save_calendar(events: List[Dict[str, Any]]):
        """カレンダーを保存"""
        calendar_path = Path("docs/ios-events-calendar.md")
        calendar_path.parent.mkdir(parents=True, exist_ok=True)

        markdown = EventCalendarGenerator.generate_markdown_calendar(events)

        with open(calendar_path, "w") as f:
            f.write(markdown)

        print(f"✅ イベントカレンダー更新: {calendar_path}")


class EventRecommender:
    """イベントレコメンドシステム"""

    @staticmethod
    def analyze_event_relevance(event: Dict[str, Any]) -> Dict[str, Any]:
        """イベントの関連性を分析"""
        score = 0
        reasons = []

        # キーワードマッチング
        important_keywords = ["SwiftUI", "iOS 17", "iOS 18", "Xcode", "App Store",
                             "Vision Pro", "visionOS", "AI", "Machine Learning"]

        title_and_catch = f"{event.get('title', '')} {event.get('catch', '')}".lower()

        for keyword in important_keywords:
            if keyword.lower() in title_and_catch:
                score += 10
                reasons.append(f"'{keyword}' に関連")

        # 参加者数
        if event.get("limit", 0) > 100:
            score += 5
            reasons.append("大規模イベント")

        # オンライン開催
        if "オンライン" in event.get("place", "") or "online" in title_and_catch:
            score += 3
            reasons.append("オンライン参加可能")

        return {
            "event_id": event["event_id"],
            "title": event["title"],
            "score": score,
            "reasons": reasons,
            "recommended": score >= 10
        }

    @staticmethod
    def get_recommendations(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """おすすめイベントを取得"""
        recommendations = []

        for event in events:
            analysis = EventRecommender.analyze_event_relevance(event)
            if analysis["recommended"]:
                recommendations.append({
                    **event,
                    "recommendation": analysis
                })

        # スコアでソート
        recommendations.sort(key=lambda x: x["recommendation"]["score"], reverse=True)

        return recommendations


def main():
    """メイン処理"""
    print("🎯 iOS コミュニティイベント自動化")
    print("=" * 40)

    fetcher = ConnpassEventFetcher()
    notifier = EventNotifier()

    while True:
        print("\n選択してください:")
        print("1. 今後のイベントを表示")
        print("2. 新着イベントをチェック")
        print("3. イベントカレンダー生成")
        print("4. おすすめイベント")
        print("5. 自動監視開始")
        print("6. 終了")

        choice = input("\n選択 (1-6): ").strip()

        if choice == "1":
            events = fetcher.fetch_upcoming_events()
            print(f"\n📅 今後のイベント ({len(events)}件)")
            for event in events[:10]:
                print(f"• {event['title']}")
                print(f"  {event['started_at']} @ {event.get('place', 'オンライン')}")
                print(f"  {event['event_url']}\n")

        elif choice == "2":
            events = fetcher.fetch_upcoming_events()
            notifier.check_and_notify(events)
            print("✅ 新着チェック完了")

        elif choice == "3":
            events = fetcher.fetch_upcoming_events()
            EventCalendarGenerator.save_calendar(events)

        elif choice == "4":
            events = fetcher.fetch_upcoming_events()
            recommendations = EventRecommender.get_recommendations(events)
            print(f"\n⭐ おすすめイベント ({len(recommendations)}件)")
            for event in recommendations[:5]:
                print(f"• {event['title']} (スコア: {event['recommendation']['score']})")
                print(f"  理由: {', '.join(event['recommendation']['reasons'])}")
                print(f"  {event['event_url']}\n")

        elif choice == "5":
            print("🔄 自動監視を開始します（1時間ごと）")

            def job():
                events = fetcher.fetch_upcoming_events()
                notifier.check_and_notify(events)
                EventCalendarGenerator.save_calendar(events)

            # 1時間ごとに実行
            schedule.every().hour.do(job)

            # 初回実行
            job()

            print("監視中... (Ctrl+C で終了)")
            while True:
                schedule.run_pending()
                time.sleep(60)

        elif choice == "6":
            break

    print("\n👋 終了しました")


if __name__ == "__main__":
    main()
