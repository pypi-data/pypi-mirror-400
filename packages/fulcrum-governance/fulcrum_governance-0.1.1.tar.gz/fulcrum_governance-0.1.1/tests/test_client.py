"""
Comprehensive unit tests for Fulcrum Python SDK.
Target: >90% coverage
"""
import pytest
import grpc
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from queue import Queue

from fulcrum.client import FulcrumClient, Envelope
from fulcrum.policy.v1 import policy_service_pb2


class TestFulcrumClientInitialization:
    """Tests for FulcrumClient initialization and configuration."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_default_initialization(self, mock_channel):
        """Test client initializes with default settings."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()

        assert client.host == "localhost:50051"
        assert client.api_key is None
        assert client.on_failure == "FAIL_OPEN"
        assert client.timeout_ms == 500
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_custom_initialization(self, mock_channel):
        """Test client initializes with custom settings."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(
            host="custom:8080",
            api_key="test-key",
            on_failure="FAIL_CLOSED",
            timeout_ms=1000
        )

        assert client.host == "custom:8080"
        assert client.api_key == "test-key"
        assert client.on_failure == "FAIL_CLOSED"
        assert client.timeout_ms == 1000
        client.shutdown()

    @patch('fulcrum.client.grpc.ssl_channel_credentials')
    @patch('fulcrum.client.grpc.secure_channel')
    def test_secure_channel_for_443(self, mock_secure, mock_creds):
        """Test secure channel is used for port 443."""
        mock_creds.return_value = Mock()
        mock_secure.return_value = Mock()

        client = FulcrumClient(host="secure.example.com:443")

        mock_creds.assert_called_once()
        mock_secure.assert_called_once()
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_on_failure_case_insensitive(self, mock_channel):
        """Test on_failure is case-insensitive."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(on_failure="fail_closed")

        assert client.on_failure == "FAIL_CLOSED"
        client.shutdown()


class TestFulcrumClientMetadata:
    """Tests for metadata handling."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_metadata_with_api_key(self, mock_channel):
        """Test metadata includes API key when set."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(api_key="my-api-key")
        metadata = client._metadata()

        assert ("x-api-key", "my-api-key") in metadata
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_metadata_without_api_key(self, mock_channel):
        """Test metadata is empty without API key."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        metadata = client._metadata()

        assert metadata == []
        client.shutdown()


class TestFulcrumClientMiddleware:
    """Tests for middleware functionality."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_add_middleware(self, mock_channel):
        """Test middleware can be added."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        middleware = lambda event_type, payload: (event_type, payload)
        client.add_middleware(middleware)

        assert middleware in client.middlewares
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_multiple_middlewares(self, mock_channel):
        """Test multiple middlewares can be added."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        mw1 = lambda et, p: (et, p)
        mw2 = lambda et, p: (et, p)
        client.add_middleware(mw1)
        client.add_middleware(mw2)

        assert len(client.middlewares) == 2
        client.shutdown()


class TestFulcrumClientShutdown:
    """Tests for shutdown behavior."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_shutdown_sets_stop_event(self, mock_channel):
        """Test shutdown sets stop event."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.shutdown()

        assert client._stop_event.is_set()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_shutdown_closes_channel(self, mock_channel):
        """Test shutdown closes gRPC channel."""
        mock_chan = Mock()
        mock_channel.return_value = mock_chan

        client = FulcrumClient()
        client.shutdown()

        mock_chan.close.assert_called()


