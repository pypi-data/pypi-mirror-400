"""
PromptOps CLI - Main Command Line Interface.

Provides commands for:
- Project initialization (init)
- Prompt management (run, test, lint)
- Approval workflow
- Safety scanning
- Budget management
- Caching
"""

import logging
import sys
import time
from pathlib import Path
from typing import Optional

import click

from ..prompt import Prompt
from ..testing.runner import run_tests
from ..approval import ApprovalManager, ApprovalStatus
from ..cost.budget import BudgetPool
from ..safety.scanner import SafetyScanner, run_safety_scan
from ..rollback.engine import rollback_prompt
from ..lint.linter import lint_prompt, lint_all_prompts, LintSeverity
from ..scaffold.generator import init_project, create_prompt, get_project_structure
from ..cache.manager import get_cache, configure_cache, clear_cache, CacheConfig

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("promptops.cli")

# Global managers
approval_mgr = ApprovalManager()
budget_pool = BudgetPool()
scanner = SafetyScanner()


# =============================================================================
# Main CLI Group
# =============================================================================


@click.group()
@click.option('--env', default='dev', help='Environment (dev, staging, prod)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--no-color', is_flag=True, help='Disable colored output')
@click.version_option(version='0.2.0', prog_name='PromptOps')
@click.pass_context
def cli(ctx, env, verbose, no_color):
    """
    PromptOps - CI/CD for AI Prompts.
    
    Manage, test, lint, and deploy AI prompts with confidence.
    
    \b
    Examples:
      promptops init my-project          Create a new project
      promptops run email_summary v1     Run a prompt
      promptops test email_summary v1    Test a prompt
      promptops lint --all               Lint all prompts
    """
    ctx.ensure_object(dict)
    ctx.obj['env'] = env
    ctx.obj['verbose'] = verbose
    ctx.obj['no_color'] = no_color
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.debug(f"CLI started in {env} mode")


# =============================================================================
# Init Command
# =============================================================================


@cli.command()
@click.argument("project_name")
@click.option(
    '--template', '-t',
    type=click.Choice(['basic', 'full', 'minimal']),
    default='basic',
    help='Project template to use'
)
@click.option('--no-github-actions', is_flag=True, help='Skip GitHub Actions setup')
@click.option('--no-examples', is_flag=True, help='Skip example prompts')
@click.option('--provider', default='openai', help='Default LLM provider')
@click.option('--description', '-d', default='', help='Project description')
@click.option('--dry-run', is_flag=True, help='Show what would be created')
@click.pass_context
def init(ctx, project_name, template, no_github_actions, no_examples, provider, description, dry_run):
    """
    Initialize a new PromptOps project.
    
    Creates a complete project structure with configuration,
    example prompts, and CI/CD workflows.
    
    \b
    Examples:
      promptops init my-ai-app
      promptops init my-project --template full
      promptops init my-project --no-github-actions
    """
    try:
        if dry_run:
            print_info("Dry run - showing what would be created:")
            structure = get_project_structure(project_name, template)
            print_project_tree(project_name, structure[project_name])
            return
        
        result = init_project(
            project_name=project_name,
            template=template,
            include_github_actions=not no_github_actions,
            include_examples=not no_examples,
            provider=provider,
            description=description,
        )
        
        print_welcome(project_name)
        
        # Show created files
        if ctx.obj.get('verbose'):
            print_info(f"Created {len(result['files_created'])} files:")
            for f in result['files_created']:
                print(f"  📄 {f}")
        
    except FileExistsError:
        print_error(f"Directory '{project_name}' already exists")
        sys.exit(1)
    except Exception as e:
        logger.exception("Init failed")
        print_error(f"Failed to create project: {e}")
        sys.exit(1)


# =============================================================================
# Run Command
# =============================================================================


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--dry-run', is_flag=True, help='Show what would run without executing')
@click.option('--input', '-i', multiple=True, help='Input values as key=value pairs')
@click.option('--no-cache', is_flag=True, help='Disable caching for this run')
@click.pass_context
def run(ctx, name, version, dry_run, input, no_cache):
    """
    Run a prompt by name and version.
    
    \b
    Examples:
      promptops run email_summary v1
      promptops run email_summary v1 --dry-run
      promptops run translator v1 -i text="Hello world" -i lang="Spanish"
    """
    try:
        prompt = Prompt.load(name, version)
        
        # Parse input values
        inputs = {"env": ctx.obj['env']}
        for inp in input:
            if '=' in inp:
                key, value = inp.split('=', 1)
                inputs[key] = value
        
        if dry_run:
            print_info(f"[DRY RUN] Would run prompt: {name} v{version}")
            print_panel(prompt.config.get('template', ''), title="Template")
            if inputs:
                print_info(f"Inputs: {inputs}")
            return
        
        start_time = time.time()
        
        # Check cache first
        if not no_cache:
            cache = get_cache()
            cached = cache.get(name, version, inputs)
            if cached:
                print_success("Using cached response")
                click.echo(cached)
                return
        
        result = prompt.run(inputs)
        duration = time.time() - start_time
        
        # Cache the result
        if not no_cache:
            cache = get_cache()
            cache.set(name, version, inputs, result)
        
        click.echo(result)
        
        if ctx.obj.get('verbose'):
            print_info(f"Completed in {duration:.2f}s")
        
    except Exception as e:
        logger.error(f"Run failed: {e}")
        print_error(f"Run failed: {e}")
        sys.exit(1)


