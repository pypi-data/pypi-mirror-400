"""Utility functions for alphai CLI."""

import os
import sys
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime
from logging.handlers import RotatingFileHandler


def setup_logging(debug: bool = False) -> logging.Logger:
    """Setup logging configuration for alphai.
    
    Args:
        debug: If True, set log level to DEBUG and output to console
        
    Returns:
        Configured logger instance
    """
    from .config import Config
    
    log_dir = Config.get_config_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("alphai")
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # File handler with rotation (max 5 files of 10MB each)
    log_file = log_dir / "alphai.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler (only in debug mode)
    if debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    logger.debug(f"Logging initialized. Debug mode: {debug}, Log file: {log_file}")
    
    return logger


def get_logger(name: str = "alphai") -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (default: alphai)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def format_datetime(dt_string: Optional[str]) -> str:
    """Format a datetime string for display."""
    if not dt_string:
        return "N/A"
    
    try:
        # Try to parse ISO format
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, AttributeError):
        return dt_string


def format_size(size_bytes: Optional[int]) -> str:
    """Format a size in bytes to human readable format."""
    if size_bytes is None:
        return "N/A"
    
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def truncate_string(text: Optional[str], max_length: int = 50) -> str:
    """Truncate a string to a maximum length."""
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def validate_name(name: str) -> bool:
    """Validate a name string (for organizations, projects, etc.)."""
    if not name or not name.strip():
        return False
    
    # Check length
    if len(name.strip()) < 2 or len(name.strip()) > 50:
        return False
    
    # Check for valid characters (alphanumeric, spaces, hyphens, underscores)
    import re
    if not re.match(r'^[a-zA-Z0-9\s\-_]+$', name.strip()):
        return False
    
    return True


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path.cwd()
    
    # Look for common project indicators
    indicators = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt', '.alphai']
    
    while current != current.parent:
        for indicator in indicators:
            if (current / indicator).exists():
                return current
        current = current.parent
    
    # If no indicators found, return current directory
    return Path.cwd()


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file safely."""
    try:
        if file_path.exists():
            with open(file_path, 'r') as f:
                return json.load(f)
        return None
    except (json.JSONDecodeError, IOError):
        return None


def save_json_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save data to a JSON file safely."""
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except (IOError, TypeError):
        return False


def get_env_var(name: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment variable with optional default."""
    value = os.getenv(name, default)
    if value is not None and value.strip():
        return value.strip()
    return default


def confirm_destructive_action(action: str) -> bool:
    """Confirm a destructive action with the user."""
    from rich.prompt import Confirm
    return Confirm.ask(f"Are you sure you want to {action}?")


def parse_key_value_pairs(pairs: list) -> Dict[str, str]:
    """Parse key=value pairs from a list of strings."""
    result = {}
    for pair in pairs:
        if '=' in pair:
            key, value = pair.split('=', 1)
            result[key.strip()] = value.strip()
    return result


def sanitize_container_name(name: str) -> str:
    """Sanitize a string to be a valid Docker container name."""
    import re
    # Replace invalid characters with hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9_.-]', '-', name)
    # Remove leading/trailing hyphens and ensure it starts with alphanumeric
    sanitized = sanitized.strip('-')
    if not sanitized or not sanitized[0].isalnum():
        sanitized = f"alphai-{sanitized}"
    return sanitized.lower()


def is_port_available(port: int) -> bool:
    """Check if a port is available on localhost."""
    import socket
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            return result != 0  # Port is available if connection fails
    except socket.error:
        return True  # Assume available if we can't check


def find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """Find an available port starting from the given port."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(port):
            return port
    
    # If no port found in range, return the start port anyway
    return start_port


class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress tracker."""
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, increment: int = 1) -> None:
        """Update progress."""
        self.current += increment
        if self.current > self.total:
            self.current = self.total
    
    def get_percentage(self) -> float:
        """Get completion percentage."""
        if self.total == 0:
            return 100.0
        return (self.current / self.total) * 100
    
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current >= self.total 