"""Configuration commands for alphai CLI."""

import sys

import click
from rich.console import Console
from rich.prompt import Confirm

from ..client import AlphAIClient
from ..config import Config as ConfigModel

console = Console()


@click.group()
@click.pass_context
def config(ctx: click.Context) -> None:
    """Manage configuration settings."""
    pass


@config.command('show')
@click.pass_context
def config_show(ctx: click.Context) -> None:
    """Show current configuration."""
    client: AlphAIClient = ctx.obj['client']
    client.display_status()


@config.command('set')
@click.argument('key')
@click.argument('value')
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    """Set a configuration value."""
    cfg: ConfigModel = ctx.obj['config']
    
    valid_keys = {'api_url', 'debug', 'current_org'}
    
    if key not in valid_keys:
        console.print(f"[red]Invalid configuration key. Valid keys: {', '.join(valid_keys)}[/red]")
        sys.exit(1)
    
    # Convert string values to appropriate types
    if key == 'debug':
        value = value.lower() in ('true', '1', 'yes', 'on')
    
    setattr(cfg, key, value)
    cfg.save()
    console.print(f"[green]✓ Set {key} = {value}[/green]")


@config.command('reset')
@click.pass_context
def config_reset(ctx: click.Context) -> None:
    """Reset configuration to defaults."""
    if Confirm.ask("Are you sure you want to reset all configuration to defaults?"):
        config_file = ConfigModel.get_config_file()
        if config_file.exists():
            config_file.unlink()
        
        # Clear keyring
        cfg = ConfigModel()
        cfg.clear_bearer_token()
        
        console.print("[green]✓ Configuration reset to defaults[/green]")