# =============================================================================
# Test Command
# =============================================================================


@cli.command()
@click.argument("name", required=False)
@click.argument("version", required=False)
@click.option('--all', '-a', 'test_all', is_flag=True, help='Test all prompts')
@click.option('--verbose', '-v', 'verbose', is_flag=True, help='Show detailed output')
@click.pass_context
def test(ctx, name, version, test_all, verbose):
    """
    Run tests for a prompt.
    
    \b
    Examples:
      promptops test email_summary v1
      promptops test --all
    """
    try:
        if test_all:
            # Test all prompts
            prompts_dir = Path("prompts")
            if not prompts_dir.exists():
                print_error("No 'prompts' directory found")
                sys.exit(1)
            
            total_passed = 0
            total_failed = 0
            
            for prompt_dir in prompts_dir.iterdir():
                if prompt_dir.is_dir():
                    for yaml_file in prompt_dir.glob("*.yaml"):
                        prompt_name = prompt_dir.name
                        prompt_version = yaml_file.stem
                        
                        try:
                            prompt = Prompt.load(prompt_name, prompt_version)
                            tests = prompt.config.get("tests", [])
                            
                            if not tests:
                                print_warning(f"{prompt_name} v{prompt_version}: No tests defined")
                                continue
                            
                            start_time = time.time()
                            report = run_tests(prompt, prompt.provider, tests)
                            duration = time.time() - start_time
                            
                            if report.passed:
                                print_success(f"{prompt_name} v{prompt_version}: PASSED ({len(tests)} tests)")
                                total_passed += 1
                            else:
                                print_error(f"{prompt_name} v{prompt_version}: FAILED")
                                total_failed += 1
                                
                        except Exception as e:
                            print_error(f"{prompt_name} v{prompt_version}: Error - {e}")
                            total_failed += 1
            
            # Summary
            print_header("Test Summary")
            if total_failed == 0:
                print_success(f"All {total_passed} prompt(s) passed!")
            else:
                print_error(f"{total_failed} failed, {total_passed} passed")
                sys.exit(1)
            return
        
        if not name or not version:
            print_error("Please specify prompt name and version, or use --all")
            sys.exit(1)
        
        prompt = Prompt.load(name, version)
        tests = prompt.config.get("tests", [])
        
        if not tests:
            print_warning("No tests defined for this prompt")
            return
        
        start_time = time.time()
        report = run_tests(prompt, prompt.provider, tests)
        duration = time.time() - start_time
        
        # Collect failed tests for display
        failed_tests = []
        for result in getattr(report, 'results', []):
            if not getattr(result, 'passed', True):
                failed_tests.append({
                    "name": getattr(result, 'name', 'Unknown'),
                    "reason": getattr(result, 'reason', str(result)),
                })
        
        print_test_results(
            prompt_name=name,
            version=version,
            passed=report.passed,
            total_tests=len(tests),
            passed_tests=len(tests) - len(failed_tests),
            failed_tests=failed_tests,
            duration=duration,
        )
        
        if not report.passed:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print_error(f"Test failed: {e}")
        sys.exit(1)


# =============================================================================
# Lint Command
# =============================================================================


