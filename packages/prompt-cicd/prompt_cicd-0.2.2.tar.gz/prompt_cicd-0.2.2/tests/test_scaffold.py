"""Tests for the scaffold module."""

import pytest
from pathlib import Path
import yaml

from promptops.scaffold.generator import (
    init_project,
    create_prompt,
    get_project_structure,
    ProjectTemplate,
)


class TestInitProject:
    """Test project initialization."""
    
    def test_init_basic_project(self, tmp_path, monkeypatch):
        """Test initializing a basic project."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "test_project"
        
        result = init_project(
            project_name="test_project",
            template="basic"
        )
        
        assert project_dir.exists()
        assert (project_dir / "promptops.yaml").exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "prompts").exists()
        assert len(result["files_created"]) > 0
    
    def test_init_full_project(self, tmp_path, monkeypatch):
        """Test initializing a full project with examples."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "full_project"
        
        result = init_project(
            project_name="full_project",
            template="full",
            include_examples=True
        )
        
        assert project_dir.exists()
        assert (project_dir / ".github" / "workflows").exists()
        assert len(list((project_dir / "prompts").glob("**/*.yaml"))) > 0
    
    def test_init_minimal_project(self, tmp_path, monkeypatch):
        """Test initializing a minimal project."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "minimal_project"
        
        result = init_project(
            project_name="minimal_project",
            template="minimal",
            include_examples=False
        )
        
        assert project_dir.exists()
        assert (project_dir / "promptops.yaml").exists()
    
    def test_init_with_github_actions(self, tmp_path, monkeypatch):
        """Test initializing project with GitHub Actions."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "gh_project"
        
        result = init_project(
            project_name="gh_project",
            template="basic",
            include_github_actions=True
        )
        
        workflow_file = project_dir / ".github" / "workflows" / "promptops.yml"
        assert workflow_file.exists()
    
    def test_init_without_github_actions(self, tmp_path, monkeypatch):
        """Test initializing project without GitHub Actions."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "no_gh_project"
        
        result = init_project(
            project_name="no_gh_project",
            template="basic",
            include_github_actions=False
        )
        
        workflow_dir = project_dir / ".github"
        assert not workflow_dir.exists()
    
    def test_init_existing_directory_raises(self, tmp_path, monkeypatch):
        """Test that initializing in existing directory raises error."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "existing"
        project_dir.mkdir()
        
        with pytest.raises(FileExistsError):
            init_project(
                project_name="existing",
                template="basic"
            )
    
    def test_init_with_custom_provider(self, tmp_path, monkeypatch):
        """Test initializing with custom provider."""
        monkeypatch.chdir(tmp_path)
        project_dir = tmp_path / "custom_provider"
        
        result = init_project(
            project_name="custom_provider",
            template="basic",
            provider="anthropic"
        )
        
        config_file = project_dir / "promptops.yaml"
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        assert config.get("default_provider") == "anthropic" or "anthropic" in str(config)


class TestCreatePrompt:
    """Test prompt file creation."""
    
    def test_create_basic_prompt(self, tmp_path):
        """Test creating a basic prompt."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        file_path = create_prompt(
            name="test_prompt",
            version="v1",
            template_type="basic",
            base_path=str(prompts_dir)
        )
        
        assert Path(file_path).exists()
        assert "test_prompt" in file_path
        assert "v1" in file_path
    
    def test_create_chat_prompt(self, tmp_path):
        """Test creating a chat prompt."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        file_path = create_prompt(
            name="chat_prompt",
            version="v1",
            template_type="chat",
            base_path=str(prompts_dir)
        )
        
        assert Path(file_path).exists()
        
        with open(file_path) as f:
            content = yaml.safe_load(f)
        
        assert "template" in content
    
    def test_create_structured_prompt(self, tmp_path):
        """Test creating a structured output prompt."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        file_path = create_prompt(
            name="structured_prompt",
            version="v1",
            template_type="structured",
            base_path=str(prompts_dir)
        )
        
        assert Path(file_path).exists()
        
        with open(file_path) as f:
            content = yaml.safe_load(f)
        
        assert "template" in content
    
    def test_create_existing_prompt_raises(self, tmp_path):
        """Test that creating existing prompt raises error."""
        prompts_dir = tmp_path / "prompts"
        prompts_dir.mkdir()
        
        # Create first time
        create_prompt("test", "v1", base_path=str(prompts_dir))
        
        # Try to create again
        with pytest.raises(FileExistsError):
            create_prompt("test", "v1", base_path=str(prompts_dir))


class TestGetProjectStructure:
    """Test project structure generation."""
    
    def test_basic_structure(self):
        """Test getting basic project structure."""
        structure = get_project_structure("test_project", "basic")
        
        assert "test_project" in structure
        assert "promptops.yaml" in str(structure)
        assert "README.md" in str(structure)
        assert "prompts" in str(structure)
    
    def test_full_structure(self):
        """Test getting full project structure."""
        structure = get_project_structure("test_project", "full")
        
        assert "test_project" in structure
        assert ".github" in str(structure) or "workflows" in str(structure)
    
    def test_minimal_structure(self):
        """Test getting minimal project structure."""
        structure = get_project_structure("test_project", "minimal")
        
        assert "test_project" in structure
        # Minimal should have fewer files than basic
