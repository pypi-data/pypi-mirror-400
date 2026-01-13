"""HTTP client for WatchCode relay server with offline queue support."""

import atexit
import httpx
from typing import Dict, Any, Optional
from .config import Config
from .crypto import CryptoManager, is_encrypted as is_encrypted_payload

# LATENCY OPTIMIZATION: Module-level HTTP client with connection pooling
# Reuses TCP+TLS connections across requests (saves 50-150ms per call)
_http_client: Optional[httpx.Client] = None


def _get_http_client() -> httpx.Client:
    """Get or create the shared HTTP client with connection pooling."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.Client(
            timeout=10.0,
            http2=True,  # Enable HTTP/2 for better multiplexing
            limits=httpx.Limits(
                max_keepalive_connections=5,
                max_connections=10,
                keepalive_expiry=30.0  # Keep connections alive for 30s
            )
        )
        # Clean up on process exit
        atexit.register(_cleanup_http_client)
    return _http_client


def _cleanup_http_client():
    """Close the HTTP client on process exit."""
    global _http_client
    if _http_client is not None:
        try:
            _http_client.close()
        except Exception:
            pass
        _http_client = None


# HARD WHITELIST - Only these events can EVER be sent
# Everything else is spam and MUST be blocked
ALLOWED_EVENTS = frozenset({
    'stop',               # Task completed
    'permission_request', # Tool needs approval
    'question',           # Claude asks user a question
})

# Events that are EXPLICITLY blocked (for clear error messages)
BLOCKED_SPAM_EVENTS = frozenset({
    'session_start',
    'session_end',
    'notification',
    'pre_tool_use',  # Only 'question' (AskUserQuestion) should be sent, not generic pre_tool_use
    'subagent_stop',
})


class RelayClient:
    """Client for communicating with the WatchCode relay server."""

    def __init__(self, config: Optional[Config] = None, enable_encryption: bool = True):
        """Initialize relay client.

        Args:
            config: Configuration manager instance (creates new one if not provided).
            enable_encryption: Whether to enable E2E encryption (default: True).
        """
        self.config = config or Config()
        self.timeout = 10.0  # 10 second timeout
        self.enable_encryption = enable_encryption
        self._crypto: Optional[CryptoManager] = None

    @property
    def crypto(self) -> CryptoManager:
        """Get or create crypto manager instance."""
        if self._crypto is None:
            self._crypto = CryptoManager()
        return self._crypto

    def send_notification(
        self,
        event: str,
        message: str,
        session_id: str,
        requires_action: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
        retry_offline: bool = True,
        notification_id: Optional[str] = None,
        question_options: Optional[list] = None,
        allows_multi_select: bool = False
    ) -> Dict[str, Any]:
        """Send notification to relay server.

        Args:
            event: Event type (e.g., 'stop', 'permission_request', 'question').
            message: Notification message.
            session_id: Claude Code session ID.
            requires_action: Whether notification requires user action.
            metadata: Additional metadata for the notification.
            retry_offline: Whether to queue notification if offline.
            notification_id: Unique ID for response correlation (optional).
            question_options: List of options for 'question' events. Each option
                should be a dict with 'label', optional 'id', and optional 'description'.
            allows_multi_select: Whether multiple options can be selected (for questions).

        Returns:
            Response dictionary from server.

        Raises:
            ValueError: If auth token not configured.
            httpx.HTTPStatusError: If server returns error status.
        """
        # BLOCK SPAM EVENTS - hard filter, no exceptions
        if event not in ALLOWED_EVENTS:
            if event in BLOCKED_SPAM_EVENTS:
                # Silently drop known spam events
                return {"success": True, "blocked": True, "reason": f"Event '{event}' is blocked spam"}
            else:
                # Unknown event - also block
                return {"success": True, "blocked": True, "reason": f"Event '{event}' not in whitelist"}

        auth_token = self.config.get_auth_token()
        if not auth_token:
            raise ValueError("WatchCode not configured. Run 'watchcode setup' first.")

        relay_url = self.config.get_relay_url()

        # Build notification content (this is what gets encrypted)
        notification_content = {
            "event": event,
            "message": message,
            "sessionId": session_id,  # Use sessionId to match APNs payload format
            "requiresAction": requires_action,
            "metadata": metadata or {}
        }

        # Include question options for 'question' events
        if question_options:
            notification_content["questionOptions"] = question_options
            notification_content["allowsMultiSelect"] = allows_multi_select

        # Build final payload - auth_token and notification_id are always unencrypted
        # (relay needs them for routing and ownership validation)
        payload: Dict[str, Any] = {
            "auth_token": auth_token,
        }

        # Include notification_id if provided (for response correlation)
        if notification_id:
            payload["notification_id"] = notification_id

        # Encrypt notification content if encryption is enabled
        if self.enable_encryption:
            try:
                encrypted = self.crypto.encrypt(notification_content, auth_token)
                payload["v"] = encrypted["v"]
                payload["nonce"] = encrypted["nonce"]
                payload["ciphertext"] = encrypted["ciphertext"]
            except Exception:
                # Fall back to plaintext on encryption failure
                payload.update({
                    "event": event,
                    "message": message,
                    "session_id": session_id,
                    "requires_action": requires_action,
                    "metadata": metadata or {},
                })
                if question_options:
                    payload["question_options"] = question_options
                    payload["allows_multi_select"] = allows_multi_select
        else:
            # Plaintext mode (for backward compatibility)
            payload.update({
                "event": event,
                "message": message,
                "session_id": session_id,
                "requires_action": requires_action,
                "metadata": metadata or {},
            })
            if question_options:
                payload["question_options"] = question_options
                payload["allows_multi_select"] = allows_multi_select

        try:
            # Use pooled client for connection reuse (saves 50-150ms)
            client = _get_http_client()
            response = client.post(
                f"{relay_url}/notify",
                json=payload
            )
            response.raise_for_status()
            return response.json()

        except (httpx.ConnectError, httpx.TimeoutException, httpx.NetworkError) as e:
            # Network error - fail immediately, no queueing
            raise ValueError(f"Network error: {str(e)}")

        except httpx.HTTPStatusError as e:
            # HTTP error - don't queue, just raise
            error_data = {}
            try:
                error_data = e.response.json()
            except Exception:
                pass
            raise ValueError(
                f"Relay server error ({e.response.status_code}): "
                f"{error_data.get('error', str(e))}"
            )


    def test_connection(self) -> bool:
        """Test connection to relay server.

        Returns:
            True if server is reachable.
        """
        relay_url = self.config.get_relay_url()
        try:
            client = _get_http_client()
            response = client.post(f"{relay_url}/health")
            return response.status_code == 200
        except Exception:
            return False

    def send_test_notification(self) -> Dict[str, Any]:
        """Send a test notification.

        Returns:
            Response from server.
        """
        import time
        # Use "stop" event type - one of the 3 supported types on Watch
        return self.send_notification(
            event="stop",
            message="Test notification from WatchCode CLI",
            session_id=f"test-{int(time.time())}",
            requires_action=False,
            metadata={"source": "watchcode-cli-test"}
        )

    def unregister_device(self) -> Dict[str, Any]:
        """Unregister device from relay server.

        Returns:
            Response dictionary from server.

        Raises:
            ValueError: If auth token not configured.
            httpx.HTTPStatusError: If server returns error status.
        """
        auth_token = self.config.get_auth_token()
        if not auth_token:
            raise ValueError("WatchCode not configured. Run 'watchcode setup' first.")

        relay_url = self.config.get_relay_url()

        try:
            client = _get_http_client()
            response = client.post(
                f"{relay_url}/unregister",
                json={"auth_token": auth_token}
            )
            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except Exception:
                pass
            raise ValueError(
                f"Relay server error ({e.response.status_code}): "
                f"{error_data.get('error', str(e))}"
            )

    def verify_device(self) -> bool:
        """Check if device is registered on relay server.

        Returns:
            True if device is registered and valid.
        """
        auth_token = self.config.get_auth_token()
        if not auth_token:
            return False

        relay_url = self.config.get_relay_url()

        try:
            client = _get_http_client()
            # Use GET /messages/{auth_token} - returns 401 if invalid
            response = client.get(f"{relay_url}/messages/{auth_token}")
            return response.status_code == 200
        except Exception:
            return False
