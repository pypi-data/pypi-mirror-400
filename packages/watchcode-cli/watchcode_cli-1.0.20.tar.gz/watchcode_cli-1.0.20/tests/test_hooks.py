"""Tests for WatchCode CLI hooks module."""

import json
import pytest
from pathlib import Path
from watchcode.hooks import HooksInstaller


class TestHooksInstaller:
    """Tests for HooksInstaller class."""

    @pytest.fixture
    def installer(self, tmp_path):
        """Create installer with temp settings directory."""
        installer = HooksInstaller()
        installer.settings_dir = tmp_path / ".claude"
        installer.settings_file = installer.settings_dir / "settings.json"
        return installer

    @pytest.fixture
    def settings_with_hooks(self, installer):
        """Create settings file with existing non-WatchCode hooks."""
        installer.ensure_settings_dir()
        settings = {
            "hooks": {
                "Stop": [
                    {
                        "hooks": [
                            {"type": "command", "command": "echo 'other tool'"}
                        ]
                    }
                ]
            }
        }
        installer.settings_file.write_text(json.dumps(settings))
        return settings


class TestLoadSaveSettings(TestHooksInstaller):
    """Tests for settings file operations."""

    def test_load_settings_nonexistent(self, installer):
        """Loading from nonexistent file returns empty dict."""
        result = installer.load_settings()
        assert result == {}

    def test_load_settings_invalid_json(self, installer):
        """Loading invalid JSON returns empty dict."""
        installer.ensure_settings_dir()
        installer.settings_file.write_text("not valid json {{{")

        result = installer.load_settings()
        assert result == {}

    def test_save_settings_creates_directory(self, installer):
        """Saving creates settings directory if missing."""
        assert not installer.settings_dir.exists()

        installer.save_settings({"key": "value"})

        assert installer.settings_dir.exists()
        assert installer.settings_file.exists()

    def test_save_and_load_roundtrip(self, installer):
        """Save and load preserves data."""
        test_data = {"hooks": {"Stop": [{"type": "test"}]}, "other": "data"}

        installer.save_settings(test_data)
        loaded = installer.load_settings()

        assert loaded == test_data


class TestIsWatchcodeHook(TestHooksInstaller):
    """Tests for is_watchcode_hook detection."""

    def test_detects_watchcode_notify_command(self, installer):
        """Detects 'watchcode notify' as WatchCode hook."""
        hook = {
            "hooks": [
                {"type": "command", "command": "watchcode notify --event stop"}
            ]
        }
        assert installer.is_watchcode_hook(hook) is True

    def test_detects_hook_handler_command(self, installer):
        """Detects hook_handler.py in .watchcode as WatchCode hook."""
        hook = {
            "hooks": [
                {"type": "command", "command": "python3 ~/.watchcode/hook_handler.py permission_request"}
            ]
        }
        assert installer.is_watchcode_hook(hook) is True

    def test_rejects_other_commands(self, installer):
        """Does not detect unrelated commands as WatchCode."""
        hook = {
            "hooks": [
                {"type": "command", "command": "echo 'some other tool'"}
            ]
        }
        assert installer.is_watchcode_hook(hook) is False

    def test_rejects_hook_without_hooks_key(self, installer):
        """Hook without 'hooks' key is not WatchCode."""
        hook = {"matcher": "Bash"}
        assert installer.is_watchcode_hook(hook) is False

    def test_rejects_non_command_type(self, installer):
        """Non-command type hooks are not WatchCode."""
        hook = {
            "hooks": [
                {"type": "url", "url": "http://watchcode.example.com"}
            ]
        }
        assert installer.is_watchcode_hook(hook) is False

    def test_detects_watchcode_in_mixed_hooks(self, installer):
        """Detects WatchCode even when mixed with other commands."""
        hook = {
            "hooks": [
                {"type": "command", "command": "echo 'first'"},
                {"type": "command", "command": "watchcode notify --event stop"},
                {"type": "command", "command": "echo 'last'"}
            ]
        }
        assert installer.is_watchcode_hook(hook) is True


