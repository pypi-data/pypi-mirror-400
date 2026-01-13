"""WatchCode CLI - Send Claude Code notifications to your Apple Watch."""

import sys
import json
import shutil
import time
import uuid
from pathlib import Path
import click
from typing import Optional
from importlib.metadata import version as get_version

from .config import Config
from .client import RelayClient
from .hooks import HooksInstaller


def check_for_updates() -> Optional[str]:
    """Check PyPI for newer version. Returns latest version if update available, None otherwise."""
    try:
        import httpx
    except ImportError:
        return None  # httpx not installed, skip update check

    try:
        current = get_version("watchcode-cli")
        response = httpx.get("https://pypi.org/pypi/watchcode-cli/json", timeout=2.0)
        if response.status_code == 200:
            latest = response.json()["info"]["version"]
            # Simple version comparison (works for x.y.z format)
            if latest != current:
                current_parts = [int(x) for x in current.split(".")]
                latest_parts = [int(x) for x in latest.split(".")]
                if latest_parts > current_parts:
                    return latest
    except (httpx.RequestError, httpx.HTTPStatusError, KeyError, ValueError, json.JSONDecodeError):
        pass  # Network or parsing error - don't fail CLI
    return None


def install_scripts() -> dict:
    """Install hook scripts to ~/.watchcode/ directory.

    Returns dict with 'installed' and 'updated' lists.
    """
    from importlib import resources

    result = {"installed": [], "updated": [], "errors": []}

    # Ensure ~/.watchcode exists
    watchcode_dir = Path.home() / ".watchcode"
    watchcode_dir.mkdir(exist_ok=True)

    # Scripts to install
    # NOTE: response_listener.py removed 2026-01-02 (obsolete - relay-only now)
    scripts = [
        "hook_handler.py",
        "cloudkit_poller.py",
        "apns_sender.py"
    ]

    try:
        # Python 3.9+ way
        from importlib.resources import files
        scripts_package = files("watchcode.scripts")

        for script in scripts:
            try:
                source = scripts_package.joinpath(script)
                dest = watchcode_dir / script

                # Read source content
                content = source.read_text()

                # Check if update needed
                if dest.exists():
                    existing = dest.read_text()
                    if existing == content:
                        continue  # Already up to date
                    result["updated"].append(script)
                else:
                    result["installed"].append(script)

                # Write script
                dest.write_text(content)
                dest.chmod(0o755)  # Make executable

            except Exception as e:
                result["errors"].append(f"{script}: {e}")

    except ImportError:
        # Python 3.8 fallback
        import pkg_resources

        for script in scripts:
            try:
                source_path = pkg_resources.resource_filename("watchcode.scripts", script)
                dest = watchcode_dir / script

                with open(source_path, 'r') as f:
                    content = f.read()

                if dest.exists():
                    existing = dest.read_text()
                    if existing == content:
                        continue
                    result["updated"].append(script)
                else:
                    result["installed"].append(script)

                dest.write_text(content)
                dest.chmod(0o755)

            except Exception as e:
                result["errors"].append(f"{script}: {e}")

    return result


def poll_for_response(auth_token: str, notification_id: str, relay_url: str, timeout: int = 55) -> Optional[dict]:
    """Poll relay server for Watch response.

    Args:
        auth_token: The WatchCode auth token
        notification_id: The notification ID to poll for
        relay_url: The relay server URL (from config)
        timeout: Maximum time to wait in seconds

    Returns:
        Response dict with 'action' key if found, None on timeout
    """
    import httpx

    url = f"{relay_url}/response/{auth_token}/{notification_id}"
    start_time = time.time()
    poll_count = 0

    while time.time() - start_time < timeout:
        poll_count += 1
        elapsed = time.time() - start_time

        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('found'):
                        return data.get('response', {})
        except Exception:
            pass  # Network errors, just retry

        # Show progress every 10 seconds
        if poll_count % 5 == 0:
            remaining = int(timeout - elapsed)
            click.echo(f"  Still waiting... ({remaining}s remaining)")

        time.sleep(2)  # Poll every 2 seconds

    return None


@click.group(invoke_without_command=True)
@click.version_option(package_name="watchcode-cli")
@click.pass_context
def main(ctx):
    """WatchCode CLI - Send Claude Code notifications to your Apple Watch."""
    # Check for updates (non-blocking, fails silently)
    latest = check_for_updates()
    if latest:
        current = get_version("watchcode-cli")
        click.echo(click.style(f"Update available: {current} → {latest}", fg="yellow"))
        click.echo(click.style("Run: pipx upgrade watchcode-cli", fg="yellow"))
        click.echo()

    # If no command given, show help + setup hint if not configured
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())
        click.echo()

        config = Config()
        if not config.is_configured():
            click.echo(click.style("Getting started:", fg="green", bold=True))
            click.echo("  Run: watchcode setup")
            click.echo()


