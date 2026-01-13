"""End-to-end encryption module for WatchCode.

Uses ChaCha20-Poly1305 (AEAD) with HKDF-SHA256 key derivation.
Key is derived from the auth token shared between Watch and Mac.

CRITICAL: HKDF parameters must match Swift implementation exactly:
- Salt: "WatchCode-E2E-v1"
- Info: b"" (empty)
- Length: 32 bytes (256 bits)
"""

import base64
import json
import os
from typing import Any, Optional

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


# HKDF parameters - MUST match Swift CryptoManager exactly
HKDF_SALT = b"WatchCode-E2E-v1"
HKDF_INFO = b""  # Empty info
KEY_LENGTH = 32  # 256 bits for ChaCha20

# Nonce length for ChaCha20-Poly1305
NONCE_LENGTH = 12  # 96 bits

# Current encryption version
ENCRYPTION_VERSION = 1


class CryptoError(Exception):
    """Base exception for crypto operations."""
    pass


class KeyDerivationError(CryptoError):
    """Failed to derive encryption key."""
    pass


class EncryptionError(CryptoError):
    """Failed to encrypt data."""
    pass


class DecryptionError(CryptoError):
    """Failed to decrypt data."""
    pass


class InvalidPayloadError(CryptoError):
    """Invalid encrypted payload format."""
    pass