class TestInstallHooks(TestHooksInstaller):
    """Tests for install_hooks method."""

    def test_install_all_hooks_empty_settings(self, installer):
        """Installs all hooks when settings file is empty."""
        result = installer.install_hooks()

        assert set(result["installed"]) == {"Stop", "PreToolUse", "PermissionRequest"}
        assert result["skipped"] == []
        assert result["blocked"] == []

        settings = installer.load_settings()
        assert "hooks" in settings
        assert "Stop" in settings["hooks"]
        assert "PreToolUse" in settings["hooks"]
        assert "PermissionRequest" in settings["hooks"]

    def test_install_preserves_existing_hooks(self, installer, settings_with_hooks):
        """Installing does not remove existing non-WatchCode hooks."""
        installer.install_hooks()

        settings = installer.load_settings()
        # Original hook should still be there
        stop_hooks = settings["hooks"]["Stop"]
        non_watchcode = [h for h in stop_hooks if not installer.is_watchcode_hook(h)]
        assert len(non_watchcode) == 1
        assert "echo 'other tool'" in non_watchcode[0]["hooks"][0]["command"]

    def test_install_skips_already_installed(self, installer):
        """Skips hooks that are already installed."""
        # First install
        installer.install_hooks()

        # Second install
        result = installer.install_hooks()

        assert result["installed"] == []
        assert set(result["skipped"]) == {"Stop", "PreToolUse", "PermissionRequest"}

    def test_install_specific_hook_types(self, installer):
        """Can install specific hook types only."""
        result = installer.install_hooks(hook_types=["Stop"])

        assert result["installed"] == ["Stop"]

        settings = installer.load_settings()
        assert "Stop" in settings["hooks"]
        assert "PreToolUse" not in settings["hooks"]

    def test_install_blocks_spam_hooks(self, installer):
        """Blocks installation of spam hook types."""
        result = installer.install_hooks(hook_types=["SessionStart", "Notification", "Stop"])

        assert "SessionStart" in result["blocked"]
        assert "Notification" in result["blocked"]
        assert "Stop" in result["installed"]

    def test_install_blocks_session_end(self, installer):
        """Blocks installation of SessionEnd hook."""
        result = installer.install_hooks(hook_types=["SessionEnd"])

        assert "SessionEnd" in result["blocked"]
        assert result["installed"] == []

    def test_install_blocks_subagent_stop(self, installer):
        """Blocks installation of SubagentStop hook."""
        result = installer.install_hooks(hook_types=["SubagentStop"])

        assert "SubagentStop" in result["blocked"]

    def test_install_blocks_unknown_hook_types(self, installer):
        """Blocks installation of unknown hook types."""
        result = installer.install_hooks(hook_types=["UnknownHook", "Stop"])

        assert "UnknownHook" in result["blocked"]
        assert "Stop" in result["installed"]


class TestUninstallHooks(TestHooksInstaller):
    """Tests for uninstall_hooks method."""

    def test_uninstall_removes_watchcode_hooks(self, installer):
        """Uninstall removes WatchCode hooks."""
        installer.install_hooks()

        result = installer.uninstall_hooks()

        assert set(result["removed"]) == {"Stop", "PreToolUse", "PermissionRequest"}

        settings = installer.load_settings()
        # Either hooks dict is empty or keys have empty lists
        for hook_type in ["Stop", "PreToolUse", "PermissionRequest"]:
            if hook_type in settings.get("hooks", {}):
                # No WatchCode hooks in the list
                hooks = settings["hooks"][hook_type]
                for hook in hooks:
                    assert not installer.is_watchcode_hook(hook)

    def test_uninstall_preserves_other_hooks(self, installer, settings_with_hooks):
        """Uninstall preserves non-WatchCode hooks."""
        installer.install_hooks()

        installer.uninstall_hooks()

        settings = installer.load_settings()
        # Original hook should still be there
        assert "Stop" in settings["hooks"]
        stop_hooks = settings["hooks"]["Stop"]
        assert len(stop_hooks) == 1
        assert "echo 'other tool'" in stop_hooks[0]["hooks"][0]["command"]

    def test_uninstall_empty_settings(self, installer):
        """Uninstall on empty settings returns empty result."""
        result = installer.uninstall_hooks()

        assert result["removed"] == []
        assert result["total"] == 0


class TestCleanupLegacyHooks(TestHooksInstaller):
    """Tests for cleanup_legacy_hooks method."""

    def test_removes_session_start_hooks(self, installer):
        """Removes WatchCode SessionStart hooks."""
        installer.ensure_settings_dir()
        settings = {
            "hooks": {
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "watchcode notify --event session_start"}]}
                ]
            }
        }
        installer.settings_file.write_text(json.dumps(settings))

        result = installer.cleanup_legacy_hooks()

        assert "SessionStart" in result["removed"]

        settings = installer.load_settings()
        assert "SessionStart" not in settings.get("hooks", {})

    def test_removes_session_end_hooks(self, installer):
        """Removes WatchCode SessionEnd hooks."""
        installer.ensure_settings_dir()
        settings = {
            "hooks": {
                "SessionEnd": [
                    {"hooks": [{"type": "command", "command": "watchcode notify --event session_end"}]}
                ]
            }
        }
        installer.settings_file.write_text(json.dumps(settings))

        result = installer.cleanup_legacy_hooks()

        assert "SessionEnd" in result["removed"]

    def test_removes_notification_hooks(self, installer):
        """Removes WatchCode Notification hooks."""
        installer.ensure_settings_dir()
        settings = {
            "hooks": {
                "Notification": [
                    {"hooks": [{"type": "command", "command": "watchcode notify --event notification"}]}
                ]
            }
        }
        installer.settings_file.write_text(json.dumps(settings))

        result = installer.cleanup_legacy_hooks()

        assert "Notification" in result["removed"]

    def test_preserves_non_watchcode_spam_hooks(self, installer):
        """Does not remove non-WatchCode SessionStart hooks."""
        installer.ensure_settings_dir()
        settings = {
            "hooks": {
                "SessionStart": [
                    {"hooks": [{"type": "command", "command": "echo 'other tool session'"}]}
                ]
            }
        }
        installer.settings_file.write_text(json.dumps(settings))

        installer.cleanup_legacy_hooks()

        # Should not remove other tools' hooks
        settings = installer.load_settings()
        if "SessionStart" in settings.get("hooks", {}):
            assert len(settings["hooks"]["SessionStart"]) == 1

    def test_fixes_pretooluse_without_matcher(self, installer):
        """Fixes PreToolUse hooks without valid matcher."""
        installer.ensure_settings_dir()
        settings = {
            "hooks": {
                "PreToolUse": [
                    # No matcher = fires on every tool = spam
                    {"hooks": [{"type": "command", "command": "watchcode notify --event pre_tool_use"}]}
                ]
            }
        }
        installer.settings_file.write_text(json.dumps(settings))

        result = installer.cleanup_legacy_hooks()

        assert "PreToolUse" in result["fixed"]

        # Should have valid PreToolUse hooks now
        settings = installer.load_settings()
        if "PreToolUse" in settings.get("hooks", {}):
            for hook in settings["hooks"]["PreToolUse"]:
                if installer.is_watchcode_hook(hook):
                    assert hook.get("matcher") in {"AskUserQuestion", "Bash"}

    def test_cleanup_empty_settings(self, installer):
        """Cleanup on empty settings returns empty result."""
        result = installer.cleanup_legacy_hooks()

        assert result["removed"] == []
        assert result["fixed"] == []


