"""
PromptOps CLI - Command Line Interface for prompt management.

This package provides a rich CLI experience with:
- Colorful output using Rich library
- Project scaffolding (init)
- Prompt linting
- Interactive testing
- Beautiful reports
"""

from .console import (
    console,
    get_console,
    print_success,
    print_error,
    print_warning,
    print_info,
    print_header,
    print_panel,
    print_test_results,
    print_lint_results,
    print_project_tree,
    print_welcome,
    print_banner,
    print_yaml,
    print_table,
    RICH_AVAILABLE,
)

from .main import cli, main

__all__ = [
    # Main CLI
    "cli",
    "main",
    # Console
    "console",
    "get_console",
    "print_success",
    "print_error",
    "print_warning",
    "print_info",
    "print_header",
    "print_panel",
    "print_test_results",
    "print_lint_results",
    "print_project_tree",
    "print_welcome",
    "print_banner",
    "print_yaml",
    "print_table",
    "RICH_AVAILABLE",
]
