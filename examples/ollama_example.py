#!/usr/bin/env python3
"""
Ollama Integration Example
ローカルLLMを使用したコード分析の例
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ollama_integration import (
    OllamaManager,
    code_review,
    explain_code,
    generate_tests,
    refactor_code,
)


def example_basic_chat():
    """基本的なチャット機能の例"""
    print("=== Basic Chat Example ===\n")

    manager = OllamaManager(model="llama3.2:3b")

    # シンプルな質問
    response = manager.chat("What is Python decorator?")
    print(f"Response: {response}\n")


def example_code_review():
    """コードレビューの例"""
    print("=== Code Review Example ===\n")

    sample_code = """
def calculate_factorial(n):
    if n == 0:
        return 1
    else:
        result = 1
        for i in range(1, n+1):
            result = result * i
        return result
"""

    review = code_review(sample_code)
    print(f"Code Review Result:\n{review}\n")


def example_explain_code():
    """コード説明の例"""
    print("=== Code Explanation Example ===\n")

    complex_code = """
@dataclass
class Person:
    name: str
    age: int

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("Age cannot be negative")
"""

    explanation = explain_code(complex_code)
    print(f"Explanation:\n{explanation}\n")


def example_generate_tests():
    """テスト生成の例"""
    print("=== Test Generation Example ===\n")

    function_code = """
def fibonacci(n):
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    else:
        fib = [0, 1]
        for i in range(2, n):
            fib.append(fib[i-1] + fib[i-2])
        return fib
"""

    tests = generate_tests(function_code)
    print(f"Generated Tests:\n{tests}\n")


def example_refactor_code():
    """リファクタリングの例"""
    print("=== Code Refactoring Example ===\n")

    old_code = """
def process_data(data):
    result = []
    for item in data:
        if item > 0:
            if item < 100:
                result.append(item * 2)
    return result
"""

    refactored = refactor_code(old_code)
    print(f"Refactored Code:\n{refactored}\n")


def example_streaming():
    """ストリーミングレスポンスの例"""
    print("=== Streaming Response Example ===\n")

    manager = OllamaManager()

    print("Streaming response: ", end="", flush=True)
    for chunk in manager.stream_chat("Write a haiku about programming"):
        print(chunk, end="", flush=True)
    print("\n")


def example_embeddings():
    """埋め込みベクトル生成の例"""
    print("=== Embeddings Example ===\n")

    manager = OllamaManager()

    text = "Python is a high-level programming language"
    embeddings = manager.embeddings(text)

    print(f"Text: {text}")
    print(f"Embedding dimensions: {len(embeddings)}")
    print(f"First 5 values: {embeddings[:5]}\n")


def main():
    """メイン実行関数"""
    print("🤖 Ollama Integration Examples\n")
    print("=" * 50)
    print()

    # 利用可能なモデルを表示
    manager = OllamaManager()
    try:
        models = manager.list_models()
        if models:
            print("Available models:")
            for model in models:
                print(f"  - {model['name']}")
            print()
    except Exception as e:
        print("⚠️  Ollama is not running. Start it with: ollama serve")
        print(f"   Error: {e}\n")
        return

    # 各例を実行
    try:
        example_basic_chat()
        example_code_review()
        example_explain_code()
        example_generate_tests()
        example_refactor_code()
        example_streaming()
        example_embeddings()
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("Make sure Ollama is running and required models are installed:")
        print("  ollama serve  # Start Ollama")
        print("  ollama pull llama3.2:3b  # Install model")
        print("  ollama pull codellama:7b  # Install code model")


if __name__ == "__main__":
    main()
