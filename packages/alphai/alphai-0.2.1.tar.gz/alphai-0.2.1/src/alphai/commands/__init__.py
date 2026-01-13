"""Command modules for alphai CLI.

This package contains the CLI commands organized by domain:
- jupyter: Jupyter Lab/Notebook commands
- docker: Docker container management (run, cleanup)
- orgs: Organization listing
- projects: Project listing
- config: Configuration management
"""

from .jupyter import jupyter
from .docker import run, cleanup
from .orgs import orgs
from .projects import projects
from .config import config

__all__ = [
    'jupyter',
    'run',
    'cleanup',
    'orgs',
    'projects',
    'config',
]
