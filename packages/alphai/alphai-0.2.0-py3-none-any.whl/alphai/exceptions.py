"""Custom exceptions for alphai CLI."""

from typing import Optional


class AlphAIException(Exception):
    """Base exception for all alphai errors."""
    
    def __init__(self, message: str, details: Optional[str] = None):
        """Initialize exception with message and optional details."""
        self.message = message
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """String representation of the exception."""
        if self.details:
            return f"{self.message}\nDetails: {self.details}"
        return self.message


class AuthenticationError(AlphAIException):
    """Raised when authentication fails."""
    pass


class AuthorizationError(AlphAIException):
    """Raised when user lacks permissions for an operation."""
    pass


class APIError(AlphAIException):
    """Raised when API request fails."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        """Initialize API error with status code."""
        self.status_code = status_code
        super().__init__(message, details)
    
    def __str__(self) -> str:
        """String representation including status code."""
        base = super().__str__()
        if self.status_code:
            return f"{base} (Status: {self.status_code})"
        return base


class DockerError(AlphAIException):
    """Raised when Docker operations fail."""
    pass


class DockerNotAvailableError(DockerError):
    """Raised when Docker is not installed or not running."""
    
    def __init__(self):
        super().__init__(
            "Docker is not available or not running",
            "Please install Docker and ensure it's running. Visit https://docs.docker.com/get-docker/"
        )


class ContainerError(DockerError):
    """Raised when container operations fail."""
    pass


class TunnelError(AlphAIException):
    """Raised when tunnel operations fail."""
    pass


class CloudflaredError(TunnelError):
    """Raised when cloudflared operations fail."""
    pass


class ConfigurationError(AlphAIException):
    """Raised when configuration is invalid."""
    pass


class ValidationError(AlphAIException):
    """Raised when input validation fails."""
    pass


class NetworkError(AlphAIException):
    """Raised when network operations fail."""
    pass


class TimeoutError(AlphAIException):
    """Raised when an operation times out."""
    
    def __init__(self, operation: str, timeout_seconds: int):
        """Initialize timeout error."""
        super().__init__(
            f"Operation '{operation}' timed out after {timeout_seconds} seconds",
            "Try increasing the timeout or check your network connection"
        )
        self.operation = operation
        self.timeout_seconds = timeout_seconds


class ResourceNotFoundError(AlphAIException):
    """Raised when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str):
        """Initialize resource not found error."""
        super().__init__(
            f"{resource_type} '{resource_id}' not found",
            f"Verify the {resource_type.lower()} ID is correct"
        )
        self.resource_type = resource_type
        self.resource_id = resource_id


class JupyterError(AlphAIException):
    """Raised when Jupyter operations fail."""
    pass

