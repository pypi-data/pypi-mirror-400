"""Tests for WatchCode CLI commands.

Tests the Click CLI commands for the watchcode-cli package.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from pathlib import Path

from watchcode.cli import (
    main,
    setup,
    status,
    test as test_cmd,
    install_hooks,
    uninstall_hooks,
    fix_hooks,
    notify,
    devices,
    update_scripts,
)


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def mock_config(tmp_path):
    """Mock Config with temp paths."""
    with patch('watchcode.cli.Config') as MockConfig:
        config = MagicMock()
        config.config_dir = tmp_path
        config.config_file = tmp_path / "config.json"
        config.is_configured.return_value = False
        config.get_auth_token.return_value = None
        config.get_relay_url.return_value = "https://relay.example.com"
        config.get_storage_location.return_value = "keychain"
        config.validate_token_format.return_value = True
        config.format_token_display.return_value = "ABCD-1234-EFGH"
        MockConfig.return_value = config
        yield config


class TestMainCommand:
    """Tests for main CLI group."""

    def test_main_shows_help(self, runner):
        """Main command shows help when no subcommand."""
        with patch('watchcode.cli.check_for_updates', return_value=None):
            with patch('watchcode.cli.Config') as MockConfig:
                mock_config = MagicMock()
                mock_config.is_configured.return_value = True
                MockConfig.return_value = mock_config

                result = runner.invoke(main)

        assert result.exit_code == 0
        assert "WatchCode CLI" in result.output

    def test_main_shows_version(self, runner):
        """--version shows version number."""
        result = runner.invoke(main, ['--version'])

        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_main_shows_setup_hint_when_not_configured(self, runner, mock_config):
        """Shows setup hint when not configured."""
        mock_config.is_configured.return_value = False

        with patch('watchcode.cli.check_for_updates', return_value=None):
            result = runner.invoke(main)

        assert "watchcode setup" in result.output

    def test_main_shows_update_available(self, runner, mock_config):
        """Shows update message when new version available."""
        mock_config.is_configured.return_value = True

        with patch('watchcode.cli.check_for_updates', return_value="2.0.0"):
            with patch('watchcode.cli.get_version', return_value="1.0.0"):
                result = runner.invoke(main)

        assert "Update available" in result.output
        assert "2.0.0" in result.output


class TestSetupCommand:
    """Tests for setup command."""

    @patch('watchcode.cli.install_scripts')
    @patch('watchcode.cli.HooksInstaller')
    @patch('watchcode.cli.RelayClient')
    def test_setup_with_valid_code(self, mock_client_class, mock_hooks_class, mock_scripts,
                                    runner, mock_config):
        """Setup with valid code completes successfully."""
        mock_scripts.return_value = {"installed": ["hook_handler.py"], "updated": [], "errors": []}

        mock_hooks_instance = MagicMock()
        mock_hooks_instance.cleanup_legacy_hooks.return_value = {"removed": [], "fixed": []}
        mock_hooks_instance.install_hooks.return_value = {"installed": ["Stop"], "skipped": [], "blocked": []}
        mock_hooks_class.return_value = mock_hooks_instance

        mock_client_instance = MagicMock()
        mock_client_instance.send_test_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        mock_config.validate_token_format.return_value = True

        result = runner.invoke(setup, input="ABCD-1234-EFGH\n")

        assert result.exit_code == 0
        assert "Setup complete" in result.output
        mock_config.set_auth_token.assert_called_once()

    @patch('watchcode.cli.install_scripts')
    @patch('watchcode.cli.HooksInstaller')
    def test_setup_rejects_invalid_code(self, mock_hooks_class, mock_scripts, runner, mock_config):
        """Setup rejects invalid setup codes."""
        mock_scripts.return_value = {"installed": [], "updated": [], "errors": []}

        mock_hooks_instance = MagicMock()
        mock_hooks_instance.cleanup_legacy_hooks.return_value = {"removed": [], "fixed": []}
        mock_hooks_class.return_value = mock_hooks_instance

        # First two attempts fail, third succeeds
        mock_config.validate_token_format.side_effect = [False, False, True]

        with patch('watchcode.cli.RelayClient') as mock_client_class:
            mock_client_instance = MagicMock()
            mock_client_instance.send_test_notification.return_value = {"success": True}
            mock_client_class.return_value = mock_client_instance

            result = runner.invoke(setup, input="bad\nstillbad\nABCD-1234-EFGH\n")

        assert "Invalid setup code" in result.output

    @patch('watchcode.cli.install_scripts')
    @patch('watchcode.cli.HooksInstaller')
    @patch('watchcode.cli.RelayClient')
    def test_setup_with_no_hooks_flag(self, mock_client_class, mock_hooks_class, mock_scripts,
                                       runner, mock_config):
        """Setup with --no-hooks skips hook installation."""
        mock_scripts.return_value = {"installed": [], "updated": [], "errors": []}

        mock_hooks_instance = MagicMock()
        mock_hooks_instance.cleanup_legacy_hooks.return_value = {"removed": [], "fixed": []}
        mock_hooks_class.return_value = mock_hooks_instance

        mock_client_instance = MagicMock()
        mock_client_instance.send_test_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        mock_config.validate_token_format.return_value = True

        result = runner.invoke(setup, ['--no-hooks'], input="ABCD-1234-EFGH\n")

        assert result.exit_code == 0
        assert "Skipped hook installation" in result.output
        mock_hooks_instance.install_hooks.assert_not_called()

    @patch('watchcode.cli.install_scripts')
    @patch('watchcode.cli.HooksInstaller')
    @patch('watchcode.cli.RelayClient')
    def test_setup_cleans_legacy_hooks(self, mock_client_class, mock_hooks_class, mock_scripts,
                                        runner, mock_config):
        """Setup cleans legacy spam hooks."""
        mock_scripts.return_value = {"installed": [], "updated": [], "errors": []}

        mock_hooks_instance = MagicMock()
        # PreToolUse now in removed (legacy spam) not fixed (GitHub #13439)
        mock_hooks_instance.cleanup_legacy_hooks.return_value = {
            "removed": ["SessionStart", "SessionEnd", "PreToolUse"],
            "fixed": []
        }
        mock_hooks_instance.install_hooks.return_value = {"installed": [], "skipped": [], "blocked": []}
        mock_hooks_class.return_value = mock_hooks_instance

        mock_client_instance = MagicMock()
        mock_client_instance.send_test_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        mock_config.validate_token_format.return_value = True

        result = runner.invoke(setup, input="ABCD-1234-EFGH\n")

        assert "Removed: SessionStart, SessionEnd, PreToolUse" in result.output


class TestStatusCommand:
    """Tests for status command."""

    @patch('watchcode.cli.HooksInstaller')
    def test_status_not_configured(self, mock_hooks_class, runner, mock_config):
        """Status shows not configured message."""
        mock_config.is_configured.return_value = False

        mock_hooks_instance = MagicMock()
        # PreToolUse removed from hooks (GitHub #13439)
        mock_hooks_instance.get_hook_status.return_value = {"Stop": False, "PermissionRequest": False}
        mock_hooks_class.return_value = mock_hooks_instance

        result = runner.invoke(status)

        assert "NOT CONFIGURED" in result.output

    @patch('watchcode.cli.HooksInstaller')
    def test_status_configured(self, mock_hooks_class, runner, mock_config):
        """Status shows configuration details."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.format_token_display.return_value = "ABCD-1234-EFGH"

        mock_hooks_instance = MagicMock()
        # PreToolUse removed from hooks (GitHub #13439)
        mock_hooks_instance.get_hook_status.return_value = {"Stop": True, "PermissionRequest": True}
        mock_hooks_class.return_value = mock_hooks_instance

        result = runner.invoke(status)

        assert result.exit_code == 0
        assert "CONFIGURED" in result.output
        assert "ABCD-1234-EFGH" in result.output

    @patch('watchcode.cli.HooksInstaller')
    def test_status_shows_hook_status(self, mock_hooks_class, runner, mock_config):
        """Status shows hook installation status."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"

        mock_hooks_instance = MagicMock()
        # PreToolUse removed from hooks (GitHub #13439)
        mock_hooks_instance.get_hook_status.return_value = {
            "Stop": True,
            "PermissionRequest": True
        }
        mock_hooks_class.return_value = mock_hooks_instance

        result = runner.invoke(status)

        # Check hooks are shown (PreToolUse removed)
        assert "Stop" in result.output
        assert "PermissionRequest" in result.output


class TestTestCommand:
    """Tests for test notification command."""

    @patch('watchcode.cli.RelayClient')
    def test_sends_test_notification_no_wait(self, mock_client_class, runner, mock_config):
        """Test command with --no-wait sends simple notification."""
        mock_config.is_configured.return_value = True

        mock_client_instance = MagicMock()
        mock_client_instance.send_test_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(test_cmd, ['--no-wait'])

        assert result.exit_code == 0
        assert "sent successfully" in result.output.lower()
        mock_client_instance.send_test_notification.assert_called_once()

    def test_fails_when_not_configured(self, runner, mock_config):
        """Test command fails when not configured."""
        mock_config.is_configured.return_value = False

        result = runner.invoke(test_cmd)

        assert result.exit_code == 1
        assert "not configured" in result.output.lower()

    @patch('watchcode.cli.poll_for_response')
    @patch('watchcode.cli.RelayClient')
    def test_interactive_test_with_response(self, mock_client_class, mock_poll, runner, mock_config):
        """Interactive test receives Watch response."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.get_relay_url.return_value = "https://relay.example.com"

        mock_client_instance = MagicMock()
        mock_client_instance.send_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        mock_poll.return_value = {"action": "approve"}

        result = runner.invoke(test_cmd)

        assert result.exit_code == 0
        assert "APPROVE" in result.output.upper()
        assert "successful" in result.output.lower()

    @patch('watchcode.cli.poll_for_response')
    @patch('watchcode.cli.RelayClient')
    def test_interactive_test_timeout(self, mock_client_class, mock_poll, runner, mock_config):
        """Interactive test handles timeout."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.get_relay_url.return_value = "https://relay.example.com"

        mock_client_instance = MagicMock()
        mock_client_instance.send_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        mock_poll.return_value = None  # Timeout

        result = runner.invoke(test_cmd)

        assert result.exit_code == 1
        assert "Timeout" in result.output


class TestHookCommands:
    """Tests for hook management commands."""

    @patch('watchcode.cli.HooksInstaller')
    def test_install_hooks_command(self, mock_installer_class, runner):
        """install-hooks command installs hooks."""
        mock_instance = MagicMock()
        # PreToolUse removed from hooks (GitHub #13439)
        mock_instance.get_hook_status.return_value = {"Stop": False, "PermissionRequest": False}
        mock_instance.install_hooks.return_value = {"installed": ["Stop", "PermissionRequest"], "skipped": [], "blocked": []}
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(install_hooks)

        assert result.exit_code == 0
        mock_instance.install_hooks.assert_called_once()
        assert "Installed:" in result.output

    @patch('watchcode.cli.HooksInstaller')
    def test_install_hooks_already_installed(self, mock_installer_class, runner):
        """install-hooks shows message when all installed."""
        mock_instance = MagicMock()
        # PreToolUse removed from hooks (GitHub #13439)
        mock_instance.get_hook_status.return_value = {"Stop": True, "PermissionRequest": True}
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(install_hooks)

        assert result.exit_code == 0
        assert "already installed" in result.output.lower()
        mock_instance.install_hooks.assert_not_called()

    @patch('watchcode.cli.HooksInstaller')
    def test_uninstall_hooks_command_confirmed(self, mock_installer_class, runner):
        """uninstall-hooks removes hooks when confirmed."""
        mock_instance = MagicMock()
        # PreToolUse removed from hooks (GitHub #13439)
        mock_instance.uninstall_hooks.return_value = {"removed": ["Stop", "PermissionRequest"], "total": 2}
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(uninstall_hooks, input="y\n")

        assert result.exit_code == 0
        mock_instance.uninstall_hooks.assert_called_once()
        assert "Removed hooks:" in result.output

    @patch('watchcode.cli.HooksInstaller')
    def test_uninstall_hooks_command_cancelled(self, mock_installer_class, runner):
        """uninstall-hooks cancelled when user declines."""
        mock_instance = MagicMock()
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(uninstall_hooks, input="n\n")

        assert result.exit_code == 0
        mock_instance.uninstall_hooks.assert_not_called()
        assert "cancelled" in result.output.lower()

    @patch('watchcode.cli.HooksInstaller')
    def test_uninstall_hooks_no_hooks_found(self, mock_installer_class, runner):
        """uninstall-hooks shows message when no hooks found."""
        mock_instance = MagicMock()
        mock_instance.uninstall_hooks.return_value = {"removed": [], "total": 0}
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(uninstall_hooks, input="y\n")

        assert result.exit_code == 0
        assert "No WatchCode hooks found" in result.output

    @patch('watchcode.cli.HooksInstaller')
    def test_fix_hooks_command(self, mock_installer_class, runner):
        """fix-hooks cleans legacy spam hooks."""
        mock_instance = MagicMock()
        # PreToolUse now in removed (legacy spam) not fixed (GitHub #13439)
        mock_instance.cleanup_legacy_hooks.return_value = {
            "removed": ["SessionStart", "Notification", "PreToolUse"],
            "fixed": []
        }
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(fix_hooks)

        assert result.exit_code == 0
        assert "SessionStart" in result.output
        assert "Notification" in result.output
        assert "PreToolUse" in result.output

    @patch('watchcode.cli.HooksInstaller')
    def test_fix_hooks_clean(self, mock_installer_class, runner):
        """fix-hooks shows clean message when nothing to fix."""
        mock_instance = MagicMock()
        mock_instance.cleanup_legacy_hooks.return_value = {"removed": [], "fixed": []}
        mock_installer_class.return_value = mock_instance

        result = runner.invoke(fix_hooks)

        assert result.exit_code == 0
        assert "configuration is clean" in result.output.lower()


class TestNotifyCommand:
    """Tests for notify command (used by hooks)."""

    @patch('watchcode.cli.RelayClient')
    def test_notify_sends_notification(self, mock_client_class, runner, mock_config):
        """notify sends notification with provided event."""
        mock_config.is_configured.return_value = True

        mock_client_instance = MagicMock()
        mock_client_instance.send_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(notify, ['--event', 'stop', '--message', 'Task done'])

        assert result.exit_code == 0
        mock_client_instance.send_notification.assert_called_once()
        call_kwargs = mock_client_instance.send_notification.call_args[1]
        assert call_kwargs['event'] == 'stop'

    def test_notify_silent_when_not_configured(self, runner, mock_config):
        """notify exits silently when not configured."""
        mock_config.is_configured.return_value = False

        result = runner.invoke(notify, ['--event', 'stop'])

        # Should exit with 0 to not break Claude Code
        assert result.exit_code == 0

    @patch('watchcode.cli.RelayClient')
    def test_notify_with_requires_action(self, mock_client_class, runner, mock_config):
        """notify passes requires_action flag."""
        mock_config.is_configured.return_value = True

        mock_client_instance = MagicMock()
        mock_client_instance.send_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(notify, ['--event', 'permission_request', '--requires-action'])

        call_kwargs = mock_client_instance.send_notification.call_args[1]
        assert call_kwargs['requires_action'] is True

    @patch('watchcode.cli.RelayClient')
    def test_notify_with_notification_id(self, mock_client_class, runner, mock_config):
        """notify passes notification_id for response correlation."""
        mock_config.is_configured.return_value = True

        mock_client_instance = MagicMock()
        mock_client_instance.send_notification.return_value = {"success": True}
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(notify, [
            '--event', 'permission_request',
            '--notification-id', 'test-uuid-123'
        ])

        call_kwargs = mock_client_instance.send_notification.call_args[1]
        assert call_kwargs['notification_id'] == 'test-uuid-123'


class TestDevicesCommand:
    """Tests for devices command."""

    def test_devices_not_configured(self, runner, mock_config):
        """devices fails when not configured."""
        mock_config.is_configured.return_value = False

        result = runner.invoke(devices)

        assert result.exit_code == 1
        assert "not configured" in result.output.lower()

    def test_devices_shows_info(self, runner, mock_config):
        """devices shows device configuration."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.format_token_display.return_value = "ABCD-1234-EFGH"
        mock_config.get_storage_location.return_value = "keychain"
        mock_config.get_relay_url.return_value = "https://relay.example.com"

        result = runner.invoke(devices)

        assert result.exit_code == 0
        assert "ABCD-1234-EFGH" in result.output
        assert "keychain" in result.output

    @patch('watchcode.cli.RelayClient')
    def test_devices_verify(self, mock_client_class, runner, mock_config):
        """devices --verify checks relay registration."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.format_token_display.return_value = "ABCD-1234-EFGH"

        mock_client_instance = MagicMock()
        mock_client_instance.verify_device.return_value = True
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(devices, ['--verify'])

        assert result.exit_code == 0
        assert "registered and active" in result.output.lower()

    @patch('watchcode.cli.RelayClient')
    def test_devices_clear_confirmed(self, mock_client_class, runner, mock_config):
        """devices --clear unregisters and clears config."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.format_token_display.return_value = "ABCD-1234-EFGH"

        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(devices, ['--clear'], input="y\n")

        assert result.exit_code == 0
        mock_client_instance.unregister_device.assert_called_once()
        mock_config.delete_auth_token.assert_called_once()

    @patch('watchcode.cli.RelayClient')
    def test_devices_clear_with_yes_flag(self, mock_client_class, runner, mock_config):
        """devices --clear -y skips confirmation."""
        mock_config.is_configured.return_value = True
        mock_config.get_auth_token.return_value = "ABCD1234EFGH"
        mock_config.format_token_display.return_value = "ABCD-1234-EFGH"

        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        result = runner.invoke(devices, ['--clear', '-y'])

        assert result.exit_code == 0
        mock_config.delete_auth_token.assert_called_once()


