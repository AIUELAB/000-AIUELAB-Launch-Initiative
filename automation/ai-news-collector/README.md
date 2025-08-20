# 🤖 AI/MCP 自動情報収集システム

## 📌 概要

このシステムは、最新のAI技術とMCP（Model Context Protocol）関連の情報を自動的に収集し、重要度に応じて分類・通知する機能を提供します。

## 🎯 主な機能

### 1. **自動巡回収集**
- 30分ごとに主要なAI/MCPニュースソースを巡回
- RSS/APIを使用して最新情報を取得
- 重複を自動的に除外

### 2. **インテリジェントフィルタリング**
- AIによる関連性スコアの自動計算
- 重要度に応じた優先度付け（Critical/High/Medium/Low）
- ノイズ（広告、スポンサー記事）の自動除去

### 3. **多様な情報源**
- **AI関連**: OpenAI, Anthropic, Google AI, Hugging Face
- **MCP関連**: 公式サイト、GitHub、ドキュメント
- **技術ニュース**: Hacker News, Reddit, Twitter/X
- **日本語源**: Zenn, Qiita

### 4. **スマート通知**
- 重要度に応じた即時通知
- 日次ダイジェストの自動生成
- Raycast/n8n連携による柔軟な通知

## 🚀 セットアップ

### 1. 依存関係のインストール

```bash
cd automation/ai-news-collector
pip install -r requirements.txt
```

### 2. 設定ファイルの編集

`config.json`を開いて、必要に応じて以下を調整：
- 情報源のURL
- フィルタリングキーワード
- 通知設定

### 3. 初回実行

```bash
# 単発実行
python collector.py

# 継続的な監視
python collector.py --continuous
```

## 📱 Raycast統合

Raycastから簡単にAI/MCPニュースをチェック：

1. Raycast設定でScript Commandsを追加
2. `scripts/raycast/ai-news-check.sh`を登録
3. `Cmd + Space`で「AI News」と入力して実行

## 🔄 n8n自動化

n8nワークフローで完全自動化：

1. n8nダッシュボードを開く
2. `automation/n8n-workflows/ai-news-workflow.json`をインポート
3. Webhook URLを設定
4. ワークフローを有効化

## 📊 収集データの構造

```
collected_data/
├── digest_20240120.json    # 日次ダイジェスト（JSON）
├── digest_20240120.md      # 日次ダイジェスト（Markdown）
├── seen_urls.json          # 収集済みURL管理
└── critical_alerts.log     # 重要アラートのログ
```

## 🎨 カスタマイズ

### 情報源の追加

`config.json`の`sources`セクションに新しいソースを追加：

```json
{
  "name": "新しいソース名",
  "url": "https://example.com/feed",
  "type": "blog",
  "priority": "high",
  "keywords": ["AI", "LLM"]
}
```

### フィルタリング調整

重要度の判定基準を変更：

```json
"filters": {
  "importance_keywords": ["新機能", "リリース"],
  "min_relevance_score": 0.6
}
```

### 通知頻度の変更

```json
"schedule": {
  "intervals": {
    "high_priority": "*/15 * * * *"  // 15分ごと
  }
}
```

## 📈 活用例

### 毎朝のルーティン

1. Raycastで「AI News」を実行
2. 重要な更新をチェック
3. 興味深い記事をClaude/ChatGPTで要約

### プロジェクト開始時

1. 最新のMCPサーバー情報を確認
2. 新しいAI APIの機能をチェック
3. ベストプラクティスの更新を確認

### 週次レビュー

1. 週間ダイジェストを確認
2. トレンドを分析
3. 次週の学習計画を立てる

## 🔧 トラブルシューティング

### 情報が収集されない

1. インターネット接続を確認
2. `config.json`のURLが正しいか確認
3. `seen_urls.json`を削除して再実行

### 通知が来ない

1. n8n/Raycastの設定を確認
2. Webhook URLが正しいか確認
3. 通知の閾値設定を確認

### エラーが発生する

```bash
# デバッグモードで実行
python collector.py --debug

# ログを確認
tail -f collected_data/error.log
```

## 💡 Tips

- **重要度の調整**: 最初は閾値を低めに設定し、徐々に調整
- **カスタムフィルター**: 自分の興味に合わせてキーワードを追加
- **定期メンテナンス**: 月1回`seen_urls.json`をクリーンアップ

## 📝 今後の機能追加予定

- [ ] ChatGPT/Claude APIによる自動要約
- [ ] Slack/Discord通知対応
- [ ] トレンド分析機能
- [ ] 類似記事のグルーピング
- [ ] 多言語対応（中国語、韓国語）

---

**質問・要望**: このREADMEを更新して、新しい機能や改善点を追加してください！
