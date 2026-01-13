"""alphai - A CLI tool and Python package for the runalph.ai platform."""

__version__ = "0.2.1"
__author__ = "American Data Science"
__email__ = "support@americandatascience.com"

from .client import AlphAIClient
from .config import Config
from .jupyter_manager import JupyterManager
from .exceptions import (
    AlphAIException,
    AuthenticationError,
    AuthorizationError,
    APIError,
    DockerError,
    DockerNotAvailableError,
    ContainerError,
    TunnelError,
    CloudflaredError,
    ConfigurationError,
    ValidationError,
    NetworkError,
    TimeoutError,
    ResourceNotFoundError,
    JupyterError,
)

__all__ = [
    "AlphAIClient",
    "Config",
    "JupyterManager",
    "__version__",
    "AlphAIException",
    "AuthenticationError",
    "AuthorizationError",
    "APIError",
    "DockerError",
    "DockerNotAvailableError",
    "ContainerError",
    "TunnelError",
    "CloudflaredError",
    "ConfigurationError",
    "ValidationError",
    "NetworkError",
    "TimeoutError",
    "ResourceNotFoundError",
    "JupyterError",
]
