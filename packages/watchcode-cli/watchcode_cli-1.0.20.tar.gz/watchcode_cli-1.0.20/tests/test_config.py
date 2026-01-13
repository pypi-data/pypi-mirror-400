"""Tests for WatchCode CLI configuration module."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from watchcode.config import Config


class TestTokenValidation:
    """Tests for token format validation."""

    def test_valid_token_with_dashes(self):
        """Token with dashes should be valid."""
        config = Config()
        assert config.validate_token_format("ABCD-1234-EFGH") is True

    def test_valid_token_without_dashes(self):
        """Token without dashes should be valid."""
        config = Config()
        assert config.validate_token_format("ABCD1234EFGH") is True

    def test_valid_token_lowercase(self):
        """Lowercase token should be valid."""
        config = Config()
        assert config.validate_token_format("abcd-1234-efgh") is True

    def test_invalid_token_too_short(self):
        """Token shorter than 12 characters should be invalid."""
        config = Config()
        assert config.validate_token_format("ABCD-1234") is False

    def test_invalid_token_too_long(self):
        """Token longer than 12 characters should be invalid."""
        config = Config()
        assert config.validate_token_format("ABCD-1234-EFGH-IJKL") is False

    def test_invalid_token_special_chars(self):
        """Token with special characters should be invalid."""
        config = Config()
        assert config.validate_token_format("ABCD-1234-EF@!") is False

    def test_empty_token(self):
        """Empty token should be invalid."""
        config = Config()
        assert config.validate_token_format("") is False


class TestTokenFormatting:
    """Tests for token display formatting."""

    def test_format_plain_token(self):
        """Plain 12-char token should get dashes."""
        config = Config()
        assert config.format_token_display("ABCD1234EFGH") == "ABCD-1234-EFGH"

    def test_format_already_formatted(self):
        """Already formatted token should stay formatted."""
        config = Config()
        assert config.format_token_display("ABCD-1234-EFGH") == "ABCD-1234-EFGH"

    def test_format_short_token(self):
        """Short token should return as-is."""
        config = Config()
        assert config.format_token_display("ABCD") == "ABCD"


class TestConfigFile:
    """Tests for config file operations."""

    def test_load_nonexistent_file(self, tmp_path):
        """Loading nonexistent config should return empty dict."""
        config = Config()
        config.config_file = tmp_path / "nonexistent.json"
        assert config.load() == {}

    def test_save_and_load(self, tmp_path):
        """Save and load should preserve data."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"

        test_data = {"relay_url": "https://example.com", "version": 1}
        config.save(test_data)

        loaded = config.load()
        assert loaded["relay_url"] == "https://example.com"
        assert loaded["version"] == 1

    def test_save_strips_auth_token(self, tmp_path):
        """Save should not include auth_token in file."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"

        test_data = {"auth_token": "SECRET123456", "relay_url": "https://example.com"}
        config.save(test_data)

        # Read file directly to verify
        with open(config.config_file) as f:
            saved = json.load(f)
        assert "auth_token" not in saved
        assert saved["relay_url"] == "https://example.com"

    def test_load_invalid_json(self, tmp_path):
        """Loading invalid JSON should return empty dict."""
        config = Config()
        config.config_file = tmp_path / "invalid.json"
        config.config_file.write_text("not valid json {{{")
        assert config.load() == {}


class TestQueue:
    """Tests for offline notification queue."""

    def test_empty_queue(self, tmp_path):
        """Empty/nonexistent queue should return empty list."""
        config = Config()
        config.queue_file = tmp_path / "queue.json"
        assert config.load_queue() == []

    def test_add_to_queue(self, tmp_path):
        """Adding to queue should persist."""
        config = Config()
        config.config_dir = tmp_path
        config.queue_file = tmp_path / "queue.json"

        notification = {"event": "test", "message": "Hello"}
        config.add_to_queue(notification)

        queue = config.load_queue()
        assert len(queue) == 1
        assert queue[0]["event"] == "test"

    def test_clear_queue(self, tmp_path):
        """Clear should empty the queue."""
        config = Config()
        config.config_dir = tmp_path
        config.queue_file = tmp_path / "queue.json"

        config.add_to_queue({"event": "test"})
        config.add_to_queue({"event": "test2"})
        assert len(config.load_queue()) == 2

        config.clear_queue()
        assert config.load_queue() == []


class TestAuthToken:
    """Tests for auth token storage."""

    def test_get_token_not_configured(self, tmp_path):
        """Get token when not configured should return None."""
        config = Config()
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False  # Force no keychain

        assert config.get_auth_token() is None

    def test_is_configured_false(self, tmp_path):
        """is_configured should return False when no token."""
        config = Config()
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False

        assert config.is_configured() is False

    @patch("watchcode.config.keyring")
    def test_get_token_from_keychain(self, mock_keyring, tmp_path):
        """Get token should retrieve from keychain."""
        config = Config()
        config.config_file = tmp_path / "config.json"
        config._keychain_available = True

        mock_keyring.get_password.return_value = "ABCD1234EFGH"

        token = config.get_auth_token()
        assert token == "ABCD1234EFGH"
        mock_keyring.get_password.assert_called_once()

    @patch("watchcode.config.keyring")
    def test_set_token_to_keychain(self, mock_keyring, tmp_path):
        """Set token should store in keychain."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = True

        config.set_auth_token("abcd-1234-efgh")

        mock_keyring.set_password.assert_called_once()
        call_args = mock_keyring.set_password.call_args
        assert call_args[0][2] == "ABCD1234EFGH"  # Token should be uppercase, no dashes

    def test_set_token_fallback_to_file(self, tmp_path):
        """Set token should fall back to file when keychain unavailable."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config._keychain_available = False

        config.set_auth_token("ABCD-1234-EFGH")

        # Read file directly
        with open(config.config_file) as f:
            saved = json.load(f)
        assert saved["auth_token"] == "ABCD1234EFGH"


class TestRelayUrl:
    """Tests for relay URL configuration."""

    def test_default_relay_url(self, tmp_path):
        """Default relay URL should be production."""
        config = Config()
        config.config_file = tmp_path / "config.json"

        url = config.get_relay_url()
        assert "watchcode-relay" in url
        assert "workers.dev" in url

    def test_custom_relay_url(self, tmp_path):
        """Custom relay URL should be returned."""
        config = Config()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"

        custom_url = "https://custom-relay.example.com"
        config.save({"relay_url": custom_url})

        assert config.get_relay_url() == custom_url
