"""Notebook commands for alphai CLI."""

import json
import sys
import webbrowser
from pathlib import Path
from typing import Any, Dict, List, Optional

import click
import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from ..client import AlphAIClient
from ..config import Config
from ..utils import get_logger

console = Console()
logger = get_logger(__name__)


def get_api_client(config: Config) -> httpx.Client:
    """Create an HTTP client for API calls."""
    return httpx.Client(
        base_url=config.api_url.rstrip('/api') if config.api_url.endswith('/api') else config.api_url,
        headers={
            "Authorization": f"Bearer {config.bearer_token}",
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )


def _select_organization(client: AlphAIClient) -> Optional[str]:
    """Interactively select an organization."""
    import questionary
    
    console.print("[yellow]Select an organization:[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching organizations...", total=None)
        try:
            orgs_data = client.get_organizations()
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error fetching organizations: {e}[/red]")
            return None
        progress.update(task, completed=1)
    
    if not orgs_data:
        console.print("[red]No organizations found. Please create one first.[/red]")
        return None
    
    org_choices = []
    for org in orgs_data:
        display_name = f"{org.name} ({org.slug})"
        org_choices.append(questionary.Choice(title=display_name, value=org.slug))
    
    selected = questionary.select(
        "Organization:",
        choices=org_choices,
        style=questionary.Style([
            ('question', 'bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
            ('selected', 'fg:#cc5454'),
        ])
    ).ask()
    
    if selected:
        org_name = next((o.name for o in orgs_data if o.slug == selected), selected)
        console.print(f"[green]✓ {org_name}[/green]\n")
    
    return selected


def _fetch_notebooks(config: Config, org_slug: str) -> List[Dict[str, Any]]:
    """Fetch notebooks for an organization."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching notebooks...", total=None)
        try:
            with get_api_client(config) as client:
                response = client.get("/api/notebooks", params={"org_slug": org_slug, "limit": 50})
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error fetching notebooks: {e}[/red]")
            return []
        progress.update(task, completed=1)
    
    return data.get("notebooks", [])


def _select_notebook(notebooks: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Interactively select a notebook."""
    import questionary
    
    if not notebooks:
        console.print("[yellow]No notebooks found in this organization.[/yellow]")
        return None
    
    # Build a lookup dict by ID
    nb_by_id = {nb.get("id"): nb for nb in notebooks}
    
    choices = []
    for nb in notebooks:
        visibility = "🌍" if nb.get("is_public") else "🔒"
        title = nb.get("title", "Untitled")
        slug = nb.get("slug", "")
        nb_id = nb.get("id", "")
        choices.append(questionary.Choice(
            title=f"{visibility} {title} ({slug})",
            value=nb_id  # Use ID as value
        ))
    
    choices.append(questionary.Choice(title="← Back", value="__back__"))
    
    selected_id = questionary.select(
        "Select a notebook:",
        choices=choices,
        style=questionary.Style([
            ('question', 'bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
        ])
    ).ask()
    
    if not selected_id or selected_id == "__back__":
        return None
    
    return nb_by_id.get(selected_id)


def _select_action(notebook: Dict[str, Any]) -> Optional[str]:
    """Interactively select an action for the notebook."""
    import questionary
    
    is_public = notebook.get("is_public", False)
    
    actions = [
        questionary.Choice(title="👁  View content", value="view"),
        questionary.Choice(title="ℹ️  Show info", value="info"),
        questionary.Choice(title="🌐 Open in browser", value="browser"),
        questionary.Choice(title="⬇️  Download", value="download"),
        questionary.Choice(title="🏷  Manage tags", value="tags"),
        questionary.Separator(),
    ]
    
    # Show only the relevant visibility toggle
    if is_public:
        actions.append(questionary.Choice(title="🔒 Make private", value="unpublish"))
    else:
        actions.append(questionary.Choice(title="🌍 Make public", value="publish"))
    
    actions.extend([
        questionary.Separator(),
        questionary.Choice(title="🗑  Delete", value="delete"),
        questionary.Separator(),
        questionary.Choice(title="← Back", value="back"),
    ])
    
    return questionary.select(
        "What would you like to do?",
        choices=actions,
        style=questionary.Style([
            ('question', 'bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
        ])
    ).ask()


def _execute_action(ctx: click.Context, notebook: Dict[str, Any], action: str) -> bool:
    """Execute an action on a notebook. Returns True to continue, False to go back."""
    config: Config = ctx.obj['config']
    nb_id = notebook.get("id", "")
    slug = notebook.get("slug", "")
    org_slug = notebook.get("organizations", {}).get("slug", "")
    
    if action == "view":
        # Fetch full content
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching notebook content...", total=None)
            try:
                with get_api_client(config) as client:
                    response = client.get(f"/api/notebooks/{nb_id}", params={"include_content": "true"})
                    response.raise_for_status()
                    data = response.json()
            except Exception as e:
                progress.update(task, completed=1)
                console.print(f"[red]Error: {e}[/red]")
                return True
            progress.update(task, completed=1)
        
        nb_data = data.get("notebook", {})
        cells = nb_data.get("content", {}).get("cells", [])
        
        if not cells:
            console.print("[yellow]Notebook has no cells.[/yellow]")
            return True
        
        from ..notebook_renderer import interactive_cell_viewer
        interactive_cell_viewer(cells, console)
        return True
    
    elif action == "info":
        from ..notebook_renderer import display_notebook_info
        display_notebook_info(notebook, console)
        console.print()
        return True
    
    elif action == "browser":
        if org_slug and slug:
            url = f"{config.api_url.replace('/api', '')}/{org_slug}/~/notebooks/{slug}"
            console.print(f"[cyan]Opening: {url}[/cyan]")
            webbrowser.open(url)
        return True
    
    elif action == "download":
        import questionary
        default_name = f"{slug or 'notebook'}.ipynb"
        filename = questionary.text(
            "Save as:",
            default=default_name
        ).ask()
        
        if filename:
            try:
                with get_api_client(config) as client:
                    response = client.get(f"/api/notebooks/{nb_id}/download")
                    response.raise_for_status()
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                console.print(f"[green]✓ Downloaded to {filename}[/green]\n")
            except Exception as e:
                console.print(f"[red]Error downloading: {e}[/red]\n")
        return True
    
    elif action == "tags":
        import questionary
        current_tags = [t.get("name", "") for t in notebook.get("tags", [])]
        console.print(f"[dim]Current tags: {', '.join(current_tags) if current_tags else 'none'}[/dim]")
        
        new_tags = questionary.text(
            "Enter tags (comma-separated):",
            default=", ".join(current_tags)
        ).ask()
        
        if new_tags is not None:
            tag_list = [t.strip() for t in new_tags.split(',') if t.strip()]
            try:
                with get_api_client(config) as client:
                    response = client.patch(f"/api/notebooks/{nb_id}", json={"tags": tag_list})
                    response.raise_for_status()
                console.print(f"[green]✓ Tags updated[/green]\n")
            except Exception as e:
                console.print(f"[red]Error updating tags: {e}[/red]\n")
        return True
    
    elif action == "publish":
        try:
            with get_api_client(config) as client:
                response = client.patch(f"/api/notebooks/{nb_id}", json={"is_public": True})
                response.raise_for_status()
            console.print(f"[green]✓ Notebook published![/green]\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")
        return True
    
    elif action == "unpublish":
        try:
            with get_api_client(config) as client:
                response = client.patch(f"/api/notebooks/{nb_id}", json={"is_public": False})
                response.raise_for_status()
            console.print(f"[green]✓ Notebook unpublished![/green]\n")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")
        return True
    
    elif action == "delete":
        if Confirm.ask(f"[red]Delete '{notebook.get('title')}'? This cannot be undone.[/red]"):
            try:
                with get_api_client(config) as client:
                    response = client.delete(f"/api/notebooks/{nb_id}")
                    response.raise_for_status()
                console.print(f"[green]✓ Notebook deleted[/green]\n")
                return False  # Go back to notebook list
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]\n")
        return True
    
    elif action == "back":
        return False
    
    return True


def _select_org_action() -> Optional[str]:
    """Select what to do in an organization."""
    import questionary
    
    actions = [
        questionary.Choice(title="📂 Browse notebooks", value="browse"),
        questionary.Choice(title="⬆️  Upload notebook", value="upload"),
        questionary.Separator(),
        questionary.Choice(title="← Back", value="back"),
    ]
    
    return questionary.select(
        "What would you like to do?",
        choices=actions,
        style=questionary.Style([
            ('question', 'bold'),
            ('pointer', 'fg:#673ab7 bold'),
            ('highlighted', 'fg:#673ab7 bold'),
        ])
    ).ask()


def _interactive_upload(ctx: click.Context, org_slug: str) -> None:
    """Interactive notebook upload flow."""
    import questionary
    
    config: Config = ctx.obj['config']
    
    # Get file path
    file_path = questionary.path(
        "Select notebook file:",
        only_directories=False,
        validate=lambda p: p.endswith('.ipynb') or "Must be a .ipynb file"
    ).ask()
    
    if not file_path:
        return
    
    path = Path(file_path)
    if not path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        return
    
    # Read and validate notebook
    try:
        with open(path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
        if 'cells' not in notebook_content:
            console.print("[red]Invalid notebook format.[/red]")
            return
    except json.JSONDecodeError:
        console.print("[red]Invalid JSON in notebook file.[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return
    
    # Get title
    default_title = path.stem.replace('_', ' ').replace('-', ' ').title()
    title = questionary.text(
        "Title:",
        default=default_title
    ).ask()
    
    if not title:
        return
    
    # Optional description
    description = questionary.text(
        "Description (optional):",
        default=""
    ).ask()
    
    # Visibility
    is_public = questionary.confirm(
        "Make public?",
        default=False
    ).ask()
    
    # Tags
    tags_input = questionary.text(
        "Tags (comma-separated, optional):",
        default=""
    ).ask()
    
    tag_list = [t.strip() for t in tags_input.split(',') if t.strip()] if tags_input else []
    
    # Upload
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Uploading notebook...", total=None)
        
        try:
            with get_api_client(config) as api_client:
                payload = {
                    "org_slug": org_slug,
                    "title": title,
                    "content": notebook_content,
                    "is_public": is_public,
                }
                if description:
                    payload["description"] = description
                if tag_list:
                    payload["tags"] = tag_list
                
                response = api_client.post("/api/notebooks", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error uploading: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebook = data.get("notebook", {})
    console.print(f"\n[green]✓ Uploaded successfully![/green]")
    console.print(f"  Title: {notebook.get('title')}")
    console.print(f"  Slug: {notebook.get('slug')}")
    visibility = "🌍 Public" if notebook.get('is_public') else "🔒 Private"
    console.print(f"  Visibility: {visibility}")
    
    slug = notebook.get("slug", "")
    if org_slug and slug:
        url = f"{config.api_url.replace('/api', '')}/{org_slug}/~/notebooks/{slug}"
        console.print(f"  URL: [cyan]{url}[/cyan]")
    console.print()


def _interactive_mode(ctx: click.Context) -> None:
    """Run the interactive notebook browser."""
    config: Config = ctx.obj['config']
    client: AlphAIClient = ctx.obj['client']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        sys.exit(1)
    
    console.print("[bold cyan]📓 Notebook Browser[/bold cyan]\n")
    
    while True:
        # Select organization
        org_slug = _select_organization(client)
        if not org_slug:
            return
        
        while True:
            # Ask what to do in this org
            org_action = _select_org_action()
            
            if not org_action or org_action == "back":
                console.print()
                break
            
            if org_action == "upload":
                _interactive_upload(ctx, org_slug)
                continue
            
            # Browse notebooks
            notebooks_list = _fetch_notebooks(config, org_slug)
            notebook = _select_notebook(notebooks_list)
            
            if not notebook:
                continue  # Back to org action menu
            
            console.print(f"\n[bold]{notebook.get('title')}[/bold]")
            console.print(f"[dim]{notebook.get('description', 'No description')}[/dim]\n")
            
            while True:
                action = _select_action(notebook)
                if not action or action == "back":
                    console.print()
                    break
                
                if not _execute_action(ctx, notebook, action):
                    break  # Action requests going back
                
                # Refresh notebook state after visibility changes
                if action in ("publish", "unpublish"):
                    notebook["is_public"] = (action == "publish")


@click.group(invoke_without_command=True)
@click.pass_context
def notebooks(ctx: click.Context) -> None:
    """Manage Jupyter notebooks.
    
    Run without arguments for interactive mode, or use subcommands:
    
    \b
    Examples:
        alphai nb              # Interactive browser
        alphai nb list
        alphai nb view my-notebook
        alphai nb upload analysis.ipynb --org my-org
    """
    if ctx.invoked_subcommand is None:
        _interactive_mode(ctx)


@notebooks.command(name="list")
@click.option('--org', help='Organization slug')
@click.option('--search', help='Search in title and description')
@click.option('--tag', help='Filter by tag')
@click.option('--public', 'visibility', flag_value='public', help='Show only public notebooks')
@click.option('--private', 'visibility', flag_value='private', help='Show only private notebooks')
@click.option('--limit', default=20, type=int, help='Maximum results')
@click.pass_context
def list_notebooks(ctx: click.Context, org: Optional[str], search: Optional[str], 
                   tag: Optional[str], visibility: Optional[str], limit: int) -> None:
    """List notebooks in your organizations."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    # Use current org if not specified
    org_slug = org or config.current_org
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching notebooks...", total=None)
        
        try:
            with get_api_client(config) as client:
                params = {"limit": limit}
                if org_slug:
                    params["org_slug"] = org_slug
                if search:
                    params["search"] = search
                if tag:
                    params["tag"] = tag
                if visibility:
                    params["visibility"] = visibility
                
                response = client.get("/api/notebooks", params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error fetching notebooks: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebooks_data = data.get("notebooks", [])
    
    if not notebooks_data:
        console.print("[yellow]No notebooks found.[/yellow]")
        return
    
    # Import here to avoid circular imports
    from ..notebook_renderer import display_notebooks_table
    display_notebooks_table(notebooks_data, console)
    
    total = data.get("total", len(notebooks_data))
    if total > limit:
        console.print(f"\n[dim]Showing {len(notebooks_data)} of {total} notebooks. Use --limit to see more.[/dim]")


@notebooks.command()
@click.argument('identifier')
@click.option('--browser', '-b', is_flag=True, help='Open in web browser')
@click.pass_context
def info(ctx: click.Context, identifier: str, browser: bool) -> None:
    """Show notebook information."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.get(f"/api/notebooks/{identifier}", params={"include_content": "false"})
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            if e.response.status_code == 404:
                console.print(f"[red]Notebook '{identifier}' not found.[/red]")
            else:
                console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error fetching notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebook = data.get("notebook", {})
    
    from ..notebook_renderer import display_notebook_info
    display_notebook_info(notebook, console)
    
    if browser:
        org_slug = notebook.get("organizations", {}).get("slug", "")
        slug = notebook.get("slug", "")
        if org_slug and slug:
            url = f"{config.api_url.replace('/api', '')}/{org_slug}/~/notebooks/{slug}"
            console.print(f"\n[cyan]Opening in browser: {url}[/cyan]")
            webbrowser.open(url)


@notebooks.command()
@click.argument('identifier')
@click.option('--browser', '-b', is_flag=True, help='Open in web browser instead')
@click.option('--static', '-s', is_flag=True, help='Show all cells at once (non-interactive)')
@click.pass_context
def view(ctx: click.Context, identifier: str, browser: bool, static: bool) -> None:
    """View notebook content in the terminal.
    
    By default, opens an interactive viewer where you can scroll through cells
    using arrow keys. Press 'q' to quit.
    
    Use --static to display all cells at once without interaction.
    """
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    if browser:
        # Just open in browser, fetch minimal info
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Fetching notebook...", total=None)
            try:
                with get_api_client(config) as client:
                    response = client.get(f"/api/notebooks/{identifier}", params={"include_content": "false"})
                    response.raise_for_status()
                    data = response.json()
            except httpx.HTTPStatusError as e:
                progress.update(task, completed=1)
                if e.response.status_code == 404:
                    console.print(f"[red]Notebook '{identifier}' not found.[/red]")
                else:
                    console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
                return
            except Exception as e:
                progress.update(task, completed=1)
                console.print(f"[red]Error: {e}[/red]")
                return
            progress.update(task, completed=1)
        
        notebook = data.get("notebook", {})
        org_slug = notebook.get("organizations", {}).get("slug", "")
        slug = notebook.get("slug", "")
        if org_slug and slug:
            url = f"{config.api_url.replace('/api', '')}/{org_slug}/~/notebooks/{slug}"
            console.print(f"[cyan]Opening: {url}[/cyan]")
            webbrowser.open(url)
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.get(f"/api/notebooks/{identifier}", params={"include_content": "true"})
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            if e.response.status_code == 404:
                console.print(f"[red]Notebook '{identifier}' not found.[/red]")
            else:
                console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error fetching notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebook = data.get("notebook", {})
    cells = notebook.get("content", {}).get("cells", [])
    
    if not cells:
        console.print("[yellow]Notebook has no cells.[/yellow]")
        return
    
    if static:
        from ..notebook_renderer import display_notebook_preview
        display_notebook_preview(notebook, console)
    else:
        from ..notebook_renderer import interactive_cell_viewer
        interactive_cell_viewer(cells, console)


@notebooks.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--org', required=True, help='Organization slug')
@click.option('--title', help='Notebook title (default: filename)')
@click.option('--description', help='Notebook description')
@click.option('--public', is_flag=True, help='Make notebook public')
@click.option('--tags', help='Comma-separated tags')
@click.pass_context
def upload(ctx: click.Context, file_path: str, org: str, title: Optional[str],
           description: Optional[str], public: bool, tags: Optional[str]) -> None:
    """Upload a local .ipynb file."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    path = Path(file_path)
    if not path.suffix == '.ipynb':
        console.print("[red]Error: File must be a .ipynb file.[/red]")
        return
    
    # Read and validate the file
    try:
        with open(path, 'r', encoding='utf-8') as f:
            notebook_content = json.load(f)
        
        if 'cells' not in notebook_content:
            console.print("[red]Error: Invalid notebook format.[/red]")
            return
    except json.JSONDecodeError:
        console.print("[red]Error: Invalid JSON in notebook file.[/red]")
        return
    except Exception as e:
        console.print(f"[red]Error reading file: {e}[/red]")
        return
    
    notebook_title = title or path.stem
    tag_list = [t.strip() for t in tags.split(',')] if tags else []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Uploading notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                payload = {
                    "org_slug": org,
                    "title": notebook_title,
                    "content": notebook_content,
                    "is_public": public,
                }
                if description:
                    payload["description"] = description
                if tag_list:
                    payload["tags"] = tag_list
                
                response = client.post("/api/notebooks", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error uploading notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebook = data.get("notebook", {})
    console.print(f"[green]✓ Notebook uploaded successfully![/green]")
    console.print(f"  Title: {notebook.get('title')}")
    console.print(f"  Slug: {notebook.get('slug')}")
    console.print(f"  Visibility: {'Public' if notebook.get('is_public') else 'Private'}")
    
    org_slug = notebook.get("organization", {}).get("slug", org)
    slug = notebook.get("slug", "")
    if org_slug and slug:
        url = f"{config.api_url.replace('/api', '')}/{org_slug}/~/notebooks/{slug}"
        console.print(f"  URL: [cyan]{url}[/cyan]")


@notebooks.command()
@click.argument('identifier')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def download(ctx: click.Context, identifier: str, output: Optional[str]) -> None:
    """Download a notebook as .ipynb file."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Downloading notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.get(f"/api/notebooks/{identifier}/download")
                response.raise_for_status()
                
                # Get filename from content-disposition or use identifier
                content_disp = response.headers.get("content-disposition", "")
                if "filename=" in content_disp:
                    filename = content_disp.split("filename=")[1].strip('"')
                else:
                    filename = f"{identifier}.ipynb"
                
                output_path = output or filename
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            if e.response.status_code == 404:
                console.print(f"[red]Notebook '{identifier}' not found.[/red]")
            else:
                console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error downloading notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    console.print(f"[green]✓ Notebook downloaded to: {output_path}[/green]")


@notebooks.command()
@click.argument('identifier')
@click.option('--force', '-f', is_flag=True, help='Skip confirmation')
@click.pass_context
def delete(ctx: click.Context, identifier: str, force: bool) -> None:
    """Delete a notebook."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    if not force:
        if not Confirm.ask(f"Are you sure you want to delete notebook '{identifier}'?"):
            console.print("[yellow]Cancelled.[/yellow]")
            return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Deleting notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.delete(f"/api/notebooks/{identifier}")
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            if e.response.status_code == 404:
                console.print(f"[red]Notebook '{identifier}' not found.[/red]")
            else:
                console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error deleting notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    console.print(f"[green]✓ Notebook deleted successfully.[/green]")


@notebooks.command()
@click.argument('identifier')
@click.pass_context
def publish(ctx: click.Context, identifier: str) -> None:
    """Publish a notebook (make it public)."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Publishing notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.patch(f"/api/notebooks/{identifier}", json={"is_public": True})
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error publishing notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    console.print(f"[green]✓ Notebook published! It is now publicly visible.[/green]")


@notebooks.command()
@click.argument('identifier')
@click.pass_context
def unpublish(ctx: click.Context, identifier: str) -> None:
    """Unpublish a notebook (make it private)."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Unpublishing notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.patch(f"/api/notebooks/{identifier}", json={"is_public": False})
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error unpublishing notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    console.print(f"[green]✓ Notebook unpublished. It is now private.[/green]")


@notebooks.command(name="tags")
@click.argument('identifier')
@click.option('--add', 'add_tags', help='Tags to add (comma-separated)')
@click.option('--remove', 'remove_tags', help='Tags to remove (comma-separated)')
@click.option('--set', 'set_tags', help='Set tags (replaces existing, comma-separated)')
@click.pass_context
def manage_tags(ctx: click.Context, identifier: str, add_tags: Optional[str],
                remove_tags: Optional[str], set_tags: Optional[str]) -> None:
    """Manage notebook tags."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    if set_tags:
        # Replace all tags
        new_tags = [t.strip() for t in set_tags.split(',') if t.strip()]
    else:
        # Get current tags first
        try:
            with get_api_client(config) as client:
                response = client.get(f"/api/notebooks/{identifier}", params={"include_content": "false"})
                response.raise_for_status()
                data = response.json()
        except Exception as e:
            console.print(f"[red]Error fetching notebook: {e}[/red]")
            return
        
        current_tags = set(t.get("name", "") for t in data.get("notebook", {}).get("tags", []))
        
        if add_tags:
            for tag in add_tags.split(','):
                current_tags.add(tag.strip())
        
        if remove_tags:
            for tag in remove_tags.split(','):
                current_tags.discard(tag.strip())
        
        new_tags = list(current_tags)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Updating tags...", total=None)
        
        try:
            with get_api_client(config) as client:
                response = client.patch(f"/api/notebooks/{identifier}", json={"tags": new_tags})
                response.raise_for_status()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error updating tags: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    if new_tags:
        console.print(f"[green]✓ Tags updated: {', '.join(new_tags)}[/green]")
    else:
        console.print(f"[green]✓ All tags removed.[/green]")


@notebooks.command()
@click.argument('identifier')
@click.option('--org', required=True, help='Target organization slug')
@click.option('--title', help='Custom title for the fork')
@click.pass_context
def fork(ctx: click.Context, identifier: str, org: str, title: Optional[str]) -> None:
    """Fork a public notebook to your organization."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Forking notebook...", total=None)
        
        try:
            with get_api_client(config) as client:
                payload = {"org_slug": org}
                if title:
                    payload["title"] = title
                
                response = client.post(f"/api/notebooks/{identifier}/fork", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            if e.response.status_code == 404:
                console.print(f"[red]Notebook '{identifier}' not found.[/red]")
            elif e.response.status_code == 403:
                console.print(f"[red]Cannot fork: notebook is not public or you don't have access.[/red]")
            else:
                console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error forking notebook: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebook = data.get("notebook", {})
    console.print(f"[green]✓ Notebook forked successfully![/green]")
    console.print(f"  Title: {notebook.get('title')}")
    console.print(f"  Slug: {notebook.get('slug')}")
    
    org_slug = notebook.get("organization", {}).get("slug", org)
    slug = notebook.get("slug", "")
    if org_slug and slug:
        url = f"{config.api_url.replace('/api', '')}/{org_slug}/~/notebooks/{slug}"
        console.print(f"  URL: [cyan]{url}[/cyan]")


@notebooks.command()
@click.argument('query')
@click.option('--org', help='Search within organization')
@click.option('--public', is_flag=True, help='Search only public notebooks')
@click.option('--limit', default=20, type=int, help='Maximum results')
@click.pass_context
def search(ctx: click.Context, query: str, org: Optional[str], public: bool, limit: int) -> None:
    """Search notebooks by title and description."""
    config: Config = ctx.obj['config']
    
    if not config.bearer_token:
        console.print("[red]Error: Not logged in. Run 'alphai login' first.[/red]")
        return
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task(f"Searching for '{query}'...", total=None)
        
        try:
            with get_api_client(config) as client:
                params = {"q": query, "limit": limit}
                if org:
                    params["org_slug"] = org
                if public:
                    params["public_only"] = "true"
                
                response = client.get("/api/notebooks/search", params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error: {e.response.status_code} - {e.response.text}[/red]")
            return
        except Exception as e:
            progress.update(task, completed=1)
            console.print(f"[red]Error searching notebooks: {e}[/red]")
            return
        
        progress.update(task, completed=1)
    
    notebooks_data = data.get("notebooks", [])
    
    if not notebooks_data:
        console.print(f"[yellow]No notebooks found matching '{query}'.[/yellow]")
        return
    
    console.print(f"\n[bold]Search results for '{query}':[/bold]\n")
    
    from ..notebook_renderer import display_notebooks_table
    display_notebooks_table(notebooks_data, console)
    
    total = data.get("total", len(notebooks_data))
    if total > limit:
        console.print(f"\n[dim]Showing {len(notebooks_data)} of {total} results.[/dim]")
