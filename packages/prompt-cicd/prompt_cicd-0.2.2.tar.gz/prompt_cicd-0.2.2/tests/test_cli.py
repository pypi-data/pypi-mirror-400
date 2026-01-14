"""Tests for CLI module."""

import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from promptops.cli.main import cli
from promptops.cli.console import (
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    print_table,
    RICH_AVAILABLE,
)


class TestCLI:
    """Test CLI commands."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.runner = CliRunner()
    
    def test_cli_version(self):
        """Test version command."""
        result = self.runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert '0.2' in result.output
    
    def test_cli_help(self):
        """Test help command."""
        result = self.runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'PromptOps' in result.output
    
    def test_list_command_no_prompts(self):
        """Test list command with no prompts directory."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['list'])
            assert result.exit_code == 0
    
    @patch('promptops.cli.main.init_project')
    def test_init_command(self, mock_init):
        """Test init command."""
        mock_init.return_value = {
            'files_created': ['promptops.yaml', 'prompts/'],
            'project_path': '/test/project',
        }
        
        result = self.runner.invoke(cli, ['init', 'test-project'])
        assert result.exit_code == 0
        mock_init.assert_called_once()
    
    def test_init_dry_run(self):
        """Test init with dry-run flag."""
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ['init', 'test', '--dry-run'])
            assert result.exit_code == 0


class TestConsole:
    """Test console output functions."""
    
    def test_print_success(self, capsys):
        """Test success message printing."""
        print_success("Test success")
        captured = capsys.readouterr()
        assert "Test success" in captured.out or len(captured.out) > 0
    
    def test_print_error(self, capsys):
        """Test error message printing."""
        print_error("Test error")
        captured = capsys.readouterr()
        assert "Test error" in captured.out or len(captured.out) > 0
    
    def test_print_warning(self, capsys):
        """Test warning message printing."""
        print_warning("Test warning")
        captured = capsys.readouterr()
        assert "Test warning" in captured.out or len(captured.out) > 0
    
    def test_print_info(self, capsys):
        """Test info message printing."""
        print_info("Test info")
        captured = capsys.readouterr()
        assert "Test info" in captured.out or len(captured.out) > 0
    
    def test_print_header(self, capsys):
        """Test header printing."""
        print_header("Test Header")
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_print_table(self, capsys):
        """Test table printing."""
        columns = [{"header": "Name"}, {"header": "Value"}]
        rows = [["Test", "123"]]
        print_table("Test Table", columns, rows)
        captured = capsys.readouterr()
        assert len(captured.out) > 0
    
    def test_rich_available(self):
        """Test RICH_AVAILABLE flag."""
        assert isinstance(RICH_AVAILABLE, bool)
