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

    def __repr__(self):
        return f"GPUSession(name='{self.name}', id='{self.short_id}', gpus={self.gpu_count}, status='{self.status}')"


@dataclass
class GPUInventory:
    """Represents GPU inventory in marketplace"""
    gpu_type: str
    gpu_name: str
    total: int
    available: int
    in_use: int
    price_per_hour: float

    def __repr__(self):
        return f"GPUInventory(type='{self.gpu_type}', available={self.available}/{self.total})"


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
        verbose: bool = True
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

        Returns:
            GPUSession object with session details

        Raises:
            InsufficientResourcesError: If requested GPU is not available
            APIError: If session creation fails
        """
        # Build request data
        data = {
            "vcpu": vcpu,
            "ram": ram,
            "storage": storage
        }

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

        response = self._request("POST", "/api/computing/sessions/create/", data=data)

        if not response.get("success"):
            error = response.get("error", "Unknown error")
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
            List of GPUInventory objects
        """
        response = self._request("GET", "/api/computing/inventory/")

        inventory = []
        for item in response.get("inventory", []):
            inventory.append(GPUInventory(
                gpu_type=item.get("gpu_type", ""),
                gpu_name=item.get("gpu_name", ""),
                total=item.get("total", 0),
                available=item.get("available", 0),
                in_use=item.get("in_use", 0),
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

    def _parse_session(self, data: Dict) -> GPUSession:
        """Parse session data into GPUSession object"""
        session_id = data.get("id", "")
        short_id = session_id[:8] if session_id else ""
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
            started_at=self._parse_datetime(data.get("started_at"))
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

    def __repr__(self):
        return f"GPUManager(user='{self.user.get('username', 'unknown')}')"
