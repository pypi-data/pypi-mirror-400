"""
Comprehensive tests for Clouditia Manager SDK v1.8.0

Run tests:
    python -m pytest tests/test_sdk_v1_8.py -v

For integration tests (requires API key):
    CLOUDITIA_API_KEY=sk_compute_... python -m pytest tests/test_sdk_v1_8.py -v -m integration
"""

import pytest
import os
import json
from dataclasses import asdict
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clouditia_manager import (
    GPUManager, GPUSession, GPUInventory, QueueJob,
    QueueAttempt, LambdaResult, S3Connection,
    ClouditiaManagerError, AuthenticationError,
    SessionNotFoundError, InsufficientResourcesError, APIError,
    __version__
)


# ==================== VERSION TESTS ====================

class TestVersion:
    def test_version_format(self):
        """Test version string format"""
        assert __version__ == "1.8.0"
        parts = __version__.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)


# ==================== DATACLASS TESTS ====================

class TestGPUSession:
    def test_gpu_session_creation(self):
        """Test GPUSession dataclass creation"""
        session = GPUSession(
            id="123e4567-e89b-12d3-a456-426614174000",
            short_id="123e4567",
            name="test-session",
            status="running",
            gpu_type="nvidia-rtx-3090",
            gpu_count=1,
            gpus=[{"id": "gpu1", "type": "RTX 3090"}],
            vcpu=4,
            ram="16GB",
            storage="50GB",
            vscode_port=8080,
            jupyter_port=8888,
            password="test123",
            url="https://clouditia.com/session/123e4567",
            created_at=datetime.now(),
            started_at=datetime.now(),
            cost_limit=10.0,
            duration_limit=3600,
            auto_stop_enabled=True
        )
        assert session.name == "test-session"
        assert session.gpu_count == 1
        assert session.auto_stop_enabled == True

    def test_gpu_session_repr(self):
        """Test GPUSession string representation"""
        session = GPUSession(
            id="123e4567-e89b-12d3-a456-426614174000",
            short_id="123e4567",
            name="test-session",
            status="running",
            gpu_type="nvidia-rtx-3090",
            gpu_count=2,
            gpus=None,
            vcpu=4,
            ram="16GB",
            storage="50GB",
            vscode_port=None,
            jupyter_port=None,
            password=None,
            url="",
            created_at=None,
            started_at=None,
            auto_stop_enabled=True
        )
        repr_str = repr(session)
        assert "test-session" in repr_str
        assert "123e4567" in repr_str


class TestGPUInventory:
    def test_gpu_inventory_creation(self):
        """Test GPUInventory dataclass creation"""
        inventory = GPUInventory(
            gpu_type="nvidia-rtx-3090",
            gpu_name="NVIDIA RTX 3090",
            available=5,
            price_per_hour=0.50
        )
        assert inventory.gpu_type == "nvidia-rtx-3090"
        assert inventory.available == 5
        assert inventory.price_per_hour == 0.50

    def test_gpu_inventory_repr(self):
        """Test GPUInventory string representation"""
        inventory = GPUInventory(
            gpu_type="nvidia-rtx-3090",
            gpu_name="NVIDIA RTX 3090",
            available=3,
            price_per_hour=0.50
        )
        repr_str = repr(inventory)
        assert "nvidia-rtx-3090" in repr_str
        assert "3" in repr_str


class TestQueueJob:
    def test_queue_job_creation(self):
        """Test QueueJob dataclass creation"""
        job = QueueJob(
            queue_id="queue123",
            position=1,
            status="pending",
            status_display="En attente",
            gpu_config={"gpu_type": "nvidia-rtx-3090"},
            vcpu=4,
            ram=16,
            storage=50,
            allow_partial=False,
            attempt_count=0,
            last_attempt_at=None,
            last_error="",
            created_at=datetime.now(),
            created_session_id=None
        )
        assert job.position == 1
        assert job.status == "pending"

    def test_queue_job_repr(self):
        """Test QueueJob string representation"""
        job = QueueJob(
            queue_id="queue123456789",
            position=2,
            status="pending",
            status_display="En attente",
            gpu_config={},
            vcpu=4,
            ram=16,
            storage=50,
            allow_partial=False,
            attempt_count=3,
            last_attempt_at=None,
            last_error="",
            created_at=None,
            created_session_id=None
        )
        repr_str = repr(job)
        assert "queue123" in repr_str
        assert "pending" in repr_str