@cli.command()
@click.argument("name", required=False)
@click.argument("version", required=False)
@click.option('--all', '-a', 'lint_all', is_flag=True, help='Lint all prompts')
@click.option(
    '--severity', '-s',
    type=click.Choice(['error', 'warning', 'info']),
    default='info',
    help='Minimum severity to report'
)
@click.option('--fix', is_flag=True, help='Auto-fix issues where possible (not implemented)')
@click.option('--format', 'output_format', type=click.Choice(['text', 'json', 'github']), default='text')
@click.pass_context
def lint(ctx, name, version, lint_all, severity, fix, output_format):
    """
    Lint prompts for issues and best practices.
    
    Checks for:
    - Missing templates or tests
    - Security patterns
    - Cost efficiency
    - Configuration errors
    
    \b
    Examples:
      promptops lint email_summary v1
      promptops lint --all
      promptops lint --all --severity warning
    """
    try:
        if lint_all:
            report = lint_all_prompts("prompts", min_severity=severity)
            
            if output_format == 'json':
                import json
                click.echo(json.dumps([r.to_dict() for r in report.results], indent=2))
                return
            
            if output_format == 'github':
                # GitHub Actions annotation format
                for result in report.results:
                    for issue in result.issues:
                        level = "error" if issue.severity == LintSeverity.ERROR else "warning"
                        click.echo(f"::{level} file={result.file_path}::{issue.message}")
                return
            
            # Text format
            print_header("Lint Results")
            
            for result in report.results:
                print_lint_results(
                    prompt_name=result.prompt_name,
                    version=result.version,
                    issues=[i.to_dict() for i in result.issues],
                    passed=result.passed,
                )
            
            # Summary
            print_header("Summary")
            click.echo(report.summary())
            
            if not report.passed:
                sys.exit(1)
            return
        
        if not name or not version:
            print_error("Please specify prompt name and version, or use --all")
            sys.exit(1)
        
        result = lint_prompt(name, version, min_severity=severity)
        
        if output_format == 'json':
            import json
            click.echo(json.dumps(result.to_dict(), indent=2))
            return
        
        print_lint_results(
            prompt_name=result.prompt_name,
            version=result.version,
            issues=[i.to_dict() for i in result.issues],
            passed=result.passed,
        )
        
        if not result.passed:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Lint failed: {e}")
        print_error(f"Lint failed: {e}")
        sys.exit(1)


# =============================================================================
# Create Command
# =============================================================================


@cli.command()
@click.argument("name")
@click.argument("version", default="v1")
@click.option(
    '--type', '-t', 'template_type',
    type=click.Choice(['basic', 'chat', 'structured']),
    default='basic',
    help='Prompt template type'
)
@click.pass_context
def create(ctx, name, version, template_type):
    """
    Create a new prompt file.
    
    \b
    Examples:
      promptops create email_summary
      promptops create chat_bot v1 --type chat
      promptops create analyzer v1 --type structured
    """
    try:
        file_path = create_prompt(name, version, template_type)
        print_success(f"Created prompt: {file_path}")
        
        print_info("Next steps:")
        click.echo(f"  1. Edit {file_path}")
        click.echo(f"  2. Run: promptops lint {name} {version}")
        click.echo(f"  3. Run: promptops test {name} {version}")
        
    except FileExistsError:
        print_error(f"Prompt {name} {version} already exists")
        sys.exit(1)
    except Exception as e:
        print_error(f"Failed to create prompt: {e}")
        sys.exit(1)


# =============================================================================
# Approval Commands
# =============================================================================


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--user', required=True, help='User requesting approval')
def request_approval(name, version, user):
    """Request approval for a prompt."""
    item_id = f"{name}:{version}"
    approval_mgr.request_approval(item_id, user)
    print_success(f"Approval requested for {item_id}")


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--approver', required=True, help='User approving')
@click.option('--reason', default=None, help='Reason for approval')
def approve(name, version, approver, reason):
    """Approve a prompt for production."""
    item_id = f"{name}:{version}"
    approval_mgr.approve(item_id, approver, reason)
    print_success(f"Approved {item_id}")


@cli.command()
@click.argument("name")
@click.argument("version")
def approval_status(name, version):
    """Check approval status for a prompt."""
    item_id = f"{name}:{version}"
    status = approval_mgr.status(item_id)
    
    icon = "✅" if status == ApprovalStatus.APPROVED else "⏳" if status == ApprovalStatus.PENDING else "❌"
    click.echo(f"{icon} {item_id}: {status.name}")


# =============================================================================
# Safety Commands
# =============================================================================


