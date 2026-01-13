"""Terminal rendering for Jupyter notebooks using Rich."""

from typing import Any, Dict, List, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.syntax import Syntax
from rich.markdown import Markdown
from rich.columns import Columns
from rich.rule import Rule


def format_relative_time(timestamp: str) -> str:
    """Format a timestamp as relative time (e.g., '2 hours ago')."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo)
        diff = now - dt
        
        seconds = diff.total_seconds()
        if seconds < 60:
            return "just now"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            return f"{minutes}m ago"
        elif seconds < 86400:
            hours = int(seconds / 3600)
            return f"{hours}h ago"
        elif seconds < 604800:
            days = int(seconds / 86400)
            return f"{days}d ago"
        elif seconds < 2592000:
            weeks = int(seconds / 604800)
            return f"{weeks}w ago"
        else:
            return dt.strftime("%Y-%m-%d")
    except Exception:
        return timestamp[:10] if len(timestamp) >= 10 else timestamp


def get_visibility_badge(is_public: bool) -> Text:
    """Create a visibility badge."""
    if is_public:
        return Text("● Public", style="green")
    else:
        return Text("○ Private", style="dim")


def format_stat(value: Optional[int], icon: str) -> str:
    """Format a statistic with icon."""
    return f"{icon} {value or 0}"


def display_notebooks_table(notebooks: List[Dict[str, Any]], console: Console) -> None:
    """Display notebooks in a rich table."""
    table = Table(show_header=True, header_style="bold", expand=True)
    table.add_column("Title", style="cyan", no_wrap=False, ratio=3)
    table.add_column("Organization", style="blue", no_wrap=True, ratio=1)
    table.add_column("Status", justify="center", ratio=1)
    table.add_column("Stats", justify="center", ratio=1)
    table.add_column("Updated", justify="right", style="dim", ratio=1)
    
    for notebook in notebooks:
        title = notebook.get("title", "Untitled")
        description = notebook.get("description", "")
        
        # Build title cell with description
        title_text = Text()
        title_text.append(title, style="bold")
        if description:
            title_text.append(f"\n{description[:60]}{'...' if len(description) > 60 else ''}", style="dim")
        
        # Organization
        org = notebook.get("organizations", {})
        org_name = org.get("name", "") if isinstance(org, dict) else ""
        
        # Visibility
        is_public = notebook.get("is_public", False)
        visibility = get_visibility_badge(is_public)
        
        # Stats
        likes = notebook.get("like_count", 0) or 0
        bookmarks = notebook.get("bookmark_count", 0) or 0
        views = notebook.get("view_count", 0) or 0
        stats = f"♥ {likes}  ★ {bookmarks}  👁 {views}"
        
        # Updated time
        updated = format_relative_time(notebook.get("updated_at", ""))
        
        table.add_row(title_text, org_name, visibility, stats, updated)
    
    console.print(table)


def display_notebook_info(notebook: Dict[str, Any], console: Console) -> None:
    """Display detailed notebook information in a panel."""
    title = notebook.get("title", "Untitled")
    description = notebook.get("description", "No description")
    slug = notebook.get("slug", "")
    is_public = notebook.get("is_public", False)
    
    # Organization info
    org = notebook.get("organizations", {})
    org_name = org.get("name", "Unknown") if isinstance(org, dict) else "Unknown"
    org_slug = org.get("slug", "") if isinstance(org, dict) else ""
    
    # Stats
    likes = notebook.get("like_count", 0) or 0
    bookmarks = notebook.get("bookmark_count", 0) or 0
    forks = notebook.get("fork_count", 0) or 0
    views = notebook.get("view_count", 0) or 0
    
    # Timestamps
    created = format_relative_time(notebook.get("created_at", ""))
    updated = format_relative_time(notebook.get("updated_at", ""))
    
    # Tags
    tags = notebook.get("tags", [])
    tag_names = [t.get("name", "") for t in tags if isinstance(t, dict)]
    
    # Build info text
    info_lines = []
    info_lines.append(f"[bold cyan]{title}[/bold cyan]")
    info_lines.append("")
    info_lines.append(f"[dim]{description}[/dim]")
    info_lines.append("")
    info_lines.append(f"[bold]Organization:[/bold] {org_name} [dim]({org_slug})[/dim]")
    info_lines.append(f"[bold]Slug:[/bold] {slug}")
    info_lines.append(f"[bold]Visibility:[/bold] {'Public' if is_public else 'Private'}")
    info_lines.append("")
    
    if tag_names:
        tags_str = "  ".join(f"[on blue] {t} [/on blue]" for t in tag_names)
        info_lines.append(f"[bold]Tags:[/bold] {tags_str}")
        info_lines.append("")
    
    info_lines.append(f"[bold]Stats:[/bold]  ♥ {likes} likes  ★ {bookmarks} bookmarks  🔀 {forks} forks  👁 {views} views")
    info_lines.append("")
    info_lines.append(f"[bold]Created:[/bold] {created}    [bold]Updated:[/bold] {updated}")
    
    # User permissions
    if notebook.get("can_edit"):
        info_lines.append("")
        info_lines.append("[green]✓ You can edit this notebook[/green]")
    
    panel = Panel(
        "\n".join(info_lines),
        title="Notebook Info",
        border_style="blue"
    )
    console.print(panel)


def display_notebook_preview(notebook: Dict[str, Any], console: Console, 
                             max_cells: int = 20) -> None:
    """Display notebook content preview with cells shown in terminal."""
    # First show info
    display_notebook_info(notebook, console)
    
    content = notebook.get("content", {})
    cells = content.get("cells", [])
    
    if not cells:
        console.print("\n[yellow]Notebook has no cells.[/yellow]")
        return
    
    # Summary
    code_cells = sum(1 for c in cells if c.get("cell_type") == "code")
    markdown_cells = sum(1 for c in cells if c.get("cell_type") == "markdown")
    
    console.print(f"\n[bold]Cells:[/bold] {len(cells)} total ({code_cells} code, {markdown_cells} markdown)")
    
    console.print("")
    console.print(Rule("Cell Contents"))
    console.print("")
    
    for i, cell in enumerate(cells[:max_cells]):
        cell_type = cell.get("cell_type", "unknown")
        source = cell.get("source", [])
        
        # Handle source as list or string
        if isinstance(source, list):
            source_text = "".join(source)
        else:
            source_text = str(source)
        
        # Cell header
        cell_icon = "📝" if cell_type == "markdown" else "💻" if cell_type == "code" else "❓"
        console.print(f"[bold]{cell_icon} Cell {i + 1}[/bold] [dim]({cell_type})[/dim]")
        
        if cell_type == "markdown":
            # Render markdown
            try:
                md = Markdown(source_text[:500] + ("..." if len(source_text) > 500 else ""))
                console.print(Panel(md, border_style="dim"))
            except Exception:
                console.print(Panel(source_text[:500], border_style="dim"))
        
        elif cell_type == "code":
            # Syntax highlight code
            # Truncate very long cells
            display_source = source_text[:1000]
            if len(source_text) > 1000:
                display_source += "\n... (truncated)"
            
            try:
                syntax = Syntax(display_source, "python", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, border_style="green"))
            except Exception:
                console.print(Panel(display_source, border_style="green"))
            
            # Show outputs if any
            outputs = cell.get("outputs", [])
            if outputs:
                console.print("[dim]  Outputs:[/dim]")
                for output in outputs[:3]:  # Limit outputs shown
                    output_type = output.get("output_type", "")
                    
                    if output_type == "stream":
                        text = output.get("text", [])
                        if isinstance(text, list):
                            text = "".join(text)
                        text = str(text)[:200]
                        console.print(f"    [dim]{text}[/dim]")
                    
                    elif output_type in ["execute_result", "display_data"]:
                        data = output.get("data", {})
                        if "text/plain" in data:
                            plain = data["text/plain"]
                            if isinstance(plain, list):
                                plain = "".join(plain)
                            plain = str(plain)[:200]
                            console.print(f"    [cyan]{plain}[/cyan]")
                        elif "image/png" in data:
                            console.print("    [yellow]📊 [Image output][/yellow]")
                        elif "application/vnd.plotly.v1+json" in data:
                            console.print("    [yellow]📈 [Plotly chart][/yellow]")
                    
                    elif output_type == "error":
                        ename = output.get("ename", "Error")
                        evalue = output.get("evalue", "")
                        console.print(f"    [red]❌ {ename}: {evalue[:100]}[/red]")
        
        console.print("")
    
    if len(cells) > max_cells:
        console.print(f"[dim]... and {len(cells) - max_cells} more cells. Use --max-cells to see more, or download the notebook.[/dim]")


def render_single_cell(cell: Dict[str, Any], index: int, total: int, console: Console) -> None:
    """Render a single cell with its content and outputs."""
    cell_type = cell.get("cell_type", "unknown")
    source = cell.get("source", [])
    
    # Handle source as list or string
    if isinstance(source, list):
        source_text = "".join(source)
    else:
        source_text = str(source)
    
    # Clear screen and show header
    console.clear()
    
    # Header with navigation info
    cell_icon = "📝" if cell_type == "markdown" else "💻" if cell_type == "code" else "❓"
    header = Text()
    header.append(f"{cell_icon} Cell {index + 1} of {total}", style="bold cyan")
    header.append(f"  ({cell_type})", style="dim")
    console.print(header)
    console.print()
    
    if cell_type == "markdown":
        # Render markdown
        try:
            md = Markdown(source_text)
            console.print(Panel(md, border_style="blue", title="Markdown", title_align="left"))
        except Exception:
            console.print(Panel(source_text, border_style="blue", title="Markdown", title_align="left"))
    
    elif cell_type == "code":
        # Syntax highlight code
        try:
            syntax = Syntax(source_text, "python", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, border_style="green", title="Python", title_align="left"))
        except Exception:
            console.print(Panel(source_text, border_style="green", title="Code", title_align="left"))
        
        # Show outputs if any
        outputs = cell.get("outputs", [])
        if outputs:
            console.print()
            console.print("[bold]Output:[/bold]")
            for output in outputs:
                output_type = output.get("output_type", "")
                
                if output_type == "stream":
                    text = output.get("text", [])
                    if isinstance(text, list):
                        text = "".join(text)
                    console.print(Panel(str(text), border_style="dim", title=f"stdout", title_align="left"))
                
                elif output_type in ["execute_result", "display_data"]:
                    data = output.get("data", {})
                    if "text/plain" in data:
                        plain = data["text/plain"]
                        if isinstance(plain, list):
                            plain = "".join(plain)
                        console.print(Panel(str(plain), border_style="cyan", title="Result", title_align="left"))
                    if "image/png" in data:
                        console.print("[yellow]  📊 [Image output - view in browser][/yellow]")
                    if "application/vnd.plotly.v1+json" in data:
                        console.print("[yellow]  📈 [Plotly chart - view in browser][/yellow]")
                
                elif output_type == "error":
                    ename = output.get("ename", "Error")
                    evalue = output.get("evalue", "")
                    traceback = output.get("traceback", [])
                    error_text = f"{ename}: {evalue}"
                    if traceback:
                        # Clean ANSI codes from traceback
                        import re
                        clean_tb = "\n".join(re.sub(r'\x1b\[[0-9;]*m', '', line) for line in traceback[:5])
                        error_text = clean_tb
                    console.print(Panel(error_text, border_style="red", title="Error", title_align="left"))
    else:
        console.print(Panel(source_text[:500], border_style="yellow"))
    
    # Footer with navigation hints
    console.print()
    nav_hints = Text()
    if index > 0:
        nav_hints.append("← ", style="bold")
        nav_hints.append("prev  ", style="dim")
    if index < total - 1:
        nav_hints.append("→ ", style="bold")
        nav_hints.append("next  ", style="dim")
    nav_hints.append("q ", style="bold red")
    nav_hints.append("quit", style="dim")
    console.print(nav_hints)


def interactive_cell_viewer(cells: List[Dict[str, Any]], console: Console) -> None:
    """Interactive viewer that allows scrolling through cells."""
    if not cells:
        console.print("[yellow]No cells in notebook.[/yellow]")
        return
    
    import sys
    
    current_index = 0
    total = len(cells)
    
    # Platform-specific key reading
    try:
        import tty
        import termios
        
        def get_key():
            """Read a single keypress (Unix)."""
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                # Handle arrow keys (escape sequences)
                if ch == '\x1b':
                    ch2 = sys.stdin.read(1)
                    if ch2 == '[':
                        ch3 = sys.stdin.read(1)
                        if ch3 == 'C':  # Right arrow
                            return 'right'
                        elif ch3 == 'D':  # Left arrow
                            return 'left'
                        elif ch3 == 'A':  # Up arrow
                            return 'left'
                        elif ch3 == 'B':  # Down arrow
                            return 'right'
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except ImportError:
        # Windows fallback
        try:
            import msvcrt
            
            def get_key():
                """Read a single keypress (Windows)."""
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):  # Special key prefix
                    ch2 = msvcrt.getch()
                    if ch2 == b'M':  # Right arrow
                        return 'right'
                    elif ch2 == b'K':  # Left arrow
                        return 'left'
                    elif ch2 == b'H':  # Up arrow
                        return 'left'
                    elif ch2 == b'P':  # Down arrow
                        return 'right'
                return ch.decode('utf-8', errors='ignore')
        except ImportError:
            # Fallback to simple input
            def get_key():
                """Fallback key reading."""
                return input("Press n/p/q: ").strip().lower()[:1] or 'n'
    
    while True:
        render_single_cell(cells[current_index], current_index, total, console)
        
        try:
            key = get_key()
        except (KeyboardInterrupt, EOFError):
            console.clear()
            break
        
        if key in ('q', 'Q', '\x03'):  # q, Q, or Ctrl+C
            console.clear()
            break
        elif key in ('right', 'n', 'j', ' ', '\r'):  # Next
            if current_index < total - 1:
                current_index += 1
        elif key in ('left', 'p', 'k'):  # Previous
            if current_index > 0:
                current_index -= 1
        elif key == 'g':  # Go to first
            current_index = 0
        elif key == 'G':  # Go to last
            current_index = total - 1


def display_notebook_cell_summary(cells: List[Dict[str, Any]], console: Console) -> None:
    """Display a summary of notebook cells."""
    if not cells:
        console.print("[yellow]No cells in notebook.[/yellow]")
        return
    
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", justify="right", style="dim")
    table.add_column("Type", justify="center")
    table.add_column("Preview", no_wrap=False)
    table.add_column("Outputs", justify="center")
    
    for i, cell in enumerate(cells[:30]):
        cell_type = cell.get("cell_type", "unknown")
        source = cell.get("source", [])
        outputs = cell.get("outputs", [])
        
        if isinstance(source, list):
            source_text = "".join(source)
        else:
            source_text = str(source)
        
        # Truncate preview
        preview = source_text[:80].replace("\n", " ")
        if len(source_text) > 80:
            preview += "..."
        
        type_style = "cyan" if cell_type == "markdown" else "green" if cell_type == "code" else "yellow"
        
        table.add_row(
            str(i + 1),
            Text(cell_type, style=type_style),
            preview,
            str(len(outputs)) if outputs else "-"
        )
    
    console.print(table)
    
    if len(cells) > 30:
        console.print(f"\n[dim]Showing first 30 of {len(cells)} cells.[/dim]")

