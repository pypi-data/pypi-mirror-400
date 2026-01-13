"""Tests for WatchCode CLI client module."""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import httpx

from watchcode.client import RelayClient
from watchcode.config import Config


class TestSendNotification:
    """Tests for sending notifications."""

    @patch("watchcode.client.httpx.Client")
    def test_send_notification_success(self, mock_client_class, tmp_path):
        """Successful notification should return response."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "message_id": "123"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        # Send notification
        client = RelayClient(config)
        result = client.send_notification(
            event="test",
            message="Test message",
            session_id="session-123"
        )

        assert result["success"] is True
        assert result["message_id"] == "123"
        mock_client.post.assert_called_once()

    def test_send_notification_not_configured(self, tmp_path):
        """Sending without config should raise ValueError."""
        config = Config()
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False

        client = RelayClient(config)

        with pytest.raises(ValueError) as exc_info:
            client.send_notification(
                event="test",
                message="Test",
                session_id="session-123"
            )

        assert "not configured" in str(exc_info.value).lower()

    @patch("watchcode.client.httpx.Client")
    def test_send_notification_queued_on_network_error(self, mock_client_class, tmp_path):
        """Network error should queue notification."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config.queue_file = tmp_path / "queue.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock network error
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        # Send notification
        client = RelayClient(config)
        result = client.send_notification(
            event="test",
            message="Test message",
            session_id="session-123",
            retry_offline=True
        )

        assert result["success"] is False
        assert result["queued"] is True

        # Verify queued
        queue = config.load_queue()
        assert len(queue) == 1
        assert queue[0]["event"] == "test"

    @patch("watchcode.client.httpx.Client")
    def test_send_notification_no_queue_when_disabled(self, mock_client_class, tmp_path):
        """Network error should raise when retry_offline=False."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock network error
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        # Send notification
        client = RelayClient(config)

        with pytest.raises(httpx.ConnectError):
            client.send_notification(
                event="test",
                message="Test message",
                session_id="session-123",
                retry_offline=False
            )

    @patch("watchcode.client.httpx.Client")
    def test_send_notification_http_error(self, mock_client_class, tmp_path):
        """HTTP error should raise ValueError with details."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP error
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": "Invalid auth token"}

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "401 Unauthorized",
            request=MagicMock(),
            response=mock_response
        )
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        # Send notification
        client = RelayClient(config)

        with pytest.raises(ValueError) as exc_info:
            client.send_notification(
                event="test",
                message="Test message",
                session_id="session-123"
            )

        assert "401" in str(exc_info.value)


class TestTestConnection:
    """Tests for connection testing."""

    @patch("watchcode.client.httpx.Client")
    def test_connection_success(self, mock_client_class, tmp_path):
        """Successful connection should return True."""
        config = Config()
        config.config_file = tmp_path / "config.json"

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        client = RelayClient(config)
        assert client.test_connection() is True

    @patch("watchcode.client.httpx.Client")
    def test_connection_failure(self, mock_client_class, tmp_path):
        """Failed connection should return False."""
        config = Config()
        config.config_file = tmp_path / "config.json"

        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.ConnectError("Connection refused")
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        client = RelayClient(config)
        assert client.test_connection() is False


class TestFlushQueue:
    """Tests for flushing offline queue."""

    def test_flush_empty_queue(self, tmp_path):
        """Flushing empty queue should return zeros."""
        config = Config()
        config.queue_file = tmp_path / "queue.json"

        client = RelayClient(config)
        result = client.flush_queue()

        assert result["sent"] == 0
        assert result["failed"] == 0
        assert result["total"] == 0

    @patch("watchcode.client.httpx.Client")
    def test_flush_success(self, mock_client_class, tmp_path):
        """Successful flush should clear queue."""
        # Setup config with queued items
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config.queue_file = tmp_path / "queue.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        config.add_to_queue({
            "event": "test1",
            "message": "Message 1",
            "session_id": "session-1"
        })
        config.add_to_queue({
            "event": "test2",
            "message": "Message 2",
            "session_id": "session-2"
        })

        # Mock successful sends
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        # Flush
        client = RelayClient(config)
        result = client.flush_queue()

        assert result["sent"] == 2
        assert result["failed"] == 0
        assert result["total"] == 2

        # Queue should be empty
        assert config.load_queue() == []


