"""
Rich Console utilities for beautiful CLI output.

Provides consistent, colorful output across all PromptOps CLI commands
with support for tables, panels, progress bars, and styled text.
"""

import sys
from typing import Any, Dict, List, Optional, Union

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.markdown import Markdown
    from rich.text import Text
    from rich.style import Style
    from rich.box import ROUNDED, SIMPLE, DOUBLE
    from rich.theme import Theme
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Custom theme for PromptOps
PROMPTOPS_THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "prompt_name": "bold magenta",
    "version": "dim cyan",
    "cost": "yellow",
    "count": "bold white",
    "header": "bold blue",
    "muted": "dim",
}) if RICH_AVAILABLE else None


# Global console instance
console = Console(theme=PROMPTOPS_THEME) if RICH_AVAILABLE else None


class FallbackConsole:
    """Fallback console when Rich is not installed."""
    
    def print(self, *args, **kwargs):
        # Strip style kwargs for plain output
        kwargs.pop('style', None)
        print(*args)
    
    def rule(self, title: str = "", **kwargs):
        print(f"\n{'=' * 50}")
        if title:
            print(f"  {title}")
        print('=' * 50)


def get_console() -> Union["Console", FallbackConsole]:
    """Get the console instance, with fallback for missing Rich."""
    if RICH_AVAILABLE and console:
        return console
    return FallbackConsole()


# =============================================================================
# Styled Print Functions
# =============================================================================


def print_success(message: str, prefix: str = "✅") -> None:
    """Print a success message."""
    c = get_console()
    if RICH_AVAILABLE:
        c.print(f"{prefix} {message}", style="success")
    else:
        print(f"{prefix} {message}")


def print_error(message: str, prefix: str = "❌") -> None:
    """Print an error message."""
    c = get_console()
    if RICH_AVAILABLE:
        c.print(f"{prefix} {message}", style="error")
    else:
        print(f"{prefix} {message}", file=sys.stderr)


def print_warning(message: str, prefix: str = "⚠️") -> None:
    """Print a warning message."""
    c = get_console()
    if RICH_AVAILABLE:
        c.print(f"{prefix}  {message}", style="warning")
    else:
        print(f"{prefix} {message}")


def print_info(message: str, prefix: str = "ℹ️") -> None:
    """Print an info message."""
    c = get_console()
    if RICH_AVAILABLE:
        c.print(f"{prefix}  {message}", style="info")
    else:
        print(f"{prefix} {message}")


def print_header(title: str) -> None:
    """Print a section header."""
    c = get_console()
    if RICH_AVAILABLE:
        c.rule(f"[header]{title}[/header]", style="header")
    else:
        print(f"\n{'=' * 50}")
        print(f"  {title}")
        print('=' * 50)


# =============================================================================
# Panels and Boxes
# =============================================================================


def print_panel(
    content: str,
    title: Optional[str] = None,
    style: str = "info",
    expand: bool = False,
) -> None:
    """Print content in a bordered panel."""
    c = get_console()
    if RICH_AVAILABLE:
        panel = Panel(content, title=title, style=style, expand=expand, box=ROUNDED)
        c.print(panel)
    else:
        if title:
            print(f"\n┌─ {title} {'─' * (40 - len(title))}┐")
        else:
            print("\n┌" + "─" * 42 + "┐")
        for line in content.split("\n"):
            print(f"│ {line:<40} │")
        print("└" + "─" * 42 + "┘")


def print_results_box(
    title: str,
    stats: Dict[str, Any],
    style: str = "green",
) -> None:
    """Print a results summary box."""
    c = get_console()
    if RICH_AVAILABLE:
        lines = []
        for key, value in stats.items():
            if isinstance(value, float):
                lines.append(f"[bold]{key}:[/bold] {value:.4f}")
            else:
                lines.append(f"[bold]{key}:[/bold] {value}")
        content = "\n".join(lines)
        panel = Panel(content, title=title, style=style, box=ROUNDED)
        c.print(panel)
    else:
        print(f"\n=== {title} ===")
        for key, value in stats.items():
            print(f"  {key}: {value}")


# =============================================================================
# Tables
# =============================================================================


def create_table(
    title: str,
    columns: List[Dict[str, Any]],
    rows: List[List[Any]],
    show_header: bool = True,
    show_lines: bool = False,
) -> Optional["Table"]:
    """Create a Rich table (returns None if Rich not available)."""
    if not RICH_AVAILABLE:
        return None
    
    table = Table(title=title, show_header=show_header, show_lines=show_lines, box=ROUNDED)
    
    for col in columns:
        table.add_column(
            col.get("header", ""),
            style=col.get("style", ""),
            justify=col.get("justify", "left"),
            width=col.get("width"),
        )
    
    for row in rows:
        table.add_row(*[str(cell) for cell in row])
    
    return table