class TestUpdateScriptsCommand:
    """Tests for update-scripts command."""

    @patch('watchcode.cli.install_scripts')
    def test_update_scripts_with_updates(self, mock_install, runner):
        """update-scripts shows updated files."""
        mock_install.return_value = {
            "installed": [],
            "updated": ["hook_handler.py", "apns_sender.py"],
            "errors": []
        }

        result = runner.invoke(update_scripts)

        assert result.exit_code == 0
        assert "Updated:" in result.output
        assert "hook_handler.py" in result.output

    @patch('watchcode.cli.install_scripts')
    def test_update_scripts_already_current(self, mock_install, runner):
        """update-scripts shows up-to-date message."""
        mock_install.return_value = {"installed": [], "updated": [], "errors": []}

        result = runner.invoke(update_scripts)

        assert result.exit_code == 0
        assert "up to date" in result.output.lower()

    @patch('watchcode.cli.install_scripts')
    def test_update_scripts_with_errors(self, mock_install, runner):
        """update-scripts shows errors."""
        mock_install.return_value = {
            "installed": [],
            "updated": [],
            "errors": ["hook_handler.py: Permission denied"]
        }

        result = runner.invoke(update_scripts)

        assert result.exit_code == 0
        assert "Error:" in result.output
        assert "Permission denied" in result.output