class TestTestNotification:
    """Tests for test notifications."""

    @patch("watchcode.client.httpx.Client")
    def test_send_test_notification(self, mock_client_class, tmp_path):
        """Test notification should have correct fields."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        # Send test
        client = RelayClient(config)
        result = client.send_test_notification()

        assert result["success"] is True

        # Verify payload
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["event"] == "notification"
        assert "test" in payload["message"].lower()
        assert payload["requires_action"] is False


class TestE2EEncryption:
    """Tests for E2E encryption in RelayClient."""

    @patch("watchcode.client._get_http_client")
    def test_send_notification_encrypted_by_default(self, mock_get_client, tmp_path):
        """Notifications should be encrypted by default."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "message_id": "123"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Send notification (encryption enabled by default)
        client = RelayClient(config)
        client.send_notification(
            event="permission_request",
            message="Allow Bash: rm -rf?",
            session_id="session-123"
        )

        # Verify encrypted payload structure
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]

        # Should have encrypted fields
        assert "v" in payload
        assert payload["v"] == 1
        assert "nonce" in payload
        assert "ciphertext" in payload
        # Should NOT have plaintext content
        assert "message" not in payload
        assert "event" not in payload
        # But should have auth_token for routing
        assert "auth_token" in payload

    @patch("watchcode.client._get_http_client")
    def test_send_notification_plaintext_when_disabled(self, mock_get_client, tmp_path):
        """Notifications should be plaintext when encryption disabled."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "message_id": "123"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Send notification with encryption disabled
        client = RelayClient(config, enable_encryption=False)
        client.send_notification(
            event="stop",
            message="Session ended",
            session_id="session-123"
        )

        # Verify plaintext payload
        call_args = mock_client.post.call_args
        payload = call_args[1]["json"]

        # Should have plaintext content
        assert payload["event"] == "stop"
        assert payload["message"] == "Session ended"
        # Should NOT have encrypted fields
        assert "v" not in payload
        assert "ciphertext" not in payload

    @patch("watchcode.client._get_http_client")
    def test_encrypted_nonce_is_unique_per_message(self, mock_get_client, tmp_path):
        """Each encrypted message should have a unique nonce."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "message_id": "123"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Send two notifications
        client = RelayClient(config)
        client.send_notification(event="stop", message="Message 1", session_id="s1")
        client.send_notification(event="stop", message="Message 2", session_id="s2")

        # Get both payloads
        calls = mock_client.post.call_args_list
        nonce1 = calls[0][1]["json"]["nonce"]
        nonce2 = calls[1][1]["json"]["nonce"]

        # Nonces should be different
        assert nonce1 != nonce2

    @patch("watchcode.client._get_http_client")
    def test_encrypted_ciphertext_is_different_for_same_message(self, mock_get_client, tmp_path):
        """Same plaintext should produce different ciphertext due to random nonce."""
        # Setup config
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False
        config.set_auth_token("ABCD1234EFGH")

        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.json.return_value = {"success": True, "message_id": "123"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        # Send same message twice
        client = RelayClient(config)
        client.send_notification(event="stop", message="Same message", session_id="s1")
        client.send_notification(event="stop", message="Same message", session_id="s1")

        # Get both payloads
        calls = mock_client.post.call_args_list
        ciphertext1 = calls[0][1]["json"]["ciphertext"]
        ciphertext2 = calls[1][1]["json"]["ciphertext"]

        # Ciphertexts should be different (due to random nonce)
        assert ciphertext1 != ciphertext2
