"""
Project Scaffolding Generator for PromptOps.

Generates new PromptOps projects with:
- Proper directory structure
- Example prompts with tests
- Configuration files
- GitHub Actions CI/CD
- Documentation templates
"""

import os
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ProjectTemplate(Enum):
    """Available project templates."""
    BASIC = "basic"
    FULL = "full"
    MINIMAL = "minimal"


@dataclass
class ScaffoldConfig:
    """Configuration for project scaffolding."""
    project_name: str
    template: ProjectTemplate = ProjectTemplate.BASIC
    include_github_actions: bool = True
    include_examples: bool = True
    include_tests: bool = True
    provider: str = "openai"
    author: str = ""
    description: str = ""


@dataclass
class GeneratedFile:
    """Represents a file to be generated."""
    path: str
    content: str
    overwrite: bool = False


class ScaffoldGenerator:
    """
    Generates PromptOps project scaffolding.
    
    Creates a complete project structure with:
    - prompts/ directory with example prompts
    - promptops.yaml configuration
    - GitHub Actions workflow (optional)
    - README.md with quickstart guide
    """
    
    def __init__(self, config: ScaffoldConfig):
        self.config = config
        self.base_path = Path(config.project_name)
        self.files: List[GeneratedFile] = []
    
    def generate(self) -> List[GeneratedFile]:
        """Generate all project files."""
        self.files = []
        
        # Core structure
        self._add_promptops_yaml()
        self._add_gitignore()
        self._add_readme()
        
        # Examples
        if self.config.include_examples:
            self._add_example_prompt()
        
        # GitHub Actions
        if self.config.include_github_actions:
            self._add_github_action()
        
        # Additional files for full template
        if self.config.template == ProjectTemplate.FULL:
            self._add_full_template_files()
        
        return self.files
    
    def write_files(self, dry_run: bool = False) -> List[str]:
        """
        Write all generated files to disk.
        
        Args:
            dry_run: If True, don't actually write files.
            
        Returns:
            List of created file paths.
        """
        created = []
        
        for file in self.files:
            full_path = self.base_path / file.path
            
            if dry_run:
                logger.info(f"[DRY RUN] Would create: {full_path}")
                created.append(str(full_path))
                continue
            
            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists
            if full_path.exists() and not file.overwrite:
                logger.warning(f"Skipping existing file: {full_path}")
                continue
            
            # Write file
            full_path.write_text(file.content)
            logger.info(f"Created: {full_path}")
            created.append(str(full_path))
        
        return created
    
    def _add_file(self, path: str, content: str, overwrite: bool = False) -> None:
        """Add a file to the generation list."""
        self.files.append(GeneratedFile(path=path, content=content, overwrite=overwrite))
    
    def _add_promptops_yaml(self) -> None:
        """Add the main configuration file."""
        content = f'''# PromptOps Configuration
# Documentation: https://github.com/prabhnoor12/promptops

# Project metadata
project:
  name: "{self.config.project_name}"
  description: "{self.config.description or 'AI prompts managed with PromptOps'}"
  version: "0.1.0"

# Global policies applied to all prompts
policies:
  # Safety settings
  safety:
    block_pii: true
    strict_mode: false
    banned_terms: []
  
  # Cost control
  cost:
    max_per_call: 0.10
    daily_limit: 10.00
    alert_threshold: 0.8
  
  # Approval workflow
  approval:
    required_for_prod: true
    require_reason: false
  
  # Rollback settings
  rollback:
    failure_threshold: 3
    window_seconds: 300
    auto_recover: true

# Default provider configuration
providers:
  default: "{self.config.provider}"
  openai:
    model: "gpt-4o-mini"
    temperature: 0.7
    max_tokens: 1000

# Environment-specific overrides
environments:
  dev:
    policies:
      approval:
        required_for_prod: false
  
  staging:
    policies:
      safety:
        strict_mode: true
  
  prod:
    policies:
      safety:
        strict_mode: true
      approval:
        required_for_prod: true
        require_reason: true

# Cache configuration
cache:
  enabled: true
  ttl: 3600
  backend: "memory"  # Options: memory, file, redis

# Logging
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
'''
        self._add_file("promptops.yaml", content)
    
    def _add_gitignore(self) -> None:
        """Add .gitignore file."""
        content = '''# PromptOps
.promptops_cache/
*.cache

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
htmlcov/

# Secrets - NEVER commit these!
.env.local
.env.*.local
secrets.yaml
*.pem
*.key
'''
        self._add_file(".gitignore", content)
    
    def _add_readme(self) -> None:
        """Add README.md file."""
        content = f'''# {self.config.project_name}

{self.config.description or 'AI prompts managed with PromptOps.'}

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key

```bash
export OPENAI_API_KEY=your_key_here
```

### Installation

```bash
pip install promptops
```

### Run a Prompt

```bash
promptops run example v1
```

### Test a Prompt

```bash
promptops test example v1
```

### Lint Prompts

```bash
promptops lint example v1
```

## 📁 Project Structure

```
{self.config.project_name}/
├── promptops.yaml       # Global configuration
├── prompts/
│   └── example/
│       └── v1.yaml      # Example prompt
└── .github/
    └── workflows/
        └── promptops.yml  # CI/CD workflow
```

## 📖 Documentation

See [PromptOps Documentation](https://github.com/prabhnoor12/promptops) for full details.

## 📄 License

MIT
'''
        self._add_file("README.md", content)
    
    def _add_example_prompt(self) -> None:
        """Add example prompt file."""
        content = '''# Example Prompt - Email Summarizer
# This prompt summarizes emails in a polite, concise manner.

template: |
  You are a helpful assistant that summarizes emails.
  
  Summarize the following email in 2-3 sentences.
  Be polite and professional.
  
  Email:
  {email}
  
  Summary:

# Prompt metadata
name: example
version: v1
description: "Summarizes emails politely and concisely"
author: ""

# Provider configuration (overrides global)
provider: openai
model: gpt-4o-mini
temperature: 0.5
max_tokens: 150

# Approval status
approved: false

# Test definitions
tests:
  - name: basic_summary
    description: "Test basic email summarization"
    input:
      email: |
        Hi Team,
        
        I wanted to follow up on our meeting yesterday. 
        We discussed the Q4 roadmap and agreed on the following priorities:
        1. Launch the new dashboard by October 15th
        2. Complete the API migration by November 1st
        3. Finalize the security audit by November 15th
        
        Please review and let me know if I missed anything.
        
        Best,
        Sarah
    assert:
      min_words: 10
      max_words: 100
      must_include:
        - "Q4"
      must_exclude:
        - "hate"
        - "stupid"
      semantic:
        - summary_present
        - is_coherent

  - name: short_email
    description: "Test with a very short email"
    input:
      email: "Meeting at 3pm. Please confirm."
    assert:
      min_words: 5
      max_words: 50

  - name: no_pii_in_output
    description: "Ensure no PII leaks"
    input:
      email: |
        Please send the report to john.doe@company.com
        His phone is 555-123-4567.
    assert:
      must_exclude:
        - "john.doe@company.com"
        - "555-123-4567"

# Caching configuration
cache:
  enabled: true
  ttl: 3600
  key_fields:
    - email
'''
        self._add_file("prompts/example/v1.yaml", content)
    
    def _add_github_action(self) -> None:
        """Add GitHub Actions workflow."""
        content = '''# PromptOps CI/CD Pipeline
# Runs prompt tests on every push and pull request

name: PromptOps CI

on:
  push:
    branches: [main, master]
    paths:
      - 'prompts/**'
      - 'promptops.yaml'
  pull_request:
    branches: [main, master]
    paths:
      - 'prompts/**'
      - 'promptops.yaml'
  workflow_dispatch:
    inputs:
      prompt_name:
        description: 'Specific prompt to test (leave empty for all)'
        required: false
        type: string

env:
  PROMPTOPS_ENV: staging

jobs:
  lint:
    name: Lint Prompts
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PromptOps
        run: pip install promptops
      
      - name: Run Linter
        run: promptops lint --all --format github

  test:
    name: Test Prompts
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PromptOps
        run: pip install promptops
      
      - name: Run Tests
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          if [ -n "${{ github.event.inputs.prompt_name }}" ]; then
            promptops test ${{ github.event.inputs.prompt_name }} --all-versions
          else
            promptops test --all
          fi

  safety-scan:
    name: Safety Scan
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PromptOps
        run: pip install promptops
      
      - name: Run Safety Scan
        run: promptops check-safety --all --strict

  cost-estimate:
    name: Cost Estimation
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PromptOps
        run: pip install promptops
      
      - name: Estimate Costs
        run: |
          echo "## 💰 Cost Estimate" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          promptops forecast --all --format markdown >> $GITHUB_STEP_SUMMARY

  approval-check:
    name: Check Approvals
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install PromptOps
        run: pip install promptops
      
      - name: Check Approval Status
        env:
          PROMPTOPS_ENV: prod
        run: promptops approval-status --all --require-approved
'''
        self._add_file(".github/workflows/promptops.yml", content)
    
    def _add_full_template_files(self) -> None:
        """Add additional files for full template."""
        
        # Add a more complex prompt example
        advanced_prompt = '''# Advanced Prompt - Code Review Assistant
# Uses structured output and multiple test cases

template: |
  You are an expert code reviewer. Review the following code and provide:
  
  1. **Summary**: A brief overview of what the code does
  2. **Issues**: List any bugs, security issues, or code smells
  3. **Suggestions**: Improvements for readability, performance, or best practices
  4. **Rating**: Score from 1-10
  
  Code to review:
  ```{language}
  {code}
  ```
  
  Respond in JSON format:
  ```json
  {
    "summary": "...",
    "issues": ["..."],
    "suggestions": ["..."],
    "rating": 0
  }
  ```

name: code_review
version: v1
description: "AI-powered code review assistant"

provider: openai
model: gpt-4o
temperature: 0.3
max_tokens: 1000

approved: false

tests:
  - name: python_review
    input:
      language: python
      code: |
        def add(a, b):
            return a + b
    assert:
      is_json: true
      min_words: 20
      
  - name: security_detection
    input:
      language: python
      code: |
        import os
        password = "hardcoded123"
        os.system(f"echo {password}")
    assert:
      is_json: true
      must_include:
        - "security"
'''
        self._add_file("prompts/code_review/v1.yaml", advanced_prompt)
        
        # Add CONTRIBUTING.md
        contributing = '''# Contributing to This Project

## Adding a New Prompt

1. Create a new directory under `prompts/`:
   ```bash
   mkdir -p prompts/my_prompt
   ```

2. Create a version file (e.g., `v1.yaml`):
   ```bash
   promptops create my_prompt v1
   ```

3. Define your template and tests

4. Run linting:
   ```bash
   promptops lint my_prompt v1
   ```

5. Run tests:
   ```bash
   promptops test my_prompt v1
   ```

6. Request approval for production:
   ```bash
   promptops request-approval my_prompt v1 --user your_name
   ```

## Versioning

- Use semantic versioning for prompts (v1, v2, etc.)
- Never modify approved prompts - create a new version instead
- Document breaking changes in the prompt file

## Testing

All prompts must have:
- At least one test case
- Both positive and negative test cases for critical prompts
- Semantic tests for output quality
'''
        self._add_file("CONTRIBUTING.md", contributing)