class CryptoManager:
    """Manages end-to-end encryption using ChaCha20-Poly1305.

    Thread-safe with cached key for performance.

    Example:
        crypto = CryptoManager()
        encrypted = crypto.encrypt({"message": "hello"}, auth_token)
        decrypted = crypto.decrypt(encrypted, auth_token)
    """

    def __init__(self):
        """Initialize crypto manager with empty key cache."""
        self._cached_key: Optional[bytes] = None
        self._cached_auth_token: Optional[str] = None

    def derive_key(self, auth_token: str) -> bytes:
        """Derive encryption key from auth token using HKDF-SHA256.

        Parameters must match Swift CryptoKit implementation exactly:
        - Salt: "WatchCode-E2E-v1"
        - Info: "" (empty)
        - Length: 32 bytes

        Args:
            auth_token: The 12-character auth token shared between Watch and Mac

        Returns:
            32-byte (256-bit) key for ChaCha20-Poly1305

        Raises:
            KeyDerivationError: If key derivation fails
        """
        # Return cached key if auth token matches
        if self._cached_key is not None and self._cached_auth_token == auth_token:
            return self._cached_key

        try:
            hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=KEY_LENGTH,
                salt=HKDF_SALT,
                info=HKDF_INFO,
            )
            key = hkdf.derive(auth_token.encode('utf-8'))

            # Cache the derived key
            self._cached_key = key
            self._cached_auth_token = auth_token

            return key

        except Exception as e:
            raise KeyDerivationError(f"Failed to derive key: {e}") from e

    def clear_key_cache(self) -> None:
        """Clear cached key (call when auth token changes)."""
        self._cached_key = None
        self._cached_auth_token = None

    def encrypt(self, data: dict[str, Any], auth_token: str) -> dict[str, Any]:
        """Encrypt a dictionary payload.

        Args:
            data: Dictionary to encrypt
            auth_token: Auth token to derive key from

        Returns:
            Encrypted payload dict: {"v": 1, "nonce": "<base64>", "ciphertext": "<base64>"}

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            key = self.derive_key(auth_token)
            chacha = ChaCha20Poly1305(key)

            # Generate random 12-byte nonce
            nonce = os.urandom(NONCE_LENGTH)

            # Serialize to JSON
            plaintext = json.dumps(data).encode('utf-8')

            # Encrypt (ChaCha20Poly1305 returns ciphertext + 16-byte tag)
            ciphertext = chacha.encrypt(nonce, plaintext, None)

            return {
                "v": ENCRYPTION_VERSION,
                "nonce": base64.b64encode(nonce).decode('ascii'),
                "ciphertext": base64.b64encode(ciphertext).decode('ascii'),
            }

        except CryptoError:
            raise
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}") from e

    def encrypt_bytes(self, data: bytes, auth_token: str) -> dict[str, Any]:
        """Encrypt raw bytes.

        Args:
            data: Bytes to encrypt
            auth_token: Auth token to derive key from

        Returns:
            Encrypted payload dict: {"v": 1, "nonce": "<base64>", "ciphertext": "<base64>"}

        Raises:
            EncryptionError: If encryption fails
        """
        try:
            key = self.derive_key(auth_token)
            chacha = ChaCha20Poly1305(key)

            # Generate random 12-byte nonce
            nonce = os.urandom(NONCE_LENGTH)

            # Encrypt (ChaCha20Poly1305 returns ciphertext + 16-byte tag)
            ciphertext = chacha.encrypt(nonce, data, None)

            return {
                "v": ENCRYPTION_VERSION,
                "nonce": base64.b64encode(nonce).decode('ascii'),
                "ciphertext": base64.b64encode(ciphertext).decode('ascii'),
            }

        except CryptoError:
            raise
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {e}") from e

    def decrypt(self, encrypted: dict[str, Any], auth_token: str) -> dict[str, Any]:
        """Decrypt an encrypted payload to dictionary.

        Args:
            encrypted: Encrypted payload dict with v, nonce, ciphertext
            auth_token: Auth token to derive key from

        Returns:
            Decrypted dictionary

        Raises:
            InvalidPayloadError: If payload format is invalid
            DecryptionError: If decryption fails (wrong key or corrupted data)
        """
        try:
            # Validate version
            version = encrypted.get("v")
            if version != ENCRYPTION_VERSION:
                raise InvalidPayloadError(
                    f"Unsupported encryption version: {version}"
                )

            # Extract nonce and ciphertext
            nonce_b64 = encrypted.get("nonce")
            ciphertext_b64 = encrypted.get("ciphertext")

            if not nonce_b64 or not ciphertext_b64:
                raise InvalidPayloadError("Missing nonce or ciphertext")

            nonce = base64.b64decode(nonce_b64)
            ciphertext = base64.b64decode(ciphertext_b64)

            if len(nonce) != NONCE_LENGTH:
                raise InvalidPayloadError(
                    f"Invalid nonce length: {len(nonce)} (expected {NONCE_LENGTH})"
                )

            # ChaCha20Poly1305 ciphertext must include 16-byte tag
            if len(ciphertext) < 16:
                raise InvalidPayloadError(
                    f"Ciphertext too short: {len(ciphertext)} bytes"
                )

            key = self.derive_key(auth_token)
            chacha = ChaCha20Poly1305(key)

            # Decrypt
            plaintext = chacha.decrypt(nonce, ciphertext, None)

            return json.loads(plaintext.decode('utf-8'))

        except InvalidPayloadError:
            raise
        except json.JSONDecodeError as e:
            raise DecryptionError(f"Decrypted data is not valid JSON: {e}") from e
        except Exception as e:
            # cryptography raises InvalidTag for auth failure
            if "tag" in str(e).lower():
                raise DecryptionError(
                    "Authentication failed - wrong key or corrupted data"
                ) from e
            raise DecryptionError(f"Decryption failed: {e}") from e

    def decrypt_bytes(self, encrypted: dict[str, Any], auth_token: str) -> bytes:
        """Decrypt an encrypted payload to raw bytes.

        Args:
            encrypted: Encrypted payload dict with v, nonce, ciphertext
            auth_token: Auth token to derive key from

        Returns:
            Decrypted bytes

        Raises:
            InvalidPayloadError: If payload format is invalid
            DecryptionError: If decryption fails (wrong key or corrupted data)
        """
        try:
            # Validate version
            version = encrypted.get("v")
            if version != ENCRYPTION_VERSION:
                raise InvalidPayloadError(
                    f"Unsupported encryption version: {version}"
                )

            # Extract nonce and ciphertext
            nonce_b64 = encrypted.get("nonce")
            ciphertext_b64 = encrypted.get("ciphertext")

            if not nonce_b64 or not ciphertext_b64:
                raise InvalidPayloadError("Missing nonce or ciphertext")

            nonce = base64.b64decode(nonce_b64)
            ciphertext = base64.b64decode(ciphertext_b64)

            if len(nonce) != NONCE_LENGTH:
                raise InvalidPayloadError(
                    f"Invalid nonce length: {len(nonce)} (expected {NONCE_LENGTH})"
                )

            # ChaCha20Poly1305 ciphertext must include 16-byte tag
            if len(ciphertext) < 16:
                raise InvalidPayloadError(
                    f"Ciphertext too short: {len(ciphertext)} bytes"
                )

            key = self.derive_key(auth_token)
            chacha = ChaCha20Poly1305(key)

            # Decrypt
            return chacha.decrypt(nonce, ciphertext, None)

        except InvalidPayloadError:
            raise
        except Exception as e:
            # cryptography raises InvalidTag for auth failure
            if "tag" in str(e).lower():
                raise DecryptionError(
                    "Authentication failed - wrong key or corrupted data"
                ) from e
            raise DecryptionError(f"Decryption failed: {e}") from e


def is_encrypted(payload: dict[str, Any]) -> bool:
    """Check if a payload is encrypted.

    Encrypted payloads have: v (int), nonce (str), ciphertext (str)

    Args:
        payload: Dictionary to check

    Returns:
        True if this is an encrypted payload
    """
    return (
        isinstance(payload.get("v"), int) and
        payload.get("v") == ENCRYPTION_VERSION and
        isinstance(payload.get("nonce"), str) and
        isinstance(payload.get("ciphertext"), str)
    )


# Module-level singleton for convenience
_crypto_manager: Optional[CryptoManager] = None


def get_crypto_manager() -> CryptoManager:
    """Get or create the shared crypto manager instance."""
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptoManager()
    return _crypto_manager


def encrypt(data: dict[str, Any], auth_token: str) -> dict[str, Any]:
    """Encrypt a dictionary payload using the shared crypto manager.

    Args:
        data: Dictionary to encrypt
        auth_token: Auth token to derive key from

    Returns:
        Encrypted payload dict
    """
    return get_crypto_manager().encrypt(data, auth_token)


def decrypt(encrypted: dict[str, Any], auth_token: str) -> dict[str, Any]:
    """Decrypt an encrypted payload using the shared crypto manager.

    Args:
        encrypted: Encrypted payload dict
        auth_token: Auth token to derive key from

    Returns:
        Decrypted dictionary
    """
    return get_crypto_manager().decrypt(encrypted, auth_token)
