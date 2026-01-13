"""Docker-related commands for alphai CLI.

Contains `run` and `cleanup` commands for Docker container management.
"""

import sys
import time
import subprocess
import webbrowser
from typing import Optional, Dict

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from ..client import AlphAIClient
from ..config import Config
from ..docker import DockerManager
from ..cleanup import DockerCleanupManager
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


def _parse_env_vars(env: tuple) -> Dict[str, str]:
    """Parse environment variables from tuple of KEY=VALUE strings."""
    env_vars = {}
    for e in env:
        if '=' in e:
            key, value = e.split('=', 1)
            env_vars[key] = value
        else:
            console.print(f"[yellow]Warning: Invalid environment variable format: {e}[/yellow]")
    logger.debug(f"Parsed {len(env_vars)} environment variables")
    return env_vars


def _parse_volumes(volume: tuple) -> Dict[str, str]:
    """Parse volume mounts from tuple of HOST:CONTAINER strings."""
    volumes = {}
    for v in volume:
        if ':' in v:
            host_path, container_path = v.split(':', 1)
            volumes[host_path] = container_path
        else:
            console.print(f"[yellow]Warning: Invalid volume format: {v}[/yellow]")
    logger.debug(f"Parsed {len(volumes)} volume mounts")
    return volumes


def _is_jupyter_installed(docker_manager: DockerManager, container_id: str) -> bool:
    """Check if Jupyter is actually installed in the container."""
    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "which", "jupyter"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return True
        
        result = subprocess.run(
            ["docker", "exec", container_id, "which", "jupyter-lab"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0
        
    except Exception as e:
        console.print(f"[yellow]Warning: Could not check Jupyter installation: {e}[/yellow]")
        return False


def _is_cloudflared_installed(docker_manager: DockerManager, container_id: str) -> bool:
    """Check if cloudflared is installed in the container."""
    try:
        result = subprocess.run(
            ["docker", "exec", container_id, "which", "cloudflared"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        return result.returncode == 0
        
    except Exception as e:
        logger.warning(f"Could not check cloudflared installation: {e}")
        return False


def _install_jupyter_in_container(docker_manager: DockerManager, container_id: str) -> bool:
    """Install Jupyter in a container that doesn't have it."""
    package_manager = docker_manager._detect_package_manager(container_id)
    
    if not package_manager:
        console.print("[red]Could not detect package manager for Jupyter installation[/red]")
        return False
    
    try:
        if package_manager in ['apt', 'apt-get']:
            install_commands = [
                "apt-get update",
                "apt-get install -y python3-pip",
                "pip3 install jupyter jupyterlab"
            ]
        elif package_manager in ['yum', 'dnf']:
            install_commands = [
                f"{package_manager} update -y",
                f"{package_manager} install -y python3-pip",
                "pip3 install jupyter jupyterlab"
            ]
        elif package_manager == 'apk':
            install_commands = [
                "apk update",
                "apk add --no-cache python3 py3-pip",
                "pip3 install jupyter jupyterlab"
            ]
        else:
            install_commands = [
                "pip3 install jupyter jupyterlab"
            ]
        
        for cmd in install_commands:
            result = subprocess.run(
                ["docker", "exec", "--user", "root", container_id, "bash", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                console.print(f"[red]Failed to run: {cmd}[/red]")
                console.print(f"[red]Error: {result.stderr}[/red]")
                return False
        
        console.print("[green]✓ Jupyter installed successfully[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]Error installing Jupyter: {e}[/red]")
        return False


def _setup_jupyter_in_container(
    docker_manager: DockerManager,
    container_id: str,
    jupyter_port: int,
    jupyter_token: str
) -> bool:
    """Setup Jupyter in container if needed."""
    logger.info(f"Setting up Jupyter in container {container_id[:12]}")
    
    if not _is_jupyter_installed(docker_manager, container_id):
        console.print("[yellow]Installing Jupyter in container...[/yellow]")
        if not _install_jupyter_in_container(docker_manager, container_id):
            logger.error("Failed to install Jupyter")
            console.print("[red]Failed to install Jupyter[/red]")
            return False
    else:
        console.print("[green]✓ Jupyter is already installed[/green]")
    
    success, actual_token = docker_manager.ensure_jupyter_running(
        container_id, 
        jupyter_port, 
        jupyter_token, 
        force_restart=True
    )
    
    if not success:
        console.print("[yellow]⚠ Jupyter may not be running[/yellow]")
        return False
    
    logger.info("Jupyter setup completed successfully")
    return True


def _connect_to_cloud(
    client: AlphAIClient,
    docker_manager: DockerManager,
    container_id: str,
    org: str,
    project: str,
    app_port: int,
    jupyter_port: int,
    jupyter_token: Optional[str]
):
    """Connect container to cloud and setup project."""
    logger.info(f"Connecting project {project} in org {org} to cloud")
    console.print("[yellow]Connecting to cloud...[/yellow]")
    
    # Create the connection (tunnel + project) via API
    connection_data = client.create_tunnel_with_project(
        org_slug=org,
        project_name=project,
        app_port=app_port,
        jupyter_port=jupyter_port,
        jupyter_token=jupyter_token
    )
    
    if not connection_data:
        logger.error("Failed to connect to cloud")
        console.print("[red]Failed to connect to cloud[/red]")
        return None
    
    # Install connector agent if needed
    if not _is_cloudflared_installed(docker_manager, container_id):
        console.print("[yellow]Installing connector...[/yellow]")
        if not docker_manager.install_cloudflared_in_container(container_id):
            console.print("[yellow]Warning: Connector installation failed, but container is running[/yellow]")
            return None
    else:
        console.print("[green]✓ Connector ready[/green]")
    
    # Start the connector
    cloudflared_token = connection_data.cloudflared_token if hasattr(connection_data, 'cloudflared_token') else connection_data.cloudflared_token
    if not docker_manager.setup_tunnel_in_container(container_id, cloudflared_token):
        console.print("[yellow]Warning: Connector setup failed, but container is running[/yellow]")
        return None
    
    logger.info("Cloud connection established successfully")
    console.print("[green]✓ Connected to cloud[/green]")
    return connection_data


def _display_deployment_summary(
    container,
    connection_data,
    app_port: int,
    jupyter_port: int,
    jupyter_token: Optional[str],
    config: Config,
    org: str,
    project: str
):
    """Display deployment summary panel."""
    logger.debug("Displaying deployment summary")
    console.print("\n[bold green]🎉 Setup complete![/bold green]")
    
    summary_content = []
    summary_content.append(f"[bold]Container ID:[/bold] {container.id[:12]}")
    summary_content.append("")
    summary_content.append("[bold blue]Local URL:[/bold blue]")
    summary_content.append(f"  • App: http://localhost:{app_port}")
    if jupyter_token:
        summary_content.append(f"  • Jupyter: http://localhost:{jupyter_port}?token={jupyter_token}")
    else:
        summary_content.append(f"  • Jupyter: http://localhost:{jupyter_port}")
    summary_content.append("")
    summary_content.append("[bold green]Public URL:[/bold green]")
    summary_content.append(f"  • App: {connection_data.app_url}")
    if jupyter_token:
        summary_content.append(f"  • Jupyter: {connection_data.jupyter_url}?token={jupyter_token}")
    else:
        summary_content.append(f"  • Jupyter: {connection_data.jupyter_url}")
    summary_content.append("")
    if jupyter_token:
        summary_content.append("[bold cyan]Jupyter Token:[/bold cyan]")
        summary_content.append(f"  {jupyter_token}")
        summary_content.append("")
    summary_content.append("[bold yellow]Management:[/bold yellow]")
    summary_content.append(f"  • Stop container: docker stop {container.id[:12]}")
    summary_content.append(f"  • View logs: docker logs {container.id[:12]}")
    summary_content.append(f"  • Cleanup: alphai cleanup {container.id[:12]}")
    summary_content.append("")
    summary_content.append("[bold cyan]Quick Cleanup:[/bold cyan]")
    summary_content.append("  • Press Ctrl+C to automatically cleanup all resources")
    
    panel = Panel(
        "\n".join(summary_content),
        title="🚀 Deployment Summary",
        title_align="left",
        border_style="green"
    )
    console.print(panel)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Waiting for cloud connection...", total=None)
        time.sleep(5)
        progress.update(task, completed=1)
    
    # Use project slug from API response if available
    frontend_url = _get_frontend_url(config.api_url)
    project_slug = project
    if connection_data.project_data:
        if hasattr(connection_data.project_data, 'slug') and connection_data.project_data.slug:
            project_slug = connection_data.project_data.slug
        elif hasattr(connection_data.project_data, 'name') and connection_data.project_data.name:
            project_slug = connection_data.project_data.name
    
    project_url = f"{frontend_url}/{org}/{project_slug}"
    console.print(f"\n[cyan]🌐 Opening browser to: {project_url}[/cyan]")
    try:
        webbrowser.open(project_url)
        logger.info(f"Opened browser to {project_url}")
    except Exception as e:
        logger.warning(f"Could not open browser: {e}")
        console.print(f"[yellow]Warning: Could not open browser automatically: {e}[/yellow]")
        console.print(f"[yellow]Please manually visit: {project_url}[/yellow]")


@click.command()
@click.option('--image', default="quay.io/jupyter/datascience-notebook:latest", required=True, help='Docker image to run')
@click.option('--app-port', default=5000, help='Application port (default: 5000)')
@click.option('--jupyter-port', default=8888, help='Jupyter port (default: 8888)')
@click.option('--name', help='Container name')
@click.option('--env', multiple=True, help='Environment variables (format: KEY=VALUE)')
@click.option('--volume', multiple=True, help='Volume mounts (format: HOST_PATH:CONTAINER_PATH)')
@click.option('--detach', '-d', is_flag=True, help='Run container in background')
@click.option('--local', is_flag=True, help='Run locally only (no cloud connection)')
@click.option('--org', help='Organization slug (interactive selection if not provided)')
@click.option('--project', help='Project name (interactive selection if not provided)')
@click.option('--command', help='Custom command to run in container (overrides default)')
@click.option('--ensure-jupyter', is_flag=True, help='Ensure Jupyter is running (auto-start if needed)')
@click.pass_context
def run(
    ctx: click.Context,
    image: str,
    app_port: int,
    jupyter_port: int,
    name: Optional[str],
    env: tuple,
    volume: tuple,
    detach: bool,
    local: bool,
    org: Optional[str],
    project: Optional[str],
    command: Optional[str],
    ensure_jupyter: bool
) -> None:
    """Launch and manage local Docker containers with cloud connection."""
    logger.info(f"Starting run command: image={image}, connect_cloud={not local}")
    config: Config = ctx.obj['config']
    client: AlphAIClient = ctx.obj['client']
    docker_manager = DockerManager(console)
    
    # Cloud connection is default behavior unless --local is specified
    connect_cloud = not local
    
    # Set up cleanup manager
    cleanup_mgr = DockerCleanupManager(
        console=console,
        docker_manager=docker_manager,
        client=client
    )
    cleanup_mgr.install_signal_handlers()
    
    try:
        # Validate cloud connection requirements and get org/project
        if connect_cloud:
            if not config.bearer_token:
                logger.error("Cloud connection requested but no authentication token found")
                console.print("[red]Error: Authentication required for cloud connection. Please run 'alphai login' first.[/red]")
                console.print("[yellow]Tip: Use --local flag to run without cloud connection[/yellow]")
                sys.exit(1)
            
            if not org:
                org = _select_organization(client)
            
            if not project:
                project = _get_project_name()
            
            ensure_jupyter = True
        
        # Generate Jupyter token upfront if we'll need it
        jupyter_token = None
        if ensure_jupyter or connect_cloud:
            jupyter_token = docker_manager.generate_jupyter_token()
            console.print(f"[cyan]Generated Jupyter token: {jupyter_token[:12]}...[/cyan]")
            logger.debug(f"Generated Jupyter token: {jupyter_token[:12]}...")
        
        # Parse environment variables and volumes
        env_vars = _parse_env_vars(env)
        volumes = _parse_volumes(volume)
        
        # Generate Jupyter startup command if needed
        startup_command = None
        if command:
            startup_command = command
        elif ensure_jupyter or connect_cloud:
            startup_command = "tail -f /dev/null"
            console.print("[yellow]Using keep-alive command to control Jupyter startup[/yellow]")
        else:
            startup_command = "tail -f /dev/null"
            console.print("[yellow]Keeping container alive for interactive use[/yellow]")
        
        # Start the container
        container = docker_manager.run_container(
            image=image,
            name=name,
            ports={app_port: app_port, jupyter_port: jupyter_port},
            environment=env_vars,
            volumes=volumes,
            detach=True,
            command=startup_command
        )
        
        if not container:
            console.print("[red]Failed to start container[/red]")
            sys.exit(1)
        
        console.print("[green]✓ Container started[/green]")
        console.print(f"[blue]Container ID: {container.id[:12]}[/blue]")
        
        # Register container for cleanup
        cleanup_mgr.set_container(container.id)
        
        # Verify container is actually running
        time.sleep(2)
        
        if not docker_manager.is_container_running(container.id):
            status = docker_manager.get_container_status(container.id)
            console.print("[red]Container failed to start or exited immediately[/red]")
            console.print(f"[red]Status: {status}[/red]")
            
            logs = docker_manager.get_container_logs(container.id, tail=20)
            if logs:
                console.print("[yellow]Container logs:[/yellow]")
                console.print(f"[dim]{logs}[/dim]")
            
            sys.exit(1)
        
        console.print("[green]✓ Container is running[/green]")
        
        # Install and ensure Jupyter is running if requested
        if ensure_jupyter:
            if not _setup_jupyter_in_container(docker_manager, container.id, jupyter_port, jupyter_token):
                console.print("[yellow]⚠ Jupyter setup had issues, continuing...[/yellow]")
        
        if connect_cloud:
            # Connect to cloud
            connection_data = _connect_to_cloud(
                client, docker_manager, container.id,
                org, project, app_port, jupyter_port, jupyter_token
            )
            
            if not connection_data:
                logger.error("Failed to connect to cloud, exiting")
                console.print("[red]Failed to connect to cloud[/red]")
                sys.exit(1)
            
            # Store IDs for cleanup
            cleanup_mgr.set_tunnel(connection_data.id)
            if connection_data.project_data and hasattr(connection_data.project_data, 'id'):
                cleanup_mgr.set_project(connection_data.project_data.id)
            
            # Display summary
            _display_deployment_summary(
                container, connection_data, app_port, jupyter_port,
                jupyter_token, config, org, project
            )
        else:
            # Local mode - just display local URLs
            console.print(f"[blue]Application: http://localhost:{app_port}[/blue]")
            if jupyter_token:
                console.print(f"[blue]Jupyter: http://localhost:{jupyter_port}?token={jupyter_token}[/blue]")
                console.print(f"[dim]Jupyter Token: {jupyter_token}[/dim]")
            else:
                console.print(f"[blue]Jupyter: http://localhost:{jupyter_port}[/blue]")
                console.print(f"[dim]Check container logs for Jupyter token: docker logs {container.id[:12]}[/dim]")
            
            console.print("\n[bold yellow]Cleanup:[/bold yellow]")
            console.print(f"  • Stop container: docker stop {container.id[:12]}")
            console.print(f"  • Quick cleanup: alphai cleanup {container.id[:12]}")
            console.print("  • Press Ctrl+C to automatically stop and remove container")
            
            if not detach:
                console.print(f"[dim]Container is running in background. Use 'docker logs {container.id[:12]}' to view logs.[/dim]")
        
        # Keep the process running and wait for Ctrl+C for cleanup
        console.print("\n[bold green]🎯 Container is running! Press Ctrl+C to cleanup all resources.[/bold green]")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        pass
    finally:
        cleanup_mgr.cleanup()
        cleanup_mgr.restore_signal_handlers()


@click.command()
@click.argument('container_id')
@click.option('--force', is_flag=True, help='Skip confirmation and force cleanup')
@click.pass_context
def cleanup(
    ctx: click.Context, 
    container_id: str, 
    force: bool
) -> None:
    """Clean up containers and projects created by alphai run.
    
    This command performs comprehensive cleanup by:
    1. Stopping any running services in the container
    2. Stopping and removing the Docker container
    3. Cleaning up the associated project
    
    Examples:
      alphai cleanup abc123456789           # Cleanup with confirmation
      alphai cleanup abc123456789 --force   # Skip confirmations
    """
    config: Config = ctx.obj['config']
    client: AlphAIClient = ctx.obj['client']
    docker_manager = DockerManager(console)
    
    # Confirmation unless force is used
    if not force:
        console.print(f"[yellow]Will cleanup: Container {container_id[:12]}[/yellow]")
        if not Confirm.ask("Continue with cleanup?"):
            console.print("[yellow]Cancelled[/yellow]")
            return
    
    console.print("[bold]🔄 Starting cleanup process...[/bold]")
    
    # Container cleanup
    success = docker_manager.cleanup_container_and_tunnel(
        container_id=container_id,
        force=force
    )
    
    # Summary
    if success:
        console.print("\n[bold green]✅ Cleanup completed successfully![/bold green]")
    else:
        console.print("\n[bold yellow]⚠ Cleanup completed with warnings[/bold yellow]")
        console.print("[dim]Check the output above for details[/dim]")
