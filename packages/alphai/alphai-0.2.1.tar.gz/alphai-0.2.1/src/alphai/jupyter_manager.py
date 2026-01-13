"""Jupyter management with automatic tunneling for alphai CLI."""

import sys
import shutil
import subprocess
import platform
import time
import socket
import webbrowser
from pathlib import Path
from typing import Optional, List, Tuple, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from .utils import get_logger
from . import exceptions

logger = get_logger(__name__)


class JupyterManager:
    """Manage Jupyter Lab/Notebook instances with automatic tunneling."""
    
    def __init__(self, console: Console):
        """Initialize the Jupyter manager."""
        self.console = console
        self._jupyter_process = None
        self._cloudflared_process = None
        self._tunnel_data = None
    
    def is_jupyter_installed(self, command: str = "jupyter") -> bool:
        """Check if Jupyter is installed."""
        installed = shutil.which(command) is not None
        if installed:
            logger.debug(f"{command} is installed")
        else:
            logger.warning(f"{command} not found in PATH")
        return installed
    
    def check_jupyter_or_exit(self, command: str = "jupyter") -> None:
        """Check if Jupyter is installed, exit with helpful message if not."""
        if not self.is_jupyter_installed(command):
            logger.error(f"{command} not found")
            self.console.print(f"[red]Error: {command} not found[/red]")
            self.console.print(f"[yellow]Install it with: pip install jupyterlab[/yellow]")
            sys.exit(1)
    
    def generate_jupyter_token(self) -> str:
        """Generate a secure token for Jupyter."""
        import secrets
        token = secrets.token_hex(32)
        logger.debug(f"Generated Jupyter token: {token[:12]}...")
        return token
    
    def build_jupyter_command(
        self,
        command: List[str],
        port: int,
        token: str,
        extra_args: List[str],
        allow_remote: bool = False
    ) -> List[str]:
        """Build the full Jupyter command with all arguments.
        
        Args:
            command: Base command (e.g., ['jupyter', 'lab'])
            port: Port number
            token: Authentication token
            extra_args: Additional user arguments
            allow_remote: If True, allow remote access (needed for tunnels)
        """
        full_command = command + [
            f'--port={port}',
            '--no-browser',  # We'll open browser to cloud URL instead
            '--ServerApp.allow_origin=*',
        ]
        
        # Add token (different format for lab vs notebook)
        if 'lab' in command:
            full_command.append(f'--ServerApp.token={token}')
            if allow_remote:
                # Allow remote access for tunnel (secure via token + cloudflare)
                full_command.append('--ServerApp.allow_remote_access=true')
        else:
            full_command.append(f'--NotebookApp.token={token}')
            if allow_remote:
                # Allow remote access for tunnel
                full_command.append('--NotebookApp.allow_remote_access=true')
        
        # Add user's extra arguments
        full_command.extend(extra_args)
        
        logger.debug(f"Built command: {' '.join(full_command[:3])}... (+ {len(extra_args)} extra args, allow_remote={allow_remote})")
        return full_command
    
    def start_jupyter(
        self,
        command: List[str],
        port: int,
        token: str,
        extra_args: List[str] = None,
        allow_remote: bool = False
    ) -> subprocess.Popen:
        """Start Jupyter in background process.
        
        Args:
            command: Base command (e.g., ['jupyter', 'lab'])
            port: Port number
            token: Authentication token
            extra_args: Additional user arguments
            allow_remote: If True, allow remote access (needed for tunnels)
        """
        extra_args = extra_args or []
        full_command = self.build_jupyter_command(command, port, token, extra_args, allow_remote)
        
        logger.info(f"Starting {' '.join(command)} on port {port} (allow_remote={allow_remote})")
        self.console.print(f"[yellow]Starting {' '.join(command)}...[/yellow]")
        
        try:
            process = subprocess.Popen(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self._jupyter_process = process
            logger.info(f"Jupyter process started with PID {process.pid}")
            return process
            
        except Exception as e:
            logger.error(f"Failed to start Jupyter: {e}", exc_info=True)
            self.console.print(f"[red]Failed to start Jupyter: {e}[/red]")
            raise exceptions.JupyterError(f"Failed to start Jupyter: {e}")
    
    def is_port_available(self, port: int) -> bool:
        """Check if a port is available for use."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.bind(('localhost', port))
                return True
        except (socket.error, OSError):
            return False
    
    def find_available_port(self, start_port: int, max_attempts: int = 10) -> int:
        """Find an available port starting from start_port.
        
        Args:
            start_port: Port to start searching from
            max_attempts: Maximum number of ports to try
            
        Returns:
            An available port number
            
        Raises:
            JupyterError: If no available port found
        """
        for offset in range(max_attempts):
            port = start_port + offset
            if self.is_port_available(port):
                if offset > 0:
                    logger.info(f"Port {start_port} was in use, using port {port} instead")
                    self.console.print(f"[yellow]Port {start_port} is in use, using port {port}[/yellow]")
                return port
        
        raise exceptions.JupyterError(
            f"Could not find available port (tried {start_port} to {start_port + max_attempts - 1})"
        )
    
    def wait_for_jupyter_ready(self, port: int, timeout: int = 30) -> bool:
        """Wait for Jupyter to be ready on the specified port."""
        logger.debug(f"Waiting for Jupyter on port {port} (timeout: {timeout}s)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    s.connect(('localhost', port))
                    logger.info(f"Jupyter is ready on port {port}")
                    return True
            except (socket.error, socket.timeout):
                time.sleep(0.5)
        
        logger.error(f"Jupyter failed to start within {timeout}s")
        return False
    
    def _get_cloudflared_path(self) -> Path:
        """Get the path where cloudflared should be installed."""
        return Path.home() / ".alphai" / "bin" / "cloudflared"
    
    def is_cloudflared_installed(self) -> bool:
        """Check if cloudflared is installed (either in PATH or in ~/.alphai/bin)."""
        # Check system PATH first
        if shutil.which("cloudflared") is not None:
            logger.debug("cloudflared found in system PATH")
            return True
        
        # Check local installation
        local_path = self._get_cloudflared_path()
        if local_path.exists() and local_path.is_file():
            logger.debug(f"cloudflared found at {local_path}")
            return True
        
        logger.debug("cloudflared not found")
        return False
    
    def _get_cloudflared_binary(self) -> str:
        """Get the cloudflared binary path (system or local)."""
        # Prefer system installation
        system_binary = shutil.which("cloudflared")
        if system_binary:
            return system_binary
        
        # Fall back to local installation
        local_path = self._get_cloudflared_path()
        if local_path.exists():
            return str(local_path)
        
        return "cloudflared"  # Fallback
    
    def install_cloudflared(self) -> bool:
        """Install cloudflared to user directory (no sudo required)."""
        logger.info("Installing connector to user directory")
        self.console.print("[yellow]Installing connector...[/yellow]")
        
        system = platform.system().lower()
        bin_dir = Path.home() / ".alphai" / "bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        
        cloudflared_path = bin_dir / "cloudflared"
        
        try:
            # Determine architecture
            machine = platform.machine().lower()
            if machine in ["x86_64", "amd64"]:
                arch = "amd64"
            elif machine in ["aarch64", "arm64"]:
                arch = "arm64"
            elif machine.startswith("arm"):
                arch = "arm"
            else:
                arch = "amd64"  # Default fallback
            
            # Build download URL based on OS
            if system == "linux":
                url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-{arch}"
                download_cmd = ["wget", "-q", "-O", str(cloudflared_path), url]
            
            elif system == "darwin":  # macOS
                url = f"https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-darwin-{arch}"
                download_cmd = ["curl", "-sL", "-o", str(cloudflared_path), url]
            
            elif system == "windows":
                self.console.print("[yellow]Windows requires manual connector setup[/yellow]")
                self.console.print("[dim]Visit: https://github.com/cloudflare/cloudflared/releases[/dim]")
                self.console.print(f"[dim]Place the binary in: {bin_dir}[/dim]")
                return False
            
            else:
                logger.error(f"Unsupported operating system: {system}")
                self.console.print(f"[red]Unsupported operating system: {system}[/red]")
                return False
            
            # Download the binary
            logger.debug(f"Downloading cloudflared from {url}")
            result = subprocess.run(download_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Download failed: {result.stderr}")
                self.console.print(f"[red]Download failed: {result.stderr}[/red]")
                return False
            
            # Make it executable
            cloudflared_path.chmod(0o755)
            
            logger.info(f"Connector installed successfully to {cloudflared_path}")
            self.console.print("[green]✓ Connector installed[/green]")
            return True
            
        except Exception as e:
            logger.error(f"Failed to install connector: {e}", exc_info=True)
            self.console.print(f"[red]Error installing connector: {e}[/red]")
            return False
    
    def ensure_cloudflared(self) -> bool:
        """Ensure connector is installed, offer to install if not."""
        if self.is_cloudflared_installed():
            self.console.print("[green]✓ Connector ready[/green]")
            return True
        
        logger.info("Connector not found, prompting user to install")
        self.console.print("[yellow]Connector not found[/yellow]")
        
        if not Confirm.ask("Install connector now?", default=True):
            logger.info("User declined connector installation")
            return False
        
        return self.install_cloudflared()
    
    def setup_cloudflared_tunnel(self, token: str) -> bool:
        """Start cloudflared connector as a subprocess (no sudo required)."""
        logger.info("Starting cloudflared connector process")
        self.console.print("[yellow]Establishing connection...[/yellow]")
        
        try:
            cloudflared_bin = self._get_cloudflared_binary()
            
            # Run cloudflared tunnel with the token
            # This doesn't require sudo and runs as a regular process
            self._cloudflared_process = subprocess.Popen(
                [cloudflared_bin, "tunnel", "run", "--token", token],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            # Check if it's still running
            if self._cloudflared_process.poll() is not None:
                # Process exited
                _, stderr = self._cloudflared_process.communicate(timeout=1)
                logger.error(f"Connection failed to start: {stderr}")
                self.console.print(f"[red]Connection failed: {stderr}[/red]")
                return False
            
            logger.info(f"Cloudflared connector started (PID: {self._cloudflared_process.pid})")
            self.console.print("[green]✓ Connection established[/green]")
            return True
                
        except Exception as e:
            logger.error(f"Error starting cloudflared: {e}", exc_info=True)
            self.console.print(f"[red]Error establishing connection: {e}[/red]")
            return False
    
    def cleanup_cloudflared_tunnel(self) -> bool:
        """Stop cloudflared tunnel process."""
        logger.info("Stopping cloudflared tunnel")
        
        if not self._cloudflared_process:
            logger.debug("No cloudflared process to stop")
            return True
        
        try:
            # Terminate the process gracefully
            logger.debug(f"Terminating cloudflared process (PID: {self._cloudflared_process.pid})")
            self._cloudflared_process.terminate()
            
            # Wait for graceful shutdown
            try:
                self._cloudflared_process.wait(timeout=5)
                logger.info("Cloudflared process terminated gracefully")
                return True
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't stop
                logger.warning("Cloudflared didn't stop gracefully, forcing...")
                self._cloudflared_process.kill()
                self._cloudflared_process.wait(timeout=2)
                logger.info("Cloudflared process force-killed")
                return True
                
        except Exception as e:
            logger.warning(f"Error stopping cloudflared: {e}")
            # Try force kill as last resort
            try:
                if self._cloudflared_process and self._cloudflared_process.poll() is None:
                    self._cloudflared_process.kill()
            except Exception:
                pass
            return True  # Don't fail cleanup if cloudflared cleanup has issues
    
    def display_jupyter_info(
        self,
        jupyter_port: int,
        token: str,
        tunnel_data: Optional[Any] = None,
        org: Optional[str] = None,
        project: Optional[str] = None,
        api_url: str = "https://www.runalph.ai",
        app_port: Optional[int] = None
    ) -> None:
        """Display access information for Jupyter and optionally app."""
        summary = []
        
        summary.append("[bold]🎓 Jupyter Lab Access Information[/bold]")
        summary.append("")
        
        # Local access
        summary.append("[bold blue]Local URL:[/bold blue]")
        summary.append(f"  • Jupyter: http://localhost:{jupyter_port}?token={token}")
        if app_port:
            summary.append(f"  • App: http://localhost:{app_port}")
        summary.append("")
        
        # Cloud access
        if tunnel_data:
            summary.append("[bold green]Public URL:[/bold green]")
            summary.append(f"  • Jupyter: {tunnel_data.jupyter_url}?token={token}")
            if app_port and hasattr(tunnel_data, 'app_url'):
                summary.append(f"  • App: {tunnel_data.app_url}")
            summary.append("")
            
            # Project URL - use slug from project_data if available
            frontend_url = api_url.replace("/api", "").rstrip("/")
            project_slug = project
            if tunnel_data.project_data:
                # Prefer slug from API response
                if hasattr(tunnel_data.project_data, 'slug') and tunnel_data.project_data.slug:
                    project_slug = tunnel_data.project_data.slug
                elif hasattr(tunnel_data.project_data, 'name') and tunnel_data.project_data.name:
                    # Fallback to name if no slug
                    project_slug = tunnel_data.project_data.name
            
            project_url = f"{frontend_url}/{org}/{project_slug}"
            summary.append(f"[bold cyan]Dashboard:[/bold cyan]")
            summary.append(f"  {project_url}")
            summary.append("")
            
            # Auto-open browser
            try:
                webbrowser.open(project_url)
                logger.info(f"Opened browser to {project_url}")
                summary.append("[dim]→ Browser opened to dashboard[/dim]")
            except Exception as e:
                logger.warning(f"Could not open browser: {e}")
        else:
            summary.append("[dim]Local only - no cloud connection[/dim]")
            summary.append("[dim]Run 'alphai login' to enable cloud access[/dim]")
        
        summary.append("")
        summary.append(f"[bold yellow]Jupyter Token:[/bold yellow] {token}")
        
        panel = Panel(
            "\n".join(summary),
            title="🚀 Jupyter Running",
            border_style="green"
        )
        self.console.print(panel)
    
    def monitor_jupyter(self, show_logs: bool = True) -> None:
        """Monitor Jupyter process until interrupted.
        
        Args:
            show_logs: If True, stream Jupyter output to console (default: True)
        """
        if not self._jupyter_process:
            logger.error("No Jupyter process to monitor")
            return
        
        self.console.print("\n[bold green]🎯 Jupyter is running! Press Ctrl+C to stop.[/bold green]")
        
        if show_logs:
            self.console.print("[dim]Streaming Jupyter logs below...[/dim]\n")
        
        try:
            if show_logs:
                # Stream logs in real-time
                logger.debug("Streaming Jupyter logs")
                import threading
                
                def stream_output(pipe, prefix=""):
                    """Stream output from pipe."""
                    try:
                        for line in iter(pipe.readline, ''):
                            if line:
                                # Print without rich formatting to preserve Jupyter's colors
                                print(f"{prefix}{line}", end='')
                    except Exception:
                        pass
                
                # Stream both stdout and stderr
                stdout_thread = threading.Thread(
                    target=stream_output, 
                    args=(self._jupyter_process.stdout, ""),
                    daemon=True
                )
                stderr_thread = threading.Thread(
                    target=stream_output, 
                    args=(self._jupyter_process.stderr, ""),
                    daemon=True
                )
                
                stdout_thread.start()
                stderr_thread.start()
                
                # Wait for process to exit
                self._jupyter_process.wait()
            else:
                # Just wait for process silently
                self._jupyter_process.wait()
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, stopping Jupyter")
            self.console.print("\n[yellow]Stopping Jupyter...[/yellow]")
    
    def cleanup(
        self, 
        client: Optional[Any] = None, 
        tunnel_id: Optional[str] = None,
        project_id: Optional[str] = None,
        force: bool = False
    ) -> bool:
        """Comprehensive cleanup of Jupyter process and tunnel resources.
        
        Args:
            client: AlphAIClient instance for API cleanup
            tunnel_id: Tunnel ID to delete (optional, uses stored tunnel_data if not provided)
            project_id: Project ID to delete (optional)
            force: If True, force cleanup even on errors
            
        Returns:
            bool: True if all cleanup successful, False if any warnings
        """
        logger.info("Starting comprehensive cleanup")
        success = True
        
        # Step 1: Stop Jupyter process
        if self._jupyter_process:
            try:
                logger.debug(f"Stopping Jupyter process (PID: {self._jupyter_process.pid})")
                # Use SIGKILL directly since SIGTERM causes Jupyter to prompt for
                # confirmation which hangs because stdin isn't connected
                self._jupyter_process.kill()
                self._jupyter_process.wait(timeout=5)
                logger.info("Jupyter process stopped")
                self.console.print("[green]✓ Jupyter stopped[/green]")
                    
            except Exception as e:
                logger.error(f"Error stopping Jupyter: {e}", exc_info=True)
                self.console.print(f"[yellow]⚠ Error stopping Jupyter: {e}[/yellow]")
                success = False
        
        # Step 2: Cleanup cloudflared connection service
        if not self.cleanup_cloudflared_tunnel():
            success = False
            self.console.print("[yellow]⚠ Connection cleanup had issues[/yellow]")
        else:
            self.console.print("[green]✓ Connection closed[/green]")
        
        # Step 3: Delete tunnel and project from API
        if client:
            # Use provided tunnel_id or fall back to stored tunnel_data
            actual_tunnel_id = tunnel_id or (self._tunnel_data.id if self._tunnel_data else None)
            
            if actual_tunnel_id or project_id:
                try:
                    logger.info(f"Deleting tunnel and project from API (tunnel={actual_tunnel_id}, project={project_id})")
                    if not client.cleanup_tunnel_and_project(
                        tunnel_id=actual_tunnel_id,
                        project_id=project_id,
                        force=force
                    ):
                        logger.warning("API cleanup had issues")
                        success = False
                except Exception as e:
                    logger.error(f"Error during API cleanup: {e}", exc_info=True)
                    self.console.print(f"[yellow]⚠ Error during API cleanup: {e}[/yellow]")
                    success = False
        
        # Summary
        if success:
            self.console.print("\n[bold green]✅ Cleanup completed successfully![/bold green]")
            logger.info("Cleanup completed successfully")
        else:
            self.console.print("\n[bold yellow]⚠ Cleanup completed with warnings[/bold yellow]")
            self.console.print("[dim]Check logs for details: ~/.alphai/logs/alphai.log[/dim]")
            logger.warning("Cleanup completed with warnings")
        
        return success
    
    def set_tunnel_data(self, tunnel_data: Any) -> None:
        """Store tunnel data for cleanup."""
        self._tunnel_data = tunnel_data

