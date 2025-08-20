# キー管理システム 🔐

このプロジェクトには、APIキーを安全に管理し、自動的に読み込むシステムが組み込まれています。

## 概要

ローカルのキーフォルダ（`/Users/admin/Documents/key`）からAPIキーを自動的に読み込み、`.env.mcp`ファイルを生成します。

## セットアップ

### 方法1: 自動セットアップ（推奨）

```bash
# キーフォルダから自動的にAPIキーを読み込む
./scripts/setup.sh --with-keys
```

### 方法2: 手動実行

```bash
# 対話モードでキーを読み込む
./scripts/load-keys.sh

# または、自動モードで実行
./scripts/load-keys.sh --auto
```

### 方法3: Pythonスクリプト直接実行

```bash
python scripts/load_keys.py
```

## 設定ファイル

### `config/keys.json`
キーファイルのマッピングを定義：

```json
{
  "keys_directory": "/Users/admin/Documents/key",
  "key_mappings": {
    "GITHUB_TOKEN": "GITHUB_PAT_key.txt",
    "BRAVE_API_KEY": "Brave Search API .txt",
    "ANTHROPIC_API_KEY": "anthropic_api_key.txt",
    "OPENAI_API_KEY": "openai_API .txt"
  }
}
```

## キーフォルダの構造

```
/Users/admin/Documents/key/
├── GITHUB_PAT_key.txt         # GitHub Personal Access Token
├── Brave Search API .txt      # Brave Search API Key
├── anthropic_api_key.txt      # Anthropic API Key
├── openai_API .txt            # OpenAI API Key
└── ...
```

## 生成される環境変数ファイル

`.env.mcp`ファイルが以下の場所に生成されます：
- `/Users/admin/Documents/Cursor/claude-code-template-mcp/.env.mcp`

## 確認方法

```bash
# 環境変数の状態を確認
python src/main.py check-env

# MCPサーバーの状態を確認
python src/main.py info
```

## セキュリティ

- `.env.mcp`ファイルは自動的に権限`600`（所有者のみ読み書き可）に設定されます
- キーフォルダのパスと`config/keys.json`は`.gitignore`に追加済み
- 生成された`.env.mcp`ファイルもGitから除外されます

## トラブルシューティング

### キーが読み込まれない場合

1. キーファイルが正しい場所にあるか確認
   ```bash
   ls -la /Users/admin/Documents/key/
   ```

2. `config/keys.json`のマッピングが正しいか確認
   ```bash
   cat config/keys.json
   ```

3. スクリプトを再実行
   ```bash
   ./scripts/load-keys.sh --auto
   ```

### 環境変数が認識されない場合

1. `.env.mcp`ファイルの存在を確認
   ```bash
   ls -la .env.mcp
   ```

2. アプリケーションを再起動
   ```bash
   python src/main.py check-env
   ```

## カスタマイズ

新しいAPIキーを追加する場合：

1. `config/keys.json`を編集してマッピングを追加
2. 対応するキーファイルをキーフォルダに配置
3. `./scripts/load-keys.sh --auto`を実行

## 注意事項

- キーフォルダのパスはハードコードされているため、異なる環境では`config/keys.json`の編集が必要
- APIキーは絶対にGitにコミットしないでください
- 本番環境では、より安全なキー管理システム（AWS Secrets Manager、HashiCorp Vaultなど）の使用を推奨
