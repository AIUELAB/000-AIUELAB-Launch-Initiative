#!/usr/bin/env python3
"""
X (Twitter) 自動化スクリプト
Twitter API v2 対応
"""

import os
import json
import tweepy
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import schedule
import time
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv('.env.twitter')


class TwitterAutomation:
    """Twitter/X 自動化クラス"""

    def __init__(self):
        """初期化"""
        self.api = None
        self.client = None
        self.setup_api()

    def setup_api(self):
        """Twitter API セットアップ"""
        try:
            # API v2 クライアント
            self.client = tweepy.Client(
                bearer_token=os.getenv('TWITTER_BEARER_TOKEN'),
                consumer_key=os.getenv('TWITTER_API_KEY'),
                consumer_secret=os.getenv('TWITTER_API_SECRET'),
                access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
                access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET'),
                wait_on_rate_limit=True
            )

            # API v1.1 (メディアアップロード用)
            auth = tweepy.OAuthHandler(
                os.getenv('TWITTER_API_KEY'),
                os.getenv('TWITTER_API_SECRET')
            )
            auth.set_access_token(
                os.getenv('TWITTER_ACCESS_TOKEN'),
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
            self.api = tweepy.API(auth)

            print("✅ Twitter API 接続成功")

        except Exception as e:
            print(f"❌ API接続エラー: {e}")
            raise

    def post_tweet(self, text: str, media_paths: Optional[List[str]] = None) -> bool:
        """ツイート投稿"""
        try:
            media_ids = []

            # メディアアップロード
            if media_paths:
                for path in media_paths:
                    if os.path.exists(path):
                        media = self.api.media_upload(path)
                        media_ids.append(media.media_id)

            # ツイート投稿
            if media_ids:
                response = self.client.create_tweet(
                    text=text,
                    media_ids=media_ids
                )
            else:
                response = self.client.create_tweet(text=text)

            tweet_id = response.data['id']
            print(f"✅ ツイート投稿成功: https://x.com/AIUELAB/status/{tweet_id}")
            return True

        except Exception as e:
            print(f"❌ ツイート投稿エラー: {e}")
            return False

    def schedule_tweet(self, text: str, scheduled_time: datetime) -> bool:
        """ツイートをスケジュール"""
        try:
            # Twitter APIはネイティブスケジュール機能がないため、
            # scheduleライブラリで実装
            def job():
                self.post_tweet(text)

            schedule.every().day.at(scheduled_time.strftime("%H:%M")).do(job)
            print(f"✅ ツイートスケジュール設定: {scheduled_time}")
            return True

        except Exception as e:
            print(f"❌ スケジュール設定エラー: {e}")
            return False

    def get_timeline(self, count: int = 10) -> List[Dict[str, Any]]:
        """タイムライン取得"""
        try:
            tweets = self.client.get_users_tweets(
                id=self.get_user_id(),
                max_results=min(count, 100),
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )

            timeline = []
            if tweets.data:
                for tweet in tweets.data:
                    timeline.append({
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'metrics': tweet.public_metrics
                    })

            return timeline

        except Exception as e:
            print(f"❌ タイムライン取得エラー: {e}")
            return []

    def get_user_id(self) -> Optional[str]:
        """ユーザーID取得"""
        try:
            user = self.client.get_user(username='AIUELAB')
            return user.data.id if user.data else None
        except Exception as e:
            print(f"❌ ユーザーID取得エラー: {e}")
            return None

    def analyze_engagement(self) -> Dict[str, Any]:
        """エンゲージメント分析"""
        try:
            tweets = self.get_timeline(100)

            if not tweets:
                return {}

            total_likes = sum(t['metrics']['like_count'] for t in tweets)
            total_retweets = sum(t['metrics']['retweet_count'] for t in tweets)
            total_replies = sum(t['metrics']['reply_count'] for t in tweets)

            analysis = {
                'total_tweets': len(tweets),
                'total_likes': total_likes,
                'total_retweets': total_retweets,
                'total_replies': total_replies,
                'avg_likes': total_likes / len(tweets),
                'avg_retweets': total_retweets / len(tweets),
                'avg_replies': total_replies / len(tweets)
            }

            return analysis

        except Exception as e:
            print(f"❌ エンゲージメント分析エラー: {e}")
            return {}

    def auto_reply(self, keywords: List[str], reply_template: str):
        """自動返信"""
        try:
            # メンション取得
            mentions = self.client.get_users_mentions(
                id=self.get_user_id(),
                max_results=10
            )

            if mentions.data:
                for mention in mentions.data:
                    # キーワードチェック
                    if any(keyword in mention.text.lower() for keyword in keywords):
                        # 返信
                        self.client.create_tweet(
                            text=reply_template,
                            in_reply_to_tweet_id=mention.id
                        )
                        print(f"✅ 自動返信: {mention.id}")

        except Exception as e:
            print(f"❌ 自動返信エラー: {e}")


class TwitterContentGenerator:
    """コンテンツ生成クラス"""

    @staticmethod
    def generate_ios_app_announcement(app_name: str, features: List[str]) -> str:
        """iOSアプリ告知ツイート生成"""
        tweet = f"🚀 新アプリ『{app_name}』リリース！\n\n"
        tweet += "✨ 主な機能:\n"
        for feature in features[:3]:  # 最大3つまで
            tweet += f"• {feature}\n"
        tweet += "\n📱 App Storeで公開中\n"
        tweet += "#iOS #AppStore #AIUELAB"
        return tweet

    @staticmethod
    def generate_blog_share(title: str, url: str, summary: str) -> str:
        """ブログ記事シェアツイート生成"""
        tweet = f"📝 ブログ更新\n\n"
        tweet += f"『{title}』\n\n"
        tweet += f"{summary[:100]}...\n\n"
        tweet += f"続きはこちら👇\n{url}\n\n"
        tweet += "#AIUELAB #Tech #AI"
        return tweet

    @staticmethod
    def generate_daily_update() -> str:
        """日次アップデートツイート生成"""
        now = datetime.now()
        tweet = f"🌅 {now.strftime('%m月%d日')}のAIUELAB\n\n"
        tweet += "今日も開発進行中！\n"
        tweet += "• 新機能実装 🛠\n"
        tweet += "• バグ修正 🐛\n"
        tweet += "• パフォーマンス改善 ⚡\n\n"
        tweet += "詳細は後日公開予定です。\n"
        tweet += "#開発日記 #個人開発"
        return tweet


def main():
    """メイン処理"""
    print("🐦 Twitter/X 自動化ツール")
    print("=" * 40)

    # 自動化インスタンス作成
    twitter = TwitterAutomation()
    generator = TwitterContentGenerator()

    while True:
        print("\n選択してください:")
        print("1. ツイート投稿")
        print("2. スケジュール投稿")
        print("3. エンゲージメント分析")
        print("4. iOSアプリ告知")
        print("5. 終了")

        choice = input("\n選択 (1-5): ").strip()

        if choice == "1":
            text = input("ツイート内容: ")
            twitter.post_tweet(text)

        elif choice == "2":
            text = input("ツイート内容: ")
            time_str = input("投稿時刻 (HH:MM): ")
            scheduled_time = datetime.strptime(time_str, "%H:%M")
            twitter.schedule_tweet(text, scheduled_time)

        elif choice == "3":
            analysis = twitter.analyze_engagement()
            print("\n📊 エンゲージメント分析:")
            for key, value in analysis.items():
                print(f"  {key}: {value}")

        elif choice == "4":
            app_name = input("アプリ名: ")
            features = input("主な機能 (カンマ区切り): ").split(",")
            tweet = generator.generate_ios_app_announcement(app_name, features)
            print(f"\n生成されたツイート:\n{tweet}")
            if input("\n投稿しますか？ (y/n): ").lower() == 'y':
                twitter.post_tweet(tweet)

        elif choice == "5":
            break

    print("\n👋 終了しました")


if __name__ == "__main__":
    main()
