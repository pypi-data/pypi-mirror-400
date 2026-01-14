"""Tests for loader module."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import yaml
from promptops.loader import (
    load_prompt,
    clear_prompt_cache,
    get_prompt_cache_keys,
    list_prompt_versions,
)
from promptops.exceptions import ConfigurationError


class TestLoadPromptLocal:
    """Test loading prompts from local YAML files."""
    
    def test_load_valid_local_prompt(self, tmp_path):
        """Test loading valid local prompt file."""
        # Create directory structure
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = {
            "template": "Hello, {name}!",
            "provider": "openai",
        }
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        
        # Change to tmp_path so "prompts/" is found
        with patch('promptops.loader.Path', side_effect=lambda x: tmp_path / x if x == "prompts/test-prompt/v1.yaml" else Path(x)):
            config = load_prompt("test-prompt", "v1", source="local")
            assert 'template' in config
            assert config['template'] == "Hello, {name}!"
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file raises error."""
        with pytest.raises(ConfigurationError):
            load_prompt("nonexistent", "v1", source="local")


class TestLoadPromptCaching:
    """Test prompt caching functionality."""
    
    def test_caching_enabled_by_default(self, tmp_path):
        """Test that prompts are cached by default."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump({"template": "Test"}))
        
        # Clear cache first
        clear_prompt_cache()
        
        # Load twice with mocked Path
        with patch('promptops.loader.Path') as mock_path:
            mock_yaml_path = Mock()
            mock_yaml_path.exists.return_value = True
            mock_yaml_path.read_text.return_value = yaml.dump({"template": "Test"})
            mock_path.return_value = mock_yaml_path
            
            config1 = load_prompt("test-prompt", "v1", source="local")
            config2 = load_prompt("test-prompt", "v1", source="local")
            
            # Should only read once due to caching
            assert mock_yaml_path.read_text.call_count == 1
    
    def test_reload_bypasses_cache(self, tmp_path):
        """Test reload=True bypasses cache."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump({"template": "Test"}))
        
        clear_prompt_cache()
        
        with patch('promptops.loader.Path') as mock_path:
            mock_yaml_path = Mock()
            mock_yaml_path.exists.return_value = True
            mock_yaml_path.read_text.return_value = yaml.dump({"template": "Test"})
            mock_path.return_value = mock_yaml_path
            
            config1 = load_prompt("test-prompt", "v1", source="local")
            config2 = load_prompt("test-prompt", "v1", source="local", reload=True)
            
            # Should read twice
            assert mock_yaml_path.read_text.call_count == 2


class TestCacheManagement:
    """Test cache management functions."""
    
    def test_clear_cache(self):
        """Test clearing the prompt cache."""
        clear_prompt_cache()
        keys = get_prompt_cache_keys()
        assert len(keys) == 0
    
    def test_get_cache_keys(self, tmp_path):
        """Test getting cache keys."""
        clear_prompt_cache()
        
        with patch('promptops.loader.Path') as mock_path:
            mock_yaml_path = Mock()
            mock_yaml_path.exists.return_value = True
            mock_yaml_path.read_text.return_value = yaml.dump({"template": "Test"})
            mock_path.return_value = mock_yaml_path
            
            load_prompt("test1", "v1", source="local")
            load_prompt("test2", "v1", source="local")
            
            keys = get_prompt_cache_keys()
            assert len(keys) == 2
            assert "local:test1:v1" in keys
            assert "local:test2:v1" in keys


class TestPromptValidation:
    """Test prompt validation functionality."""
    
    def test_validate_disabled(self, tmp_path):
        """Test loading with validation disabled."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        # Invalid YAML (missing required fields)
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump({"template": "Test"}))
        
        with patch('promptops.loader.Path', side_effect=lambda x: tmp_path / x if x == "prompts/test-prompt/v1.yaml" else Path(x)):
            # Should work with validation disabled
            config = load_prompt("test-prompt", "v1", source="local", validate=False)
            assert config['template'] == "Test"
    
    def test_name_mismatch_validation(self, tmp_path):
        """Test validation catches name mismatch."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = {
            "name": "different-name",
            "template": "Test"
        }
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        
        # Mock Path to return our tmp_path file
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            with pytest.raises(ConfigurationError, match="name mismatch"):
                load_prompt("test-prompt", "v1", source="local", validate=True)
    
    def test_version_mismatch_validation(self, tmp_path):
        """Test validation catches version mismatch."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = {
            "version": "v2",
            "template": "Test"
        }
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            with pytest.raises(ConfigurationError, match="version mismatch"):
                load_prompt("test-prompt", "v1", source="local", validate=True)
    
    def test_schema_validation(self, tmp_path):
        """Test schema validation."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = {
            "template": "Test",
            "provider": "openai"
        }
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        
        schema = {
            "template": str,
            "provider": str
        }
        
        with patch('promptops.loader.Path', side_effect=lambda x: tmp_path / x if x == "prompts/test-prompt/v1.yaml" else Path(x)):
            # Should pass with correct schema
            config = load_prompt("test-prompt", "v1", source="local", schema=schema)
            assert config['template'] == "Test"
    
    def test_schema_validation_missing_key(self, tmp_path):
        """Test schema validation fails on missing key."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = {
            "template": "Test"
        }
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        
        schema = {
            "template": str,
            "provider": str  # Missing in YAML
        }
        
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            with pytest.raises(ConfigurationError, match="Missing required key"):
                load_prompt("test-prompt", "v1", source="local", schema=schema)
    
    def test_schema_validation_wrong_type(self, tmp_path):
        """Test schema validation fails on wrong type."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = {
            "template": "Test",
            "max_tokens": "100"  # Should be int
        }
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml.dump(yaml_content))
        
        schema = {
            "template": str,
            "max_tokens": int
        }
        
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            with pytest.raises(ConfigurationError, match="must be"):
                load_prompt("test-prompt", "v1", source="local", schema=schema)


