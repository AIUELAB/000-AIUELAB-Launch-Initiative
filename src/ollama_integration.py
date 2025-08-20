"""
Ollama Integration for Claude Code Template
完全無料のローカルLLM統合
"""

from typing import Any, Iterator, cast

import ollama
from langchain_ollama import ChatOllama, OllamaLLM
from llama_index.llms.ollama import Ollama as LlamaIndexOllama


class OllamaManager:
    """Ollama LLM Manager for local inference.

    A comprehensive manager for interacting with Ollama's local LLM models.
    Provides interfaces for chat, streaming, embeddings, and model management.

    Attributes:
        model (str): The name of the Ollama model to use.
        client (ollama.Client): Direct Ollama client for API calls.
        langchain_llm (OllamaLLM): LangChain integration for LLM operations.
        langchain_chat (ChatOllama): LangChain chat model interface.
        llamaindex_llm (LlamaIndexOllama): LlamaIndex integration.

    Example:
        >>> manager = OllamaManager("llama3.2:3b")
        >>> response = manager.chat("Hello, how are you?")
        >>> print(response)
    """

    def __init__(self, model: str = "llama3.2:3b") -> None:
        """Initialize the Ollama manager with specified model.

        Args:
            model: The Ollama model to use. Defaults to "llama3.2:3b".
                  Common options: "llama3.2:3b", "codellama:7b", "mistral:7b"

        Raises:
            ConnectionError: If Ollama service is not running.
        """
        self.model = model
        self.client = ollama.Client()
        self.langchain_llm = OllamaLLM(model=model)
        self.langchain_chat = ChatOllama(model=model)
        self.llamaindex_llm = LlamaIndexOllama(model=model)

    def chat(self, prompt: str, system: str | None = None) -> str:
        """Send a chat message to the model and get a response.

        Args:
            prompt: The user message to send to the model.
            system: Optional system prompt to set context for the conversation.
                   Used to guide the model's behavior and responses.

        Returns:
            The model's response as a string.

        Example:
            >>> response = manager.chat(
            ...     "Explain Python decorators",
            ...     system="You are a Python expert teacher"
            ... )
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = cast(dict[str, Any], self.client.chat(model=self.model, messages=messages))
        message = cast(dict[str, Any], response.get("message", {}))
        return cast(str, message.get("content", ""))

    def stream_chat(self, prompt: str, system: str | None = None) -> Iterator[str]:
        """Stream chat responses in real-time.

        Yields response chunks as they are generated, enabling real-time
        display of the model's output.

        Args:
            prompt: The user message to send to the model.
            system: Optional system prompt to set context.

        Yields:
            str: Individual chunks of the response as they are generated.

        Example:
            >>> for chunk in manager.stream_chat("Write a story about AI"):
            ...     print(chunk, end="", flush=True)
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = self.client.chat(model=self.model, messages=messages, stream=True)

        for chunk in stream:
            yield cast(str, chunk["message"]["content"])

    def generate(self, prompt: str) -> str:
        """Generate text completion for a given prompt.

        Uses the raw generation API without chat formatting.
        Best for simple completions and text generation tasks.

        Args:
            prompt: The text prompt to complete.

        Returns:
            The generated text completion.

        Example:
            >>> completion = manager.generate("The future of AI is")
        """
        response = cast(dict[str, Any], self.client.generate(model=self.model, prompt=prompt))
        return cast(str, response.get("response", ""))

    def list_models(self) -> list[dict[str, Any]]:
        """List all locally available Ollama models.

        Returns:
            A list of dictionaries containing model information.
            Each dict includes 'name', 'size', 'modified', and other metadata.

        Example:
            >>> models = manager.list_models()
            >>> for model in models:
            ...     print(f"{model['name']}: {model.get('size', 'N/A')}")
        """
        info = cast(dict[str, Any], self.client.list())
        return cast(list[dict[str, Any]], info.get("models", []))

    def pull_model(self, model_name: str) -> dict[str, Any]:
        """Download a new model from Ollama's model library.

        Args:
            model_name: The name of the model to download.
                       Format: "model:tag" (e.g., "llama3.2:3b")

        Returns:
            Pull status information from Ollama.

        Example:
            >>> manager.pull_model("codellama:7b")

        Note:
            This operation may take several minutes depending on model size.
        """
        return cast(dict[str, Any], self.client.pull(model_name))

    def embeddings(self, text: str) -> list[float]:
        """Generate vector embeddings for text.

        Creates high-dimensional vector representations of text
        for use in similarity search, clustering, or ML pipelines.

        Args:
            text: The text to generate embeddings for.

        Returns:
            A list of floating-point values representing the text embedding.
            Typically 768-4096 dimensions depending on the model.

        Example:
            >>> embeddings = manager.embeddings("Python programming")
            >>> print(f"Embedding size: {len(embeddings)}")
        """
        response = cast(dict[str, Any], self.client.embeddings(model=self.model, prompt=text))
        return cast(list[float], response.get("embedding", []))


