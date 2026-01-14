"""
Project Scaffolding Module for PromptOps.

Provides project initialization and template generation:
- Create new PromptOps projects
- Generate prompt templates
- Set up GitHub Actions
- Initialize configuration files
"""

from .generator import (
    ScaffoldGenerator,
    ProjectTemplate,
    init_project,
    create_prompt,
    generate_github_action,
)

__all__ = [
    "ScaffoldGenerator",
    "ProjectTemplate",
    "init_project",
    "create_prompt",
    "generate_github_action",
]
