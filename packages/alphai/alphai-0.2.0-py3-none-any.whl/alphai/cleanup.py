"""Cleanup management for alphai CLI.

Provides a class-based approach to resource cleanup that replaces
global mutable state and handles signal registration safely.
"""

import signal
import sys
from typing import Optional, Callable, Dict, Any
from rich.console import Console

from .utils import get_logger

logger = get_logger(__name__)


class CleanupManager:
    """Manages cleanup of resources with proper signal handling.
    
    This class replaces the global _cleanup_state and _jupyter_cleanup_state
    dictionaries with a proper encapsulated approach that:
    - Avoids global mutable state
    - Allows safe signal handler installation/restoration
    - Can be tested in isolation
    """
    
    def __init__(self, console: Optional[Console] = None):
        """Initialize the cleanup manager.
        
        Args:
            console: Rich console for output. Creates one if not provided.
        """
        self.console = console or Console()
        self._resources: Dict[str, Dict[str, Any]] = {}
        self._cleanup_done = False
        self._original_handlers: Dict[int, Any] = {}
        self._cleanup_callbacks: list[Callable[[], None]] = []
    
    def register_resource(
        self,
        resource_type: str,
        resource_id: str,
        cleanup_fn: Optional[Callable[[], bool]] = None,
        **metadata
    ) -> None:
        """Register a resource for cleanup.
        
        Args:
            resource_type: Type of resource (e.g., 'container', 'tunnel', 'process')
            resource_id: Unique identifier for the resource
            cleanup_fn: Optional function to call for cleanup (returns success bool)
            **metadata: Additional metadata to store with the resource
        """
        key = f"{resource_type}:{resource_id}"
        self._resources[key] = {
            'type': resource_type,
            'id': resource_id,
            'cleanup_fn': cleanup_fn,
            **metadata
        }
        logger.debug(f"Registered resource for cleanup: {key}")
    
    def unregister_resource(self, resource_type: str, resource_id: str) -> None:
        """Unregister a resource (e.g., after successful manual cleanup).
        
        Args:
            resource_type: Type of resource
            resource_id: Unique identifier for the resource
        """
        key = f"{resource_type}:{resource_id}"
        if key in self._resources:
            del self._resources[key]
            logger.debug(f"Unregistered resource: {key}")
    
    def add_cleanup_callback(self, callback: Callable[[], None]) -> None:
        """Add a cleanup callback to be called during cleanup.
        
        Args:
            callback: Function to call during cleanup (no arguments, no return)
        """
        self._cleanup_callbacks.append(callback)
    
    def get_resource(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get a registered resource by type and ID.
        
        Args:
            resource_type: Type of resource
            resource_id: Unique identifier for the resource
            
        Returns:
            Resource metadata dict or None if not found
        """
        key = f"{resource_type}:{resource_id}"
        return self._resources.get(key)
    
    def has_resources(self) -> bool:
        """Check if there are any resources registered for cleanup."""
        return len(self._resources) > 0 or len(self._cleanup_callbacks) > 0
    
    def install_signal_handlers(self) -> None:
        """Install signal handlers for cleanup on interrupt.
        
        Stores original handlers so they can be restored later.
        """
        if self._original_handlers:
            logger.debug("Signal handlers already installed")
            return
        
        # Store original handlers
        self._original_handlers[signal.SIGINT] = signal.signal(
            signal.SIGINT, self._signal_handler
        )
        self._original_handlers[signal.SIGTERM] = signal.signal(
            signal.SIGTERM, self._signal_handler
        )
        logger.debug("Signal handlers installed")
    
    def restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        for sig, handler in self._original_handlers.items():
            signal.signal(sig, handler)
        self._original_handlers.clear()
        logger.debug("Signal handlers restored")
    
    def _signal_handler(self, signum: int, frame) -> None:
        """Handle interrupt signals by running cleanup.
        
        Args:
            signum: Signal number received
            frame: Current stack frame
        """
        if self._cleanup_done:
            return
        
        if not self.has_resources():
            sys.exit(0)
        
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self) -> bool:
        """Run cleanup for all registered resources.
        
        Returns:
            True if all cleanup succeeded, False if any failed
        """
        if self._cleanup_done:
            logger.debug("Cleanup already done, skipping")
            return True
        
        if not self.has_resources():
            logger.debug("No resources to clean up")
            return True
        
        self.console.print("\n[yellow]🔄 Cleaning up resources...[/yellow]")
        success = True
        
        # Run cleanup callbacks first
        for callback in self._cleanup_callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Cleanup callback failed: {e}", exc_info=True)
                self.console.print(f"[red]Error in cleanup callback: {e}[/red]")
                success = False
        
        # Clean up registered resources
        for key, resource in list(self._resources.items()):
            cleanup_fn = resource.get('cleanup_fn')
            if cleanup_fn:
                try:
                    logger.debug(f"Running cleanup for {key}")
                    if not cleanup_fn():
                        success = False
                except Exception as e:
                    logger.error(f"Cleanup failed for {key}: {e}", exc_info=True)
                    self.console.print(f"[red]Error cleaning up {resource['type']}: {e}[/red]")
                    success = False
        
        if success:
            self.console.print("[green]✓ Cleanup completed[/green]")
        else:
            self.console.print("[yellow]⚠ Cleanup completed with warnings[/yellow]")
        
        self._cleanup_done = True
        self._resources.clear()
        self._cleanup_callbacks.clear()
        
        return success
    
    def reset(self) -> None:
        """Reset the cleanup manager state (useful for testing)."""
        self._resources.clear()
        self._cleanup_callbacks.clear()
        self._cleanup_done = False
        self.restore_signal_handlers()


class DockerCleanupManager(CleanupManager):
    """Cleanup manager specialized for Docker container cleanup."""
    
    def __init__(
        self,
        console: Optional[Console] = None,
        docker_manager: Any = None,
        client: Any = None
    ):
        """Initialize Docker cleanup manager.
        
        Args:
            console: Rich console for output
            docker_manager: DockerManager instance for container operations
            client: AlphAIClient instance for API operations
        """
        super().__init__(console)
        self.docker_manager = docker_manager
        self.client = client
        self._container_id: Optional[str] = None
        self._tunnel_id: Optional[str] = None
        self._project_id: Optional[str] = None
    
    def set_container(self, container_id: str) -> None:
        """Set the container ID for cleanup."""
        self._container_id = container_id
    
    def set_tunnel(self, tunnel_id: str) -> None:
        """Set the tunnel ID for cleanup."""
        self._tunnel_id = tunnel_id
    
    def set_project(self, project_id: str) -> None:
        """Set the project ID for cleanup."""
        self._project_id = project_id
    
    def cleanup(self) -> bool:
        """Clean up Docker resources (container, tunnel, project)."""
        if self._cleanup_done:
            return True
        
        if not any([self._container_id, self._tunnel_id, self._project_id]):
            return True
        
        self.console.print("\n[yellow]🔄 Cleaning up resources...[/yellow]")
        success = True
        
        try:
            # Clean up container and cloudflared service
            if self._container_id and self.docker_manager:
                if not self.docker_manager.cleanup_container_and_tunnel(
                    container_id=self._container_id,
                    tunnel_id=self._tunnel_id,
                    project_id=self._project_id,
                    force=True
                ):
                    success = False
            
            # Clean up tunnel and project via API
            if self.client and (self._tunnel_id or self._project_id):
                if not self.client.cleanup_tunnel_and_project(
                    tunnel_id=self._tunnel_id,
                    project_id=self._project_id,
                    force=True
                ):
                    success = False
            
            if success:
                self.console.print("[green]✓ Cleanup completed[/green]")
            else:
                self.console.print("[yellow]⚠ Cleanup completed with warnings[/yellow]")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            self.console.print(f"[red]Error during cleanup: {e}[/red]")
            success = False
        
        # Reset state
        self._container_id = None
        self._tunnel_id = None
        self._project_id = None
        self._cleanup_done = True
        
        return success


class JupyterCleanupManager(CleanupManager):
    """Cleanup manager specialized for Jupyter process cleanup."""
    
    def __init__(
        self,
        console: Optional[Console] = None,
        jupyter_manager: Any = None,
        client: Any = None
    ):
        """Initialize Jupyter cleanup manager.
        
        Args:
            console: Rich console for output
            jupyter_manager: JupyterManager instance for process operations
            client: AlphAIClient instance for API operations
        """
        super().__init__(console)
        self.jupyter_manager = jupyter_manager
        self.client = client
        self._tunnel_id: Optional[str] = None
        self._project_id: Optional[str] = None
    
    def set_tunnel(self, tunnel_id: str) -> None:
        """Set the tunnel ID for cleanup."""
        self._tunnel_id = tunnel_id
    
    def set_project(self, project_id: str) -> None:
        """Set the project ID for cleanup."""
        self._project_id = project_id
    
    def cleanup(self) -> bool:
        """Clean up Jupyter resources (process, tunnel, project)."""
        if self._cleanup_done:
            return True
        
        if not self.jupyter_manager:
            return True
        
        self.console.print("\n[yellow]🔄 Cleaning up Jupyter resources...[/yellow]")
        success = True
        
        try:
            # Comprehensive cleanup via JupyterManager
            if not self.jupyter_manager.cleanup(
                client=self.client,
                tunnel_id=self._tunnel_id,
                project_id=self._project_id,
                force=True
            ):
                success = False
            
            if success:
                self.console.print("[green]✓ Cleanup completed[/green]")
            else:
                self.console.print("[yellow]⚠ Cleanup completed with warnings[/yellow]")
                
        except Exception as e:
            logger.error(f"Error during Jupyter cleanup: {e}", exc_info=True)
            self.console.print(f"[red]Error during cleanup: {e}[/red]")
            success = False
        
        # Reset state
        self._tunnel_id = None
        self._project_id = None
        self._cleanup_done = True
        
        return success

