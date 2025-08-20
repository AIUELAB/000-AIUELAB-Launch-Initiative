"""
Tests for Ollama integration
"""

import os
import sys
from unittest.mock import Mock, patch

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ollama_integration import (
    OllamaManager,
    code_review,
    explain_code,
    generate_tests,
    refactor_code,
)


class TestOllamaManager:
    """Test OllamaManager class"""

    @patch("src.ollama_integration.ollama.Client")
    @patch("src.ollama_integration.OllamaLLM")
    @patch("src.ollama_integration.ChatOllama")
    @patch("src.ollama_integration.LlamaIndexOllama")
    def test_initialization(self, mock_llama_index, mock_chat, mock_llm, mock_client):
        """Test OllamaManager initialization"""
        manager = OllamaManager(model="test-model")

        assert manager.model == "test-model"
        assert manager.client is not None
        mock_llm.assert_called_once_with(model="test-model")
        mock_chat.assert_called_once_with(model="test-model")
        mock_llama_index.assert_called_once_with(model="test-model")

    @patch("src.ollama_integration.ollama.Client")
    def test_chat(self, mock_client):
        """Test chat method"""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.chat.return_value = {"message": {"content": "Test response"}}

        manager = OllamaManager()
        response = manager.chat("Test prompt", "Test system")

        mock_instance.chat.assert_called_once()
        call_args = mock_instance.chat.call_args[1]
        assert call_args["model"] == "llama3.2:3b"
        assert len(call_args["messages"]) == 2
        assert call_args["messages"][0]["role"] == "system"
        assert call_args["messages"][1]["content"] == "Test prompt"
        assert response == "Test response"

    @patch("src.ollama_integration.ollama.Client")
    def test_generate(self, mock_client):
        """Test generate method"""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.generate.return_value = {"response": "Generated text"}

        manager = OllamaManager()
        response = manager.generate("Test prompt")

        mock_instance.generate.assert_called_once_with(model="llama3.2:3b", prompt="Test prompt")
        assert response == "Generated text"

    @patch("src.ollama_integration.ollama.Client")
    def test_list_models(self, mock_client):
        """Test list_models method"""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.list.return_value = {"models": [{"name": "model1"}, {"name": "model2"}]}

        manager = OllamaManager()
        models = manager.list_models()

        assert len(models) == 2
        assert models[0]["name"] == "model1"
        assert models[1]["name"] == "model2"

    @patch("src.ollama_integration.ollama.Client")
    def test_embeddings(self, mock_client):
        """Test embeddings method"""
        mock_instance = Mock()
        mock_client.return_value = mock_instance
        mock_instance.embeddings.return_value = {"embedding": [0.1, 0.2, 0.3]}

        manager = OllamaManager()
        embedding = manager.embeddings("Test text")

        mock_instance.embeddings.assert_called_once_with(model="llama3.2:3b", prompt="Test text")
        assert embedding == [0.1, 0.2, 0.3]


class TestUtilityFunctions:
    """Test utility functions"""

    @patch("src.ollama_integration.OllamaManager")
    def test_code_review(self, mock_manager_class):
        """Test code_review function"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.chat.return_value = "Review result"

        result = code_review("def test(): pass")

        mock_manager_class.assert_called_once_with("codellama:7b")
        mock_manager.chat.assert_called_once()
        assert result == "Review result"

    @patch("src.ollama_integration.OllamaManager")
    def test_explain_code(self, mock_manager_class):
        """Test explain_code function"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.chat.return_value = "Explanation"

        result = explain_code("def test(): pass")

        mock_manager_class.assert_called_once_with("llama3.2:3b")
        mock_manager.chat.assert_called_once()
        assert result == "Explanation"

    @patch("src.ollama_integration.OllamaManager")
    def test_generate_tests(self, mock_manager_class):
        """Test generate_tests function"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.chat.return_value = "Generated tests"

        result = generate_tests("def add(a, b): return a + b")

        mock_manager_class.assert_called_once_with("codellama:7b")
        mock_manager.chat.assert_called_once()
        assert result == "Generated tests"

    @patch("src.ollama_integration.OllamaManager")
    def test_refactor_code(self, mock_manager_class):
        """Test refactor_code function"""
        mock_manager = Mock()
        mock_manager_class.return_value = mock_manager
        mock_manager.chat.return_value = "Refactored code"

        result = refactor_code("def test(): pass")

        mock_manager_class.assert_called_once_with("codellama:7b")
        mock_manager.chat.assert_called_once()
        assert result == "Refactored code"


class TestStreamingChat:
    """Test streaming functionality"""

    @patch("src.ollama_integration.ollama.Client")
    def test_stream_chat(self, mock_client):
        """Test stream_chat method"""
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        # Mock streaming response
        mock_stream = [
            {"message": {"content": "Hello"}},
            {"message": {"content": " "}},
            {"message": {"content": "World"}},
        ]
        mock_instance.chat.return_value = iter(mock_stream)

        manager = OllamaManager()
        result = list(manager.stream_chat("Test prompt"))

        mock_instance.chat.assert_called_once()
        call_args = mock_instance.chat.call_args[1]
        assert call_args["stream"] is True
        assert result == ["Hello", " ", "World"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
