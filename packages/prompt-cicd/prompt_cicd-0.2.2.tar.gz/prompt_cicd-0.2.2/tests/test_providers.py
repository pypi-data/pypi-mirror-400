"""Tests for providers module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from promptops.providers.openai_provider import (
    OpenAIProvider,
    OpenAIConfig,
    ModelConfig,
)


class TestOpenAIConfig:
    """Test OpenAIConfig dataclass."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = OpenAIConfig()
        assert config.model == "gpt-4"
        assert config.temperature == 0.7
        assert config.max_tokens is None
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = OpenAIConfig(
            model="gpt-3.5-turbo",
            temperature=0.5,
            max_tokens=1000,
        )
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.max_tokens == 1000


class TestModelConfig:
    """Test ModelConfig dataclass."""
    
    def test_model_pricing(self):
        """Test model pricing information."""
        config = ModelConfig(
            name="gpt-4",
            cost_per_1k_tokens=0.03,
            max_tokens=8192,
        )
        assert config.name == "gpt-4"
        assert config.cost_per_1k_tokens == 0.03
        assert config.max_tokens == 8192


class TestOpenAIProvider:
    """Test OpenAIProvider class."""
    
    @patch('promptops.providers.openai_provider.OpenAI')
    def test_provider_initialization(self, mock_openai):
        """Test provider initialization."""
        provider = OpenAIProvider(api_key="test-key-123")
        assert provider is not None
    
    @patch('promptops.providers.openai_provider.OpenAI')
    def test_custom_config(self, mock_openai):
        """Test provider with custom config."""
        config = OpenAIConfig(model="gpt-3.5-turbo")
        provider = OpenAIProvider(api_key="test-key-123", config=config)
        assert provider.config.default_model == "gpt-3.5-turbo"
    
    @patch('promptops.providers.openai_provider.OpenAI')
    def test_generate_mock(self, mock_openai):
        """Test generate method with mock."""
        # Setup mock response with all required attributes
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.content = "Test response"
        mock_message.function_call = None
        mock_message.tool_calls = None
        
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_choice.finish_reason = "stop"
        
        mock_usage = MagicMock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30
        
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]
        mock_response.model = "gpt-4"
        mock_response.usage = mock_usage
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        provider = OpenAIProvider(api_key="test-key-123")
        result = provider.generate("Test prompt")
        
        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()