class TestEnvironmentInterpolation:
    """Test environment variable interpolation."""
    
    def test_env_interpolation_enabled(self, tmp_path, monkeypatch):
        """Test environment variable interpolation."""
        monkeypatch.setenv("API_KEY", "test-key-123")
        
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = "api_key: ${API_KEY}\ntemplate: Test"
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml_content)
        
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            config = load_prompt("test-prompt", "v1", source="local", env_interpolate=True)
            assert config['api_key'] == "test-key-123"
    
    def test_env_interpolation_disabled(self, tmp_path, monkeypatch):
        """Test environment variable interpolation can be disabled."""
        monkeypatch.setenv("API_KEY", "test-key-123")
        
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = "api_key: ${API_KEY}\ntemplate: Test"
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml_content)
        
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            config = load_prompt("test-prompt", "v1", source="local", env_interpolate=False)
            assert config['api_key'] == "${API_KEY}"  # Not interpolated
    
    def test_env_missing_variable(self, tmp_path):
        """Test missing env variable is left as-is."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_content = "api_key: ${NONEXISTENT_VAR}\ntemplate: Test"
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text(yaml_content)
        
        with patch('promptops.loader.Path') as mock_path_class:
            mock_path_instance = tmp_path / "prompts" / "test-prompt" / "v1.yaml"
            mock_path_class.return_value = mock_path_instance
            
            config = load_prompt("test-prompt", "v1", source="local", env_interpolate=True)
            assert config['api_key'] == "${NONEXISTENT_VAR}"


class TestRemotePromptLoading:
    """Test loading prompts from remote sources."""
    
    @patch('promptops.loader.requests')
    def test_load_remote_prompt(self, mock_requests):
        """Test loading prompt from remote URL."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = yaml.dump({"template": "Remote test"})
        mock_requests.get.return_value = mock_response
        
        clear_prompt_cache()
        config = load_prompt("http://example.com/prompts/test", "v1", source="remote")
        assert config['template'] == "Remote test"
        mock_requests.get.assert_called_once()
    
    @patch('promptops.loader.requests')
    def test_remote_prompt_not_found(self, mock_requests):
        """Test remote prompt returns 404."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_requests.get.return_value = mock_response
        
        with pytest.raises(ConfigurationError, match="Remote prompt not found"):
            load_prompt("http://example.com/prompts/missing", "v1", source="remote")
    
    def test_remote_without_requests(self):
        """Test remote loading fails without requests library."""
        # Temporarily set the module-level requests to None
        import promptops.loader
        original_requests = promptops.loader.requests
        try:
            promptops.loader.requests = None
            with pytest.raises(ConfigurationError, match="requests not installed"):
                load_prompt("http://example.com/prompts/test", "v1", source="remote")
        finally:
            promptops.loader.requests = original_requests


class TestListPromptVersions:
    """Test listing available prompt versions."""
    
    def test_list_local_versions(self, tmp_path):
        """Test listing versions from local directory."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        (prompts_dir / "v1.yaml").write_text("template: Test")
        (prompts_dir / "v2.yaml").write_text("template: Test")
        (prompts_dir / "v3.yaml").write_text("template: Test")
        
        with patch('promptops.loader.Path', side_effect=lambda x: tmp_path / x if x.startswith("prompts/") else Path(x)):
            versions = list_prompt_versions("test-prompt", source="local")
            assert "v1" in versions
            assert "v2" in versions
            assert "v3" in versions
            assert len(versions) == 3
    
    def test_list_versions_nonexistent_prompt(self):
        """Test listing versions for non-existent prompt."""
        versions = list_prompt_versions("nonexistent-prompt", source="local")
        assert versions == []


class TestInvalidYAML:
    """Test handling of invalid YAML."""
    
    def test_invalid_yaml_format(self, tmp_path):
        """Test loading invalid YAML raises error."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text("invalid: yaml: content: [")
        
        with patch('promptops.loader.Path', side_effect=lambda x: tmp_path / x if x == "prompts/test-prompt/v1.yaml" else Path(x)):
            with pytest.raises(ConfigurationError):
                load_prompt("test-prompt", "v1", source="local")
    
    def test_yaml_not_dict(self, tmp_path):
        """Test YAML that's not a dict raises error."""
        prompts_dir = tmp_path / "prompts" / "test-prompt"
        prompts_dir.mkdir(parents=True)
        
        yaml_file = prompts_dir / "v1.yaml"
        yaml_file.write_text("- item1\n- item2")  # List, not dict
        
        with patch('promptops.loader.Path', side_effect=lambda x: tmp_path / x if x == "prompts/test-prompt/v1.yaml" else Path(x)):
            with pytest.raises(ConfigurationError, match="must be a dict"):
                load_prompt("test-prompt", "v1", source="local")


class TestUnknownSource:
    """Test handling of unknown sources."""
    
    def test_unknown_source_type(self):
        """Test unknown source raises error."""
        with pytest.raises(ConfigurationError, match="Unknown prompt source"):
            load_prompt("test", "v1", source="unknown_source")