class TestFulcrumClientPolicyEvaluation:
    """Tests for policy evaluation."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_policy_evaluation_success(self, mock_channel):
        """Test successful policy evaluation."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()

        # Mock policy stub
        mock_result = policy_service_pb2.EvaluationResult(
            decision=policy_service_pb2.EVALUATION_DECISION_ALLOW,
            message="Allowed"
        )
        mock_response = policy_service_pb2.EvaluatePolicyResponse(result=mock_result)
        client.policy_stub = Mock()
        client.policy_stub.EvaluatePolicy.return_value = mock_response

        req = policy_service_pb2.EvaluatePolicyRequest()
        result = client._evaluate_policy(req)

        assert result.result.decision == policy_service_pb2.EVALUATION_DECISION_ALLOW
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_policy_evaluation_fail_open(self, mock_channel):
        """Test policy evaluation fails open on error."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(on_failure="FAIL_OPEN")
        client.policy_stub = Mock()
        client.policy_stub.EvaluatePolicy.side_effect = Exception("Connection error")

        req = policy_service_pb2.EvaluatePolicyRequest()
        result = client._evaluate_policy(req)

        assert result.result.decision == policy_service_pb2.EVALUATION_DECISION_ALLOW
        assert "Fail-safe" in result.result.message
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_policy_evaluation_fail_closed(self, mock_channel):
        """Test policy evaluation fails closed on error."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(on_failure="FAIL_CLOSED")
        client.policy_stub = Mock()
        client.policy_stub.EvaluatePolicy.side_effect = Exception("Connection error")

        req = policy_service_pb2.EvaluatePolicyRequest()
        result = client._evaluate_policy(req)

        assert result.result.decision == policy_service_pb2.EVALUATION_DECISION_DENY
        assert "Fail-safe (Closed)" in result.result.message
        client.shutdown()


class TestFulcrumClientEnvelopeCreation:
    """Tests for envelope creation."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_create_envelope_success(self, mock_channel):
        """Test successful envelope creation."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()

        # Mock envelope stub response
        mock_envelope = Mock()
        mock_envelope.envelope_id = "test-envelope-id"
        mock_response = Mock()
        mock_response.envelope = mock_envelope
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.return_value = mock_response

        envelope_id = client._create_envelope_grpc("tenant-1", "python-sdk", {"key": "value"})

        assert envelope_id == "test-envelope-id"
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_create_envelope_failure_fail_open(self, mock_channel):
        """Test envelope creation failure with fail open."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(on_failure="FAIL_OPEN")
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.side_effect = Exception("Network error")

        envelope_id = client._create_envelope_grpc("tenant-1")

        assert envelope_id is None
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_create_envelope_failure_fail_closed(self, mock_channel):
        """Test envelope creation failure with fail closed raises."""
        mock_channel.return_value = Mock()

        client = FulcrumClient(on_failure="FAIL_CLOSED")
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.side_effect = Exception("Network error")

        with pytest.raises(Exception, match="Network error"):
            client._create_envelope_grpc("tenant-1")

        client.shutdown()


class TestFulcrumClientContextManager:
    """Tests for envelope context manager."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_context_manager(self, mock_channel):
        """Test envelope context manager basic usage."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.return_value = Mock(envelope=Mock(envelope_id="env-123"))

        with client.envelope(tenant_id="tenant-1") as env:
            assert env.tenant_id == "tenant-1"
            assert env.envelope_id == "env-123"

        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_context_manager_with_custom_execution_id(self, mock_channel):
        """Test envelope with custom execution ID."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.return_value = Mock(envelope=Mock(envelope_id="env-123"))

        with client.envelope(execution_id="custom-exec-id") as env:
            assert env.execution_id == "custom-exec-id"

        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_context_manager_generates_execution_id(self, mock_channel):
        """Test envelope generates execution ID if not provided."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.return_value = Mock(envelope=Mock(envelope_id="env-123"))

        with client.envelope() as env:
            assert env.execution_id is not None
            assert len(env.execution_id) > 0

        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_context_manager_exception_handling(self, mock_channel):
        """Test envelope logs failure on exception."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.envelope_stub = Mock()
        client.envelope_stub.CreateEnvelope.return_value = Mock(envelope=Mock(envelope_id="env-123"))

        with pytest.raises(ValueError):
            with client.envelope() as env:
                raise ValueError("Test error")

        client.shutdown()


