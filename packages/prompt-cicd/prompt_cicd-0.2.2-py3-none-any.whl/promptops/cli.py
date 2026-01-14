
import click
import logging
import sys
from .prompt import Prompt
from .testing.runner import run_tests
from .approval import ApprovalManager, ApprovalStatus
from .cost.budget import BudgetPool
from .safety.scanner import SafetyScanner
from .rollback.engine import RollbackEngine
from .providers.openai_provider import OpenAIProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("promptops.cli")

approval_mgr = ApprovalManager()
budget_pool = BudgetPool()
scanner = SafetyScanner()
rollback_engine = RollbackEngine()


@click.group()
@click.option('--env', default='dev', help='Environment (dev, staging, prod)')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, env, verbose):
    """PromptOps CLI: Manage, run, test, and approve prompts."""
    ctx.ensure_object(dict)
    ctx.obj['env'] = env
    if verbose:
        logger.setLevel(logging.DEBUG)
    logger.debug(f"CLI started in {env} mode.")


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--dry-run', is_flag=True, help='Show what would run, but do not execute')
@click.pass_context
def run(ctx, name, version, dry_run):
    """Run a prompt by name and version."""
    try:
        prompt = Prompt.load(name, version)
        if dry_run:
            click.echo(f"[DRY RUN] Would run prompt: {name} v{version}")
            return
        result = prompt.run({"env": ctx.obj['env']})
        click.echo(result)
    except Exception as e:
        logger.error(f"Run failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.argument("version")
@click.pass_context
def test(ctx, name, version):
    """Run tests for a prompt."""
    try:
        prompt = Prompt.load(name, version)
        report = run_tests(prompt, prompt.provider, prompt.config.get("tests", []))
        click.echo("PASSED" if report.passed else "FAILED")
        if not report.passed:
            click.echo(report.summary())
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--user', required=True, help='User requesting approval')
def request_approval(name, version, user):
    """Request approval for a prompt."""
    item_id = f"{name}:{version}"
    approval_mgr.request_approval(item_id, user)
    click.echo(f"Approval requested for {item_id}")


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--approver', required=True, help='User approving')
@click.option('--reason', default=None, help='Reason for approval')
def approve(name, version, approver, reason):
    """Approve a prompt for production."""
    item_id = f"{name}:{version}"
    approval_mgr.approve(item_id, approver, reason)
    click.echo(f"Approved {item_id}")


@cli.command()
@click.argument("name")
@click.argument("version")
def approval_status(name, version):
    """Check approval status for a prompt."""
    item_id = f"{name}:{version}"
    status = approval_mgr.status(item_id)
    click.echo(f"{item_id} status: {status.name}")


@cli.command()
@click.argument("name")
@click.argument("version")
@click.option('--amount', type=float, required=True, help='Budget amount to allocate')
def allocate_budget(name, version, amount):
    """Allocate budget for a prompt."""
    item_id = f"{name}:{version}"
    budget_pool.allocate(item_id, amount)
    click.echo(f"Allocated ${amount:.2f} to {item_id}")


@cli.command()
@click.argument("name")
@click.argument("version")
def check_safety(name, version):
    """Run safety scan on a prompt."""
    prompt = Prompt.load(name, version)
    result = scanner.scan(prompt.text)
    click.echo(f"Safety scan: {result['risk']} risk. Issues: {result['issues']}")


@cli.command()
@click.argument("name")
@click.argument("version")
def rollback(name, version):
    """Rollback a prompt to previous version."""
    item_id = f"{name}:{version}"
    rollback_engine.rollback(item_id)
    click.echo(f"Rolled back {item_id}")


@cli.command()
def list_prompts():
    """List all available prompts."""
    prompts = Prompt.list_all()
    for p in prompts:
        click.echo(f"{p['name']} v{p['version']}")


@cli.command()
@click.argument("name")
@click.argument("version")
def show_prompt(name, version):
    """Show details for a prompt."""
    prompt = Prompt.load(name, version)
    click.echo(f"Name: {prompt.name}\nVersion: {prompt.version}\nText: {prompt.text}")


@cli.command()
def version():
    """Show CLI version."""
    click.echo("PromptOps CLI v1.0.0")