def print_table(
    title: str,
    columns: List[Dict[str, Any]],
    rows: List[List[Any]],
    show_header: bool = True,
) -> None:
    """Print a formatted table."""
    c = get_console()
    
    if RICH_AVAILABLE:
        table = create_table(title, columns, rows, show_header)
        c.print(table)
    else:
        # Fallback ASCII table
        print(f"\n{title}")
        print("-" * 60)
        
        headers = [col.get("header", "") for col in columns]
        print(" | ".join(f"{h:<15}" for h in headers))
        print("-" * 60)
        
        for row in rows:
            print(" | ".join(f"{str(cell):<15}" for cell in row))


def print_prompt_table(prompts: List[Dict[str, Any]]) -> None:
    """Print a table of prompts."""
    columns = [
        {"header": "Name", "style": "prompt_name"},
        {"header": "Version", "style": "version"},
        {"header": "Approved", "style": "success"},
        {"header": "Tests", "style": "count"},
    ]
    
    rows = []
    for p in prompts:
        approved = "✅" if p.get("approved") else "❌"
        test_count = len(p.get("tests", []))
        rows.append([p.get("name", ""), p.get("version", ""), approved, test_count])
    
    print_table("Available Prompts", columns, rows)


# =============================================================================
# Test Results Display
# =============================================================================


def print_test_results(
    prompt_name: str,
    version: str,
    passed: bool,
    total_tests: int,
    passed_tests: int,
    failed_tests: List[Dict[str, Any]],
    duration: float,
    estimated_cost: Optional[float] = None,
) -> None:
    """Print beautifully formatted test results."""
    c = get_console()
    
    status_icon = "✅" if passed else "❌"
    status_text = "PASSED" if passed else "FAILED"
    status_style = "success" if passed else "error"
    
    if RICH_AVAILABLE:
        # Header
        c.print()
        c.rule(f"[prompt_name]{prompt_name}[/prompt_name] [version]v{version}[/version]")
        c.print()
        
        # Stats panel
        stats_lines = [
            f"[bold]Status:[/bold] [{status_style}]{status_icon} {status_text}[/{status_style}]",
            f"[bold]Tests:[/bold] {passed_tests}/{total_tests} passed",
            f"[bold]Duration:[/bold] {duration:.2f}s",
        ]
        if estimated_cost is not None:
            stats_lines.append(f"[bold]Est. Cost:[/bold] [cost]${estimated_cost:.4f}[/cost]")
        
        panel = Panel(
            "\n".join(stats_lines),
            title="Test Results",
            style=status_style,
            box=ROUNDED,
        )
        c.print(panel)
        
        # Failed tests details
        if failed_tests:
            c.print()
            c.print("[error]Failed Tests:[/error]")
            for i, test in enumerate(failed_tests, 1):
                c.print(f"  {i}. [bold]{test.get('name', 'Unknown')}[/bold]")
                if test.get("reason"):
                    c.print(f"     [muted]{test['reason']}[/muted]")
                if test.get("expected"):
                    c.print(f"     Expected: [success]{test['expected']}[/success]")
                if test.get("actual"):
                    c.print(f"     Actual: [error]{test['actual']}[/error]")
        
        c.print()
    else:
        # Fallback plain output
        print(f"\n{'=' * 50}")
        print(f"  {prompt_name} v{version}")
        print('=' * 50)
        print(f"{status_icon} {status_text}")
        print(f"Tests: {passed_tests}/{total_tests} passed")
        print(f"Duration: {duration:.2f}s")
        if estimated_cost:
            print(f"Est. Cost: ${estimated_cost:.4f}")
        
        if failed_tests:
            print("\nFailed Tests:")
            for test in failed_tests:
                print(f"  - {test.get('name', 'Unknown')}: {test.get('reason', '')}")


# =============================================================================
# Lint Results Display
# =============================================================================


def print_lint_results(
    prompt_name: str,
    version: str,
    issues: List[Dict[str, Any]],
    passed: bool,
) -> None:
    """Print beautifully formatted lint results."""
    c = get_console()
    
    error_count = sum(1 for i in issues if i.get("severity") == "error")
    warning_count = sum(1 for i in issues if i.get("severity") == "warning")
    info_count = sum(1 for i in issues if i.get("severity") == "info")
    
    if RICH_AVAILABLE:
        c.print()
        c.rule(f"[prompt_name]{prompt_name}[/prompt_name] [version]v{version}[/version] - Lint Results")
        c.print()
        
        if passed:
            c.print("[success]✅ No issues found![/success]")
        else:
            # Summary
            summary = []
            if error_count:
                summary.append(f"[error]{error_count} error(s)[/error]")
            if warning_count:
                summary.append(f"[warning]{warning_count} warning(s)[/warning]")
            if info_count:
                summary.append(f"[info]{info_count} info(s)[/info]")
            
            c.print("Issues: " + ", ".join(summary))
            c.print()
            
            # Issue details
            for issue in issues:
                severity = issue.get("severity", "info")
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "•")
                style = {"error": "error", "warning": "warning", "info": "info"}.get(severity, "")
                
                c.print(f"  [{style}]{icon} {issue.get('message', '')}[/{style}]")
                if issue.get("suggestion"):
                    c.print(f"     [muted]💡 {issue['suggestion']}[/muted]")
        
        c.print()
    else:
        print(f"\n=== Lint: {prompt_name} v{version} ===")
        if passed:
            print("✅ No issues found!")
        else:
            print(f"Found: {error_count} errors, {warning_count} warnings, {info_count} info")
            for issue in issues:
                print(f"  [{issue.get('severity', 'info').upper()}] {issue.get('message', '')}")


