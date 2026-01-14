# PromptOps

**CI/CD for AI prompts.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/promptops.svg)](https://badge.fury.io/py/promptops)
[![CI](https://github.com/promptops/promptops/actions/workflows/promptops.yml/badge.svg)](https://github.com/promptops/promptops/actions)

PromptOps helps teams **version, test, lint, cache, and safely deploy AI prompts** — just like modern DevOps, but for LLM behavior.

If prompts can break production, they deserve:

- ✅ **Tests** — Rule-based and semantic assertions
- ✅ **Linting** — Best practices and security checks
- ✅ **Caching** — Fast, cost-effective responses
- ✅ **Approvals** — Gated deployments with audit trails
- ✅ **Rollbacks** — Automatic recovery with circuit breakers
- ✅ **Cost & Safety Controls** — Budget limits and content scanning
- ✅ **Beautiful CLI** — Rich terminal output for developer joy

---

## 📑 Table of Contents

- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [CLI Reference](#-cli-reference)
- [Project Initialization](#-project-initialization)
- [Prompt Linting](#-prompt-linting)
- [Response Caching](#-response-caching)
- [Testing](#-testing)
- [Safety Scanning](#-safety-scanning)
- [Approval Workflow](#-approval-workflow)
- [Cost Management](#-cost-management)
- [Rollback Engine](#-rollback-engine)
- [GitHub Actions](#-github-actions)
- [Python API](#-python-api)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## ✨ Features

### 🎨 Beautiful CLI with Rich Output
Colorful, informative terminal output powered by Rich library:
- Progress bars and spinners
- Syntax-highlighted YAML
- Beautiful tables and panels
- Interactive project trees

### 📁 Project Scaffolding
Initialize new projects with best-practice structure:
```bash
promptops init my-ai-app
```

### 🔍 Prompt Linting
11+ built-in rules checking for:
- Missing templates or tests
- Security vulnerabilities
- Cost optimization opportunities
- Best practice violations

### ⚡ Response Caching
Three caching backends for faster, cheaper operations:
- **Memory Cache** — Fast in-process caching
- **File Cache** — Persistent file-based storage
- **SQLite Cache** — Production-ready with TTL support

### 🧪 Prompt Testing
- **Rule-based assertions** — Word count, JSON validation, regex
- **Semantic tests** — LLM-as-Judge evaluation
- **CI-friendly output** — GitHub Actions integration

### 🔒 Safety Scanning
- PII detection (SSN, credit cards, emails)
- Prompt injection detection
- Sensitive keyword filtering
- Risk scoring

### ✅ Approval Gates
- Workflow management with audit trail
- Environment enforcement
- Gated production deployments

### ⏪ Rollback Engine
- Circuit breaker pattern
- Automatic failure recovery
- Health monitoring

### 💰 Budget Management
- Per-model cost tracking
- Budget periods and alerts
- Usage analytics

---

## 📦 Installation

```bash
pip install promptops
```

Install with all extras:
```bash
pip install "promptops[all]"
```

Install for development:
```bash
git clone https://github.com/promptops/promptops.git
cd promptops
pip install -e ".[dev]"
```

### Requirements

- **Python 3.9+**
- **OpenAI API key** (for LLM features)

```bash
export OPENAI_API_KEY=your_key_here
```

---

## 🚀 Quick Start

### 1. Initialize a project

```bash
promptops init my-ai-app
cd my-ai-app
```

This creates:
```
my-ai-app/
├── prompts/
│   └── example/
│       └── v1.yaml
├── promptops.yaml
├── .gitignore
└── README.md
```

### 2. Create a prompt

```bash
promptops create email_summary v1
```

Edit `prompts/email_summary/v1.yaml`:

```yaml
template: |
  Summarize the following email politely and concisely:
  
  {email}

approved: false
provider: openai

tests:
  - name: polite_summary
    input:
      email: "This is a long email about a delayed shipment..."
    assert:
      max_words: 60
      min_words: 10
      must_exclude: ["hate", "stupid"]
```

### 3. Lint your prompts

```bash
promptops lint --all
```

### 4. Run tests

```bash
promptops test email_summary v1
```

### 5. Run the prompt

```bash
promptops run email_summary v1
```

---

## 📖 CLI Reference

### Global Options

```bash
promptops --help
promptops --version
promptops --env prod     # Set environment
promptops --verbose      # Enable debug output
```

### Commands

| Command | Description |
|---------|-------------|
| `init <name>` | Create a new PromptOps project |
| `create <name> <version>` | Create a new prompt file |
| `run <name> <version>` | Execute a prompt |
| `test <name> <version>` | Run prompt tests |
| `lint [--all]` | Lint prompts for issues |
| `list` | List all available prompts |
| `show <name> <version>` | Show prompt details |
| `check-safety [--all]` | Run safety scans |
| `cache --stats` | Show cache statistics |
| `cache-clear` | Clear response cache |
| `approve <name> <version>` | Approve a prompt |
| `rollback <name> <version>` | Rollback to previous version |

---

## 📁 Project Initialization

### Basic Setup

```bash
promptops init my-project
```

### With Options

```bash
# Use full template with more examples
promptops init my-project --template full

# Skip GitHub Actions setup
promptops init my-project --no-github-actions

# Specify provider
promptops init my-project --provider anthropic

# Dry run - see what would be created
promptops init my-project --dry-run
```

### Templates

| Template | Contents |
|----------|----------|
| `minimal` | Just config and one prompt |
| `basic` | Config, examples, and tests |
| `full` | Everything including CI/CD |

---

## 🔍 Prompt Linting

### Lint All Prompts

```bash
promptops lint --all
```

### Lint Single Prompt

```bash
promptops lint email_summary v1
```

### Filter by Severity

```bash
promptops lint --all --severity warning  # Only warnings and errors
promptops lint --all --severity error    # Only errors
```

### Output Formats

```bash
promptops lint --all --format text     # Human-readable (default)
promptops lint --all --format json     # JSON output
promptops lint --all --format github   # GitHub Actions annotations
```

### Built-in Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `template-required` | ERROR | Template must be defined |
| `tests-required` | WARNING | Tests should be defined |
| `security-patterns` | ERROR | No hardcoded secrets |
| `prompt-length` | WARNING | Reasonable token count |
| `cache-config` | INFO | Caching recommended |
| `provider-valid` | ERROR | Valid provider specified |
| `jinja-syntax` | ERROR | Valid Jinja2 syntax |
| `variable-naming` | WARNING | Consistent variable names |
| `test-coverage` | WARNING | Test all assertions |
| `model-specified` | INFO | Explicit model version |
| `metadata-complete` | INFO | Description and tags |

---

## ⚡ Response Caching

### Enable Caching

Caching is enabled by default. Disable for a single run:

```bash
promptops run email_summary v1 --no-cache
```

### Cache Configuration

In `promptops.yaml`:

```yaml
cache:
  backend: sqlite      # memory, file, or sqlite
  ttl: 3600           # Time-to-live in seconds
  max_size: 1000      # Maximum entries
  path: .promptops/cache  # Cache directory
```

### Cache Management

```bash
# View cache statistics
promptops cache --stats

# Clear all cached responses
promptops cache-clear
```

### Python API

```python
from promptops.cache import get_cache, configure_cache, cache_prompt

# Configure cache
configure_cache(
    backend="sqlite",
    ttl=3600,
    max_size=1000
)

# Use decorator
@cache_prompt(ttl=1800)
def get_summary(text: str) -> str:
    return prompt.run({"text": text})

# Manual cache access
cache = get_cache()
cache.set("key", "value", ttl=3600)
value = cache.get("key")
```

### Cache Backends

| Backend | Use Case | Persistence |
|---------|----------|-------------|
| `memory` | Development, testing | No |
| `file` | Single-machine production | Yes |
| `sqlite` | Production, shared access | Yes |

---

## 🧪 Testing

### Run All Tests

```bash
promptops test --all
```

### Test Single Prompt

```bash
promptops test email_summary v1
```

### Test Assertions

```yaml
tests:
  - name: basic_test
    input:
      email: "Test email content..."
    assert:
      # Length assertions
      max_words: 100
      min_words: 10
      max_chars: 500
      
      # Content assertions
      must_include: ["summary", "regards"]
      must_exclude: ["error", "fail"]
      matches_pattern: "^Dear.*"
      
      # Format assertions
      is_json: true
      
      # Semantic assertions (LLM-based)
      semantic:
        - is_polite
        - summary_present
        - professional_tone
```

### Semantic Testing

Use LLM-as-Judge for meaning-based evaluation:

```yaml
tests:
  - name: semantic_test
    input:
      text: "Angry customer complaint..."
    assert:
      semantic:
        - response_is_empathetic
        - offers_solution
        - maintains_brand_voice
```

---

## 🔒 Safety Scanning

### Scan All Prompts

```bash
promptops check-safety --all
```

### Strict Mode

```bash
promptops check-safety --all --strict
```

### Detection Capabilities

- **PII Detection**: SSN, credit cards, emails, phone numbers
- **Injection Detection**: Jailbreak attempts, system overrides
- **Sensitive Keywords**: Customizable patterns

### Configuration

```yaml
policies:
  safety:
    block_pii: true
    strict_mode: true
    custom_patterns:
      - "CONFIDENTIAL"
      - "password.*="
```

---

## ✅ Approval Workflow

### Request Approval

```bash
promptops request-approval email_summary v1 --user alice
```

### Approve Prompt

```bash
promptops approve email_summary v1 --approver bob --reason "Reviewed and tested"
```

### Check Status

```bash
promptops approval-status email_summary v1
```

### Python API

```python
from promptops import ApprovalManager

manager = ApprovalManager()
manager.request_approval("email_summary:v1", "alice")
manager.approve("email_summary:v1", "bob", reason="LGTM")
status = manager.status("email_summary:v1")
```

---

## 💰 Cost Management

### Allocate Budget

```bash
promptops allocate-budget email_summary v1 --amount 10.00
```

### Configuration

```yaml
policies:
  cost:
    max_daily_spend: 100.0
    alerts:
      - threshold: 0.5
        action: warn
      - threshold: 0.9
        action: alert
```

### Python API

```python
from promptops.cost import BudgetPool

pool = BudgetPool()
pool.allocate("email_summary:v1", 10.0)
pool.consume("email_summary:v1", 0.05)
balance = pool.balance("email_summary:v1")
```

---

## ⏪ Rollback Engine

### Manual Rollback

```bash
promptops rollback email_summary v1
```

### Circuit Breaker

Automatic rollback after failures:

```yaml
policies:
  rollback:
    circuit_breaker:
      failure_threshold: 5
      recovery_timeout: 60
```

### Python API

```python
from promptops.rollback import RollbackEngine

engine = RollbackEngine()
engine.record_failure("email_summary:v1", Exception("API error"))

if engine.should_circuit_break("email_summary:v1"):
    engine.rollback("email_summary:v1")
```

---

## 🔄 GitHub Actions

PromptOps includes a ready-to-use GitHub Actions workflow.

### Setup

When initializing a project:
```bash
promptops init my-project  # Includes .github/workflows/promptops.yml
```

Or copy the workflow manually:
```bash
cp .github/workflows/promptops.yml your-repo/.github/workflows/
```

### Workflow Features

- **Lint on Push**: Validate prompts on every push
- **Safety Scan**: Automatic security checks
- **Test Suite**: Run all prompt tests
- **Approval Gates**: Enforce approvals for production
- **Deployment**: Automated production deployment

### Required Secrets

Add these to your repository secrets:

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for tests |
| `ANTHROPIC_API_KEY` | (Optional) Anthropic key |
| `DEPLOY_TOKEN` | Deployment credentials |

### Workflow Jobs

```yaml
jobs:
  lint:      # 🔍 Lint all prompts
  safety:    # 🔒 Security scan
  test:      # 🧪 Run tests
  approval:  # ✅ Check approvals
  deploy:    # 🚀 Deploy to production
  rollback:  # ⏪ Manual rollback trigger
```

---

## 🐍 Python API

### Basic Usage

```python
from promptops import Prompt

# Load and run a prompt
prompt = Prompt.load("email_summary", "v1")
result = prompt.run({"email": "..."})
```

### With Caching

```python
from promptops import Prompt
from promptops.cache import cache_prompt

@cache_prompt(ttl=3600)
def summarize(email: str) -> str:
    prompt = Prompt.load("email_summary", "v1")
    return prompt.run({"email": email})
```

### Run Tests

```python
from promptops import Prompt
from promptops.testing import run_tests

prompt = Prompt.load("email_summary", "v1")
report = run_tests(prompt, prompt.provider, prompt.config["tests"])

if not report.passed:
    for failure in report.failures:
        print(f"Failed: {failure.name} - {failure.reason}")
```

### Lint Prompts

```python
from promptops.lint import lint_prompt, lint_all_prompts

# Single prompt
result = lint_prompt("email_summary", "v1")
print(f"Passed: {result.passed}")
for issue in result.issues:
    print(f"  {issue.severity}: {issue.message}")

# All prompts
report = lint_all_prompts("prompts/")
print(report.summary())
```

### Custom Lint Rules

```python
from promptops.lint import LintRule, LintIssue, LintSeverity

class CustomRule(LintRule):
    id = "custom-rule"
    name = "Custom Rule"
    description = "Check for custom requirements"
    severity = LintSeverity.WARNING
    
    def check(self, config: dict, file_path: str) -> list[LintIssue]:
        issues = []
        if "custom_field" not in config:
            issues.append(self.create_issue(
                message="Missing custom_field",
                line=1
            ))
        return issues
```

---

## ⚙️ Configuration

### Prompt YAML Schema

```yaml
# Required
template: |
  Your prompt with {variables}

# Optional
approved: false           # Approval status
provider: openai          # Provider name
model: gpt-4             # Specific model
description: "..."        # Human description
tags: [summarization]     # Categorization

# Caching
cache:
  enabled: true
  ttl: 3600

# Tests
tests:
  - name: test_name
    input:
      variable: "value"
    assert:
      max_words: 100
      must_include: ["word"]
      semantic:
        - is_coherent
```

### Global Config (promptops.yaml)

```yaml
# Default provider
provider: openai

# Environment settings
environments:
  dev:
    require_approval: false
    strict_safety: false
  staging:
    require_approval: false
    strict_safety: true
  prod:
    require_approval: true
    strict_safety: true

# Caching
cache:
  backend: sqlite
  ttl: 3600
  max_size: 1000

# Policies
policies:
  safety:
    block_pii: true
    strict_mode: true
  cost:
    max_daily_spend: 100.0
  rollback:
    failure_threshold: 5
```

---

## 📁 Project Structure

```
promptops/
├── __init__.py              # Package exports
├── prompt.py                # Core Prompt class
├── loader.py                # YAML/remote loading
├── renderer.py              # Template rendering
├── guard.py                 # Safety guard
├── approval.py              # Approval workflow
├── policies.py              # Global policies
├── env.py                   # Environment detection
├── diff.py                  # Prompt diffing
├── exceptions.py            # Exception hierarchy
├── utils.py                 # Utility functions
├── promptops.yaml           # Default policies
├── pyproject.toml           # Package config
├── cli/
│   ├── __init__.py
│   ├── main.py              # CLI commands
│   └── console.py           # Rich output helpers
├── cache/
│   ├── __init__.py
│   └── manager.py           # Cache backends
├── lint/
│   ├── __init__.py
│   ├── rules.py             # Lint rules
│   └── linter.py            # Linter engine
├── scaffold/
│   ├── __init__.py
│   └── generator.py         # Project scaffolding
├── cost/
│   ├── __init__.py
│   └── budget.py            # Budget management
├── providers/
│   ├── __init__.py
│   └── openai_provider.py   # OpenAI integration
├── rollback/
│   ├── __init__.py
│   ├── engine.py            # Rollback logic
│   └── store.py             # Failure tracking
├── safety/
│   ├── __init__.py
│   └── scanner.py           # Safety scanning
└── testing/
    ├── __init__.py
    ├── assertions.py        # Rule assertions
    ├── llm_judge.py         # Semantic tests
    ├── results.py           # Test results
    └── runner.py            # Test runner
```

---

## 🗺️ Roadmap

### Completed ✅
- [x] Prompt versioning and loading
- [x] Rule-based testing
- [x] Semantic testing (LLM-as-Judge)
- [x] Safety scanning
- [x] Approval workflow
- [x] Rollback engine
- [x] Budget management
- [x] Rich CLI output
- [x] Project scaffolding (`promptops init`)
- [x] Prompt linting (11+ rules)
- [x] Response caching (3 backends)
- [x] GitHub Actions workflow

### Coming Soon 🔜
- [ ] VS Code extension
- [ ] Web dashboard
- [ ] Prompt playground
- [ ] A/B testing framework
- [ ] Multi-provider support (Anthropic, Cohere)
- [ ] Prompt embeddings and search
- [ ] Team collaboration features

---

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

```bash
# Setup development environment
git clone https://github.com/promptops/promptops.git
cd promptops
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check promptops
mypy promptops
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 💬 Support

- 📚 [Documentation](https://promptops.dev/docs)
- 💬 [Discord Community](https://discord.gg/promptops)
- 🐛 [Issue Tracker](https://github.com/promptops/promptops/issues)
- 📧 [Email Support](mailto:support@promptops.dev)

---

<p align="center">
  <b>Made with ❤️ for the AI engineering community</b>
</p>