@cli.command()
@click.argument("name", required=False)
@click.argument("version", required=False)
@click.option('--all', '-a', 'scan_all', is_flag=True, help='Scan all prompts')
@click.option('--strict', is_flag=True, help='Use strict mode')
@click.pass_context
def check_safety(ctx, name, version, scan_all, strict):
    """Run safety scan on prompts."""
    try:
        if scan_all:
            prompts_dir = Path("prompts")
            if not prompts_dir.exists():
                print_error("No 'prompts' directory found")
                sys.exit(1)
            
            issues_found = False
            for prompt_dir in prompts_dir.iterdir():
                if prompt_dir.is_dir():
                    for yaml_file in prompt_dir.glob("*.yaml"):
                        prompt_name = prompt_dir.name
                        prompt_version = yaml_file.stem
                        
                        try:
                            prompt = Prompt.load(prompt_name, prompt_version)
                            template = prompt.config.get('template', '')
                            report = run_safety_scan(template, strict=strict)
                            
                            if not getattr(report, 'safe', True):
                                print_error(f"{prompt_name} v{prompt_version}: Safety issues found")
                                issues_found = True
                            else:
                                print_success(f"{prompt_name} v{prompt_version}: Safe")
                        except Exception as e:
                            print_warning(f"{prompt_name} v{prompt_version}: {e}")
            
            if issues_found:
                sys.exit(1)
            return
        
        if not name or not version:
            print_error("Please specify prompt name and version, or use --all")
            sys.exit(1)
        
        prompt = Prompt.load(name, version)
        template = prompt.config.get('template', '')
        report = run_safety_scan(template, strict=strict)
        
        if getattr(report, 'safe', True):
            print_success(f"{name} v{version}: Safe")
        else:
            print_error(f"{name} v{version}: Safety issues found")
            for finding in getattr(report, 'findings', []):
                print_warning(f"  - {getattr(finding, 'message', str(finding))}")
            sys.exit(1)
        
    except Exception as e:
        print_error(f"Safety scan failed: {e}")
        sys.exit(1)


# =============================================================================
# Budget Commands
# =============================================================================


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--amount', type=float, required=True, help='Budget amount to allocate')
def allocate_budget(name, version, amount):
    """Allocate budget for a prompt."""
    item_id = f"{name}:{version}"
    budget_pool.allocate(item_id, amount)
    print_success(f"Allocated ${amount:.2f} to {item_id}")


# =============================================================================
# Cache Commands
# =============================================================================


@cli.command()
@click.option('--stats', is_flag=True, help='Show cache statistics')
def cache(stats):
    """Manage the prompt cache."""
    cache_mgr = get_cache()
    
    if stats:
        cache_stats = cache_mgr.get_stats()
        print_panel(
            f"Size: {cache_stats.size}/{cache_stats.max_size}\n"
            f"Hits: {cache_stats.hits}\n"
            f"Misses: {cache_stats.misses}\n"
            f"Hit Rate: {cache_stats.hit_rate:.1%}\n"
            f"Evictions: {cache_stats.evictions}",
            title="Cache Statistics",
            style="info"
        )
    else:
        # Show help
        click.echo("Cache commands:")
        click.echo("  promptops cache --stats     Show cache statistics")
        click.echo("  promptops cache-clear       Clear the cache")


@cli.command('cache-clear')
def cache_clear():
    """Clear the prompt cache."""
    count = clear_cache()
    print_success(f"Cleared {count} cached entries")


# =============================================================================
# Rollback Command
# =============================================================================


@cli.command()
@click.argument("name")
@click.argument("version")
def rollback(name, version):
    """Rollback a prompt to previous version."""
    item_id = f"{name}:{version}"
    rollback_prompt(item_id)
    print_success(f"Rolled back {item_id}")


# =============================================================================
# List Commands
# =============================================================================

@cli.command('list')
def list_prompts():
    """List all available prompts."""
    prompts_dir = Path("prompts")
    
    if not prompts_dir.exists():
        print_warning("No 'prompts' directory found")
        return
    
    prompts = []
    for prompt_dir in sorted(prompts_dir.iterdir()):
        if prompt_dir.is_dir():
            for yaml_file in sorted(prompt_dir.glob("*.yaml")):
                prompts.append({
                    "name": prompt_dir.name,
                    "version": yaml_file.stem,
                    "path": str(yaml_file),
                })
    
    if not prompts:
        print_info("No prompts found")
        return
    
    print_table(
        "Available Prompts",
        columns=[
            {"header": "Name", "style": "bold"},
            {"header": "Version"},
            {"header": "Path", "style": "dim"},
        ],
        rows=[[p["name"], p["version"], p["path"]] for p in prompts],
    )


@cli.command()
@click.argument("name")
@click.argument("version")
def show(name, version):
    """Show details for a prompt."""
    try:
        prompt = Prompt.load(name, version)
        
        print_header(f"{name} v{version}")
        
        # Show template
        template = prompt.config.get('template', '')
        print_yaml(template, title="Template")
        
        # Show metadata
        click.echo()
        print_info(f"Approved: {'✅' if prompt.config.get('approved') else '❌'}")
        print_info(f"Provider: {prompt.config.get('provider', 'default')}")
        print_info(f"Tests: {len(prompt.config.get('tests', []))}")
        
    except Exception as e:
        print_error(f"Failed to load prompt: {e}")
        sys.exit(1)


@cli.command()
def version():
    """Show CLI version."""
    print_banner()


# =============================================================================
# Entry Point
# =============================================================================


def main():
    """Main entry point for the CLI."""
    try:
        cli(obj={})
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled")
        sys.exit(130)
    except Exception as e:
        logger.exception("Unexpected error")
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