class TestGetHookStatus(TestHooksInstaller):
    """Tests for get_hook_status method."""

    def test_all_hooks_not_installed(self, installer):
        """Reports all hooks as not installed when empty."""
        status = installer.get_hook_status()

        assert status == {
            "Stop": False,
            "PreToolUse": False,
            "PermissionRequest": False
        }

    def test_all_hooks_installed(self, installer):
        """Reports all hooks as installed after install."""
        installer.install_hooks()

        status = installer.get_hook_status()

        assert status == {
            "Stop": True,
            "PreToolUse": True,
            "PermissionRequest": True
        }

    def test_partial_installation(self, installer):
        """Reports correct status for partial installation."""
        installer.install_hooks(hook_types=["Stop"])

        status = installer.get_hook_status()

        assert status["Stop"] is True
        assert status["PreToolUse"] is False
        assert status["PermissionRequest"] is False

    def test_status_after_uninstall(self, installer):
        """Reports correct status after uninstall."""
        installer.install_hooks()
        installer.uninstall_hooks()

        status = installer.get_hook_status()

        assert status == {
            "Stop": False,
            "PreToolUse": False,
            "PermissionRequest": False
        }


class TestWatchcodeHooksDefinitions(TestHooksInstaller):
    """Tests for WATCHCODE_HOOKS definitions."""

    def test_stop_hook_has_correct_command(self, installer):
        """Stop hook uses watchcode notify command."""
        stop_hooks = installer.WATCHCODE_HOOKS["Stop"]
        assert len(stop_hooks) == 1
        command = stop_hooks[0]["hooks"][0]["command"]
        assert "watchcode notify --event stop" in command

    def test_permission_request_hook_uses_hook_handler(self, installer):
        """PermissionRequest hook uses hook_handler.py."""
        hooks = installer.WATCHCODE_HOOKS["PermissionRequest"]
        assert len(hooks) == 1
        command = hooks[0]["hooks"][0]["command"]
        assert "hook_handler.py" in command
        assert "permission_request" in command

    def test_pretooluse_hook_has_askuserquestion_matcher(self, installer):
        """PreToolUse hook has AskUserQuestion matcher."""
        hooks = installer.WATCHCODE_HOOKS["PreToolUse"]
        assert len(hooks) == 1
        assert hooks[0]["matcher"] == "AskUserQuestion"

    def test_all_hooks_use_command_type(self, installer):
        """All WatchCode hooks use 'command' type."""
        for hook_type, hooks_list in installer.WATCHCODE_HOOKS.items():
            for hook in hooks_list:
                for h in hook["hooks"]:
                    assert h["type"] == "command", f"{hook_type} should use command type"


class TestAllowedAndBlockedHookTypes(TestHooksInstaller):
    """Tests for ALLOWED_HOOK_TYPES and BLOCKED_SPAM_HOOKS."""

    def test_allowed_hook_types_are_valid(self, installer):
        """All WATCHCODE_HOOKS keys are in ALLOWED_HOOK_TYPES."""
        for hook_type in installer.WATCHCODE_HOOKS.keys():
            assert hook_type in installer.ALLOWED_HOOK_TYPES

    def test_blocked_hooks_not_in_allowed(self, installer):
        """BLOCKED_SPAM_HOOKS and ALLOWED_HOOK_TYPES are disjoint."""
        overlap = installer.BLOCKED_SPAM_HOOKS & installer.ALLOWED_HOOK_TYPES
        assert len(overlap) == 0, f"Overlap between blocked and allowed: {overlap}"

    def test_blocked_spam_hooks_contains_expected(self, installer):
        """BLOCKED_SPAM_HOOKS contains all expected spam types."""
        expected = {"SessionStart", "SessionEnd", "Notification", "SubagentStop"}
        assert expected == installer.BLOCKED_SPAM_HOOKS
