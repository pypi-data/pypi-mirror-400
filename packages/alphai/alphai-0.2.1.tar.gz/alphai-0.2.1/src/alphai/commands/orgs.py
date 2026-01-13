"""Organization commands for alphai CLI."""

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..client import AlphAIClient

console = Console()


@click.command()
@click.pass_context
def orgs(ctx: click.Context) -> None:
    """List your organizations."""
    client: AlphAIClient = ctx.obj['client']
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching organizations...", total=None)
        orgs_data = client.get_organizations()
        progress.update(task, completed=1)
    
    client.display_organizations(orgs_data)
