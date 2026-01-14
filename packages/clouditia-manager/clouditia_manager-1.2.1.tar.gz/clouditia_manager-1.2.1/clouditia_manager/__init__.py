"""
Clouditia Manager SDK - Manage GPU sessions via the Computing API

Usage:
    from clouditia_manager import GPUManager

    manager = GPUManager(api_key="sk_compute_...")

    # Create a session
    session = manager.create_session(
        gpu_type="nvidia-rtx-3090",
        vcpu=2,
        ram=4,
        storage=20
    )

    # List sessions
    sessions = manager.list_sessions()

    # Stop a session
    manager.stop_session("369bde33")
"""

__version__ = "1.0.0"
__author__ = "Clouditia"

from .client import GPUManager
from .exceptions import (
    ClouditiaManagerError,
    AuthenticationError,
    SessionNotFoundError,
    InsufficientResourcesError,
    APIError
)

__all__ = [
    "GPUManager",
    "ClouditiaManagerError",
    "AuthenticationError",
    "SessionNotFoundError",
    "InsufficientResourcesError",
    "APIError"
]