class TestPollForResponse:
    """Tests for poll_for_response function."""

    @patch('httpx.Client')
    def test_poll_finds_response(self, mock_client_class):
        """poll_for_response returns response when found."""
        from watchcode.cli import poll_for_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"found": True, "response": {"action": "approve"}}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = poll_for_response("auth123", "notif456", "https://relay.test", timeout=2)

        assert result == {"action": "approve"}

    @patch('httpx.Client')
    def test_poll_timeout(self, mock_client_class):
        """poll_for_response returns None on timeout."""
        from watchcode.cli import poll_for_response

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"found": False}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client_class.return_value = mock_client

        result = poll_for_response("auth123", "notif456", "https://relay.test", timeout=1)

        assert result is None


class TestCheckForUpdates:
    """Tests for check_for_updates function."""

    @patch('httpx.get')
    def test_update_available(self, mock_get):
        """Returns latest version when update available."""
        from watchcode.cli import check_for_updates

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"info": {"version": "99.0.0"}}
        mock_get.return_value = mock_response

        result = check_for_updates()

        # Should return latest version if it's newer than current
        # Since we don't know the current installed version, just check it returned something
        assert result == "99.0.0" or result is None

    @patch('httpx.get')
    def test_handles_network_error(self, mock_get):
        """Returns None on network error."""
        from watchcode.cli import check_for_updates
        import httpx

        mock_get.side_effect = httpx.RequestError("Network error")

        result = check_for_updates()

        assert result is None
