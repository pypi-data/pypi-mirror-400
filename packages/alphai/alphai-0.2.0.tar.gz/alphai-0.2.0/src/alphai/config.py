"""Configuration management for alphai CLI."""

import os
import stat
from pathlib import Path
from typing import Optional, Dict, Any
import json
from pydantic import BaseModel, Field


class Config(BaseModel):
    """Configuration model for alphai CLI."""
    
    api_url: str = Field(default="https://www.runalph.ai/api", description="API base URL")
    bearer_token: Optional[str] = Field(default=None, description="Bearer token for API authentication")
    current_org: Optional[str] = Field(default=None, description="Current organization slug")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """Get the configuration directory."""
        config_dir = Path.home() / ".alphai"
        config_dir.mkdir(exist_ok=True)
        # Set directory permissions to be readable/writable only by owner
        config_dir.chmod(0o700)
        return config_dir
    
    @classmethod
    def get_config_file(cls) -> Path:
        """Get the configuration file path."""
        return cls.get_config_dir() / "config.json"
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file and environment."""
        config_file = cls.get_config_file()
        config_data = {}
        
        # Load from file if it exists
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Override with environment variables
        if os.getenv("ALPHAI_API_URL"):
            config_data["api_url"] = os.getenv("ALPHAI_API_URL")
        
        if os.getenv("ALPHAI_DEBUG"):
            config_data["debug"] = os.getenv("ALPHAI_DEBUG").lower() in ("true", "1", "yes")
        
        # Load bearer token from environment if available (takes precedence)
        if os.getenv("ALPHAI_BEARER_TOKEN"):
            config_data["bearer_token"] = os.getenv("ALPHAI_BEARER_TOKEN")
        
        return cls(**config_data)
    
    def save(self) -> None:
        """Save configuration to file with secure permissions."""
        config_file = self.get_config_file()
        config_data = self.model_dump()
        
        # Write the config file
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Set file permissions to be readable/writable only by owner for security
        config_file.chmod(0o600)
    
    def set_bearer_token(self, token: str) -> None:
        """Set and save bearer token securely."""
        self.bearer_token = token
        self.save()
    
    def clear_bearer_token(self) -> None:
        """Clear the bearer token."""
        self.bearer_token = None
        self.save()
    
    @property
    def base_url(self) -> str:
        """Get the base URL (without /api suffix) for auth and frontend URLs."""
        if self.api_url.endswith("/api"):
            return self.api_url[:-4]
        return self.api_url.rstrip("/")
    
    def to_sdk_config(self) -> Dict[str, Any]:
        """Convert to SDK configuration format.
        
        Note: The SDK expects the base URL without /api suffix,
        as it constructs paths like /api/orgs internally.
        """
        return {
            "bearer_auth": self.bearer_token,
            "server_url": self.base_url,
        } 