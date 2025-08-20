# ターミナル表示設定ガイド

## 推奨設定

### ターミナルサイズ
- **幅**: 120文字以上（推奨: 140文字）
- **高さ**: 30行以上（推奨: 40行）

### フォント設定
```
推奨フォント:
- JetBrains Mono
- Fira Code
- Source Code Pro
- SF Mono（macOS標準）

サイズ: 14pt
行間: 1.2
```

### 文字エンコーディング
```bash
# 確認コマンド
echo $LANG
echo $LC_ALL

# 推奨設定
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8
```

## macOS Terminal.app設定

1. Terminal → Preferences → Profiles
2. Window タブ:
   - Columns: 120
   - Rows: 40
3. Text タブ:
   - Font: SF Mono Regular 14pt
   - Use bright colors for bold text: ON

## iTerm2設定

1. Preferences → Profiles → Window
   - Columns: 120
   - Rows: 40
2. Preferences → Profiles → Text
   - Font: JetBrains Mono 14pt
   - Vertical spacing: 110%

## Cursor内蔵ターミナル設定

`.vscode/settings.json`に追加:
```json
{
  "terminal.integrated.fontSize": 14,
  "terminal.integrated.fontFamily": "JetBrains Mono, monospace",
  "terminal.integrated.lineHeight": 1.2,
  "terminal.integrated.cols": 120,
  "terminal.integrated.rows": 30
}
```

## トラブルシューティング

### 文字が重なる場合
```bash
# ターミナルをリセット
reset
clear
```

### 日本語が文字化けする場合
```bash
# ~/.zshrcまたは~/.bashrcに追加
export LANG=ja_JP.UTF-8
export LC_ALL=ja_JP.UTF-8
```

### Claude Codeの表示が崩れる場合
```bash
# シンプルモードで起動
claude --no-color --plain-output
```
