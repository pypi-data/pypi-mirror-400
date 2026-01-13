"""Project commands for alphai CLI."""

from typing import Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..client import AlphAIClient
from ..config import Config

console = Console()


@click.command()
@click.option('--org', help='Organization slug to filter by')
@click.pass_context
def projects(ctx: click.Context, org: Optional[str]) -> None:
    """List your projects."""
    client: AlphAIClient = ctx.obj['client']
    config: Config = ctx.obj['config']
    
    # Use provided org or current org
    org_id = org or config.current_org
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching projects...", total=None)
        projects_data = client.get_projects(org_id)
        progress.update(task, completed=1)
    
    client.display_projects(projects_data)