def _setup_manual(config: Config) -> str:
    """Manual setup with full 12-character code entry.

    Returns:
        The validated auth token.
    """
    click.echo("To get your setup code:")
    click.echo("1. Open WatchCode on your Apple Watch")
    click.echo("2. Go to Settings")
    click.echo("3. Your setup code will be displayed (format: XXXX-XXXX-XXXX)")
    click.echo()

    # Prompt for setup code
    while True:
        setup_code = click.prompt("Enter your setup code", type=str).strip()

        # Validate format
        if config.validate_token_format(setup_code):
            break
        else:
            click.echo("Invalid setup code format. Expected: XXXX-XXXX-XXXX (12 alphanumeric characters)")

    return setup_code.replace("-", "").upper()


@main.command()
@click.option('--no-hooks', is_flag=True, help='Skip Claude Code hook installation')
def setup(no_hooks: bool):
    """Interactive setup - configure WatchCode with your setup code."""
    config = Config()
    installer = HooksInstaller()

    click.echo("WatchCode Setup")
    click.echo("=" * 50)
    click.echo()

    # FIRST: Install/update hook scripts to ~/.watchcode/
    click.echo("Installing hook scripts...")
    scripts_result = install_scripts()
    if scripts_result["installed"]:
        click.echo(f"  Installed: {', '.join(scripts_result['installed'])}")
    if scripts_result["updated"]:
        click.echo(f"  Updated: {', '.join(scripts_result['updated'])}")
    if scripts_result["errors"]:
        for err in scripts_result["errors"]:
            click.echo(f"  Error: {err}", err=True)
    if not scripts_result["installed"] and not scripts_result["updated"]:
        click.echo("  Scripts already up to date")
    click.echo()

    # Clean up legacy spam hooks
    cleanup_result = installer.cleanup_legacy_hooks()
    if cleanup_result["removed"] or cleanup_result["fixed"]:
        click.echo("Cleaning up legacy spam hooks...")
        if cleanup_result["removed"]:
            click.echo(f"  Removed: {', '.join(cleanup_result['removed'])}")
        if cleanup_result["fixed"]:
            click.echo(f"  Fixed: {', '.join(cleanup_result['fixed'])}")
        click.echo()

    # Get setup code from user
    clean_token = _setup_manual(config)

    # Save auth token
    config.set_auth_token(clean_token)

    click.echo()
    click.echo(f"Setup code saved: {config.format_token_display(clean_token)}")
    click.echo()

    # Auto-install hooks (unless --no-hooks flag is used)
    if no_hooks:
        click.echo("Skipped hook installation (--no-hooks flag).")
        click.echo("Run 'watchcode install-hooks' later to enable Claude Code integration.")
    else:
        click.echo("Installing Claude Code hooks... ", nl=False)
        result = installer.install_hooks()
        click.echo("done")

        if result["installed"]:
            click.echo(f"  Installed: {', '.join(result['installed'])}")
        if result["skipped"]:
            click.echo(f"  Already installed: {', '.join(result['skipped'])}")

    click.echo()

    # Send test notification automatically
    click.echo("Sending test notification...")
    try:
        client = RelayClient(config)
        response = client.send_test_notification()

        if response.get("success"):
            click.echo("Test notification sent! Check your Apple Watch.")
        else:
            click.echo(f"Error: {response.get('error', 'Unknown error')}")
    except Exception as e:
        click.echo(f"Error sending test notification: {str(e)}", err=True)

    click.echo()
    click.echo("Setup complete! Claude Code notifications will now be sent to your Watch.")


@main.command()
def install_hooks():
    """Install Claude Code hooks for WatchCode."""
    installer = HooksInstaller()

    # Show current status
    status = installer.get_hook_status()
    click.echo("Current hook status:")
    for hook_type, installed in status.items():
        status_text = "INSTALLED" if installed else "NOT INSTALLED"
        click.echo(f"  {hook_type}: {status_text}")

    click.echo()

    if all(status.values()):
        click.echo("All hooks are already installed.")
        return

    # Install hooks automatically
    click.echo("Installing hooks...")
    result = installer.install_hooks()

    click.echo()
    if result["installed"]:
        click.echo(f"Installed: {', '.join(result['installed'])}")
    if result["skipped"]:
        click.echo(f"Already installed: {', '.join(result['skipped'])}")

    click.echo()
    click.echo("Hooks installed successfully!")


@main.command()
def uninstall_hooks():
    """Uninstall Claude Code hooks for WatchCode."""
    installer = HooksInstaller()

    if click.confirm("Remove all WatchCode hooks?", default=False):
        result = installer.uninstall_hooks()

        if result["removed"]:
            click.echo(f"Removed hooks: {', '.join(result['removed'])}")
            click.echo("Hooks uninstalled successfully!")
        else:
            click.echo("No WatchCode hooks found.")
    else:
        click.echo("Uninstall cancelled.")


