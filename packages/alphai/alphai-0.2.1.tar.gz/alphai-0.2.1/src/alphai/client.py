"""Client wrapper for alph-sdk."""

import sys
from typing import Optional, List, Dict, Any
from alph_sdk import AlphSDK
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .config import Config
from .utils import get_logger
from . import exceptions

logger = get_logger(__name__)


class TunnelData:
    """Custom wrapper for tunnel data with additional fields."""
    
    def __init__(self, tunnel_data, cloudflared_token: str, jupyter_token: Optional[str] = None):
        """Initialize with tunnel data and tokens."""
        self.original_data = tunnel_data
        self.cloudflared_token = cloudflared_token
        self.jupyter_token = jupyter_token
        self.project_data = None
        
        # Proxy all attributes from original data
        for attr in ['id', 'name', 'app_url', 'jupyter_url', 'hostname', 'jupyter_hostname', 'created_at']:
            if hasattr(tunnel_data, attr):
                setattr(self, attr, getattr(tunnel_data, attr))
    

class AlphAIClient:
    """High-level client for interacting with the Alph API."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the client with configuration."""
        self.config = config or Config.load()
        self.console = Console()
        self._sdk = None
    
    @property
    def sdk(self) -> AlphSDK:
        """Get the SDK instance, creating it if necessary."""
        if self._sdk is None:
            if not self.config.bearer_token:
                logger.error("SDK initialization failed: No authentication token")
                self.console.print("[red]Error: No authentication token found. Please run 'alphai login' first.[/red]")
                raise exceptions.AuthenticationError("No authentication token found")
            
            try:
                self._sdk = AlphSDK(**self.config.to_sdk_config())
                logger.debug("SDK initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize SDK: {e}")
                raise exceptions.APIError(f"Failed to initialize SDK: {e}")
        return self._sdk
    
    def test_connection(self) -> bool:
        """Test the connection to the API."""
        try:
            logger.info("Testing API connection")
            # Try to get organizations as a connection test
            response = self.sdk.orgs.get()
            success = response.result.status == "success" if response.result.status else True
            if success:
                logger.info("API connection test successful")
            else:
                logger.warning("API connection test failed: unexpected response")
            return success
        except exceptions.AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Connection test failed: {e}", exc_info=True)
            self.console.print(f"[red]Connection test failed: {e}[/red]")
            raise exceptions.NetworkError(f"Connection test failed: {e}")
    
    def get_organizations(self) -> List[Dict[str, Any]]:
        """Get all organizations."""
        try:
            logger.debug("Fetching organizations from API")
            response = self.sdk.orgs.get()
            # Access organizations from response.result.organizations
            orgs = response.result.organizations or []
            logger.info(f"Successfully fetched {len(orgs)} organization(s)")
            return orgs
        except exceptions.AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Error getting organizations: {e}", exc_info=True)
            self.console.print(f"[red]Error getting organizations: {e}[/red]")
            raise exceptions.APIError(f"Failed to get organizations: {e}")
    
    def create_organization(self, name: str, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Create a new organization."""
        try:
            response = self.sdk.orgs.create({
                "name": name,
                "description": description or ""
            })
            if response.result.status == "success":
                self.console.print(f"[green]✓ Organization '{name}' created successfully[/green]")
                return response.result.organization
            else:
                self.console.print(f"[red]Failed to create organization: {response.result.status}[/red]")
                return None
        except Exception as e:
            self.console.print(f"[red]Error creating organization: {e}[/red]")
            return None
    
    def get_projects(self, org_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all projects, optionally filtered by organization."""
        try:
            params = {}
            if org_id:
                params["org_id"] = org_id
            
            response = self.sdk.projects.get(**params)
            # Access projects from response.result.projects
            return response.result.projects or []
        except Exception as e:
            self.console.print(f"[red]Error getting projects: {e}[/red]")
            return []
    
    def display_organizations(self, orgs: List[Dict[str, Any]]) -> None:
        """Display organizations in a nice table format."""
        if not orgs:
            self.console.print("[yellow]No organizations found.[/yellow]")
            return
        
        table = Table(title="Organizations")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Role", style="blue")
        table.add_column("Slug", style="dim")
        
        for org in orgs:
            table.add_row(
                org.id or "",
                org.name or "",
                org.role or "",
                org.slug or ""
            )
        
        self.console.print(table)
    
    def display_projects(self, projects: List[Dict[str, Any]]) -> None:
        """Display projects in a nice table format."""
        if not projects:
            self.console.print("[yellow]No projects found.[/yellow]")
            return
        
        table = Table(title="Projects")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="green")
        table.add_column("Organization", style="blue")
        table.add_column("Status", style="yellow")
        table.add_column("Created", style="dim")
        
        for project in projects:
            # Handle organization name safely
            org_name = ""
            if project.organization:
                org_name = project.organization.name or ""
            
            table.add_row(
                project.id or "",
                project.name or "",
                org_name,
                project.status or "",
                project.created_at or ""
            )
        
        self.console.print(table)
    
    def display_status(self) -> None:
        """Display current configuration status."""
        status_info = []
        
        # Only show API URL if it's not the default (for developers using custom endpoints)
        default_api_url = "https://www.runalph.ai/api"
        if self.config.api_url != default_api_url:
            status_info.append(f"[bold]API:[/bold] {self.config.api_url} [dim](custom)[/dim]")
        
        # Authentication status and user info
        if self.config.bearer_token:
            status_info.append("[bold]Authentication:[/bold] [green]✓ Logged in[/green]")
            
            # Try to fetch organizations to show helpful context
            try:
                orgs = self.get_organizations()
                if orgs:
                    # Show current/default organization
                    if self.config.current_org:
                        # Find the org name for the current org slug
                        current_org_name = None
                        for org in orgs:
                            if hasattr(org, 'slug') and org.slug == self.config.current_org:
                                current_org_name = org.name
                                break
                        if current_org_name:
                            status_info.append(f"[bold]Organization:[/bold] {current_org_name} [dim]({self.config.current_org})[/dim]")
                        else:
                            status_info.append(f"[bold]Organization:[/bold] {self.config.current_org}")
                    elif len(orgs) == 1:
                        # If only one org, show it as the default
                        org = orgs[0]
                        status_info.append(f"[bold]Organization:[/bold] {org.name} [dim]({org.slug})[/dim]")
                    else:
                        # Multiple orgs, show count and list them
                        status_info.append(f"[bold]Organizations:[/bold] {len(orgs)} available")
                        for org in orgs[:3]:  # Show up to 3
                            # Handle role which may be an enum or string
                            role_str = ""
                            if hasattr(org, 'role') and org.role:
                                role_val = org.role.value if hasattr(org.role, 'value') else str(org.role)
                                role_str = f"[cyan]{role_val}[/cyan]"
                            status_info.append(f"  • {org.name} [dim]({org.slug})[/dim] {role_str}")
                        if len(orgs) > 3:
                            status_info.append(f"  [dim]... and {len(orgs) - 3} more[/dim]")
            except Exception:
                # Silently fail if we can't fetch orgs - just don't show org info
                pass
        else:
            status_info.append("[bold]Authentication:[/bold] [red]✗ Not logged in[/red]")
        
        # Debug mode
        if self.config.debug:
            status_info.append("[bold]Debug Mode:[/bold] [yellow]Enabled[/yellow]")
        
        panel = Panel(
            "\n".join(status_info),
            title="alphai Status",
            title_align="left"
        )
        self.console.print(panel)
        
        # Show helpful tips based on state
        if not self.config.bearer_token:
            self.console.print("\n[bold yellow]Quick Start:[/bold yellow]")
            self.console.print("  [cyan]alphai login[/cyan]         Log in to runalph.ai")
            self.console.print("  [cyan]alphai login --browser[/cyan] Log in via browser (recommended)")
        else:
            self.console.print("\n[bold yellow]Quick Start:[/bold yellow]")
            self.console.print("  [cyan]alphai jupyter lab[/cyan]   Start Jupyter Lab with cloud sync")
            self.console.print("  [cyan]alphai nb[/cyan]       List your notebooks")
            self.console.print("  [cyan]alphai orgs[/cyan]     List your organizations")
            self.console.print("  [cyan]alphai --help[/cyan]        Show all commands")
    
    def create_tunnel(
        self, 
        org_slug: str, 
        project_name: str, 
        app_port: int = 5000, 
        jupyter_port: int = 8888
    ) -> Optional[Dict[str, Any]]:
        """Create a new tunnel and return the tunnel data including token."""
        try:
            response = self.sdk.tunnels.create(request={
                "org_slug": org_slug,
                "project_name": project_name,
                "app_port": app_port,
                "jupyter_port": jupyter_port
            })
            
            if response.result.status == "success":
                tunnel_data = response.result.data
                logger.info(f"Connection created: {tunnel_data.id}")
                return tunnel_data
            else:
                self.console.print(f"[red]Failed to connect: {response.result.status}[/red]")
                return None
        except Exception as e:
            self.console.print(f"[red]Error connecting: {e}[/red]")
            return None
    
    def get_tunnel(self, tunnel_id: str) -> Optional[Dict[str, Any]]:
        """Get connection information by ID."""
        try:
            response = self.sdk.tunnels.get(tunnel_id=tunnel_id)
            return response.result.data if response.result.status == "success" else None
        except Exception as e:
            logger.error(f"Error getting connection: {e}")
            return None
    
    def delete_tunnel(self, tunnel_id: str) -> bool:
        """Delete a connection by ID."""
        try:
            logger.info(f"Cleaning up connection: {tunnel_id}")
            response = self.sdk.tunnels.delete(tunnel_id=tunnel_id)
            if response.result.status == "success":
                logger.info(f"Connection {tunnel_id} cleaned up successfully")
                return True
            else:
                logger.warning(f"Failed to clean up connection {tunnel_id}: {response.result.status}")
                return False
        except Exception as e:
            logger.error(f"Error cleaning up connection {tunnel_id}: {e}", exc_info=True)
            raise exceptions.TunnelError(f"Failed to clean up connection: {e}")
    
    def create_project(
        self, 
        name: str, 
        organization_id: str,
        port: int = 5000,
        url: Optional[str] = None,
        port_forward_url: Optional[str] = None,
        token: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new project."""
        try:
            response = self.sdk.projects.create(request={
                "name": name,
                "organization_id": organization_id,
                "port": port,
                "url": url,
                "port_forward_url": port_forward_url,
                "token": token,
                "server_request": "external",
            })
            
            if response.result.status == "success":
                project_data = response.result.project  # Use 'project' instead of 'data'
                self.console.print(f"[green]✓ Project '{name}' created successfully[/green]")
                return project_data
            else:
                self.console.print(f"[red]Failed to create project: {response.result.status}[/red]")
                return None
        except Exception as e:
            self.console.print(f"[red]Error creating project: {e}[/red]")
            return None
    
    def get_organization_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Get organization by slug."""
        try:
            logger.debug(f"Looking up organization by slug: {slug}")
            orgs = self.get_organizations()
            for org in orgs:
                if hasattr(org, 'slug') and org.slug == slug:
                    logger.info(f"Found organization: {slug}")
                    return org
            logger.warning(f"Organization not found: {slug}")
            raise exceptions.ResourceNotFoundError("Organization", slug)
        except exceptions.ResourceNotFoundError:
            self.console.print(f"[red]Organization '{slug}' not found[/red]")
            raise
        except Exception as e:
            logger.error(f"Error getting organization by slug: {e}", exc_info=True)
            self.console.print(f"[red]Error getting organization by slug: {e}[/red]")
            raise
    
    def create_tunnel_with_project(
        self, 
        org_slug: str, 
        project_name: str, 
        app_port: int = 5000, 
        jupyter_port: int = 8888,
        jupyter_token: Optional[str] = None
    ) -> Optional[TunnelData]:
        """Create a tunnel and associated project."""
        # First, get the organization
        org = self.get_organization_by_slug(org_slug)
        if not org:
            self.console.print(f"[red]Organization with slug '{org_slug}' not found[/red]")
            return None
        
        # Create the tunnel
        tunnel_data = self.create_tunnel(org_slug, project_name, app_port, jupyter_port)
        if not tunnel_data:
            return None
        
        # Create custom wrapper with tokens
        wrapped_tunnel = TunnelData(
            tunnel_data=tunnel_data,
            cloudflared_token=tunnel_data.token,
            jupyter_token=jupyter_token
        )
        
        # Create the associated project (with Jupyter token if available)
        self.console.print(f"[yellow]Creating associated project '{project_name}'...[/yellow]")
        project_data = self.create_project(
            name=project_name,
            organization_id=org.id,
            port=app_port,
            url=tunnel_data.jupyter_url,
            port_forward_url=tunnel_data.app_url,
            token=jupyter_token  # Use Jupyter token, not cloudflared token
        )
        
        # Store project data in wrapper
        wrapped_tunnel.project_data = project_data
        
        # Log success (user-facing details shown by caller)
        logger.info(f"Project setup complete: {project_name}")
        
        return wrapped_tunnel
    
    def update_project_jupyter_token(self, project_data: Dict[str, Any], jupyter_token: str) -> bool:
        """Update project with Jupyter token after container starts."""
        # Since there's no update method, we'll store this for the next version
        # For now, just print that we have the token
        self.console.print(f"[green]✓ Jupyter token extracted: {jupyter_token[:12]}...[/green]")
        return True

    def delete_project(self, project_id: str) -> bool:
        """Delete a project by ID."""
        try:
            response = self.sdk.projects.delete(project_id=project_id)
            if response.result.status == "success":
                logger.info(f"Project {project_id} deleted successfully")
                return True
            else:
                logger.warning(f"Failed to delete project: {response.result.status}")
                return False
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False

    def cleanup_tunnel_and_project(
        self, 
        tunnel_id: Optional[str] = None, 
        project_id: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """Comprehensive cleanup of connection and project resources."""
        success = True
        
        if not tunnel_id and not project_id:
            logger.debug("No resources to clean up")
            return True
        
        # Clean up connection first
        if tunnel_id:
            logger.info(f"Cleaning up connection...")
            if not self.delete_tunnel(tunnel_id):
                success = False
        
        # Delete project second  
        if project_id:
            logger.info(f"Cleaning up project...")
            if not self.delete_project(project_id):
                success = False
        
        return success 