"""
Clouditia Manager SDK Client

Manage GPU sessions via the Computing API (sk_compute_ keys)
"""

import requests
import time
import sys
from typing import Optional, Dict, List, Any, Callable
from dataclasses import dataclass
from datetime import datetime

from .exceptions import (
    ClouditiaManagerError,
    AuthenticationError,
    SessionNotFoundError,
    InsufficientResourcesError,
    APIError
)


@dataclass
class GPUSession:
    """Represents a GPU session"""
    id: str
    short_id: str
    name: str
    status: str
    gpu_type: str
    gpu_count: int
    gpus: Optional[List[Dict]]
    vcpu: int
    ram: str
    storage: str
    vscode_port: Optional[int]
    jupyter_port: Optional[int]
    password: Optional[str]
    url: str
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    # Auto-stop limits
    cost_limit: Optional[float] = None
    duration_limit: Optional[int] = None
    auto_stop_enabled: bool = False

    def __repr__(self):
        limits = ""
        if self.auto_stop_enabled:
            limits = f", limits=True"
        return f"GPUSession(name='{self.name}', id='{self.short_id}', gpus={self.gpu_count}, status='{self.status}'{limits})"


@dataclass
class GPUInventory:
    """Represents available GPU in marketplace"""
    gpu_type: str
    gpu_name: str
    available: int
    price_per_hour: float

    def __repr__(self):
        return f"GPUInventory(type='{self.gpu_type}', available={self.available})"


@dataclass
class QueueJob:
    """Represents a queued session creation request"""
    queue_id: str
    position: int
    status: str
    status_display: str
    gpu_config: Dict
    vcpu: int
    ram: int
    storage: int
    allow_partial: bool
    attempt_count: int
    last_attempt_at: Optional[datetime]
    last_error: str
    created_at: Optional[datetime]
    created_session_id: Optional[str]

    def __repr__(self):
        return f"QueueJob(id='{self.queue_id[:8]}', position={self.position}, status='{self.status}', attempts={self.attempt_count})"


@dataclass
class QueueAttempt:
    """Represents an attempt to create a session from queue"""
    attempt_id: str
    success: bool
    error_message: str
    available_gpus: List[str]
    unavailable_gpus: List[str]
    attempted_at: Optional[datetime]

    def __repr__(self):
        status = "Success" if self.success else "Failed"
        return f"QueueAttempt(id='{self.attempt_id[:8]}', {status})"


@dataclass
class LambdaResult:
    """Result of a lambda GPU execution"""
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    output_files: List[str]
    session_id: str
    duration_seconds: float
    cost: float
    error: Optional[str] = None

    def __repr__(self):
        status = "Success" if self.success else f"Failed(exit={self.exit_code})"
        return f"LambdaResult({status}, duration={self.duration_seconds:.1f}s, cost={self.cost:.2f}EUR)"