# Example usage functions
def code_review(code: str, model: str = "codellama:7b") -> str:
    """Perform automated code review using Ollama.

    Analyzes code for potential bugs, performance issues,
    security vulnerabilities, and adherence to best practices.

    Args:
        code: The source code to review.
        model: The Ollama model to use. Defaults to "codellama:7b"
               which is optimized for code analysis.

    Returns:
        A detailed code review with findings and suggestions.

    Example:
        >>> code = '''def factorial(n):
        ...     return 1 if n <= 1 else n * factorial(n-1)'''
        >>> review = code_review(code)
        >>> print(review)
    """
    manager = OllamaManager(model)
    system = "You are an expert code reviewer. Analyze the code for bugs, performance issues, and best practices."
    prompt = f"Review this code:\n\n{code}"
    return manager.chat(prompt, system)


def explain_code(code: str, model: str = "llama3.2:3b") -> str:
    """Generate clear explanations of code functionality.

    Provides beginner-friendly explanations of what code does,
    how it works, and its key concepts.

    Args:
        code: The source code to explain.
        model: The Ollama model to use. Defaults to "llama3.2:3b".

    Returns:
        A clear, educational explanation of the code.

    Example:
        >>> code = "lambda x: x**2 if x > 0 else 0"
        >>> explanation = explain_code(code)
        >>> print(explanation)
    """
    manager = OllamaManager(model)
    system = "You are a helpful programming tutor. Explain code clearly and concisely."
    prompt = f"Explain this code:\n\n{code}"
    return manager.chat(prompt, system)


def generate_tests(code: str, model: str = "codellama:7b") -> str:
    """Generate comprehensive unit tests for given code.

    Creates pytest-compatible test cases covering various scenarios
    including edge cases, error conditions, and typical usage.

    Args:
        code: The source code to generate tests for.
        model: The Ollama model to use. Defaults to "codellama:7b".

    Returns:
        Generated pytest test code with multiple test cases.

    Example:
        >>> code = '''def add(a, b):
        ...     return a + b'''
        >>> tests = generate_tests(code)
        >>> print(tests)  # Returns pytest test functions
    """
    manager = OllamaManager(model)
    system = "You are an expert at writing comprehensive unit tests. Generate pytest tests."
    prompt = f"Write unit tests for this code:\n\n{code}"
    return manager.chat(prompt, system)


def refactor_code(code: str, model: str = "codellama:7b") -> str:
    """Suggest code refactoring for improved quality.

    Analyzes code and provides refactored version with improvements
    in readability, performance, maintainability, and adherence to
    Python best practices and idioms.

    Args:
        code: The source code to refactor.
        model: The Ollama model to use. Defaults to "codellama:7b".

    Returns:
        Refactored code with explanations of improvements made.

    Example:
        >>> code = '''for i in range(len(items)):
        ...     print(items[i])'''
        >>> refactored = refactor_code(code)
        >>> print(refactored)  # Suggests: for item in items: print(item)
    """
    manager = OllamaManager(model)
    system = "You are an expert at code refactoring. Suggest improvements for clarity, performance, and maintainability."
    prompt = f"Refactor this code:\n\n{code}"
    return manager.chat(prompt, system)


if __name__ == "__main__":
    # Test the integration
    print("Testing Ollama integration...")

    manager = OllamaManager()

    # List available models
    print("\nAvailable models:")
    for model in manager.list_models():
        print(f"  - {model['name']}")

    # Simple test
    response = manager.chat("Write a Python function to calculate factorial")
    print(f"\nTest response:\n{response}")

    print("\nOllama integration is working!")