class TestEnvelope:
    """Tests for Envelope class."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_guard_allowed(self, mock_channel):
        """Test guard returns True when allowed."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.policy_stub = Mock()
        mock_result = policy_service_pb2.EvaluationResult(
            decision=policy_service_pb2.EVALUATION_DECISION_ALLOW
        )
        client.policy_stub.EvaluatePolicy.return_value = policy_service_pb2.EvaluatePolicyResponse(
            result=mock_result
        )

        envelope = Envelope(
            client=client,
            execution_id="exec-1",
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            envelope_id="env-1"
        )

        result = envelope.guard("test_action")

        assert result is True
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_guard_denied(self, mock_channel):
        """Test guard returns False when denied."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.policy_stub = Mock()
        mock_result = policy_service_pb2.EvaluationResult(
            decision=policy_service_pb2.EVALUATION_DECISION_DENY
        )
        client.policy_stub.EvaluatePolicy.return_value = policy_service_pb2.EvaluatePolicyResponse(
            result=mock_result
        )

        envelope = Envelope(
            client=client,
            execution_id="exec-1",
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            envelope_id="env-1"
        )

        result = envelope.guard("test_action")

        assert result is False
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_log_queues_event(self, mock_channel):
        """Test log queues events."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()

        envelope = Envelope(
            client=client,
            execution_id="exec-1",
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            envelope_id="env-1"
        )

        initial_size = client.queue.qsize()
        envelope.log("test_event", {"key": "value"})

        assert client.queue.qsize() == initial_size + 1
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_log_middleware_drops_event(self, mock_channel):
        """Test middleware can drop events."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.add_middleware(lambda et, p: None)  # Drops all events

        envelope = Envelope(
            client=client,
            execution_id="exec-1",
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            envelope_id="env-1"
        )

        initial_size = client.queue.qsize()
        envelope.log("test_event", {"key": "value"})

        assert client.queue.qsize() == initial_size  # Event was dropped
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_log_middleware_modifies_event(self, mock_channel):
        """Test middleware can modify events."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        client.add_middleware(lambda et, p: (et + "_modified", p))

        envelope = Envelope(
            client=client,
            execution_id="exec-1",
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            envelope_id="env-1"
        )

        envelope.log("test_event", {"key": "value"})

        # Get the queued event
        req = client.queue.get_nowait()
        assert req.event.event_type == "test_event_modified"
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_envelope_log_after_shutdown_noop(self, mock_channel):
        """Test logging after shutdown does nothing."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()

        envelope = Envelope(
            client=client,
            execution_id="exec-1",
            tenant_id="tenant-1",
            workflow_id="workflow-1",
            envelope_id="env-1"
        )

        client.shutdown()

        # Drain the queue first
        while not client.queue.empty():
            try:
                client.queue.get_nowait()
            except:
                break

        initial_size = client.queue.qsize()
        envelope.log("test_event", {"key": "value"})

        # Event should not be queued after shutdown
        assert client.queue.qsize() == initial_size


class TestPublishWithRetry:
    """Tests for retry logic."""

    @patch('fulcrum.client.grpc.insecure_channel')
    @patch('fulcrum.client.time.sleep')
    def test_publish_retry_on_unavailable(self, mock_sleep, mock_channel):
        """Test publish retries on unavailable error."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        mock_stub = Mock()
        client.stub = mock_stub

        # Fail twice, then succeed
        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.UNAVAILABLE
        mock_stub.PublishEvent.side_effect = [error, error, None]

        # Prevent _connect from overwriting our mock stub
        with patch.object(client, '_connect', return_value=None):
            req = Mock()
            client._publish_with_retry(req, attempts=3)

        assert mock_stub.PublishEvent.call_count == 3
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    @patch('fulcrum.client.time.sleep')
    def test_publish_gives_up_after_max_attempts(self, mock_sleep, mock_channel):
        """Test publish gives up after max attempts."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()
        mock_stub = Mock()
        client.stub = mock_stub

        error = grpc.RpcError()
        error.code = lambda: grpc.StatusCode.UNAVAILABLE
        error.details = lambda: "Connection refused"
        mock_stub.PublishEvent.side_effect = error

        # Prevent _connect from overwriting our mock stub
        with patch.object(client, '_connect', return_value=None):
            req = Mock()
            client._publish_with_retry(req, attempts=3)

        assert mock_stub.PublishEvent.call_count == 3
        client.shutdown()


class TestConnectionReconnect:
    """Tests for reconnection logic."""

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_connect_creates_stubs(self, mock_channel):
        """Test _connect creates all required stubs."""
        mock_channel.return_value = Mock()

        client = FulcrumClient()

        assert client.stub is not None
        assert client.policy_stub is not None
        assert client.envelope_stub is not None
        client.shutdown()

    @patch('fulcrum.client.grpc.insecure_channel')
    def test_reconnect_closes_old_channel(self, mock_channel):
        """Test reconnect closes old channel."""
        mock_chan1 = Mock()
        mock_chan2 = Mock()
        mock_channel.side_effect = [mock_chan1, mock_chan2]

        client = FulcrumClient()
        client._connect()  # Reconnect

        mock_chan1.close.assert_called()
        client.shutdown()
