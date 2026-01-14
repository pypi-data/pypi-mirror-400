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

    # Create with queue fallback if GPUs unavailable
    result = manager.create_session(
        gpu_type="nvidia-rtx-3090",
        queue_if_unavailable=True
    )
    if isinstance(result, dict) and result.get('queued'):
        print(f"Queued at position #{result['position']}")

    # List sessions
    sessions = manager.list_sessions()

    # Stop a session
    manager.stop_session("369bde33")

    # List queue jobs
    queue_jobs = manager.list_queue_jobs()
"""

__version__ = "1.5.0"
__author__ = "Clouditia"

from .client import GPUManager, GPUSession, GPUInventory, QueueJob, QueueAttempt
from .exceptions import (
    ClouditiaManagerError,
    AuthenticationError,
    SessionNotFoundError,
    InsufficientResourcesError,
    APIError
)

__all__ = [
    "GPUManager",
    "GPUSession",
    "GPUInventory",
    "QueueJob",
    "QueueAttempt",
    "ClouditiaManagerError",
    "AuthenticationError",
    "SessionNotFoundError",
    "InsufficientResourcesError",
    "APIError"
]