class TestQueueAttempt:
    def test_queue_attempt_creation(self):
        """Test QueueAttempt dataclass creation"""
        attempt = QueueAttempt(
            attempt_id="attempt123",
            success=False,
            error_message="GPU unavailable",
            available_gpus=["gpu1"],
            unavailable_gpus=["gpu2", "gpu3"],
            attempted_at=datetime.now()
        )
        assert attempt.success == False
        assert len(attempt.unavailable_gpus) == 2

    def test_queue_attempt_repr(self):
        """Test QueueAttempt string representation"""
        attempt = QueueAttempt(
            attempt_id="attempt123456789",
            success=True,
            error_message="",
            available_gpus=[],
            unavailable_gpus=[],
            attempted_at=None
        )
        repr_str = repr(attempt)
        assert "attempt12" in repr_str
        assert "Success" in repr_str


class TestLambdaResult:
    def test_lambda_result_creation(self):
        """Test LambdaResult dataclass creation"""
        result = LambdaResult(
            success=True,
            exit_code=0,
            stdout="Hello World",
            stderr="",
            output_files=["s3://bucket/output.pt"],
            session_id="sess123",
            duration_seconds=45.5,
            cost=0.25,
            error=None
        )
        assert result.success == True
        assert result.exit_code == 0
        assert result.duration_seconds == 45.5

    def test_lambda_result_repr(self):
        """Test LambdaResult string representation"""
        result = LambdaResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            output_files=[],
            session_id="",
            duration_seconds=120.5,
            cost=1.50
        )
        repr_str = repr(result)
        assert "Success" in repr_str
        assert "120.5" in repr_str


