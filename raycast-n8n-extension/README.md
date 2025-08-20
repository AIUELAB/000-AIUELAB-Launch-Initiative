# n8n Runner (Raycast Extension)

- URL かパスを入力して、n8n の Webhook を実行
- JSON ペイロードを任意指定
- タイムアウトで固まり防止

## インストール

```bash
cd raycast-n8n-extension
npm install
```

Raycast で「Import Extension」→ このディレクトリを選択。

## 設定

- Preferences: baseUrl, timeoutSec, defaultUseTestUrl を必要に応じ設定

## 使い方

- URL か `raycast-cli` などのパスを入力
- Shift+P で Production、Shift+T で Test に切替
