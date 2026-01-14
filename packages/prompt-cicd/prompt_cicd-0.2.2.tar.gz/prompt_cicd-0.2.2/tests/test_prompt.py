"""Tests for prompt module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from promptops.prompt import Prompt


class TestPrompt:
    """Test Prompt class."""
    
    @patch('promptops.prompt.load_prompt')
    @patch('promptops.prompt.OpenAIProvider')
    def test_load_prompt(self, mock_provider, mock_load):
        """Test loading a prompt."""
        mock_load.return_value = {
            'name': 'test',
            'version': 'v1',
            'template': 'Hello {name}',
            'provider': 'openai',
        }
        
        prompt = Prompt.load('test', 'v1')
        assert prompt.name == 'test'
        assert prompt.version == 'v1'
    
    @patch('promptops.prompt.load_prompt')
    @patch('promptops.prompt.OpenAIProvider')
    def test_prompt_config(self, mock_provider, mock_load):
        """Test accessing prompt config."""
        mock_load.return_value = {
            'name': 'test',
            'template': 'Test template',
            'provider': 'openai',
            'approved': True,
        }
        
        prompt = Prompt.load('test', 'v1')
        assert prompt.config['approved'] is True
    
    @patch('promptops.prompt.load_prompt')
    @patch('promptops.prompt.OpenAIProvider')
    def test_prompt_with_tests(self, mock_provider, mock_load):
        """Test prompt with test cases."""
        mock_load.return_value = {
            'name': 'test',
            'template': 'Hello {name}',
            'provider': 'openai',
            'tests': [
                {'name': 'test1', 'input': {'name': 'World'}},
            ],
        }
        
        prompt = Prompt.load('test', 'v1')
        assert len(prompt.config.get('tests', [])) == 1
