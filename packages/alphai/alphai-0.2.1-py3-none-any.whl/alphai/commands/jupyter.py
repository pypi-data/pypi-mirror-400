"""Jupyter commands for alphai CLI.

Contains `jupyter lab` and `jupyter notebook` commands with shared implementation.
"""

import sys
import signal
from typing import Optional, List

import click
from rich.console import Console

from ..client import AlphAIClient
from ..config import Config
from ..jupyter_manager import JupyterManager
from ..cleanup import JupyterCleanupManager
from ..utils import get_logger

logger = get_logger(__name__)
console = Console()


def _get_frontend_url(api_url: str) -> str:
    """Convert API URL to frontend URL for browser opening."""
    if api_url.startswith("http://localhost") or api_url.startswith("https://localhost"):
        return api_url.replace("/api", "").rstrip("/")
    elif "runalph.ai" in api_url:
        if "/api" in api_url:
            return api_url.replace("runalph.ai/api", "runalph.ai").rstrip("/")
        else:
            return api_url.replace("runalph.ai", "runalph.ai").rstrip("/")
    else:
        return api_url.replace("/api", "").rstrip("/")


def _select_organization(client: AlphAIClient) -> str:
    """Interactively select an organization."""
    import questionary
    from rich.progress import Progress, SpinnerColumn, TextColumn
    
    logger.debug("Prompting user to select organization")
    console.print("[yellow]No organization specified. Please select one:[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching organizations...", total=None)
        orgs_data = client.get_organizations()
        progress.update(task, completed=1)
    
    if not orgs_data or len(orgs_data) == 0:
        logger.error("No organizations found for user")
        console.print("[red]No organizations found. Please create one first.[/red]")
        sys.exit(1)
    
    org_choices = []
    for org_data in orgs_data:
        display_name = f"{org_data.name} ({org_data.slug})"
        org_choices.append(questionary.Choice(title=display_name, value=org_data.slug))
    
    selected_org_slug = questionary.select(
        "Select organization (use ↑↓ arrows and press Enter):",
        choices=org_choices,
        style=questionary.Style([
            ('question', 'bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
            ('selected', 'fg:#cc5454'),
            ('instruction', 'fg:#888888 italic')
        ])
    ).ask()
    
    if not selected_org_slug:
        logger.warning("User cancelled organization selection")
        console.print("[red]No organization selected. Exiting.[/red]")
        sys.exit(1)
    
    selected_org_name = next((o.name for o in orgs_data if o.slug == selected_org_slug), selected_org_slug)
    console.print(f"[green]✓ Selected organization: {selected_org_name} ({selected_org_slug})[/green]")
    logger.info(f"Organization selected: {selected_org_slug}")
    
    return selected_org_slug


def _get_project_name() -> str:
    """Interactively get project name from user."""
    from rich.prompt import Prompt
    
    logger.debug("Prompting user to enter project name")
    console.print("[yellow]No project specified. Please enter a project name:[/yellow]")
    
    while True:
        project = Prompt.ask("Enter project name")
        if project and project.strip():
            project = project.strip()
            console.print(f"[green]✓ Will create project: {project}[/green]")
            logger.info(f"Project name entered: {project}")
            return project
        else:
            console.print("[red]Project name cannot be empty[/red]")


def _run_jupyter_session(
    ctx: click.Context,
    jupyter_command: List[str],
    port: int,
    app_port: Optional[int],
    org: Optional[str],
    project: Optional[str],
    local_only: bool,
    quiet: bool,
    extra_args: List[str]
) -> None:
    """Shared implementation for jupyter lab and jupyter notebook commands.
    
    Args:
        ctx: Click context
        jupyter_command: Base command (e.g., ['jupyter', 'lab'] or ['jupyter', 'notebook'])
        port: Jupyter port
        app_port: Optional app port for cloud connection
        org: Organization slug (interactive if not provided)
        project: Project name (interactive if not provided)
        local_only: Skip cloud connection
        quiet: Suppress Jupyter log output
        extra_args: Additional arguments to pass to Jupyter
    """
    command_name = ' '.join(jupyter_command)
    logger.info(f"Starting {command_name} (jupyter_port={port}, app_port={app_port}, local_only={local_only}, quiet={quiet})")
    
    config: Config = ctx.obj['config']
    client: AlphAIClient = ctx.obj['client']
    jupyter_manager = JupyterManager(console)
    
    # Set up cleanup manager
    cleanup_mgr = JupyterCleanupManager(
        console=console,
        jupyter_manager=jupyter_manager,
        client=client
    )
    cleanup_mgr.install_signal_handlers()
    
    try:
        # Check Jupyter is installed
        jupyter_manager.check_jupyter_or_exit("jupyter")
        
        # Find an available port (auto-increment if specified port is in use)
        actual_port = jupyter_manager.find_available_port(port)
        
        # Generate token
        jupyter_token = jupyter_manager.generate_jupyter_token()
        console.print(f"[cyan]Generated Jupyter token: {jupyter_token[:12]}...[/cyan]")
        
        # Start Jupyter (allow remote access if connecting to cloud)
        jupyter_process = jupyter_manager.start_jupyter(
            command=jupyter_command,
            port=actual_port,
            token=jupyter_token,
            extra_args=extra_args,
            allow_remote=not local_only
        )
        
        # Wait for Jupyter to be ready
        if not jupyter_manager.wait_for_jupyter_ready(actual_port, timeout=30):
            console.print("[red]Failed to start Jupyter[/red]")
            jupyter_process.kill()
            sys.exit(1)
        
        console.print("[green]✓ Jupyter started successfully[/green]")
        
        # Connect to cloud if not local-only
        connection_data = None
        if not local_only:
            if not config.bearer_token:
                logger.info("Not authenticated, skipping cloud connection")
                console.print("[yellow]⚠ Not authenticated - running locally only[/yellow]")
                console.print("[dim]Run 'alphai login' to enable cloud access[/dim]")
            else:
                # Interactive org/project selection
                if not org:
                    org = _select_organization(client)
                if not project:
                    project = _get_project_name()
                
                # Ensure connector is available
                if not jupyter_manager.ensure_cloudflared():
                    logger.info("Connector not available, running locally only")
                    console.print("[yellow]⚠ Connector not available - running locally only[/yellow]")
                else:
                    # Connect to cloud
                    logger.info(f"Connecting {org}/{project} to cloud")
                    console.print("[yellow]Connecting to cloud...[/yellow]")
                    
                    try:
                        connect_kwargs = {
                            'org_slug': org,
                            'project_name': project,
                            'jupyter_port': actual_port,
                            'jupyter_token': jupyter_token
                        }
                        if app_port is not None:
                            connect_kwargs['app_port'] = app_port
                        
                        connection_data = client.create_tunnel_with_project(**connect_kwargs)
                        
                        if connection_data:
                            # Setup connector
                            if jupyter_manager.setup_cloudflared_tunnel(connection_data.cloudflared_token):
                                console.print("[green]✓ Connected to cloud[/green]")
                                jupyter_manager.set_tunnel_data(connection_data)
                                
                                # Store IDs for cleanup
                                cleanup_mgr.set_tunnel(connection_data.id)
                                if connection_data.project_data and hasattr(connection_data.project_data, 'id'):
                                    cleanup_mgr.set_project(connection_data.project_data.id)
                            else:
                                console.print("[yellow]⚠ Connection setup failed - running locally only[/yellow]")
                                connection_data = None
                        
                    except Exception as e:
                        logger.error(f"Failed to connect to cloud: {e}", exc_info=True)
                        console.print("[yellow]⚠ Cloud connection failed - running locally only[/yellow]")
                        connection_data = None
        
        # Display access information
        jupyter_manager.display_jupyter_info(
            jupyter_port=actual_port,
            token=jupyter_token,
            tunnel_data=connection_data,
            org=org,
            project=project,
            api_url=config.api_url,
            app_port=app_port
        )
        
        # Monitor and wait for interrupt
        try:
            jupyter_manager.monitor_jupyter(show_logs=not quiet)
        except KeyboardInterrupt:
            pass
            
    finally:
        # Cleanup
        cleanup_mgr.cleanup()
        cleanup_mgr.restore_signal_handlers()


@click.group()
@click.pass_context
def jupyter(ctx: click.Context) -> None:
    """Run Jupyter with automatic cloud sync to runalph.ai."""
    pass


@jupyter.command(
    name='lab',
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.option('--port', default=8888, help='Port for Jupyter Lab (default: 8888)')
@click.option('--app-port', default=None, type=int, help='Additional port for your app (optional)')
@click.option('--org', help='Organization slug (interactive if not provided)')
@click.option('--project', help='Project name (interactive if not provided)')
@click.option('--local-only', is_flag=True, help='Run locally only, skip cloud connection')
@click.option('--quiet', is_flag=True, help='Suppress Jupyter log output')
@click.pass_context
def jupyter_lab(
    ctx: click.Context,
    port: int,
    app_port: Optional[int],
    org: Optional[str],
    project: Optional[str],
    local_only: bool,
    quiet: bool
) -> None:
    """Start Jupyter Lab with automatic cloud sync.
    
    This command starts Jupyter Lab locally and connects it to your
    cloud workspace, making it accessible from anywhere.
    
    All standard Jupyter Lab arguments are supported and passed through.
    
    Examples:
        alphai jupyter lab
        alphai jupyter lab --port 9999
        alphai jupyter lab --port 8888 --app-port 5000
        alphai jupyter lab --org my-org --project my-project
        alphai jupyter lab --local-only
        alphai jupyter lab --quiet  # Suppress Jupyter logs
        alphai jupyter lab --ServerApp.root_dir=/path/to/notebooks
    """
    _run_jupyter_session(
        ctx=ctx,
        jupyter_command=['jupyter', 'lab'],
        port=port,
        app_port=app_port,
        org=org,
        project=project,
        local_only=local_only,
        quiet=quiet,
        extra_args=ctx.args
    )


@jupyter.command(
    name='notebook',
    context_settings=dict(ignore_unknown_options=True, allow_extra_args=True)
)
@click.option('--port', default=8888, help='Port for Jupyter Notebook (default: 8888)')
@click.option('--app-port', default=None, type=int, help='Additional port for your app (optional)')
@click.option('--org', help='Organization slug (interactive if not provided)')
@click.option('--project', help='Project name (interactive if not provided)')
@click.option('--local-only', is_flag=True, help='Run locally only, skip cloud connection')
@click.option('--quiet', is_flag=True, help='Suppress Jupyter log output')
@click.pass_context
def jupyter_notebook(
    ctx: click.Context,
    port: int,
    app_port: Optional[int],
    org: Optional[str],
    project: Optional[str],
    local_only: bool,
    quiet: bool
) -> None:
    """Start Jupyter Notebook with automatic cloud sync.
    
    This command starts Jupyter Notebook locally and connects it to your
    cloud workspace, making it accessible from anywhere.
    
    All standard Jupyter Notebook arguments are supported and passed through.
    
    Examples:
        alphai jupyter notebook
        alphai jupyter notebook --port 9999
        alphai jupyter notebook --port 8888 --app-port 5000
        alphai jupyter notebook --org my-org --project my-project
        alphai jupyter notebook --local-only
        alphai jupyter notebook --quiet  # Suppress Jupyter logs
    """
    _run_jupyter_session(
        ctx=ctx,
        jupyter_command=['jupyter', 'notebook'],
        port=port,
        app_port=app_port,
        org=org,
        project=project,
        local_only=local_only,
        quiet=quiet,
        extra_args=ctx.args
    )
