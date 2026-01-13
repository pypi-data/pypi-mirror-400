#!/usr/bin/env python3
"""
APNs notification sender for WatchCode
Generates JWT tokens and sends HTTP/2 requests to APNs

Security hardened version:
- Credential filtering in logs
- JWT token caching (45 min)
- Keychain support for .p8 key
- File permission validation

This script is called by Claude Code hooks to send notifications to the Watch.
"""

import jwt
import json
import time
import argparse
import subprocess
import stat
import logging
import re
import os
import uuid
from pathlib import Path
from datetime import datetime

import httpx

# Try to import keyring for Keychain support
try:
    import keyring
    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

# Configuration
APNS_HOST_DEV = "api.sandbox.push.apple.com"
APNS_HOST_PROD = "api.push.apple.com"
CONFIG_DIR = Path.home() / ".watchcode"
P8_KEY_PATH = CONFIG_DIR / "apns_key.p8"
CONFIG_FILE = CONFIG_DIR / "config.json"
TOKEN_CACHE_PATH = CONFIG_DIR / "device_token.txt"
WATCH_TOKEN_CACHE_PATH = CONFIG_DIR / "watch_device_token.txt"

# Bundle IDs (used as APNs topics)
IPHONE_BUNDLE_ID = "com.watchcode.app"
WATCH_BUNDLE_ID = "com.watchcode.app.watchkitapp"

# Keychain identifiers
KEYCHAIN_SERVICE = "com.watchcode.apns"
KEYCHAIN_AUTH_KEY = "auth_key"


# =============================================================================
# Security: Credential Filtering (V6)
# =============================================================================

