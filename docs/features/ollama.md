# Ollama統合ガイド

## 概要

Ollamaは完全無料のローカルLLMプラットフォームです。APIキー不要で、プライバシー保護とオフライン動作が可能です。

## 主な特徴

- 🆓 **完全無料** - APIキー・利用料金不要
- 🔒 **プライバシー保護** - データはローカルに留まる
- ⚡ **高速レスポンス** - ネットワーク遅延なし
- 🌐 **オフライン対応** - インターネット接続不要
- 🤖 **豊富なモデル** - Llama 3、CodeLlama、Mistral等

## サポートモデル

| モデル | サイズ | 用途 | 推奨メモリ |
|-------|--------|------|------------|
| llama3.2:3b | 3B | 汎用チャット | 8GB |
| codellama:7b | 7B | コード生成・レビュー | 16GB |
| mistral:7b | 7B | 高度な分析 | 16GB |
| deepseek-r1:1.5b | 1.5B | 高速レスポンス | 4GB |
| gemma:2b | 2B | 軽量タスク | 4GB |

## 基本的な使い方

### OllamaManagerクラス

```python
from src.ollama_integration import OllamaManager

# マネージャーの初期化
manager = OllamaManager(model="llama3.2:3b")

# シンプルなチャット
response = manager.chat("Pythonの利点を説明して")
print(response)

# システムプロンプト付きチャット
response = manager.chat(
    prompt="def factorial(n): return 1 if n <= 1 else n * factorial(n-1)",
    system="You are a code reviewer. Analyze this code."
)
```

### ストリーミングレスポンス

```python
# リアルタイムストリーミング
for chunk in manager.stream_chat("長い物語を書いて"):
    print(chunk, end="", flush=True)
```

### 埋め込みベクトル生成

```python
# テキストの埋め込み生成
text = "Python is a versatile programming language"
embeddings = manager.embeddings(text)
print(f"Embedding dimensions: {len(embeddings)}")
```

## ユーティリティ関数

### コードレビュー

```python
from src.ollama_integration import code_review

code = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr)-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
"""

review = code_review(code)
print(review)
```

### コード説明

```python
from src.ollama_integration import explain_code

explanation = explain_code(code)
print(explanation)
```

### テスト生成

```python
from src.ollama_integration import generate_tests

tests = generate_tests(code)
print(tests)
```

### リファクタリング提案

```python
from src.ollama_integration import refactor_code

refactored = refactor_code(code)
print(refactored)
```

## 高度な設定

### カスタムモデル設定

`.ollama.yml`ファイルで詳細設定が可能：

```yaml
models:
  chat: llama3.2:3b
  code: codellama:7b
  analysis: mistral:7b

parameters:
  temperature: 0.7
  top_p: 0.9
  max_tokens: 2048
  seed: 42
```

### パフォーマンス最適化

```yaml
performance:
  num_threads: 8      # CPU スレッド数
  num_gpu: 1          # GPU使用（0で無効）
  batch_size: 512     # バッチサイズ
```

## モデル管理

### モデルのダウンロード

```python
# 新しいモデルをダウンロード
manager.pull_model("phi:2.7b")
```

### 利用可能なモデル一覧

```python
models = manager.list_models()
for model in models:
    print(f"- {model['name']} ({model.get('size', 'N/A')})")
```

## ベストプラクティス

### 1. モデル選択

- **軽量タスク**: `deepseek-r1:1.5b`、`gemma:2b`
- **一般的なチャット**: `llama3.2:3b`
- **コード関連**: `codellama:7b`
- **高度な分析**: `mistral:7b`

### 2. メモリ管理

```python
# 使用後のクリーンアップ
import gc
del manager
gc.collect()
```

### 3. エラーハンドリング

```python
try:
    response = manager.chat("質問")
except Exception as e:
    print(f"Ollamaエラー: {e}")
    print("Ollamaが起動していることを確認してください")
```

### 4. バッチ処理

```python
# 複数の質問を効率的に処理
questions = ["Q1", "Q2", "Q3"]
responses = []

for q in questions:
    response = manager.chat(q)
    responses.append(response)
```

## トラブルシューティング

### Ollamaが見つからない

```bash
# Ollamaのインストール確認
which ollama

# 再インストール
curl -fsSL https://ollama.com/install.sh | sh
```

### モデルが利用できない

```bash
# モデル一覧確認
ollama list

# モデルのダウンロード
ollama pull llama3.2:3b
```

### メモリ不足

- より小さいモデルを使用（1.5B〜3B）
- バッチサイズを減らす
- GPU利用を無効化（CPU only）

## 実装例

完全な実装例は[examples/ollama_example.py](../../examples/ollama_example.py)を参照してください。

## 関連リンク

- [Ollama公式サイト](https://ollama.com/)
- [利用可能なモデル一覧](https://ollama.com/library)
- [Ollama GitHub](https://github.com/ollama/ollama)