class TestS3Connection:
    def test_s3_connection_creation(self):
        """Test S3Connection dataclass creation"""
        s3 = S3Connection(
            bucket="my-bucket",
            access_key="AKIAIOSFODNN7EXAMPLE",
            secret_key="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        )
        assert s3.bucket == "my-bucket"
        assert s3.endpoint == "https://s3.amazonaws.com"
        assert s3.region == "us-east-1"

    def test_s3_connection_custom_endpoint(self):
        """Test S3Connection with custom endpoint"""
        s3 = S3Connection(
            bucket="my-bucket",
            access_key="key",
            secret_key="secret",
            endpoint="https://minio.example.com",
            region="eu-west-1",
            prefix="outputs/"
        )
        assert s3.endpoint == "https://minio.example.com"
        assert s3.region == "eu-west-1"
        assert s3.prefix == "outputs/"

    def test_s3_connection_repr(self):
        """Test S3Connection string representation"""
        s3 = S3Connection(
            bucket="test-bucket",
            access_key="key",
            secret_key="secret",
            endpoint="https://s3.eu-west-1.amazonaws.com"
        )
        repr_str = repr(s3)
        assert "test-bucket" in repr_str


# ==================== EXCEPTION TESTS ====================

class TestExceptions:
    def test_exception_hierarchy(self):
        """Test exception inheritance"""
        assert issubclass(AuthenticationError, ClouditiaManagerError)
        assert issubclass(SessionNotFoundError, ClouditiaManagerError)
        assert issubclass(InsufficientResourcesError, ClouditiaManagerError)
        assert issubclass(APIError, ClouditiaManagerError)

    def test_exception_messages(self):
        """Test exception message handling"""
        error = AuthenticationError("Invalid API key")
        assert str(error) == "Invalid API key"

        error = SessionNotFoundError("Session not found")
        assert str(error) == "Session not found"

    def test_invalid_api_key_raises_auth_error(self):
        """Test that invalid API key raises AuthenticationError"""
        with pytest.raises(AuthenticationError):
            GPUManager(api_key="invalid_key")

        with pytest.raises(AuthenticationError):
            GPUManager(api_key="sk_wrong_prefix_xxx")


# ==================== GPUMANAGER UNIT TESTS ====================

class TestGPUManagerUnit:
    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    def test_manager_initialization(self, mock_verify):
        """Test GPUManager initialization"""
        mock_verify.return_value = None
        manager = GPUManager(api_key="sk_compute_test123")
        assert manager.api_key == "sk_compute_test123"
        assert manager.base_url == "https://clouditia.com/jobs"

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    def test_manager_custom_base_url(self, mock_verify):
        """Test GPUManager with custom base URL"""
        mock_verify.return_value = None
        manager = GPUManager(
            api_key="sk_compute_test123",
            base_url="https://custom.clouditia.com/jobs"
        )
        assert manager.base_url == "https://custom.clouditia.com/jobs"

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    def test_s3_connect_method(self, mock_verify):
        """Test s3_connect method"""
        mock_verify.return_value = None
        manager = GPUManager(api_key="sk_compute_test123")

        s3 = manager.s3_connect(
            bucket="test-bucket",
            access_key="AKIAEXAMPLE",
            secret_key="secretkey123",
            endpoint="https://s3.eu-west-1.amazonaws.com",
            prefix="lambda-outputs/"
        )

        assert isinstance(s3, S3Connection)
        assert s3.bucket == "test-bucket"
        assert s3.access_key == "AKIAEXAMPLE"
        assert s3.prefix == "lambda-outputs/"

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    @patch('clouditia_manager.client.GPUManager._upload_to_s3')
    def test_lambda_output_json(self, mock_upload, mock_verify):
        """Test lambda_output with JSON data"""
        mock_verify.return_value = None
        mock_upload.return_value = "https://bucket.s3.amazonaws.com/results.json"

        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(
            bucket="test-bucket",
            access_key="key",
            secret_key="secret"
        )

        data = {"accuracy": 0.95, "loss": 0.05}
        url = manager.lambda_output("results.json", data, s3=s3, verbose=False)

        assert url == "https://bucket.s3.amazonaws.com/results.json"
        mock_upload.assert_called_once()

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    def test_lambda_output_file_not_found(self, mock_verify):
        """Test lambda_output_file with non-existent file"""
        mock_verify.return_value = None
        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(bucket="bucket", access_key="key", secret_key="secret")

        with pytest.raises(FileNotFoundError):
            manager.lambda_output_file("/nonexistent/file.txt", s3=s3)


# ==================== INTEGRATION TESTS ====================

@pytest.mark.integration
class TestGPUManagerIntegration:
    """
    Integration tests that require a valid API key.
    Set CLOUDITIA_API_KEY environment variable to run these.
    """

    @pytest.fixture
    def manager(self):
        api_key = os.environ.get("CLOUDITIA_API_KEY")
        if not api_key:
            pytest.skip("CLOUDITIA_API_KEY not set")
        return GPUManager(api_key=api_key)

    def test_get_balance(self, manager):
        """Test get_balance returns valid balance"""
        balance = manager.get_balance()
        assert isinstance(balance, float)
        assert balance >= 0

    def test_get_inventory(self, manager):
        """Test get_inventory returns GPU list"""
        inventory = manager.get_inventory()
        assert isinstance(inventory, list)
        if inventory:
            assert isinstance(inventory[0], GPUInventory)

    def test_list_sessions(self, manager):
        """Test list_sessions returns session list"""
        sessions = manager.list_sessions()
        assert isinstance(sessions, list)

    def test_list_queue_jobs(self, manager):
        """Test list_queue_jobs returns queue list"""
        jobs = manager.list_queue_jobs()
        assert isinstance(jobs, list)

    def test_get_nonexistent_session(self, manager):
        """Test get_session with invalid ID raises error"""
        with pytest.raises(SessionNotFoundError):
            manager.get_session("nonexistent123")

    def test_s3_connect_creates_connection(self, manager):
        """Test s3_connect creates valid S3Connection"""
        s3 = manager.s3_connect(
            bucket="test-bucket",
            access_key="test-key",
            secret_key="test-secret"
        )
        assert isinstance(s3, S3Connection)
        assert s3.bucket == "test-bucket"


# ==================== S3 UPLOAD TESTS ====================

class TestS3Upload:
    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    def test_upload_to_s3_requires_boto3(self, mock_verify):
        """Test that _upload_to_s3 requires boto3"""
        mock_verify.return_value = None
        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(bucket="bucket", access_key="key", secret_key="secret")

        # Mock boto3 import to fail
        with patch.dict('sys.modules', {'boto3': None}):
            with pytest.raises(APIError) as exc_info:
                manager._upload_to_s3("test.txt", b"data", s3, verbose=False)
            # The error message should mention boto3
            assert "boto3" in str(exc_info.value).lower() or "import" in str(exc_info.value).lower()

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    @patch('boto3.client')
    def test_upload_to_s3_with_prefix(self, mock_boto_client, mock_verify):
        """Test S3 upload with prefix"""
        mock_verify.return_value = None
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(
            bucket="my-bucket",
            access_key="key",
            secret_key="secret",
            prefix="outputs/2024/"
        )

        url = manager._upload_to_s3("model.pt", b"data", s3, verbose=False)

        # Verify put_object was called with correct key
        mock_s3.put_object.assert_called_once()
        call_kwargs = mock_s3.put_object.call_args[1]
        assert call_kwargs['Bucket'] == "my-bucket"
        assert call_kwargs['Key'] == "outputs/2024/model.pt"


# ==================== DATA SERIALIZATION TESTS ====================

class TestDataSerialization:
    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    @patch('clouditia_manager.client.GPUManager._upload_to_s3')
    def test_lambda_output_string(self, mock_upload, mock_verify):
        """Test lambda_output with string data"""
        mock_verify.return_value = None
        mock_upload.return_value = "https://bucket.s3.amazonaws.com/output.txt"

        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(bucket="bucket", access_key="key", secret_key="secret")

        manager.lambda_output("output.txt", "Hello World", s3=s3, verbose=False)

        # Verify the data was encoded
        call_args = mock_upload.call_args[0]
        assert call_args[0] == "output.txt"
        assert call_args[1] == b"Hello World"

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    @patch('clouditia_manager.client.GPUManager._upload_to_s3')
    def test_lambda_output_bytes(self, mock_upload, mock_verify):
        """Test lambda_output with bytes data"""
        mock_verify.return_value = None
        mock_upload.return_value = "https://bucket.s3.amazonaws.com/output.bin"

        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(bucket="bucket", access_key="key", secret_key="secret")

        binary_data = b"\x00\x01\x02\x03"
        manager.lambda_output("output.bin", binary_data, s3=s3, verbose=False)

        call_args = mock_upload.call_args[0]
        assert call_args[1] == binary_data

    @patch('clouditia_manager.client.GPUManager._verify_api_key')
    @patch('clouditia_manager.client.GPUManager._upload_to_s3')
    def test_lambda_output_dict_as_json(self, mock_upload, mock_verify):
        """Test lambda_output with dict saves as JSON"""
        mock_verify.return_value = None
        mock_upload.return_value = "https://bucket.s3.amazonaws.com/data.json"

        manager = GPUManager(api_key="sk_compute_test123")
        s3 = S3Connection(bucket="bucket", access_key="key", secret_key="secret")

        data = {"key": "value", "number": 42}
        manager.lambda_output("data.json", data, s3=s3, verbose=False)

        call_args = mock_upload.call_args[0]
        saved_data = json.loads(call_args[1].decode('utf-8'))
        assert saved_data == data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