class GPUManager:
    """
    Clouditia GPU Manager Client

    Manage GPU sessions using the Computing API.

    Args:
        api_key: Your sk_compute_ API key
        base_url: API base URL (default: https://clouditia.com/jobs)
        timeout: Request timeout in seconds (default: 60)
    """

    DEFAULT_BASE_URL = "https://clouditia.com/jobs"

    def __init__(
        self,
        api_key: str,
        base_url: str = None,
        timeout: int = 60
    ):
        if not api_key or not api_key.startswith("sk_compute_"):
            raise AuthenticationError("Invalid API key. Must start with 'sk_compute_'")

        self.api_key = api_key
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "clouditia-manager/1.0.0"
        })

        # Verify API key on init
        self._verify_api_key()

    def _verify_api_key(self):
        """Verify the API key is valid"""
        try:
            response = self._request("GET", "/api/computing/verify/")
            if not response.get("valid"):
                raise AuthenticationError("API key is not valid")
            self.user = response.get("user", {})
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to verify API key: {e}")

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None
    ) -> Dict:
        """Make an API request"""
        url = f"{self.base_url}{endpoint}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 401:
                raise AuthenticationError("Invalid or expired API key")
            elif response.status_code == 403:
                raise AuthenticationError("Access denied")
            elif response.status_code == 404:
                raise SessionNotFoundError("Resource not found")
            elif response.status_code == 400:
                # Return JSON response for 400 errors (may contain availability info)
                try:
                    return response.json()
                except:
                    raise APIError(f"Bad request: {response.text}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.JSONDecodeError:
            return {"raw": response.text}
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

    def create_session(
        self,
        gpu_type: str = None,
        gpu_count: int = 1,
        gpus: List[Dict] = None,
        vcpu: int = 4,
        ram: int = 16,
        storage: int = 20,
        wait_ready: bool = True,
        timeout: int = 180,
        verbose: bool = True,
        allow_partial: bool = False,
        queue_if_unavailable: bool = False,
        cost_limit: float = None,
        duration_limit: int = None
    ) -> GPUSession:
        """
        Create a new GPU session.

        Args:
            gpu_type: GPU type slug (e.g., 'nvidia-rtx-3090') - for single GPU
            gpu_count: Number of GPUs of same type (default: 1)
            gpus: List of GPU configs for multiple GPU types
                  Example: [{'type': 'nvidia-rtx-3090', 'count': 1},
                           {'type': 'nvidia-rtx-3060ti', 'count': 1}]
            vcpu: Number of vCPUs (default: 4)
            ram: RAM in GB (default: 16)
            storage: Storage in GB (default: 20)
            wait_ready: Wait for session to be fully ready (default: True)
            timeout: Max wait time in seconds (default: 180)
            verbose: Print status messages (default: True)
            allow_partial: If True, create session with only available GPUs
                          when some requested GPUs are unavailable (default: False)
            queue_if_unavailable: If True, add request to queue when GPUs are unavailable
                                 instead of raising an error (default: False)
            cost_limit: Maximum cost in EUR before auto-stop (default: None = no limit)
            duration_limit: Maximum duration in seconds before auto-stop (default: None = no limit)

        Returns:
            GPUSession object with session details
            Or Dict with queue info if queue_if_unavailable=True and request was queued

        Raises:
            InsufficientResourcesError: If requested GPU is not available (and not queued)
            APIError: If session creation fails
        """
        # Build request data
        data = {
            "vcpu": vcpu,
            "ram": ram,
            "storage": storage,
            "allow_partial": allow_partial,
            "queue_if_unavailable": queue_if_unavailable
        }

        # Add limits if specified
        if cost_limit is not None:
            data["cost_limit"] = cost_limit
        if duration_limit is not None:
            data["duration_limit"] = duration_limit

        # Support both single GPU and multiple GPUs
        if gpus:
            data["gpus"] = gpus
            gpu_desc = ", ".join([f"{g.get('count', 1)}x {g.get('type', 'GPU')}" for g in gpus])
        else:
            gpu_type = gpu_type or "nvidia-rtx-3090"
            data["gpu_type"] = gpu_type
            data["gpu_count"] = gpu_count
            gpu_desc = f"{gpu_count}x {gpu_type}"

        if verbose:
            print(f"Creating GPU session with {gpu_desc}...")
            print(f"Checking GPU availability...")

        response = self._request("POST", "/api/computing/sessions/create/", data=data)

        # Handle queued response
        if response.get("queued"):
            queue_id = response.get("queue_id")
            position = response.get("position")
            message = response.get("message", "Demande ajoutée à la queue")

            if verbose:
                print(f"\n{'='*50}")
                print(f"  REQUEST QUEUED")
                print(f"{'='*50}")
                print(f"  Queue ID  : {queue_id[:8]}...")
                print(f"  Position  : #{position}")
                print(f"  Message   : {message}")
                unavailable = response.get("unavailable_gpus", [])
                available = response.get("available_gpus", [])
                if unavailable:
                    print(f"  Unavailable GPUs: {', '.join(unavailable)}")
                if available:
                    print(f"  Available GPUs  : {', '.join(available)}")
                print(f"{'='*50}")
                print(f"\nUse manager.get_queue_job('{queue_id[:8]}') to check status")
                print(f"Use manager.cancel_queue_job('{queue_id[:8]}') to cancel\n")

            # Return queue info as dict
            return {
                'queued': True,
                'queue_id': queue_id,
                'position': position,
                'message': message,
                'unavailable_gpus': response.get('unavailable_gpus', []),
                'available_gpus': response.get('available_gpus', [])
            }

        # Handle partial availability response
        if not response.get("success"):
            error = response.get("error", "Unknown error")
            unavailable = response.get("unavailable_gpus", [])
            available = response.get("available_gpus", [])

            # Check if this is a partial availability situation
            if unavailable and available:
                if verbose:
                    print(f"\n{'='*50}")
                    print(f"  GPU AVAILABILITY CHECK")
                    print(f"{'='*50}")
                    print(f"  Unavailable GPUs:")
                    for gpu in unavailable:
                        print(f"    - {gpu}")
                    print(f"  Available GPUs:")
                    for gpu in available:
                        print(f"    - {gpu}")
                    print(f"{'='*50}")

                    # Ask user if they want to continue with available GPUs
                    try:
                        user_input = input(f"\nContinue with {len(available)} available GPU(s)? [y/N]: ").strip().lower()
                        if user_input in ['y', 'yes', 'o', 'oui']:
                            # Retry with allow_partial=True
                            data["allow_partial"] = True
                            if verbose:
                                print(f"\nCreating session with available GPUs only...")
                            response = self._request("POST", "/api/computing/sessions/create/", data=data)

                            if not response.get("success"):
                                raise APIError(response.get("error", "Failed to create session"))
                        else:
                            raise InsufficientResourcesError(
                                f"GPUs indisponibles: {', '.join(unavailable)}"
                            )
                    except EOFError:
                        # Non-interactive mode, raise error
                        raise InsufficientResourcesError(
                            f"GPUs indisponibles: {', '.join(unavailable)}. "
                            f"Utilisez allow_partial=True pour continuer avec: {', '.join(available)}"
                        )
                else:
                    # Not verbose, just raise error with info
                    raise InsufficientResourcesError(
                        f"GPUs indisponibles: {', '.join(unavailable)}. "
                        f"GPUs disponibles: {', '.join(available)}. "
                        f"Utilisez allow_partial=True pour continuer."
                    )

            # No GPUs available at all
            elif unavailable and not available:
                raise InsufficientResourcesError(
                    f"Aucun GPU disponible. Indisponibles: {', '.join(unavailable)}"
                )

            # Other error
            if "disponible" in error.lower() or "available" in error.lower():
                raise InsufficientResourcesError(error)
            raise APIError(error)

        session_data = response.get("session", {})
        session = self._parse_session(session_data)

        if verbose:
            print(f"Session created: {session.short_id}")

        # Wait for session to be fully ready
        if wait_ready:
            session = self._wait_for_ready(session.short_id, timeout=timeout, verbose=verbose)

        return session

    def _wait_for_ready(
        self,
        session_id: str,
        timeout: int = 180,
        poll_interval: int = 3,
        verbose: bool = True
    ) -> GPUSession:
        """
        Internal method: Wait for session and GPU resources to be ready.

        This method polls the session status until it's running and ready.
        GPU resource updates are handled automatically by the server.
        """
        if verbose:
            print(f"Waiting for session {session_id} to be ready...", end="", flush=True)

        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            try:
                session = self.get_session(session_id)

                if session.status != last_status:
                    last_status = session.status
                    if verbose and session.status == "pending":
                        print(".", end="", flush=True)

                if session.status == "running":
                    # Give a moment for GPU resources to fully initialize
                    time.sleep(2)

                    if verbose:
                        print(" Ready!")
                        print(f"\n{'='*50}")
                        print(f"  SESSION READY")
                        print(f"{'='*50}")
                        print(f"  Name     : {session.name}")
                        print(f"  Short ID : {session.short_id}")
                        print(f"  Status   : {session.status}")
                        # Display GPUs
                        if session.gpus and len(session.gpus) > 1:
                            print(f"  GPUs     : {session.gpu_count} total")
                            for gpu in session.gpus:
                                print(f"           - {gpu.get('slug', 'GPU')} x{gpu.get('quantity', 1)}")
                        else:
                            print(f"  GPU      : {session.gpu_type} x{session.gpu_count}")
                        print(f"  vCPU     : {session.vcpu}")
                        print(f"  RAM      : {session.ram}")
                        print(f"  Storage  : {session.storage}")
                        # Display limits if set
                        if session.auto_stop_enabled:
                            print(f"  {'-'*46}")
                            print(f"  AUTO-STOP ENABLED")
                            if session.cost_limit:
                                print(f"  Cost Limit     : {session.cost_limit} EUR")
                            if session.duration_limit:
                                hours = session.duration_limit // 3600
                                mins = (session.duration_limit % 3600) // 60
                                print(f"  Duration Limit : {hours}h {mins}m ({session.duration_limit}s)")
                            print(f"  {'-'*46}")
                        print(f"  URL      : {session.url}")
                        print(f"  Password : {session.password}")
                        print(f"{'='*50}\n")

                    return session

                elif session.status == "failed":
                    if verbose:
                        print(" Failed!")
                    raise APIError(f"Session {session_id} failed to start")

            except SessionNotFoundError:
                pass

            if verbose:
                print(".", end="", flush=True)

            time.sleep(poll_interval)

        if verbose:
            print(" Timeout!")
        raise APIError(f"Timeout waiting for session {session_id} to be ready")

    def stop_session(
        self,
        session_id: str,
        wait_stopped: bool = True,
        timeout: int = 120,
        verbose: bool = True
    ) -> GPUSession:
        """
        Stop a running GPU session.

        Args:
            session_id: Session ID (short or full UUID)
            wait_stopped: Wait for session to be fully stopped (default: True)
            timeout: Max wait time in seconds (default: 120)
            verbose: Print status messages (default: True)

        Returns:
            GPUSession object with final status

        Raises:
            SessionNotFoundError: If session is not found
        """
        # Get session info first
        try:
            session = self.get_session(session_id)
        except SessionNotFoundError:
            raise SessionNotFoundError(f"Session {session_id} not found")

        if verbose:
            print(f"Stopping session {session.short_id}...")

        response = self._request(
            "POST",
            "/api/computing/sessions/stop/",
            data={"session_id": session_id}
        )

        if not response.get("success"):
            error = response.get("error", "Unknown error")
            if "not found" in error.lower() or "non trouvée" in error.lower():
                raise SessionNotFoundError(f"Session {session_id} not found")
            raise APIError(error)

        # Wait for session to be fully stopped
        if wait_stopped:
            session = self._wait_for_stopped(
                session.short_id,
                session_info=session,
                timeout=timeout,
                verbose=verbose
            )

        return session

    def _wait_for_stopped(
        self,
        session_id: str,
        session_info: GPUSession = None,
        timeout: int = 120,
        poll_interval: int = 2,
        verbose: bool = True
    ) -> GPUSession:
        """
        Internal method: Wait for session and pods to be fully stopped.

        GPU resource updates are handled automatically by the server.
        """
        if verbose:
            print(f"Waiting for pod termination...", end="", flush=True)

        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                session = self.get_session(session_id)

                if session.status == "stopped":
                    if verbose:
                        print(" Done!")
                        print(f"\n{'='*50}")
                        print(f"  SESSION STOPPED")
                        print(f"{'='*50}")
                        print(f"  Name     : {session.name}")
                        print(f"  Short ID : {session.short_id}")
                        print(f"  Status   : {session.status}")
                        # Display GPUs
                        if session.gpus and len(session.gpus) > 1:
                            print(f"  GPUs     : {session.gpu_count} released")
                            for gpu in session.gpus:
                                print(f"           - {gpu.get('slug', 'GPU')}")
                        else:
                            print(f"  GPU      : {session.gpu_type} (released)")
                        print(f"{'='*50}\n")

                    return session

            except SessionNotFoundError:
                # Session might be deleted, consider it stopped
                session_name = session_info.name if session_info else f"compute-gpu-{session_id}"
                if verbose:
                    print(" Done!")
                    print(f"\n{'='*50}")
                    print(f"  SESSION STOPPED")
                    print(f"{'='*50}")
                    print(f"  Name     : {session_name}")
                    print(f"  Short ID : {session_id}")
                    print(f"  Status   : stopped (deleted)")
                    print(f"{'='*50}\n")

                if session_info:
                    session_info.status = "stopped"
                    return session_info
                return None

            if verbose:
                print(".", end="", flush=True)

            time.sleep(poll_interval)

        if verbose:
            print(" Timeout!")

        # Return last known state
        try:
            return self.get_session(session_id)
        except:
            if session_info:
                return session_info
            raise APIError(f"Timeout waiting for session {session_id} to stop")

    def get_session(self, session_id: str) -> GPUSession:
        """
        Get details of a specific session.

        Args:
            session_id: Session ID (short or full UUID)

        Returns:
            GPUSession object
        """
        response = self._request(
            "GET",
            "/api/computing/sessions/status/",
            params={"session_id": session_id}
        )

        if not response.get("success"):
            raise SessionNotFoundError(f"Session {session_id} not found")

        return self._parse_session(response.get("session", {}))

    def list_sessions(self, status: str = None) -> List[GPUSession]:
        """
        List all GPU sessions.

        Args:
            status: Filter by status ('running', 'stopped', 'pending')

        Returns:
            List of GPUSession objects
        """
        params = {}
        if status:
            params["status"] = status

        response = self._request("GET", "/api/computing/sessions/", params=params)

        sessions = []
        for session_data in response.get("sessions", []):
            sessions.append(self._parse_session(session_data))

        return sessions

    def get_inventory(self) -> List[GPUInventory]:
        """
        Get available GPU inventory.

        Returns:
            List of GPUInventory objects (only GPUs with available stock)
            Empty list if no GPUs are available
        """
        response = self._request("GET", "/api/computing/inventory/")

        inventory = []
        for item in response.get("inventory", []):
            inventory.append(GPUInventory(
                gpu_type=item.get("gpu_type", ""),
                gpu_name=item.get("gpu_name", ""),
                available=item.get("available", 0),
                price_per_hour=item.get("price_per_hour", 0.0)
            ))

        return inventory

    def generate_sdk_key(self, session_id: str, name: str = "SDK Key") -> str:
        """
        Generate an sk_live_ API key for a session.

        This key can be used with the 'clouditia' SDK to execute code.

        Args:
            session_id: Session ID
            name: Key name (default: "SDK Key")

        Returns:
            The generated sk_live_ API key
        """
        response = self._request(
            "POST",
            "/api/computing/sessions/generate-key/",
            data={"session_id": session_id, "name": name}
        )

        if not response.get("success"):
            raise APIError(response.get("error", "Failed to generate key"))

        return response.get("api_key")

    def rename_session(self, session_id: str, new_name: str) -> GPUSession:
        """
        Rename a GPU session.

        Args:
            session_id: Session ID (short or full UUID)
            new_name: New name for the session

        Returns:
            GPUSession object with updated name
        """
        response = self._request(
            "POST",
            "/api/computing/sessions/rename/",
            data={"session_id": session_id, "name": new_name}
        )

        if not response.get("success"):
            error = response.get("error", "Failed to rename session")
            if "not found" in error.lower():
                raise SessionNotFoundError(f"Session {session_id} not found")
            raise APIError(error)

        # Get updated session
        return self.get_session(session_id)

    def get_balance(self) -> Dict:
        """
        Get user's credit balance.

        Returns:
            Dict with 'balance' (float) and 'currency' (str)
        """
        response = self._request("GET", "/api/computing/balance/")

        if not response.get("success"):
            raise APIError(response.get("error", "Failed to get balance"))

        return {
            'balance': response.get('balance', 0.0),
            'currency': response.get('currency', 'EUR')
        }

    def get_session_cost(self, session_id: str) -> Dict:
        """
        Get cost and duration of a specific session.

        Args:
            session_id: Session ID (short or full UUID)

        Returns:
            Dict with session cost details:
            - session_id: Full session ID
            - short_id: Short session ID (8 chars)
            - name: Session name
            - status: Session status
            - cost: Current cost in EUR
            - hourly_rate: Hourly rate in EUR
            - duration_seconds: Duration in seconds
            - duration_hours: Duration in hours
            - duration_display: Human readable duration (e.g., "2h 30m 15s")
            - started_at: Start time (ISO format)
            - ended_at: End time (ISO format) or None if still running
        """
        response = self._request(
            "GET",
            "/api/computing/sessions/cost/",
            params={"session_id": session_id}
        )

        if not response.get("success"):
            error = response.get("error", "Failed to get session cost")
            if "not found" in error.lower():
                raise SessionNotFoundError(f"Session {session_id} not found")
            raise APIError(error)

        return {
            'session_id': response.get('session_id'),
            'short_id': response.get('short_id'),
            'name': response.get('name'),
            'status': response.get('status'),
            'cost': response.get('cost', 0.0),
            'hourly_rate': response.get('hourly_rate', 0.0),
            'duration_seconds': response.get('duration_seconds', 0),
            'duration_hours': response.get('duration_hours', 0.0),
            'duration_display': response.get('duration_display', '0h 0m 0s'),
            'started_at': response.get('started_at'),
            'ended_at': response.get('ended_at'),
            'currency': response.get('currency', 'EUR')
        }

    def get_session_duration(self, session_id: str) -> Dict:
        """
        Get duration of a specific session.

        Args:
            session_id: Session ID (short or full UUID)

        Returns:
            Dict with duration details:
            - duration_seconds: Duration in seconds
            - duration_hours: Duration in hours
            - duration_display: Human readable duration (e.g., "2h 30m 15s")
            - started_at: Start time (ISO format)
            - ended_at: End time (ISO format) or None if still running
        """
        cost_info = self.get_session_cost(session_id)
        return {
            'duration_seconds': cost_info['duration_seconds'],
            'duration_hours': cost_info['duration_hours'],
            'duration_display': cost_info['duration_display'],
            'started_at': cost_info['started_at'],
            'ended_at': cost_info['ended_at']
        }

    def get_sessions_cost(self, session_ids: List[str]) -> Dict:
        """
        Get cost of multiple sessions.

        Args:
            session_ids: List of session IDs (short or full UUIDs)

        Returns:
            Dict with:
            - sessions: List of session cost details
            - session_count: Number of sessions
            - total_cost: Total cost in EUR
            - total_duration_seconds: Total duration in seconds
            - total_duration_display: Human readable total duration
        """
        response = self._request(
            "POST",
            "/api/computing/sessions/costs/",
            data={"session_ids": session_ids}
        )

        if not response.get("success"):
            raise APIError(response.get("error", "Failed to get sessions cost"))

        return {
            'sessions': response.get('sessions', []),
            'session_count': response.get('session_count', 0),
            'total_cost': response.get('total_cost', 0.0),
            'total_duration_seconds': response.get('total_duration_seconds', 0),
            'total_duration_display': response.get('total_duration_display', '0h 0m'),
            'currency': response.get('currency', 'EUR')
        }

    def get_active_sessions_cost(self) -> Dict:
        """
        Get cost of all active (running) sessions.

        Returns:
            Dict with:
            - sessions: List of active session cost details
            - session_count: Number of active sessions
            - total_cost: Total cost of all active sessions in EUR
            - total_duration_seconds: Total duration in seconds
            - total_duration_display: Human readable total duration
        """
        response = self._request(
            "GET",
            "/api/computing/sessions/costs/",
            params={"active_only": "true"}
        )

        if not response.get("success"):
            raise APIError(response.get("error", "Failed to get active sessions cost"))

        return {
            'sessions': response.get('sessions', []),
            'session_count': response.get('session_count', 0),
            'total_cost': response.get('total_cost', 0.0),
            'total_duration_seconds': response.get('total_duration_seconds', 0),
            'total_duration_display': response.get('total_duration_display', '0h 0m'),
            'currency': response.get('currency', 'EUR')
        }

    def _parse_session(self, data: Dict) -> GPUSession:
        """Parse session data into GPUSession object"""
        session_id = data.get("id", "")
        short_id = session_id[:8] if session_id else ""

        # Parse limits
        limits = data.get("limits", {})
        cost_limit = limits.get("cost_limit")
        duration_limit = limits.get("duration_limit")
        auto_stop_enabled = limits.get("auto_stop_enabled", False)

        return GPUSession(
            id=session_id,
            short_id=short_id,
            name=data.get("name", f"compute-gpu-{short_id}"),
            status=data.get("status", "unknown"),
            gpu_type=data.get("gpu_type", ""),
            gpu_count=data.get("gpu_count", 1),
            gpus=data.get("gpus"),
            vcpu=data.get("vcpu", 0),
            ram=data.get("ram", ""),
            storage=data.get("storage", ""),
            vscode_port=data.get("vscode_port"),
            jupyter_port=data.get("jupyter_port"),
            password=data.get("password"),
            url=data.get("url", f"https://clouditia.com/code-editor/{session_id}/"),
            created_at=self._parse_datetime(data.get("created_at")),
            started_at=self._parse_datetime(data.get("started_at")),
            cost_limit=cost_limit,
            duration_limit=duration_limit,
            auto_stop_enabled=auto_stop_enabled
        )

    def _parse_queue_job(self, data: Dict) -> QueueJob:
        """Parse queue job data into QueueJob object"""
        return QueueJob(
            queue_id=data.get("queue_id", ""),
            position=data.get("position", 0),
            status=data.get("status", "unknown"),
            status_display=data.get("status_display", ""),
            gpu_config=data.get("gpu_config", {}),
            vcpu=data.get("vcpu", 4),
            ram=data.get("ram", 16),
            storage=data.get("storage", 20),
            allow_partial=data.get("allow_partial", False),
            attempt_count=data.get("attempt_count", 0),
            last_attempt_at=self._parse_datetime(data.get("last_attempt_at")),
            last_error=data.get("last_error", ""),
            created_at=self._parse_datetime(data.get("created_at")),
            created_session_id=data.get("created_session_id")
        )

    def _parse_queue_attempt(self, data: Dict) -> QueueAttempt:
        """Parse queue attempt data into QueueAttempt object"""
        return QueueAttempt(
            attempt_id=data.get("attempt_id", ""),
            success=data.get("success", False),
            error_message=data.get("error_message", ""),
            available_gpus=data.get("available_gpus", []),
            unavailable_gpus=data.get("unavailable_gpus", []),
            attempted_at=self._parse_datetime(data.get("attempted_at"))
        )

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Parse datetime string"""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None

    # ==================== QUEUE METHODS ====================

    def list_queue_jobs(self, status: str = None) -> List[QueueJob]:
        """
        List user's queued session creation requests.

        Args:
            status: Filter by status ('pending', 'processing', 'completed', 'failed', 'cancelled')

        Returns:
            List of QueueJob objects
        """
        params = {}
        if status:
            params["status"] = status

        response = self._request("GET", "/api/computing/queue/", params=params)

        if not response.get("success"):
            raise APIError(response.get("error", "Failed to list queue jobs"))

        jobs = []
        for job_data in response.get("queue_jobs", []):
            jobs.append(self._parse_queue_job(job_data))

        return jobs

    def get_queue_job(self, queue_id: str, verbose: bool = False) -> Dict:
        """
        Get details of a specific queued job with attempt history.

        Args:
            queue_id: Queue job ID (short or full UUID)
            verbose: Print details to console (default: False)

        Returns:
            Dict with:
            - job: QueueJob object
            - attempts: List of QueueAttempt objects
            - attempts_count: Number of attempts
        """
        response = self._request(
            "GET",
            "/api/computing/queue/job/",
            params={"queue_id": queue_id}
        )

        if not response.get("success"):
            error = response.get("error", "Failed to get queue job")
            if "not found" in error.lower():
                raise SessionNotFoundError(f"Queue job {queue_id} not found")
            raise APIError(error)

        job = self._parse_queue_job(response.get("queue_job", {}))
        attempts = [
            self._parse_queue_attempt(a)
            for a in response.get("attempts", [])
        ]

        if verbose:
            print(f"\n{'='*50}")
            print(f"  QUEUE JOB DETAILS")
            print(f"{'='*50}")
            print(f"  Queue ID    : {job.queue_id[:8]}...")
            print(f"  Position    : #{job.position}")
            print(f"  Status      : {job.status_display}")
            print(f"  GPU Config  : {job.gpu_config}")
            print(f"  vCPU        : {job.vcpu}")
            print(f"  RAM         : {job.ram}GB")
            print(f"  Storage     : {job.storage}GB")
            print(f"  Attempts    : {job.attempt_count}")
            if job.last_attempt_at:
                print(f"  Last Tested : {job.last_attempt_at}")
            if job.last_error:
                print(f"  Last Error  : {job.last_error}")
            if job.created_session_id:
                print(f"  Session ID  : {job.created_session_id[:8]}...")
            print(f"{'='*50}")

            if attempts:
                print(f"\n  ATTEMPT HISTORY ({len(attempts)} attempts)")
                print(f"  {'-'*46}")
                for i, attempt in enumerate(attempts, 1):
                    status = "✓ Success" if attempt.success else "✗ Failed"
                    print(f"  {i}. [{status}] {attempt.attempted_at}")
                    if attempt.error_message:
                        print(f"     Error: {attempt.error_message[:50]}...")
                    if attempt.unavailable_gpus:
                        print(f"     Unavailable: {', '.join(attempt.unavailable_gpus)}")
                print()

        return {
            'job': job,
            'attempts': attempts,
            'attempts_count': len(attempts)
        }

    def cancel_queue_job(self, queue_id: str, verbose: bool = True) -> bool:
        """
        Cancel a queued session creation request.

        Args:
            queue_id: Queue job ID (short or full UUID)
            verbose: Print status message (default: True)

        Returns:
            True if cancelled successfully

        Raises:
            SessionNotFoundError: If queue job is not found
            APIError: If cancellation fails
        """
        response = self._request(
            "POST",
            "/api/computing/queue/cancel/",
            data={"queue_id": queue_id}
        )

        if not response.get("success"):
            error = response.get("error", "Failed to cancel queue job")
            if "not found" in error.lower():
                raise SessionNotFoundError(f"Queue job {queue_id} not found")
            raise APIError(error)

        if verbose:
            print(f"Queue job {queue_id[:8]}... cancelled successfully")

        return True

    # ==================== LAMBDA GPU ====================

    def lambda_gpu(
        self,
        script: str,
        gpu_type: str = None,
        gpu_count: int = 1,
        gpus: List[Dict] = None,
        vcpu: int = 4,
        ram: int = 16,
        storage: int = 20,
        input_files: List[str] = None,
        output_files: List[str] = None,
        output_dir: str = ".",
        queue_if_unavailable: bool = True,
        verbose: bool = True
    ) -> LambdaResult:
        """
        Execute a script on a GPU session and auto-stop when complete.

        This is a serverless-like GPU execution: the session is created,
        the script runs, results are retrieved, and the session is stopped.
        All in one blocking call.

        Args:
            script: Command/script to execute (e.g., "python train.py")
            gpu_type: GPU type slug (e.g., 'nvidia-rtx-3090')
            gpu_count: Number of GPUs (default: 1)
            gpus: List of GPU configs for multiple GPU types
            vcpu: Number of vCPUs (default: 4)
            ram: RAM in GB (default: 16)
            storage: Storage in GB (default: 20)
            input_files: List of local files to upload before execution
            output_files: List of remote files to download after execution
            output_dir: Local directory to save output files (default: current dir)
            queue_if_unavailable: Add to queue if GPUs unavailable (default: True)
            verbose: Print status messages (default: True)

        Returns:
            LambdaResult with execution results

        Example:
            result = manager.lambda_gpu(
                script="python train.py --epochs 10",
                gpu_type="nvidia-rtx-3090",
                input_files=["train.py", "data.csv"],
                output_files=["model.pt", "logs/"]
            )
            print(f"Exit code: {result.exit_code}")
            print(f"Output: {result.stdout}")
            print(f"Cost: {result.cost} EUR")
        """
        import os
        start_time = time.time()
        session = None
        sdk_key = None

        try:
            # Step 1: Create session
            if verbose:
                print(f"\n{'='*50}")
                print(f"  LAMBDA GPU")
                print(f"{'='*50}")
                print(f"  Script: {script}")
                print(f"{'='*50}")
                print(f"\n[1/5] Creating GPU session...")

            session_result = self.create_session(
                gpu_type=gpu_type,
                gpu_count=gpu_count,
                gpus=gpus,
                vcpu=vcpu,
                ram=ram,
                storage=storage,
                wait_ready=True,
                verbose=False,
                queue_if_unavailable=queue_if_unavailable
            )

            # Check if queued
            if isinstance(session_result, dict) and session_result.get('queued'):
                queue_id = session_result['queue_id']
                if verbose:
                    print(f"  Request queued at position #{session_result['position']}")
                    print(f"  Waiting for session to be created...")

                # Poll queue until session is created
                while True:
                    queue_info = self.get_queue_job(queue_id)
                    job = queue_info['job']

                    if job.status == 'completed' and job.created_session_id:
                        session = self.get_session(job.created_session_id)
                        if verbose:
                            print(f"  Session created: {session.short_id}")
                        break
                    elif job.status in ['failed', 'cancelled']:
                        raise APIError(f"Queue job {job.status}: {job.last_error}")

                    time.sleep(5)
            else:
                session = session_result
                if verbose:
                    print(f"  Session created: {session.short_id}")

            # Step 2: Generate SDK key
            if verbose:
                print(f"[2/5] Generating execution key...")

            sdk_key = self.generate_sdk_key(session.short_id, name="lambda-gpu")
            if verbose:
                print(f"  Key generated: sk_live_...{sdk_key[-8:]}")

            # Step 3: Import clouditia SDK and connect
            if verbose:
                print(f"[3/5] Connecting to session...")

            try:
                from clouditia import GPUSession as ClouditiaGPU
            except ImportError:
                raise APIError(
                    "clouditia SDK not installed. "
                    "Install with: pip install clouditia"
                )

            gpu = ClouditiaGPU(api_key=sdk_key)
            if verbose:
                print(f"  Connected to {session.name}")

            # Step 4: Upload input files
            uploaded_files = []
            if input_files:
                if verbose:
                    print(f"[3.5/5] Uploading {len(input_files)} input file(s)...")

                for file_path in input_files:
                    if os.path.exists(file_path):
                        try:
                            gpu.upload(file_path)
                            uploaded_files.append(file_path)
                            if verbose:
                                print(f"  Uploaded: {file_path}")
                        except Exception as e:
                            if verbose:
                                print(f"  Warning: Failed to upload {file_path}: {e}")
                    else:
                        if verbose:
                            print(f"  Warning: File not found: {file_path}")

            # Step 5: Execute script
            if verbose:
                print(f"[4/5] Executing script...")
                print(f"  $ {script}")

            try:
                exec_result = gpu.run(script)
                stdout = exec_result.get('stdout', '') if isinstance(exec_result, dict) else str(exec_result)
                stderr = exec_result.get('stderr', '') if isinstance(exec_result, dict) else ''
                exit_code = exec_result.get('exit_code', 0) if isinstance(exec_result, dict) else 0
            except Exception as e:
                stdout = ''
                stderr = str(e)
                exit_code = 1

            if verbose:
                if exit_code == 0:
                    print(f"  Execution completed (exit code: 0)")
                else:
                    print(f"  Execution failed (exit code: {exit_code})")

            # Step 6: Download output files
            downloaded_files = []
            if output_files:
                if verbose:
                    print(f"[4.5/5] Downloading {len(output_files)} output file(s)...")

                os.makedirs(output_dir, exist_ok=True)

                for file_path in output_files:
                    try:
                        local_path = os.path.join(output_dir, os.path.basename(file_path))
                        gpu.download(file_path, local_path)
                        downloaded_files.append(local_path)
                        if verbose:
                            print(f"  Downloaded: {file_path} -> {local_path}")
                    except Exception as e:
                        if verbose:
                            print(f"  Warning: Failed to download {file_path}: {e}")

            # Step 7: Get cost and stop session
            if verbose:
                print(f"[5/5] Stopping session...")

            try:
                cost_info = self.get_session_cost(session.short_id)
                cost = cost_info.get('cost', 0)
            except:
                cost = 0

            self.stop_session(session.short_id, verbose=False)

            duration = time.time() - start_time

            if verbose:
                print(f"  Session stopped")
                print(f"\n{'='*50}")
                print(f"  LAMBDA GPU COMPLETE")
                print(f"{'='*50}")
                print(f"  Exit Code : {exit_code}")
                print(f"  Duration  : {duration:.1f}s")
                print(f"  Cost      : {cost:.4f} EUR")
                if downloaded_files:
                    print(f"  Output    : {len(downloaded_files)} file(s)")
                print(f"{'='*50}\n")

            return LambdaResult(
                success=(exit_code == 0),
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr,
                output_files=downloaded_files,
                session_id=session.short_id if session else '',
                duration_seconds=duration,
                cost=cost,
                error=stderr if exit_code != 0 else None
            )

        except Exception as e:
            duration = time.time() - start_time

            # Try to stop session if it was created
            if session:
                try:
                    self.stop_session(session.short_id, verbose=False)
                    if verbose:
                        print(f"  Session stopped after error")
                except:
                    pass

            if verbose:
                print(f"\n{'='*50}")
                print(f"  LAMBDA GPU FAILED")
                print(f"{'='*50}")
                print(f"  Error: {str(e)}")
                print(f"{'='*50}\n")

            return LambdaResult(
                success=False,
                exit_code=1,
                stdout='',
                stderr=str(e),
                output_files=[],
                session_id=session.short_id if session else '',
                duration_seconds=duration,
                cost=0,
                error=str(e)
            )

    def __repr__(self):
        return f"GPUManager(user='{self.user.get('username', 'unknown')}')"