@main.command()
def fix_hooks():
    """Remove legacy spam hooks that cause notification spam.

    Removes: SessionStart, SessionEnd, Notification hooks
    Fixes: PreToolUse without matcher (should only trigger for AskUserQuestion)
    """
    installer = HooksInstaller()

    click.echo("Checking for legacy spam hooks...")

    result = installer.cleanup_legacy_hooks()

    if result["removed"]:
        click.echo(f"Removed spam hooks: {', '.join(result['removed'])}")
    if result["fixed"]:
        click.echo(f"Fixed hooks: {', '.join(result['fixed'])}")

    if not result["removed"] and not result["fixed"]:
        click.echo("No spam hooks found - your configuration is clean!")
    else:
        click.echo()
        click.echo("Done! Restart Claude Code for changes to take effect.")


@main.command()
@click.option('--no-wait', is_flag=True, help='Send notification and exit without waiting for response')
def test(no_wait: bool):
    """Send interactive test notification to your Apple Watch.

    By default, sends a test notification with Allow/Deny buttons and waits
    for your response. Use --no-wait to send a simple notification and exit.
    """
    config = Config()

    if not config.is_configured():
        click.echo("WatchCode not configured. Run 'watchcode setup' first.", err=True)
        sys.exit(1)

    try:
        client = RelayClient(config)
        auth_token = config.get_auth_token()

        if no_wait:
            # Simple one-way notification (legacy behavior)
            click.echo("Sending test notification...")
            response = client.send_test_notification()

            if response.get("success"):
                click.echo("Test notification sent successfully!")
                click.echo("Check your Apple Watch for the notification.")
            else:
                click.echo(f"Error: {response.get('error', 'Unknown error')}", err=True)
                sys.exit(1)
        else:
            # Interactive test with approval buttons
            notification_id = str(uuid.uuid4())
            click.echo("Sending test notification with approval buttons...")

            # Send as permission_request type (has Allow/Deny buttons)
            response = client.send_notification(
                event="permission_request",
                message="Test notification - tap Allow or Deny",
                session_id=f"test-{int(time.time())}",
                requires_action=True,
                notification_id=notification_id,
                metadata={"source": "watchcode-cli-test"}
            )

            if not response.get("success"):
                click.echo(f"Error: {response.get('error', 'Unknown error')}", err=True)
                sys.exit(1)

            click.echo("Test notification sent!")
            click.echo("Waiting for response (55s timeout)...")

            # Poll for response using configured relay URL
            watch_response = poll_for_response(auth_token, notification_id, config.get_relay_url(), timeout=55)

            if watch_response:
                action = watch_response.get('action', 'unknown')
                click.echo(f"Received: {action.upper()}")
                click.echo()
                click.echo("Test successful! The full approval flow is working.")
            else:
                click.echo("Timeout - no response received.")
                click.echo()
                click.echo("This could mean:")
                click.echo("  - Notification didn't arrive on Watch")
                click.echo("  - User didn't respond in time")
                click.echo("  - Response didn't make it back")
                sys.exit(1)

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--event", required=True, help="Event type (e.g., stop, permission_request)")
@click.option("--requires-action", is_flag=True, help="Notification requires user action")
@click.option("--message", "message_opt", default=None, help="Custom notification message (overrides HOOK_INPUT)")
@click.option("--notification-id", "notification_id_opt", default=None, help="Unique notification ID for response correlation")
def notify(event: str, requires_action: bool, message_opt: Optional[str], notification_id_opt: Optional[str]):
    """Send notification from Claude Code hook (reads hook data from HOOK_INPUT env or stdin)."""
    import os
    config = Config()

    if not config.is_configured():
        # Silently fail if not configured (hooks shouldn't break Claude Code)
        sys.exit(0)

    try:
        # Read hook input from HOOK_INPUT env var (Claude Code) or stdin (fallback)
        hook_data = {}
        hook_input = os.environ.get("HOOK_INPUT", "")

        if hook_input.strip():
            # Claude Code provides data via HOOK_INPUT environment variable
            try:
                hook_data = json.loads(hook_input)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON
        elif not sys.stdin.isatty():
            # Fallback to stdin for manual testing
            try:
                stdin_content = sys.stdin.read()
                if stdin_content.strip():
                    hook_data = json.loads(stdin_content)
            except json.JSONDecodeError:
                pass  # Ignore invalid JSON

        # Use CLI option if provided, otherwise use hook data
        message = message_opt if message_opt else hook_data.get("message", f"Claude Code: {event}")
        session_id = hook_data.get("session_id", "unknown")

        # Build metadata
        metadata = {
            "hook_type": event,
            "timestamp": hook_data.get("timestamp"),
        }

        # Add tool-specific metadata for pre_tool_use
        if event == "pre_tool_use":
            metadata["tool_name"] = hook_data.get("tool_name")
            metadata["tool_input"] = hook_data.get("tool_input")

        # Use CLI option if provided, otherwise use hook data
        notification_id = notification_id_opt if notification_id_opt else hook_data.get("notification_id")

        # Send notification
        client = RelayClient(config)
        response = client.send_notification(
            event=event,
            message=message,
            session_id=session_id,
            requires_action=requires_action,
            metadata=metadata,
            notification_id=notification_id
        )

        # Don't print anything on success (hooks should be silent)
        if not response.get("success"):
            # Only log errors to stderr
            click.echo(f"WatchCode error: {response.get('error')}", err=True)

    except Exception as e:
        # Log errors but don't break Claude Code
        click.echo(f"WatchCode error: {str(e)}", err=True)