# =============================================================================
# Progress Indicators
# =============================================================================


def create_progress() -> Optional["Progress"]:
    """Create a progress bar context manager."""
    if not RICH_AVAILABLE:
        return None
    
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    )


def print_spinner(message: str) -> None:
    """Print a message with spinner (one-shot, not animated)."""
    c = get_console()
    if RICH_AVAILABLE:
        c.print(f"⏳ {message}...", style="info")
    else:
        print(f"... {message}")


# =============================================================================
# Code and YAML Display
# =============================================================================


def print_yaml(content: str, title: Optional[str] = None) -> None:
    """Print YAML content with syntax highlighting."""
    c = get_console()
    
    if RICH_AVAILABLE:
        syntax = Syntax(content, "yaml", theme="monokai", line_numbers=True)
        if title:
            c.print(Panel(syntax, title=title, box=ROUNDED))
        else:
            c.print(syntax)
    else:
        if title:
            print(f"\n--- {title} ---")
        print(content)


def print_diff(old: str, new: str, title: str = "Diff") -> None:
    """Print a diff between two strings."""
    c = get_console()
    
    import difflib
    diff_lines = list(difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile="old",
        tofile="new",
    ))
    
    if RICH_AVAILABLE:
        if not diff_lines:
            c.print("[muted]No differences[/muted]")
            return
        
        text = Text()
        for line in diff_lines:
            if line.startswith("+") and not line.startswith("+++"):
                text.append(line, style="green")
            elif line.startswith("-") and not line.startswith("---"):
                text.append(line, style="red")
            elif line.startswith("@@"):
                text.append(line, style="cyan")
            else:
                text.append(line)
        
        c.print(Panel(text, title=title, box=ROUNDED))
    else:
        print(f"\n--- {title} ---")
        print("".join(diff_lines) if diff_lines else "No differences")


# =============================================================================
# Tree Display
# =============================================================================


def print_project_tree(root: str, structure: Dict[str, Any]) -> None:
    """Print a project structure as a tree."""
    c = get_console()
    
    if RICH_AVAILABLE:
        tree = Tree(f"📁 [bold]{root}[/bold]")
        _build_tree(tree, structure)
        c.print(tree)
    else:
        print(f"\n{root}/")
        _print_tree_fallback(structure, "  ")


def _build_tree(tree: "Tree", structure: Dict[str, Any]) -> None:
    """Recursively build a Rich tree."""
    for name, content in structure.items():
        if isinstance(content, dict):
            branch = tree.add(f"📁 {name}")
            _build_tree(branch, content)
        else:
            icon = "📄" if name.endswith((".py", ".yaml", ".yml", ".md")) else "📝"
            tree.add(f"{icon} {name}")


def _print_tree_fallback(structure: Dict[str, Any], indent: str) -> None:
    """Print tree structure without Rich."""
    for name, content in structure.items():
        if isinstance(content, dict):
            print(f"{indent}{name}/")
            _print_tree_fallback(content, indent + "  ")
        else:
            print(f"{indent}{name}")


# =============================================================================
# Welcome Banner
# =============================================================================


def print_banner() -> None:
    """Print the PromptOps welcome banner."""
    c = get_console()
    
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ████████╗   ║
║   ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝   ║
║   ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝   ██║      ║
║   ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝    ██║      ║
║   ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║        ██║      ║
║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝        ╚═╝      ║
║                      ██████╗ ██████╗ ███████╗             ║
║                     ██╔═══██╗██╔══██╗██╔════╝             ║
║                     ██║   ██║██████╔╝███████╗             ║
║                     ██║   ██║██╔═══╝ ╚════██║             ║
║                     ╚██████╔╝██║     ███████║             ║
║                      ╚═════╝ ╚═╝     ╚══════╝             ║
║                                                           ║
║            CI/CD for AI Prompts - v0.1.0                  ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
"""
    
    if RICH_AVAILABLE:
        c.print(banner, style="bold blue")
    else:
        print(banner)


def print_welcome(project_name: str) -> None:
    """Print a welcome message for a new project."""
    c = get_console()
    
    if RICH_AVAILABLE:
        c.print()
        c.print(f"[success]✨ Successfully created project:[/success] [prompt_name]{project_name}[/prompt_name]")
        c.print()
        c.print("[header]Next steps:[/header]")
        c.print("  1. [info]cd[/info] " + project_name)
        c.print("  2. [info]promptops run[/info] example v1")
        c.print("  3. [info]promptops test[/info] example v1")
        c.print()
        c.print("[muted]Documentation: https://github.com/prabhnoor12/promptops[/muted]")
        c.print()
    else:
        print(f"\n✨ Successfully created project: {project_name}")
        print("\nNext steps:")
        print(f"  1. cd {project_name}")
        print("  2. promptops run example v1")
        print("  3. promptops test example v1")
