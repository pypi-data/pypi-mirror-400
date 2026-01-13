"""Main CLI module for alphai.

This module provides the main entry point and core commands (login, logout, status).
Domain-specific commands are organized in the commands/ package.
"""

import sys
from typing import Optional

import click
from rich.console import Console
from rich.prompt import Confirm

from .client import AlphAIClient
from .config import Config
from .auth import AuthManager
from .utils import setup_logging, get_logger

# Import command groups from commands package
from .commands.jupyter import jupyter
from .commands.docker import run, cleanup
from .commands.orgs import orgs
from .commands.projects import projects
from .commands.config import config
from .commands.notebooks import notebooks


console = Console()
logger = get_logger(__name__)


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--version', is_flag=True, help='Show version information')
@click.pass_context
def main(ctx: click.Context, debug: bool, version: bool) -> None:
    """alphai - A CLI tool for the runalph.ai platform."""
    
    if version:
        from . import __version__
        console.print(f"alphai version {__version__}")
        return
    
    # Set up context
    ctx.ensure_object(dict)
    cfg = Config.load()
    
    if debug:
        cfg.debug = True
        cfg.save()
    
    # Initialize logging
    setup_logging(debug=debug or cfg.debug)
    logger.info(f"alphai CLI started (debug={debug or cfg.debug})")
    
    ctx.obj['config'] = cfg
    ctx.obj['client'] = AlphAIClient(cfg)
    
    # If no command is provided, show status
    if ctx.invoked_subcommand is None:
        ctx.obj['client'].display_status()


@main.command()
@click.option('--token', help='Bearer token for authentication')
@click.option('--api-url', help='API base URL (optional)')
@click.option('--browser', is_flag=True, help='Use browser-based authentication')
@click.option('--force', is_flag=True, help='Force re-authentication even if already logged in')
@click.pass_context
def login(ctx: click.Context, token: Optional[str], api_url: Optional[str], browser: bool, force: bool) -> None:
    """Authenticate with the runalph.ai API.
    
    If you're already authenticated, this command will validate your existing
    credentials and exit. Use --force to re-authenticate."""
    cfg: Config = ctx.obj['config']
    
    if api_url:
        cfg.api_url = api_url
    
    auth_manager = AuthManager(cfg)
    
    # Check if already authenticated (unless force is used or token is provided)
    if not force and not token:
        if auth_manager.check_existing_authentication():
            console.print("[green]✓ You are already logged in![/green]")
            console.print("[dim]Use 'alphai login --force' to re-authenticate or 'alphai status' to view details[/dim]")
            return
    
    if token:
        # Use provided token
        success = auth_manager.login_with_token(token)
    elif browser:
        # Use browser login
        success = auth_manager.browser_login()
    else:
        # Interactive login (will offer browser as default option)
        success = auth_manager.interactive_login()
    
    if success:
        cfg.save()
        console.print("[green]✓ Successfully logged in![/green]")
        
        # Test the connection
        client = AlphAIClient(cfg)
        if client.test_connection():
            console.print("[green]✓ Connection to API verified[/green]")
        else:
            console.print("[yellow]⚠ Warning: Could not verify API connection[/yellow]")
    else:
        console.print("[red]✗ Login failed[/red]")
        sys.exit(1)


@main.command()
@click.pass_context
def logout(ctx: click.Context) -> None:
    """Log out and clear authentication credentials."""
    cfg: Config = ctx.obj['config']
    
    if not cfg.bearer_token:
        console.print("[yellow]Already logged out[/yellow]")
        return
    
    if Confirm.ask("Are you sure you want to log out?"):
        cfg.clear_bearer_token()
        cfg.current_org = None
        cfg.save()
        console.print("[green]✓ Successfully logged out[/green]")


@main.command()
@click.pass_context
def status(ctx: click.Context) -> None:
    """Show current configuration and authentication status."""
    client: AlphAIClient = ctx.obj['client']
    client.display_status()


# Register commands from commands package
main.add_command(jupyter)
main.add_command(run)
main.add_command(cleanup)
main.add_command(orgs)
main.add_command(projects)
main.add_command(config)
main.add_command(notebooks, name="nb")


if __name__ == '__main__':
    main()