@main.command()
def status():
    """Show WatchCode configuration status."""
    config = Config()
    installer = HooksInstaller()

    click.echo("WatchCode Status")
    click.echo("=" * 50)

    # Configuration status
    if config.is_configured():
        token = config.get_auth_token()
        click.echo(f"Configuration: CONFIGURED")
        click.echo(f"Setup code: {config.format_token_display(token)}")
        click.echo(f"Token storage: {config.get_storage_location()}")
        click.echo(f"Relay URL: {config.get_relay_url()}")
    else:
        click.echo("Configuration: NOT CONFIGURED")
        click.echo("Run 'watchcode setup' to configure.")

    click.echo()

    # Hook status
    hook_status = installer.get_hook_status()
    click.echo("Installed hooks:")
    for hook_type, installed in hook_status.items():
        status_icon = "✓" if installed else "✗"
        click.echo(f"  {status_icon} {hook_type}")

    if not all(hook_status.values()):
        click.echo()
        click.echo("Run 'watchcode install-hooks' to install missing hooks.")


@main.command()
@click.option("--clear", is_flag=True, help="Unregister device and clear local configuration")
@click.option("--verify", is_flag=True, help="Verify device registration on relay server")
@click.option("--yes", "-y", is_flag=True, help="Skip confirmation prompt for --clear")
def devices(clear: bool, verify: bool, yes: bool):
    """Manage device registration.

    Shows current device configuration by default.
    Use --clear to unregister and remove local config.
    Use --verify to check if device is registered on relay server.
    """
    config = Config()

    if not config.is_configured():
        click.echo("WatchCode not configured. Run 'watchcode setup' first.", err=True)
        sys.exit(1)

    token = config.get_auth_token()

    if verify:
        # Check if token is valid on relay
        click.echo(f"Verifying device {config.format_token_display(token)}...")
        client = RelayClient(config)
        is_valid = client.verify_device()
        if is_valid:
            click.echo(f"Device is registered and active on relay server.")
        else:
            click.echo(f"Device is NOT registered on relay server.", err=True)
            click.echo("Run 'watchcode setup' to re-register.")
            sys.exit(1)
        return

    if clear:
        if not yes:
            click.echo(f"This will unregister device {config.format_token_display(token)} and clear local config.")
            if not click.confirm("Continue?"):
                click.echo("Cancelled.")
                return

        # Unregister from relay
        click.echo("Unregistering from relay server...", nl=False)
        client = RelayClient(config)
        try:
            client.unregister_device()
            click.echo(" Done")
        except Exception as e:
            click.echo(f" Warning: {e}", err=True)
            click.echo("  (Continuing with local cleanup)")

        # Clear local config
        click.echo("Clearing local configuration...", nl=False)
        config.delete_auth_token()
        click.echo(" Done")

        click.echo()
        click.echo("Device cleared. Run 'watchcode setup' to configure a new device.")
        return

    # Default: show device info
    click.echo("Device Configuration")
    click.echo("=" * 50)
    click.echo(f"Setup code: {config.format_token_display(token)}")
    click.echo(f"Storage: {config.get_storage_location()}")
    click.echo(f"Relay: {config.get_relay_url()}")
    click.echo()
    click.echo("Use --verify to check relay registration status.")
    click.echo("Use --clear to unregister and remove configuration.")


@main.command("update-scripts")
def update_scripts():
    """Update hook scripts in ~/.watchcode/ to latest version."""
    click.echo("Updating hook scripts...")
    result = install_scripts()

    if result["installed"]:
        click.echo(f"Installed: {', '.join(result['installed'])}")
    if result["updated"]:
        click.echo(f"Updated: {', '.join(result['updated'])}")
    if result["errors"]:
        for err in result["errors"]:
            click.echo(f"Error: {err}", err=True)

    if not result["installed"] and not result["updated"] and not result["errors"]:
        click.echo("All scripts already up to date.")
    else:
        click.echo("Done!")


if __name__ == "__main__":
    main()