class SensitiveDataFilter(logging.Filter):
    """Filter to redact sensitive data from logs."""
    PATTERNS = [
        (re.compile(r'[a-fA-F0-9]{64}'), '[DEVICE_TOKEN_REDACTED]'),
        (re.compile(r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'), '[JWT_REDACTED]'),
        (re.compile(r'-----BEGIN PRIVATE KEY-----.*?-----END PRIVATE KEY-----', re.DOTALL), '[PRIVATE_KEY_REDACTED]'),
        (re.compile(r'AuthKey_[A-Z0-9]+\.p8'), '[KEY_FILE_REDACTED]'),
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        # Format message with args first, then filter
        try:
            if record.args:
                msg = str(record.msg) % record.args
                record.args = None  # Clear args since we've formatted
            else:
                msg = str(record.msg)
        except (TypeError, ValueError):
            msg = str(record.msg)

        # Apply redaction patterns
        for pattern, replacement in self.PATTERNS:
            msg = pattern.sub(replacement, msg)
        record.msg = msg
        return True


# Set up logging with credential filter
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)
logger.addFilter(SensitiveDataFilter())

# Suppress httpx logging (it logs URLs which contain device tokens)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


# =============================================================================
# Security: File Permission Validation (V9)
# =============================================================================

def validate_file_permissions(path: Path, required_mode: int = 0o600) -> None:
    """Validate that a file has secure permissions."""
    if not path.exists():
        return
    mode = path.stat().st_mode & 0o777
    if mode & (stat.S_IRWXG | stat.S_IRWXO):  # Group or world accessible
        raise PermissionError(
            f"Insecure permissions {oct(mode)} on {path}. "
            f"Run: chmod {oct(required_mode)[2:]} {path}"
        )


# =============================================================================
# Security: JWT Token Caching (V7)
# =============================================================================

class JWTCache:
    """Cache JWT tokens to avoid regeneration (Apple rate limits)."""

    def __init__(self):
        self._token: str | None = None
        self._issued_at: float | None = None
        self._team_id: str | None = None
        self._key_id: str | None = None
        self.refresh_threshold = 45 * 60  # 45 minutes (Apple allows 20-60 min)

    def get_token(self, team_id: str, key_id: str, p8_key: str) -> str:
        """Get cached token or generate new one if expired."""
        # Check if we can use cached token
        if (self._token and self._issued_at and
            self._team_id == team_id and self._key_id == key_id):
            age = time.time() - self._issued_at
            if age < self.refresh_threshold:
                logger.info("✓ Using cached JWT token")
                return self._token

        # Generate new token
        logger.info("⟳ Generating new JWT token")
        self._token = self._generate_jwt(team_id, key_id, p8_key)
        self._issued_at = time.time()
        self._team_id = team_id
        self._key_id = key_id
        return self._token

    def _generate_jwt(self, team_id: str, key_id: str, p8_key: str) -> str:
        """Generate JWT token for APNs authentication."""
        headers = {
            "alg": "ES256",
            "kid": key_id
        }
        payload = {
            "iss": team_id,
            "iat": int(time.time())
        }
        try:
            return jwt.encode(payload, p8_key, algorithm="ES256", headers=headers)
        except Exception as e:
            logger.error(f"❌ Failed to generate JWT: {e}")
            raise


# Global JWT cache instance
_jwt_cache = JWTCache()


# =============================================================================
# Security: Keychain Storage for .p8 Key (V3)
# =============================================================================

def load_p8_key() -> str:
    """Load .p8 private key for APNs.

    Priority:
    1. macOS Keychain (most secure)
    2. File with permission validation (fallback)
    """
    # Try Keychain first (most secure)
    if KEYRING_AVAILABLE:
        try:
            key = keyring.get_password(KEYCHAIN_SERVICE, KEYCHAIN_AUTH_KEY)
            if key:
                logger.info("✓ Loaded APNs key from Keychain")
                return key
        except Exception as e:
            logger.warning(f"⚠️ Keychain read failed: {e}")

    # Fallback to file (with security validation)
    if P8_KEY_PATH.exists():
        # Validate permissions before reading
        validate_file_permissions(P8_KEY_PATH, 0o600)

        with open(P8_KEY_PATH, 'r') as f:
            key = f.read()

        logger.info("✓ Loaded APNs key from file")

        # Suggest migrating to Keychain
        if KEYRING_AVAILABLE:
            logger.info("  💡 Tip: Run 'python3 ~/.watchcode/import_apns_key.py' to migrate to Keychain")

        return key

    # No key found
    logger.error("❌ APNs key not found!")
    if KEYRING_AVAILABLE:
        logger.error("   Option 1: Import key to Keychain with:")
        logger.error(f"     python3 ~/.watchcode/import_apns_key.py /path/to/AuthKey.p8")
    logger.error("   Option 2: Place key file at:")
    logger.error(f"     {P8_KEY_PATH}")
    logger.error("   Download from: https://developer.apple.com/account/resources/authkeys")
    raise FileNotFoundError("APNs key not found in Keychain or file")


def load_config():
    """Load configuration from JSON file."""
    if not CONFIG_FILE.exists():
        return {
            "team_id": "YOUR_TEAM_ID",
            "key_id": "YOUR_KEY_ID",
            "bundle_id": "com.watchcode.app"
        }

    # Validate permissions on config file
    validate_file_permissions(CONFIG_FILE, 0o600)

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_device_token():
    """Read device token from local cache (legacy iPhone path, now unused)."""
    if TOKEN_CACHE_PATH.exists():
        # Validate permissions
        validate_file_permissions(TOKEN_CACHE_PATH, 0o600)

        token = TOKEN_CACHE_PATH.read_text().strip()
        if token:
            logger.info("✓ Device token loaded (length: %d chars)", len(token))
            return token

    # If no token found, print helpful message
    logger.error("❌ Device token not found!")
    logger.error("   For standalone Watch mode, use --watch-only flag")
    logger.error("   Watch token path: %s", WATCH_TOKEN_CACHE_PATH)
    raise ValueError("Device token not found. Use --watch-only for standalone Watch mode.")


def get_watch_device_token():
    """Read Watch device token from CloudKit, local cache, or iCloud Drive."""
    # Try local cache first (fastest)
    if WATCH_TOKEN_CACHE_PATH.exists():
        try:
            validate_file_permissions(WATCH_TOKEN_CACHE_PATH, 0o600)
            token = WATCH_TOKEN_CACHE_PATH.read_text().strip()
            if token:
                logger.info("✓ Watch device token loaded (length: %d chars)", len(token))
                return token
        except PermissionError:
            pass

    # Try CloudKit (most reliable for Watch sync)
    try:
        from cloudkit_poller import get_watch_token
        token = get_watch_token()
        if token:
            logger.info("✓ Watch device token loaded from CloudKit (length: %d chars)", len(token))
            # Cache locally for faster access
            try:
                WATCH_TOKEN_CACHE_PATH.write_text(token)
                WATCH_TOKEN_CACHE_PATH.chmod(0o600)
            except Exception:
                pass
            return token
    except ImportError:
        pass  # cloudkit_poller not available
    except Exception as e:
        logger.warning(f"⚠️ CloudKit lookup failed: {e}")

    # Try iCloud Drive (legacy path)
    icloud_path = Path.home() / "Library/Mobile Documents/iCloud~com~watchcode~app/Documents/watch_device_token.txt"
    if icloud_path.exists():
        token = icloud_path.read_text().strip()
        if token:
            logger.info("✓ Watch device token loaded from iCloud Drive (length: %d chars)", len(token))
            try:
                WATCH_TOKEN_CACHE_PATH.write_text(token)
                WATCH_TOKEN_CACHE_PATH.chmod(0o600)
            except Exception:
                pass
            return token

    # Watch token is optional
    logger.info("ℹ️  Watch device token not found (Watch-native APNs not configured)")
    return None


def send_notification(device_token, payload, jwt_token, topic, is_production=False, push_type='alert'):
    """Send APNs notification via HTTP/2.

    Args:
        device_token: APNs device token
        payload: Notification payload dict
        jwt_token: JWT authentication token
        topic: APNs topic (bundle ID)
        is_production: Use production APNs server
        push_type: 'alert' (visible) or 'background' (silent wake)
    """
    host = APNS_HOST_PROD if is_production else APNS_HOST_DEV
    url = f"https://{host}/3/device/{device_token}"

    # Background pushes must use priority 5, alerts use priority 10
    priority = '5' if push_type == 'background' else '10'

    try:
        headers = {
            'authorization': f'bearer {jwt_token}',
            'apns-topic': topic,
            'apns-push-type': push_type,
            'apns-priority': priority,
            'apns-expiration': '0'
        }

        # Add apns-collapse-id for reliable notification removal
        # This enables removeDeliveredNotifications(withIdentifiers:) to work
        collapse_id = payload.get('id') or payload.get('payloadId')
        if collapse_id:
            headers['apns-collapse-id'] = collapse_id

        payload_json = json.dumps(payload)

        with httpx.Client(http2=True, timeout=10.0) as client:
            response = client.post(url, headers=headers, content=payload_json)

        if response.status_code == 200:
            return True, "Success"
        else:
            error_data = response.json() if response.text else {}
            reason = error_data.get('reason', 'Unknown error')
            return False, f"HTTP {response.status_code}: {reason}"

    except Exception as e:
        return False, str(e)


def build_wake_push_payload(session_id, sequence_id=0):
    """Build silent wake push payload to wake iOS app.

    This sends a background notification that wakes the app to process
    any queued WatchConnectivity messages from the Watch.
    """
    return {
        "aps": {
            "content-available": 1  # Triggers background fetch
        },
        "event": "wake",
        "sessionId": session_id,
        "sequenceId": sequence_id,
        "timestamp": datetime.now().isoformat(),
        "isWakePush": True
    }


def build_apns_payload(event, message, session_id, requires_action=False, project_name=None, full_response=None, user_prompt=None, sequence_id=0, notification_id=None):
    """Build APNs payload structure."""
    # Sound mapping
    sound_map = {
        "session_start": "session_start.caf",
        "session_end": "success.caf",
        "stop": "success.caf",
        "notification": "notification.caf",
        "permission_request": "notification.caf",
        "error": "error.caf"
    }

    sound = sound_map.get(event, "default")

    # Category for actionable notifications
    # Questions get their own category with no action buttons
    if event == 'question':
        category = "QUESTION_NOTIFICATION"
    elif requires_action:
        category = "PERMISSION_REQUEST"
    else:
        category = "WATCHCODE_NOTIFICATION"

    # Generate a single UUID for deduplication (must be same for both id fields)
    payload_uuid = notification_id or str(uuid.uuid4())

    payload = {
        "aps": {
            "alert": {
                "title": "Claude Code",
                "body": message,
                "subtitle": event.replace('_', ' ').title()
            },
            "sound": sound,
            "badge": 1,
            "category": category,
            "thread-id": session_id
        },
        "event": event,
        "sessionId": session_id,
        "timestamp": datetime.now().isoformat(),
        "requiresAction": requires_action,
        "id": payload_uuid,  # Valid UUID for deduplication
        "payloadId": payload_uuid,  # Duplicate for Watch compatibility
        "sequenceId": sequence_id
    }

    if project_name:
        payload["projectName"] = project_name

    # Add metadata for full context
    metadata = {}
    if full_response:
        metadata["fullResponse"] = full_response
    if user_prompt:
        metadata["userPrompt"] = user_prompt
    if metadata:
        payload["metadata"] = metadata

    return payload


def main():
    parser = argparse.ArgumentParser(
        description='Send APNs notification for WatchCode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --event session_start --message "Session started" --session-id abc123
  %(prog)s --event permission_request --message "Approve file write?" --session-id abc123 --requires-action
        """
    )

    parser.add_argument('--event', required=True,
                       help='Event type (notification, session_start, stop, etc.)')
    parser.add_argument('--message', required=True,
                       help='Notification message')
    parser.add_argument('--session-id', required=True,
                       help='Claude Code session ID')
    parser.add_argument('--requires-action', action='store_true',
                       help='Notification requires user action')
    parser.add_argument('--project-name',
                       help='Project name (optional)')
    parser.add_argument('--full-response',
                       help='Full Claude response text (optional)')
    parser.add_argument('--user-prompt',
                       help='User prompt that triggered this response (optional)')
    parser.add_argument('--production', action='store_true',
                       help='Use production APNs server (default: sandbox)')
    parser.add_argument('--push-type', choices=['alert', 'background'], default='alert',
                       help='Push type: alert (visible) or background (silent wake)')
    parser.add_argument('--sequence-id', type=int, default=0,
                       help='Sequence ID for correlation tracking')
    parser.add_argument('--config',
                       help=f'Config file path (default: {CONFIG_FILE})')
    parser.add_argument('--watch-only', action='store_true',
                       help='Send only to Watch (recommended for standalone mode)')
    parser.add_argument('--iphone-only', action='store_true',
                       help='Send only to legacy device token (deprecated)')
    parser.add_argument('--notification-id',
                       help='Unique notification ID for tracking')

    args = parser.parse_args()

    # Load configuration
    config = load_config()

    # Log differently for wake vs alert pushes
    is_wake = args.push_type == 'background'
    if is_wake:
        logger.info("🔔 Sending wake push (silent)...")
        logger.info("   Session: %s", args.session_id)
        logger.info("   Sequence: %d", args.sequence_id)
    else:
        logger.info("📱 Sending notification...")
        logger.info("   Event: %s", args.event)
        logger.info("   Session: %s", args.session_id)
        msg_preview = args.message[:50] + "..." if len(args.message) > 50 else args.message
        logger.info("   Message: %s", msg_preview)

    try:
        # Load P8 key
        p8_key = load_p8_key()

        # Get JWT token (cached)
        jwt_token = _jwt_cache.get_token(config['team_id'], config['key_id'], p8_key)

        # Get device tokens
        iphone_token = None if args.watch_only else get_device_token()
        watch_token = None if args.iphone_only else get_watch_device_token()

        # Build payload - wake push vs regular notification
        if is_wake:
            payload_data = build_wake_push_payload(
                session_id=args.session_id,
                sequence_id=args.sequence_id
            )
        else:
            payload_data = build_apns_payload(
                event=args.event,
                message=args.message,
                session_id=args.session_id,
                requires_action=args.requires_action,
                project_name=args.project_name,
                full_response=args.full_response,
                user_prompt=args.user_prompt,
                sequence_id=args.sequence_id,
                notification_id=args.notification_id
            )

        # Track results
        any_success = False
        errors = []

        # Send to iPhone
        if iphone_token:
            logger.info("📱 Sending to iPhone...")
            success, message = send_notification(
                iphone_token,
                payload_data,
                jwt_token,
                topic=IPHONE_BUNDLE_ID,
                is_production=args.production,
                push_type=args.push_type
            )
            if success:
                logger.info("✓ iPhone notification sent")
                any_success = True
            else:
                logger.error("❌ iPhone failed: %s", message)
                errors.append(f"iPhone: {message}")

        # Send to Watch (if token available and not wake push)
        if watch_token and not is_wake:
            logger.info("⌚ Sending to Watch...")
            success, message = send_notification(
                watch_token,
                payload_data,
                jwt_token,
                topic=WATCH_BUNDLE_ID,
                is_production=args.production,
                push_type='alert'  # Watch always gets alert type
            )
            if success:
                logger.info("✓ Watch notification sent")
                any_success = True
            else:
                logger.error("❌ Watch failed: %s", message)
                errors.append(f"Watch: {message}")

        if any_success:
            logger.info("✓ Notification(s) sent successfully")
            return 0
        else:
            logger.error("❌ All notifications failed: %s", "; ".join(errors))
            return 1

    except PermissionError as e:
        logger.error("❌ Security error: %s", e)
        return 1
    except FileNotFoundError as e:
        logger.error("❌ Configuration error: %s", e)
        return 1
    except ValueError as e:
        logger.error("❌ %s", e)
        return 1
    except Exception as e:
        logger.error("❌ Unexpected error: %s", e)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
