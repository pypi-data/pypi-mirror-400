"""Claude Code hooks installer for WatchCode."""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional


class HooksInstaller:
    """Manages installation of Claude Code hooks."""

    CLAUDE_SETTINGS_DIR = Path.home() / ".claude"
    CLAUDE_SETTINGS_FILE = CLAUDE_SETTINGS_DIR / "settings.json"

    # ALLOWED hook types - ONLY these can be installed
    # PermissionRequest IS a valid Claude Code hook event (fires only for permission dialogs)
    # NOTE: PreToolUse removed - causes stdin conflict with AskUserQuestion (GitHub #13439)
    ALLOWED_HOOK_TYPES = frozenset({"Stop", "PermissionRequest"})

    # BLOCKED hook types - these MUST NEVER be installed (cause spam)
    BLOCKED_SPAM_HOOKS = frozenset({
        "SessionStart",
        "SessionEnd",
        "Notification",
        "SubagentStop",
    })

    # Hook definitions for WatchCode
    # Event types supported by the Watch app:
    # - stop (task completed)
    # - permission_request (tool needs approval) - via PermissionRequest hook
    # - question (Claude asks user a question via AskUserQuestion)
    WATCHCODE_HOOKS = {
        "Stop": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": "watchcode notify --event stop"
                    }
                ]
            }
        ],
        "PermissionRequest": [
            {
                # Send notification for permission dialogs (Bash, Write, Edit, etc.)
                # Also handles AskUserQuestion (multi-choice questions) via handle_ask_user_question()
                "hooks": [
                    {
                        "type": "command",
                        "command": "python3 ~/.watchcode/hook_handler.py permission_request"
                    }
                ]
            }
        ]
        # NOTE: PreToolUse removed - caused double notifications and stdin conflict
        # with AskUserQuestion (GitHub #13439). PermissionRequest handles questions.
    }

    def __init__(self):
        """Initialize hooks installer."""
        self.settings_dir = self.CLAUDE_SETTINGS_DIR
        self.settings_file = self.CLAUDE_SETTINGS_FILE

    def ensure_settings_dir(self) -> None:
        """Ensure Claude settings directory exists."""
        self.settings_dir.mkdir(parents=True, exist_ok=True)

    def load_settings(self) -> Dict[str, Any]:
        """Load Claude Code settings.

        Returns:
            Settings dictionary.
        """
        if not self.settings_file.exists():
            return {}

        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}

    def save_settings(self, settings: Dict[str, Any]) -> None:
        """Save Claude Code settings.

        Args:
            settings: Settings dictionary to save.
        """
        self.ensure_settings_dir()
        with open(self.settings_file, 'w') as f:
            json.dump(settings, f, indent=2)

    def get_installed_hooks(self) -> Dict[str, List]:
        """Get currently installed hooks.

        Returns:
            Dictionary of hook types to hook lists.
        """
        settings = self.load_settings()
        return settings.get("hooks", {})

    def is_watchcode_hook(self, hook: Dict[str, Any]) -> bool:
        """Check if a hook is a WatchCode hook.

        Args:
            hook: Hook configuration to check.

        Returns:
            True if this is a WatchCode hook.
        """
        if "hooks" not in hook:
            return False

        for h in hook["hooks"]:
            if h.get("type") == "command":
                command = h.get("command", "")
                # Check for both CLI commands and MacTools hook_handler
                if "watchcode notify" in command:
                    return True
                if "hook_handler.py" in command and ".watchcode" in command:
                    return True
        return False

    def install_hooks(self, hook_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Install WatchCode hooks.

        Args:
            hook_types: List of hook types to install (None = all).

        Returns:
            Dictionary with installation results.
        """
        # First, ALWAYS clean up legacy spam hooks
        self.cleanup_legacy_hooks()

        settings = self.load_settings()

        if "hooks" not in settings:
            settings["hooks"] = {}

        if hook_types is None:
            hook_types = list(self.WATCHCODE_HOOKS.keys())

        installed = []
        skipped = []
        blocked = []

        for hook_type in hook_types:
            # BLOCK spam hook types - NEVER install these
            if hook_type in self.BLOCKED_SPAM_HOOKS:
                blocked.append(hook_type)
                continue

            # Only allow whitelisted hook types
            if hook_type not in self.ALLOWED_HOOK_TYPES:
                blocked.append(hook_type)
                continue

            if hook_type not in self.WATCHCODE_HOOKS:
                skipped.append(hook_type)
                continue

            # Get existing hooks for this type
            existing_hooks = settings["hooks"].get(hook_type, [])

            # Check if WatchCode hook already exists
            has_watchcode_hook = any(
                self.is_watchcode_hook(hook) for hook in existing_hooks
            )

            if has_watchcode_hook:
                skipped.append(hook_type)
                continue

            # Add WatchCode hooks (preserving existing hooks)
            watchcode_hooks = self.WATCHCODE_HOOKS[hook_type]
            settings["hooks"][hook_type] = existing_hooks + watchcode_hooks
            installed.append(hook_type)

        self.save_settings(settings)

        return {
            "installed": installed,
            "skipped": skipped,
            "blocked": blocked,
            "total": len(hook_types)
        }

    def uninstall_hooks(self) -> Dict[str, Any]:
        """Uninstall WatchCode hooks.

        Returns:
            Dictionary with uninstallation results.
        """
        settings = self.load_settings()

        if "hooks" not in settings:
            return {"removed": [], "total": 0}

        removed = []
        empty_types = []

        for hook_type, hooks in settings["hooks"].items():
            # Filter out WatchCode hooks
            filtered_hooks = [
                hook for hook in hooks
                if not self.is_watchcode_hook(hook)
            ]

            if len(filtered_hooks) != len(hooks):
                settings["hooks"][hook_type] = filtered_hooks
                removed.append(hook_type)

            # Track empty hook types for cleanup after iteration
            if not filtered_hooks:
                empty_types.append(hook_type)

        # Clean up empty hook types (after iteration to avoid dict size change)
        for hook_type in empty_types:
            del settings["hooks"][hook_type]

        self.save_settings(settings)

        return {
            "removed": removed,
            "total": len(removed)
        }

    def get_hook_status(self) -> Dict[str, bool]:
        """Get installation status for each hook type.

        Returns:
            Dictionary mapping hook type to installation status.
        """
        settings = self.load_settings()
        hooks = settings.get("hooks", {})

        status = {}
        for hook_type in self.WATCHCODE_HOOKS.keys():
            hook_list = hooks.get(hook_type, [])
            status[hook_type] = any(
                self.is_watchcode_hook(hook) for hook in hook_list
            )

        return status

    # Legacy spam hooks that should be cleaned up
    # PreToolUse added - causes stdin conflict with AskUserQuestion (GitHub #13439)
    LEGACY_SPAM_HOOKS = {"SessionStart", "SessionEnd", "Notification", "PreToolUse"}

    def cleanup_legacy_hooks(self) -> Dict[str, Any]:
        """Remove legacy spam hooks that should never have been installed.

        These hooks cause notification spam or bugs:
        - SessionStart: fires on every session start
        - SessionEnd: fires on every session end
        - Notification: fires on random notifications
        - PreToolUse: causes stdin conflict with AskUserQuestion (GitHub #13439)

        Returns:
            Dictionary with cleanup results.
        """
        settings = self.load_settings()

        if "hooks" not in settings:
            return {"removed": [], "fixed": []}

        removed = []
        fixed = []

        # Remove entire spam hook types
        for spam_hook in self.LEGACY_SPAM_HOOKS:
            if spam_hook in settings["hooks"]:
                # Check if it's a watchcode hook before removing
                hooks_list = settings["hooks"][spam_hook]
                has_watchcode = any(self.is_watchcode_hook(h) for h in hooks_list)
                if has_watchcode:
                    # Remove only watchcode hooks, keep user's other hooks
                    filtered = [h for h in hooks_list if not self.is_watchcode_hook(h)]
                    if filtered:
                        settings["hooks"][spam_hook] = filtered
                    else:
                        del settings["hooks"][spam_hook]
                    removed.append(spam_hook)

        # NOTE: PreToolUse fix logic removed - PreToolUse is now in LEGACY_SPAM_HOOKS
        # and will be fully removed by the loop above (GitHub #13439)

        self.save_settings(settings)

        return {
            "removed": removed,
            "fixed": fixed
        }
