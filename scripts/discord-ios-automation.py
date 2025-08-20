#!/usr/bin/env python3
"""
iOS Discord Tokyo 自動化スクリプト
Discord サーバーID: 1118089502259421214
"""

import discord
from discord.ext import commands, tasks
import asyncio
import os
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import aiohttp
from pathlib import Path

# Discord設定
DISCORD_SERVER_ID = 1118089502259421214
DISCORD_BOT_PREFIX = "!"

# チャンネル設定（実際のチャンネルIDに置き換える必要あり）
CHANNELS = {
    "announcements": None,  # お知らせチャンネル
    "events": None,         # イベント情報チャンネル
    "general": None,        # 雑談チャンネル
    "dev-questions": None,  # 開発質問チャンネル
    "showcase": None,       # 作品紹介チャンネル
    "jobs": None,          # 求人情報チャンネル
}


class iOSDiscordBot(commands.Bot):
    """iOS Discord Bot"""

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True

        super().__init__(
            command_prefix=DISCORD_BOT_PREFIX,
            intents=intents,
            description="iOS Discord Tokyo Bot - AIUELAB"
        )

        self.server_id = DISCORD_SERVER_ID
        self.connpass_events = []

    async def setup_hook(self):
        """Bot起動時のセットアップ"""
        # コマンドを追加
        await self.add_cog(iOSCommands(self))
        await self.add_cog(EventManager(self))
        await self.add_cog(CommunityManager(self))

        # 定期タスクを開始
        self.check_events.start()
        self.update_stats.start()

    async def on_ready(self):
        """Bot準備完了時"""
        print(f"✅ {self.user} として接続しました")
        print(f"サーバーID: {self.server_id}")

        # ステータス設定
        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="iOS Development"
            )
        )

        # サーバー情報取得
        guild = self.get_guild(self.server_id)
        if guild:
            print(f"サーバー名: {guild.name}")
            print(f"メンバー数: {guild.member_count}")

    @tasks.loop(hours=1)
    async def check_events(self):
        """定期的にイベント情報をチェック"""
        # Connpass APIからイベント取得
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://connpass.com/api/v1/event/",
                params={"series_id": "14027", "order": 2, "count": 10}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.connpass_events = data.get("events", [])

                    # イベントチャンネルに投稿
                    if CHANNELS["events"]:
                        channel = self.get_channel(CHANNELS["events"])
                        if channel and self.connpass_events:
                            await self.post_upcoming_events(channel)

    @tasks.loop(hours=24)
    async def update_stats(self):
        """サーバー統計を更新"""
        guild = self.get_guild(self.server_id)
        if guild:
            stats = {
                "members": guild.member_count,
                "channels": len(guild.channels),
                "roles": len(guild.roles),
                "created_at": guild.created_at.isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            # 統計を保存
            stats_path = Path.home() / ".aiuelab" / "discord_stats.json"
            stats_path.parent.mkdir(parents=True, exist_ok=True)
            with open(stats_path, "w") as f:
                json.dump(stats, f, indent=2)

    async def post_upcoming_events(self, channel):
        """今後のイベントを投稿"""
        if not self.connpass_events:
            return

        embed = discord.Embed(
            title="📅 今後のiOSイベント",
            description="iOS Discord Tokyo 関連イベント",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )

        for event in self.connpass_events[:5]:
            start_time = datetime.fromisoformat(
                event["started_at"].replace("T", " ").replace("+09:00", "")
            )

            embed.add_field(
                name=event["title"][:50],
                value=f"📅 {start_time.strftime('%m/%d %H:%M')}\n"
                      f"📍 {event.get('place', 'オンライン')[:30]}\n"
                      f"👥 {event.get('accepted', 0)}/{event.get('limit', '∞')}\n"
                      f"[詳細]({event['event_url']})",
                inline=False
            )

        embed.set_footer(text="AIUELAB Event Bot")
        await channel.send(embed=embed)


class iOSCommands(commands.Cog):
    """iOS関連コマンド"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="swift")
    async def swift_info(self, ctx):
        """Swift情報を表示"""
        embed = discord.Embed(
            title="Swift Language",
            description="Apple's modern programming language",
            color=discord.Color.orange()
        )
        embed.add_field(
            name="最新バージョン",
            value="Swift 5.9",
            inline=True
        )
        embed.add_field(
            name="リリース",
            value="2023年9月",
            inline=True
        )
        embed.add_field(
            name="リソース",
            value="[公式サイト](https://swift.org)\n"
                  "[ドキュメント](https://docs.swift.org)",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="xcode")
    async def xcode_info(self, ctx):
        """Xcode情報を表示"""
        embed = discord.Embed(
            title="Xcode",
            description="Apple's IDE for iOS development",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="最新バージョン",
            value="Xcode 15.2",
            inline=True
        )
        embed.add_field(
            name="対応OS",
            value="macOS 14.0+",
            inline=True
        )
        embed.add_field(
            name="ダウンロード",
            value="[App Store](https://apps.apple.com/app/id497799835)",
            inline=False
        )
        await ctx.send(embed=embed)

    @commands.command(name="events")
    async def show_events(self, ctx):
        """イベント一覧を表示"""
        if not self.bot.connpass_events:
            await ctx.send("現在、予定されているイベントはありません。")
            return

        events_text = "**📅 今後のイベント**\n\n"
        for event in self.bot.connpass_events[:5]:
            events_text += f"• [{event['title']}]({event['event_url']})\n"

        await ctx.send(events_text)

    @commands.command(name="aiuelab")
    async def aiuelab_info(self, ctx):
        """AIUELAB情報を表示"""
        embed = discord.Embed(
            title="AIUELAB",
            description="iOS App Development by Takashi Gunji",
            color=discord.Color.green(),
            url="https://aiuelab.com"
        )
        embed.add_field(
            name="🌐 Website",
            value="[aiuelab.com](https://aiuelab.com)",
            inline=True
        )
        embed.add_field(
            name="🐦 Twitter",
            value="[@AIUELAB](https://x.com/AIUELAB)",
            inline=True
        )
        embed.add_field(
            name="💻 GitHub",
            value="[AIUELAB](https://github.com/AIUELAB)",
            inline=True
        )
        embed.set_footer(text="Creating meaningful iOS experiences")
        await ctx.send(embed=embed)


class EventManager(commands.Cog):
    """イベント管理"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="create_event")
    @commands.has_permissions(manage_events=True)
    async def create_event(self, ctx, title: str, date: str, time: str):
        """Discordイベントを作成"""
        try:
            # 日時パース
            event_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

            # イベント作成
            guild = ctx.guild
            event = await guild.create_scheduled_event(
                name=title,
                start_time=event_time,
                location="iOS Discord Tokyo",
                description=f"Created by {ctx.author.mention}"
            )

            await ctx.send(f"✅ イベント「{title}」を作成しました！\nID: {event.id}")

        except Exception as e:
            await ctx.send(f"❌ イベント作成エラー: {e}")


class CommunityManager(commands.Cog):
    """コミュニティ管理"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """新メンバー参加時"""
        # ウェルカムメッセージ
        welcome_channel = self.bot.get_channel(CHANNELS.get("general"))
        if welcome_channel:
            embed = discord.Embed(
                title="👋 ようこそ！",
                description=f"{member.mention} さん、iOS Discord Tokyo へようこそ！",
                color=discord.Color.green()
            )
            embed.add_field(
                name="はじめに",
                value="• <#rules> でルールをご確認ください\n"
                      "• <#self-intro> で自己紹介をどうぞ\n"
                      "• <#dev-questions> で開発の質問ができます",
                inline=False
            )
            embed.set_footer(text="Powered by AIUELAB")
            await welcome_channel.send(embed=embed)

    @commands.command(name="stats")
    async def server_stats(self, ctx):
        """サーバー統計を表示"""
        guild = ctx.guild

        embed = discord.Embed(
            title="📊 サーバー統計",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        embed.add_field(name="メンバー数", value=guild.member_count, inline=True)
        embed.add_field(name="チャンネル数", value=len(guild.channels), inline=True)
        embed.add_field(name="ロール数", value=len(guild.roles), inline=True)
        embed.add_field(
            name="作成日",
            value=guild.created_at.strftime("%Y/%m/%d"),
            inline=True
        )
        embed.add_field(name="ブースト数", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="ブーストレベル", value=guild.premium_tier, inline=True)

        await ctx.send(embed=embed)


async def main():
    """メイン処理"""
    # 環境変数からトークンを取得
    token = os.getenv("DISCORD_BOT_TOKEN")
    if not token:
        print("❌ DISCORD_BOT_TOKEN が設定されていません")
        print("1. https://discord.com/developers/applications でアプリ作成")
        print("2. Bot セクションでトークンを取得")
        print("3. .env.discord に DISCORD_BOT_TOKEN=xxx を設定")
        return

    # Bot起動
    bot = iOSDiscordBot()

    try:
        await bot.start(token)
    except KeyboardInterrupt:
        await bot.close()


if __name__ == "__main__":
    asyncio.run(main())