def init_project(
    project_name: str,
    template: str = "basic",
    include_github_actions: bool = True,
    include_examples: bool = True,
    provider: str = "openai",
    description: str = "",
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Initialize a new PromptOps project.
    
    Args:
        project_name: Name of the project directory to create.
        template: Project template (basic, full, minimal).
        include_github_actions: Whether to include GitHub Actions workflow.
        include_examples: Whether to include example prompts.
        provider: Default LLM provider.
        description: Project description.
        dry_run: If True, don't actually create files.
    
    Returns:
        Dictionary with created files and status.
    """
    # Validate project name
    if not project_name or not project_name.replace("-", "").replace("_", "").isalnum():
        raise ValueError(f"Invalid project name: {project_name}")
    
    # Check if directory exists
    if Path(project_name).exists() and not dry_run:
        raise FileExistsError(f"Directory already exists: {project_name}")
    
    # Create config
    config = ScaffoldConfig(
        project_name=project_name,
        template=ProjectTemplate(template),
        include_github_actions=include_github_actions,
        include_examples=include_examples,
        provider=provider,
        description=description,
    )
    
    # Generate and write files
    generator = ScaffoldGenerator(config)
    files = generator.generate()
    created = generator.write_files(dry_run=dry_run)
    
    return {
        "project_name": project_name,
        "files_created": created,
        "template": template,
        "dry_run": dry_run,
    }


def create_prompt(
    name: str,
    version: str = "v1",
    template_type: str = "basic",
    base_path: str = ".",
) -> str:
    """
    Create a new prompt file.
    
    Args:
        name: Prompt name.
        version: Version string (e.g., v1).
        template_type: Type of template (basic, chat, structured).
        base_path: Base path for prompts directory.
    
    Returns:
        Path to created file.
    """
    templates = {
        "basic": '''# {name} - {version}
template: |
  {description}
  
  Input: {{input}}
  
  Response:

name: {name}
version: {version}
description: "Add description here"

provider: openai
model: gpt-4o-mini
temperature: 0.7
max_tokens: 500

approved: false

tests:
  - name: basic_test
    input:
      input: "test input"
    assert:
      min_words: 5
      max_words: 200
''',
        "chat": '''# {name} - {version}
# Chat-style prompt with system message

system: |
  You are a helpful assistant.

template: |
  User: {{user_message}}
  
  Assistant:

name: {name}
version: {version}
description: "Chat assistant"

provider: openai
model: gpt-4o-mini
temperature: 0.7
max_tokens: 500

approved: false

tests:
  - name: greeting
    input:
      user_message: "Hello!"
    assert:
      min_words: 2
      semantic:
        - is_coherent
''',
        "structured": '''# {name} - {version}
# Structured output prompt (JSON)

template: |
  Analyze the following and respond in JSON format:
  
  Input: {{input}}
  
  Respond with:
  ```json
  {{
    "result": "...",
    "confidence": 0.0,
    "details": []
  }}
  ```

name: {name}
version: {version}
description: "Structured JSON output"

provider: openai
model: gpt-4o-mini
temperature: 0.3
max_tokens: 500
response_format:
  type: json_object

approved: false

tests:
  - name: json_output
    input:
      input: "test data"
    assert:
      is_json: true
''',
    }
    
    template = templates.get(template_type, templates["basic"])
    content = template.format(name=name, version=version, description="Your prompt here")
    
    # Create file
    prompt_dir = Path(base_path) / "prompts" / name
    prompt_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = prompt_dir / f"{version}.yaml"
    if file_path.exists():
        raise FileExistsError(f"Prompt already exists: {file_path}")
    
    file_path.write_text(content)
    return str(file_path)


def generate_github_action(base_path: str = ".") -> str:
    """
    Generate or update GitHub Actions workflow.
    
    Returns:
        Path to created workflow file.
    """
    config = ScaffoldConfig(project_name=".", include_github_actions=True)
    generator = ScaffoldGenerator(config)
    generator._add_github_action()
    
    workflow_path = Path(base_path) / ".github" / "workflows" / "promptops.yml"
    workflow_path.parent.mkdir(parents=True, exist_ok=True)
    workflow_path.write_text(generator.files[0].content)
    
    return str(workflow_path)


def get_project_structure(project_name: str, template: str = "basic") -> Dict[str, Any]:
    """Get the project structure as a dictionary (for display)."""
    structure = {
        "promptops.yaml": "config",
        ".gitignore": "config",
        "README.md": "docs",
        "prompts": {
            "example": {
                "v1.yaml": "prompt",
            },
        },
    }
    
    if template == "full":
        structure["prompts"]["code_review"] = {"v1.yaml": "prompt"}
        structure["CONTRIBUTING.md"] = "docs"
    
    structure[".github"] = {
        "workflows": {
            "promptops.yml": "workflow",
        },
    }
    
    return {project_name: structure}
