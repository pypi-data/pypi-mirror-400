#!/usr/bin/env python3
"""
Centralized hook handler for WatchCode Claude Code hooks.

Security hardened:
- Safe JSON parsing
- Path validation with realpath
- No shell=True in subprocess
- Input size limits
- Sanitized environment

Usage:
    export HOOK_INPUT='{"session_id": "...", ...}'
    python3 hook_handler.py <hook_type>

Hook types: stop, notification, session_start, session_end, subagent_stop, permission_request
"""

import json
import os
import sys
import subprocess
import logging
import time
import uuid
import atexit
from pathlib import Path
from datetime import datetime
from typing import Optional

# LATENCY OPTIMIZATION: Use httpx with HTTP/2 for relay polling
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# E2E encryption support
try:
    from watchcode.crypto import CryptoManager, is_encrypted
    CRYPTO_AVAILABLE = True
    _crypto_manager: Optional[CryptoManager] = None

    def _get_crypto_manager() -> CryptoManager:
        """Get or create crypto manager instance."""
        global _crypto_manager
        if _crypto_manager is None:
            _crypto_manager = CryptoManager()
        return _crypto_manager
except ImportError:
    CRYPTO_AVAILABLE = False
    is_encrypted = lambda x: False  # noqa: E731
    def _get_crypto_manager():
        return None

# Module-level HTTP client for connection reuse
_relay_client: Optional['httpx.Client'] = None


def _get_relay_client() -> 'httpx.Client':
    """Get or create shared HTTP client for relay polling."""
    global _relay_client
    if _relay_client is None and HTTPX_AVAILABLE:
        _relay_client = httpx.Client(
            timeout=5.0,
            http2=True,
            limits=httpx.Limits(keepalive_expiry=60.0)
        )
        atexit.register(_cleanup_relay_client)
    return _relay_client


def _cleanup_relay_client():
    """Clean up HTTP client on exit."""
    global _relay_client
    if _relay_client is not None:
        try:
            _relay_client.close()
        except Exception:
            pass
        _relay_client = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Security constants
MAX_INPUT_SIZE = 1024 * 1024  # 1MB
ALLOWED_HOOKS = {'stop', 'notification', 'notification_debug', 'session_start', 'session_end', 'subagent_stop', 'permission_request', 'pre_tool_use'}
APNS_SENDER = Path.home() / ".watchcode" / "apns_sender.py"
DEBUG_LOG = Path.home() / ".watchcode" / "hook_debug.log"
# NOTE: CloudKit/iCloud paths removed 2026-01-02 (security: relay-only now)

# Response polling configuration
DEFAULT_PERMISSION_TIMEOUT = 55  # seconds to wait for Watch response

# Relay server configuration
RELAY_URL = "https://relay.vgbndg.net"
AUTH_TOKEN_FILE = Path.home() / ".watchcode" / "auth_token.txt"
CLAUDE_SETTINGS_FILE = Path.home() / ".claude" / "settings.json"

# Keyboard injection configuration
KEYBOARD_INJECTION_ENABLED = True  # Can be disabled via config if needed


# ============================================================================
# KEYBOARD INJECTION FUNCTIONS
# Injects text into terminal via clipboard + paste (osascript)
# Requires: System Settings > Privacy & Security > Accessibility permission
# ============================================================================

def type_text(text: str) -> bool:
    """Type text into the focused application via clipboard paste.

    Uses pbcopy to set clipboard, then osascript to simulate Cmd+V.
    This method handles ALL special characters, unicode, and emoji.

    Requires Accessibility permission for the terminal app.
    Returns True on success, False on failure (silent - check permissions).
    """
    if not KEYBOARD_INJECTION_ENABLED:
        log_debug("Keyboard injection disabled")
        return False

    try:
        # Copy text to clipboard
        proc = subprocess.run(
            ['pbcopy'],
            input=text.encode('utf-8'),
            check=True,
            timeout=5
        )

        # Simulate Cmd+V to paste
        script = 'tell application "System Events" to keystroke "v" using command down'
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            log_debug(f"✓ Typed text via clipboard: {text[:50]}...")
            return True
        else:
            log_debug(f"⚠️ osascript failed: {result.stderr.decode()[:100]}")
            return False

    except subprocess.TimeoutExpired:
        log_debug("⚠️ Keyboard injection timed out")
        return False
    except Exception as e:
        log_debug(f"⚠️ Keyboard injection error: {e}")
        return False


def press_enter() -> bool:
    """Press Enter key to submit the typed text.

    Uses osascript key code 36 (Return key).
    Requires Accessibility permission.
    """
    if not KEYBOARD_INJECTION_ENABLED:
        return False

    try:
        script = 'tell application "System Events" to key code 36'
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            log_debug("✓ Pressed Enter key")
            return True
        else:
            log_debug(f"⚠️ Enter key failed: {result.stderr.decode()[:100]}")
            return False

    except Exception as e:
        log_debug(f"⚠️ Enter key error: {e}")
        return False


# ============================================================================
# VOICE INPUT NAVIGATION FUNCTIONS
# Maps voice text to option numbers and navigates using arrow keys
# ============================================================================

def match_voice_to_option(voice_text: str, options: list) -> int:
    """Return 1-indexed option number that best matches voice input.

    Handles various voice input patterns:
    - Direct numbers: "1", "2", "3"
    - Number words: "one", "two", "first", "second"
    - Option labels: "Allow", "Deny", "Hello World"
    - Partial matches: "hello" matches "Hello World"

    Args:
        voice_text: The text spoken by user (e.g., "Allow", "two", "Hello")
        options: List of option dicts with 'label' keys

    Returns:
        1-indexed option number (1 if no match found)
    """
    voice_lower = voice_text.lower().strip()

    # Direct number
    if voice_lower.isdigit():
        num = int(voice_lower)
        if 1 <= num <= len(options):
            return num
        return 1  # Out of range, default to 1

    # Number words
    number_words = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
        "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
        "1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5
    }
    if voice_lower in number_words:
        num = number_words[voice_lower]
        if 1 <= num <= len(options):
            return num
        return 1

    # Extract option labels
    option_labels = [opt.get('label', '') for opt in options]

    # Exact match (case-insensitive)
    for i, label in enumerate(option_labels, 1):
        if voice_lower == label.lower():
            return i

    # Voice contains label (e.g., "option allow" matches "Allow")
    for i, label in enumerate(option_labels, 1):
        if label.lower() in voice_lower:
            return i

    # Label contains voice (e.g., "hello" matches "Hello World")
    for i, label in enumerate(option_labels, 1):
        if voice_lower in label.lower():
            return i

    # No match - default to first option
    log_debug(f"No match for voice '{voice_text}', defaulting to option 1")
    return 1


def navigate_to_option(option_num: int) -> bool:
    """Navigate to option using arrow keys.

    Claude Code's terminal prompt starts at option 1 (highlighted).
    Press Down arrow (option_num - 1) times to reach option N.
    Press Enter to select.

    Uses osascript:
    - key code 125 = Down arrow
    - key code 36 = Enter/Return

    Args:
        option_num: 1-indexed option number to select

    Returns:
        True if navigation succeeded, False on error.
    """
    if not KEYBOARD_INJECTION_ENABLED:
        log_debug("Keyboard injection disabled, cannot navigate")
        return False

    log_debug(f"Navigating to option {option_num} via arrow keys")

    try:
        # Press Down arrow (option_num - 1) times
        for i in range(option_num - 1):
            script = 'tell application "System Events" to key code 125'
            result = subprocess.run(
                ['osascript', '-e', script],
                capture_output=True,
                timeout=5
            )
            if result.returncode != 0:
                log_debug(f"⚠️ Down arrow failed at step {i+1}: {result.stderr.decode()[:100]}")
                return False
            time.sleep(0.05)  # Small delay between keypresses

        # Press Enter to select
        script = 'tell application "System Events" to key code 36'
        result = subprocess.run(
            ['osascript', '-e', script],
            capture_output=True,
            timeout=5
        )

        if result.returncode == 0:
            log_debug(f"✓ Selected option {option_num} via arrow navigation")
            return True
        else:
            log_debug(f"⚠️ Enter key failed: {result.stderr.decode()[:100]}")
            return False

    except Exception as e:
        log_debug(f"⚠️ Arrow navigation error: {e}")
        return False


def inject_voice_response(voice_text: str, options: list) -> bool:
    """Inject voice response by navigating to matching option.

    This is the main function for handling voice input from Watch.
    Maps the voice text to an option number and uses arrow key navigation.

    Args:
        voice_text: The spoken text from Watch (e.g., "Allow", "two")
        options: List of option dicts with 'label' keys

    Returns:
        True if injection succeeded, False on error.
    """
    if not voice_text or not options:
        log_debug("⚠️ Missing voice_text or options for voice navigation")
        return False

    # Match voice to option number
    option_num = match_voice_to_option(voice_text, options)
    log_debug(f"Voice '{voice_text}' matched to option {option_num}")

    # Small delay before navigation to ensure terminal is ready
    time.sleep(0.1)

    # Navigate using arrow keys
    return navigate_to_option(option_num)


def type_and_submit(text: str) -> bool:
    """Type text and press Enter to submit.

    This is the main function for injecting Watch answers into the terminal.
    The text will appear in the terminal and be submitted automatically.
    """
    if not text:
        log_debug("⚠️ Empty text, nothing to type")
        return False

    # Small delay before typing to ensure terminal is ready
    time.sleep(0.1)

    if type_text(text):
        # Small delay between paste and Enter for reliability
        time.sleep(0.1)
        return press_enter()

    return False


def inject_keystroke(text: str) -> bool:
    """Inject text into Terminal.app via detached subprocess.

    Uses a completely detached process (start_new_session=True) that runs AFTER
    the hook exits. This bypasses the WindowServer access issue that prevents
    osascript from working in hook subprocess context.

    Targets Terminal.app specifically and uses base64 encoding to handle
    special characters safely.

    Args:
        text: The text to type (can be any string including special chars)

    Returns:
        True if the detached process was launched, False on error.
    """
    if not KEYBOARD_INJECTION_ENABLED:
        log_debug("Keyboard injection disabled")
        return False

    log_debug(f"Scheduling keystroke injection: '{text}'")

    try:
        import base64
        # Base64 encode the text to safely pass through bash
        encoded_text = base64.b64encode(text.encode('utf-8')).decode('ascii')

        # Build the bash script that runs AFTER this hook exits
        # Uses base64 decoding for safe text handling
        # Targets Terminal.app specifically for reliable focus
        script = f'''
sleep 0.3
echo "{encoded_text}" | base64 -d | pbcopy
osascript <<'APPLESCRIPT'
tell application "Terminal"
    activate
    delay 0.15
    tell application "System Events"
        keystroke "v" using command down
        delay 0.1
        key code 36
    end tell
end tell
APPLESCRIPT
'''

        # Launch completely detached subprocess
        # start_new_session=True creates new process group, detached from hook
        subprocess.Popen(
            ['bash', '-c', script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

        log_debug(f"✓ Launched detached keystroke injector for '{text}'")
        return True

    except Exception as e:
        log_debug(f"⚠️ Failed to launch keystroke injector: {e}")
        return False


def launch_background_responder(
    auth_token: str,
    notification_id: str,
    options: list,
    timeout: int = 55
) -> bool:
    """Launch a background process to poll for Watch response and inject keystroke.

    This allows the hook to return immediately while the background process
    handles polling and keystroke injection.

    Args:
        auth_token: The WatchCode auth token
        notification_id: The notification ID to poll for
        options: List of option dicts with 'label' keys (for mapping to numbers)
        timeout: How long to poll before giving up

    Returns:
        True if background process launched, False on error.
    """
    if not KEYBOARD_INJECTION_ENABLED:
        log_debug("Keyboard injection disabled, not launching responder")
        return False

    # Build option labels for the bash script to map
    option_labels = [opt.get('label', '') for opt in options]
    labels_json = json.dumps(option_labels)

    log_debug(f"Launching background responder for notification {notification_id[:8]}...")

    try:
        # Python script to run in background - polls relay and uses arrow navigation
        python_script = f'''
import urllib.request
import json
import subprocess
import time

AUTH_TOKEN = "{auth_token}"
NOTIFICATION_ID = "{notification_id}"
OPTION_LABELS = {labels_json}
RELAY_URL = "https://relay.vgbndg.net"
TIMEOUT = {timeout}

# Number words for voice input matching
NUMBER_WORDS = {{
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5,
    "1st": 1, "2nd": 2, "3rd": 3, "4th": 4, "5th": 5
}}

def poll_response():
    url = f"{{RELAY_URL}}/response/{{AUTH_TOKEN}}/{{NOTIFICATION_ID}}"
    try:
        req = urllib.request.Request(url, method='GET')
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                if data.get('found'):
                    return data.get('response', {{}})
    except:
        pass
    return None

def match_voice_to_option(voice_text):
    """Match voice text to 1-indexed option number."""
    voice_lower = voice_text.lower().strip()

    # Direct number
    if voice_lower.isdigit():
        num = int(voice_lower)
        if 1 <= num <= len(OPTION_LABELS):
            return num
        return 1

    # Number words
    if voice_lower in NUMBER_WORDS:
        num = NUMBER_WORDS[voice_lower]
        if 1 <= num <= len(OPTION_LABELS):
            return num
        return 1

    # Exact match (case-insensitive)
    for i, label in enumerate(OPTION_LABELS, 1):
        if voice_lower == label.lower():
            return i

    # Partial matches
    for i, label in enumerate(OPTION_LABELS, 1):
        if label.lower() in voice_lower or voice_lower in label.lower():
            return i

    return 1  # Default to first option

def navigate_to_option(option_num):
    """Navigate using arrow keys: Down arrow (N-1) times, then Enter."""
    time.sleep(0.1)

    # Press Down arrow (option_num - 1) times
    for _ in range(option_num - 1):
        subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 125'], capture_output=True)
        time.sleep(0.05)

    # Press Enter to select
    subprocess.run(['osascript', '-e', 'tell application "System Events" to key code 36'], capture_output=True)

# Poll for response
start = time.time()
while time.time() - start < TIMEOUT:
    response = poll_response()
    if response:
        action = response.get('action', '').lower()
        if action == 'selectoption':
            selected = response.get('selected_options', [])
            message = response.get('message', '')
            if selected:
                label = selected[0]
                # Handle custom/voice input (Watch sends "__custom__" with message)
                if label == '__custom__' and message:
                    # Map voice text to option and navigate
                    option_num = match_voice_to_option(message)
                    navigate_to_option(option_num)
                else:
                    # Find index of selected label and navigate
                    for idx, opt_label in enumerate(OPTION_LABELS, 1):
                        if opt_label == label:
                            navigate_to_option(idx)
                            break
        break
    time.sleep(1.5)
'''

        # Launch as completely detached Python process
        subprocess.Popen(
            ['python3', '-c', python_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

        log_debug(f"✓ Launched background responder")
        return True

    except Exception as e:
        log_debug(f"⚠️ Failed to launch background responder: {e}")
        return False


def load_allowed_patterns() -> list:
    """Load auto-allowed tool patterns from Claude settings."""
    try:
        if not CLAUDE_SETTINGS_FILE.exists():
            return []
        with open(CLAUDE_SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
        return settings.get('permissions', {}).get('allow', [])
    except Exception as e:
        log_debug(f"Failed to load allowed patterns: {e}")
        return []


def is_auto_allowed(tool_name: str, tool_input: dict) -> bool:
    """Check if a tool call is auto-allowed (no permission needed).

    Parses patterns like:
    - Bash(curl -s:*) - Bash commands starting with "curl -s"
    - Write(path:/tmp/*) - Write to files under /tmp
    - Edit(path:*.py) - Edit Python files

    Returns True if auto-allowed (skip notification), False if permission needed.
    """
    import fnmatch

    patterns = load_allowed_patterns()
    if not patterns:
        return False  # No patterns = nothing auto-allowed

    for pattern in patterns:
        # Parse pattern format: Tool(arg:value)
        if not pattern.startswith(tool_name + '('):
            continue

        # Extract the inner part: e.g., "curl -s:*" from "Bash(curl -s:*)"
        inner = pattern[len(tool_name)+1:-1] if pattern.endswith(')') else ''
        if not inner:
            continue

        if tool_name == 'Bash':
            command = tool_input.get('command', '')
            # Pattern format: "command_prefix:*" or just the command
            if ':' in inner:
                prefix = inner.split(':')[0]
                # Check if command starts with prefix
                if command.startswith(prefix):
                    log_debug(f"Auto-allowed: Bash command matches '{prefix}:*'")
                    return True
            else:
                # Exact match or fnmatch
                if fnmatch.fnmatch(command, inner):
                    log_debug(f"Auto-allowed: Bash command matches '{inner}'")
                    return True

        elif tool_name in ('Write', 'Edit'):
            file_path = tool_input.get('file_path', '')
            if file_path and fnmatch.fnmatch(file_path, inner):
                log_debug(f"Auto-allowed: {tool_name} path matches '{inner}'")
                return True

    return False


def log_debug(msg: str) -> None:
    """Append debug message to log file."""
    try:
        with open(DEBUG_LOG, 'a') as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def validate_path(path: str, allowed_base: Path | None = None) -> Path | None:
    """Validate and resolve a path, preventing traversal attacks."""
    if not path:
        return None

    try:
        resolved = Path(path).expanduser().resolve()

        # If allowed_base specified, ensure path is under it
        if allowed_base:
            allowed_resolved = allowed_base.resolve()
            if not str(resolved).startswith(str(allowed_resolved)):
                logger.warning(f"Path traversal blocked: {path}")
                return None

        return resolved
    except Exception as e:
        logger.warning(f"Path validation failed: {e}")
        return None


def parse_input() -> dict:
    """Parse JSON input from stdin (Claude Code) or HOOK_INPUT env (manual testing)."""
    input_data = None
    source = "unknown"

    # First try stdin (Claude Code sends data via stdin for hooks)
    if not sys.stdin.isatty():
        try:
            stdin_content = sys.stdin.read()
            if stdin_content.strip():
                input_data = stdin_content
                source = "stdin"
        except Exception as e:
            log_debug(f"Failed to read stdin: {e}")

    # Fallback to HOOK_INPUT env var (for manual testing)
    if not input_data:
        input_data = os.environ.get('HOOK_INPUT', '{}')
        source = "HOOK_INPUT" if input_data != '{}' else "default"

    # ALWAYS log raw input for debugging
    log_debug(f"=== RAW INPUT (source: {source}) ===")
    log_debug(f"Length: {len(input_data)}")
    log_debug(f"Content: {input_data[:1000]}")

    # Size limit
    if len(input_data) > MAX_INPUT_SIZE:
        raise ValueError(f"Input too large: {len(input_data)} bytes (max {MAX_INPUT_SIZE})")

    try:
        return json.loads(input_data)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON input: {e}")


def extract_transcript_data(transcript_path: str) -> tuple[str, str]:
    """Extract the task request and assistant response from transcript.

    Finds the most likely "task request" - a substantial user message that
    triggered the work, not just follow-ups like "yes do it".

    Returns: (user_prompt, full_response)
    """
    user_prompt = ''
    full_response = ''

    validated_path = validate_path(transcript_path)
    if not validated_path or not validated_path.exists():
        log_debug(f"Transcript not found: {transcript_path}")
        return user_prompt, full_response

    try:
        with open(validated_path, 'r') as f:
            lines = f.readlines()

        # Collect all user messages and assistant responses
        user_messages = []
        last_assistant_msg = ''

        for line in lines:
            try:
                entry = json.loads(line.strip())
                entry_type = entry.get('type', '')

                if entry_type == 'user':
                    msg = entry.get('message', {})
                    if isinstance(msg, dict):
                        content = msg.get('content', [])
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text = block.get('text', '').strip()
                                if text and not text.startswith('[Request interrupted'):
                                    user_messages.append(text)

                elif entry_type == 'assistant':
                    msg = entry.get('message', {})
                    if isinstance(msg, dict):
                        content = msg.get('content', [])
                        texts = []
                        for block in content:
                            if isinstance(block, dict) and block.get('type') == 'text':
                                text = block.get('text', '').strip()
                                if text:
                                    texts.append(text)
                        if texts:
                            last_assistant_msg = '\n'.join(texts)
            except json.JSONDecodeError:
                continue

        # Find the most likely "task request" - look for substantial user messages
        # Short messages like "yes", "do it", "sounds good" are follow-ups, not requests
        SHORT_FOLLOWUP_PATTERNS = [
            'yes', 'no', 'ok', 'okay', 'do it', 'go ahead', 'sounds good',
            'perfect', 'great', 'thanks', 'thank you', 'sure', 'yep', 'nope',
            'continue', 'proceed', 'looks good', 'lgtm', 'approved'
        ]

        task_request = ''
        # Search from most recent to oldest for a substantial message
        for msg in reversed(user_messages):
            msg_lower = msg.lower().strip()
            # Skip very short messages
            if len(msg) < 20:
                # Check if it's just a short confirmation
                if any(msg_lower.startswith(p) or msg_lower == p for p in SHORT_FOLLOWUP_PATTERNS):
                    continue
            # Skip messages that are complaints/feedback about the current work
            if 'don\'t see' in msg_lower or 'didn\'t work' in msg_lower or 'still' in msg_lower:
                continue
            # Found a substantial message - this is likely the task request
            task_request = msg
            break

        # If no substantial message found, use the last one
        if not task_request and user_messages:
            task_request = user_messages[-1]

        user_prompt = task_request
        full_response = last_assistant_msg

    except Exception as e:
        log_debug(f"Transcript parsing error: {e}")

    return user_prompt, full_response


def send_notification(
    event: str,
    message: str,
    session_id: str,
    project_name: str = '',
    full_response: str = '',
    user_prompt: str = '',
    requires_action: bool = False,
    notification_id: str = ''
) -> int:
    """Send notification via watchcode CLI (uses relay server)."""

    # DEBUG: Log the notification_id being sent
    # This is crucial for tracing response matching issues
    if notification_id:
        log_debug(f"[Send Notification] notification_id={notification_id}")
        log_debug(f"[Send Notification] event={event}, requires_action={requires_action}")

    # Build command using watchcode CLI
    cmd = ['watchcode', 'notify', '--event', event]

    if message:
        cmd.extend(['--message', message[:500]])

    if requires_action:
        cmd.append('--requires-action')

    if notification_id:
        cmd.extend(['--notification-id', notification_id])

    try:
        # Build safe environment
        safe_env = os.environ.copy()
        for var in ['LD_PRELOAD', 'LD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES',
                    'BASH_ENV', 'CDPATH', 'ENV']:
            safe_env.pop(var, None)
        # Include common paths where watchcode might be installed
        safe_env['PATH'] = '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:' + \
                          str(Path.home() / '.local' / 'bin') + ':' + \
                          '/Library/Frameworks/Python.framework/Versions/3.12/bin'

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            env=safe_env
        )

        log_debug(f"watchcode notify exit code: {result.returncode}")
        if result.stdout:
            log_debug(f"stdout: {result.stdout}")
        if result.stderr:
            log_debug(f"stderr: {result.stderr}")

        return result.returncode

    except subprocess.TimeoutExpired:
        logger.error("watchcode notify timed out after 30s")
        return 1
    except FileNotFoundError:
        logger.error("watchcode CLI not found in PATH")
        return 1
    except Exception as e:
        logger.error(f"Failed to run watchcode notify: {e}")
        return 1


def handle_stop(data: dict) -> int:
    """Handle 'stop' hook - task completion."""
    session_id = data.get('session_id', 'claude')
    transcript_path = data.get('transcript_path', '')
    cwd = data.get('cwd', '')
    project_name = Path(cwd).name if cwd else ''

    log_debug(f"Stop hook: session={session_id}, project={project_name}")

    # Extract transcript data
    user_prompt, full_response = extract_transcript_data(transcript_path)

    # Create summary
    if full_response:
        summary = full_response[:200]
        if len(full_response) > 200:
            summary += '...'
    else:
        summary = 'Task completed'

    log_debug(f"user_prompt: {user_prompt[:100] if user_prompt else 'EMPTY'}")
    log_debug(f"full_response: {full_response[:100] if full_response else 'EMPTY'}")

    return send_notification(
        event='stop',
        message=summary,
        session_id=session_id,
        project_name=project_name,
        full_response=full_response,
        user_prompt=user_prompt
    )


def handle_notification(data: dict) -> int:
    """Handle 'notification' hook - fires when Claude awaits user input.

    This includes permission dialogs. We send notification and wait for response.
    """
    message = data.get('message', 'Notification')
    session_id = data.get('session_id', 'unknown')
    cwd = data.get('cwd', '')
    project_name = Path(cwd).name if cwd else ''

    # Generate unique notification ID
    notification_id = str(uuid.uuid4())
    sequence_id = generate_sequence_id()

    log_debug(f"[seq={sequence_id}] Notification hook: {message[:50]}...")

    # Send notification with requires_action since we're awaiting input
    send_result = send_notification(
        event='permission_request',
        message=message[:200] if message else 'Claude needs your input',
        session_id=session_id,
        project_name=project_name,
        requires_action=True,
        notification_id=notification_id
    )

    if send_result != 0:
        log_debug(f"[seq={sequence_id}] Failed to send notification")
        return 0  # Don't block, let terminal handle it

    # Wait for Watch response via relay server
    log_debug(f"[seq={sequence_id}] Waiting for Watch response...")
    response = wait_for_response(
        sequence_id=sequence_id,
        timeout=DEFAULT_PERMISSION_TIMEOUT,
        notification_id=notification_id
    )

    # Output decision via JSON only (no keystroke injection for permission_request)
    # Claude Code reads hookSpecificOutput JSON - keystroke injection caused double input
    if response:
        action = response.get('action', '').lower()
        if action == 'approve':
            output_decision('allow')
            log_debug(f"[seq={sequence_id}] User APPROVED via Watch")
        elif action == 'deny':
            output_decision('deny', 'Denied via Apple Watch')
            log_debug(f"[seq={sequence_id}] User DENIED via Watch")
        elif action == 'always_allow':
            output_decision('allow')  # JSON doesn't have "always allow" option
            log_debug(f"[seq={sequence_id}] User set ALWAYS ALLOW via Watch")
        else:
            log_debug(f"[seq={sequence_id}] Unknown action '{action}', no decision output")
            # Send invalidation - unknown action
            send_invalidation(notification_id, 'unknown_action')
    else:
        log_debug(f"[seq={sequence_id}] No response, falling back to terminal")
        # Send invalidation so Watch knows user will respond via terminal
        send_invalidation(notification_id, 'terminal_fallback')

    return 0


def handle_session_start(data: dict) -> int:
    """Handle 'session_start' hook."""
    session_id = data.get('session_id', 'unknown')
    cwd = data.get('cwd', '')
    project_name = Path(cwd).name if cwd else 'Unknown Project'

    return send_notification(
        event='session_start',
        message=f'Session started: {project_name}',
        session_id=session_id,
        project_name=project_name
    )


def handle_session_end(data: dict) -> int:
    """Handle 'session_end' hook."""
    session_id = data.get('session_id', 'unknown')
    cwd = data.get('cwd', '')
    project_name = Path(cwd).name if cwd else ''

    return send_notification(
        event='session_end',
        message='Session ended',
        session_id=session_id,
        project_name=project_name
    )


def handle_subagent_stop(data: dict) -> int:
    """Handle 'subagent_stop' hook - subagent (Task tool) completion."""
    session_id = data.get('session_id', 'unknown')
    cwd = data.get('cwd', '')
    project_name = Path(cwd).name if cwd else 'Unknown'

    log_debug(f"SubagentStop hook: session={session_id}, project={project_name}")

    return send_notification(
        event='notification',
        message=f'Subagent completed in {project_name}',
        session_id=session_id,
        project_name=project_name
    )


def generate_sequence_id() -> int:
    """Generate a unique sequence ID for correlation tracking."""
    return int(time.time() * 1000) % 1000000  # 6-digit millisecond-based ID


def get_auth_token() -> str | None:
    """Read auth token from Keychain or file."""
    # Try Keychain first - use same service name as CLI (com.watchcode.cli)
    try:
        result = subprocess.run(
            ['security', 'find-generic-password', '-s', 'com.watchcode.cli', '-a', 'auth_token', '-w'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    # Fallback to file
    try:
        if AUTH_TOKEN_FILE.exists():
            return AUTH_TOKEN_FILE.read_text().strip()
    except Exception:
        pass

    return None


def decrypt_response(response_data: dict, auth_token: str) -> dict:
    """Decrypt an E2E encrypted response from Watch.

    If response is encrypted (has v, nonce, ciphertext), decrypts it.
    If plaintext, returns as-is for backward compatibility.

    Args:
        response_data: Response dict from relay server
        auth_token: Auth token for decryption

    Returns:
        Decrypted response dict
    """
    if not CRYPTO_AVAILABLE:
        log_debug("[Crypto] cryptography module not available, returning plaintext")
        return response_data

    # Check if response is encrypted
    if not is_encrypted(response_data):
        log_debug("[Crypto] Response is plaintext (not encrypted)")
        return response_data

    try:
        crypto = _get_crypto_manager()
        decrypted = crypto.decrypt(response_data, auth_token)
        log_debug(f"✓ [Crypto] Decrypted E2E response: action={decrypted.get('action')}")
        return decrypted
    except Exception as e:
        log_debug(f"⚠️ [Crypto] Decryption failed: {e}, returning raw response")
        # Return raw response - might be partially usable or a format issue
        return response_data


def check_relay_response(notification_id: str) -> dict | None:
    """Check relay server for Watch response.

    The Watch sends responses to POST /respond on the relay.
    The Mac polls GET /response/:auth_token/:notification_id to get them.
    Responses may be E2E encrypted - decryption is handled automatically.

    Returns response dict if found, None otherwise.
    """
    auth_token = get_auth_token()
    if not auth_token:
        log_debug("No auth token found for relay polling")
        return None

    if not notification_id:
        log_debug("No notification_id for relay polling")
        return None

    # DEBUG: Log the exact notification_id being polled
    # This helps trace mismatches between Mac and Watch
    log_debug(f"[Relay Poll] notification_id={notification_id}")
    log_debug(f"[Relay Poll] auth_token={auth_token[:8]}...")

    url = f"{RELAY_URL}/response/{auth_token}/{notification_id}"

    try:
        # LATENCY OPTIMIZATION: Use httpx with HTTP/2 if available
        if HTTPX_AVAILABLE:
            client = _get_relay_client()
            resp = client.get(url, headers={'Accept': 'application/json'})
            if resp.status_code == 200:
                data = resp.json()
                log_debug(f"[Relay Poll] Response: found={data.get('found')}")
                if data.get('found'):
                    response_data = data.get('response', {})

                    # Decrypt if encrypted (E2E encryption)
                    response_data = decrypt_response(response_data, auth_token)

                    action = response_data.get('action')
                    if action:
                        selected_opts = response_data.get('selected_options', [])
                        stored_notif_id = response_data.get('notification_id', 'unknown')
                        log_debug(f"✓ Relay response found: action={action}, selected={selected_opts}")
                        log_debug(f"  stored_notification_id={stored_notif_id}")
                        return response_data
                else:
                    log_debug(f"[Relay Poll] No response stored for this notification_id")
            elif resp.status_code != 404:
                log_debug(f"Relay HTTP error: {resp.status_code}")
        else:
            # Fallback to urllib if httpx not available
            import urllib.request
            import urllib.error

            req = urllib.request.Request(url, method='GET')
            req.add_header('Accept', 'application/json')

            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    log_debug(f"[Relay Poll] Response: found={data.get('found')}")
                    if data.get('found'):
                        response_data = data.get('response', {})

                        # Decrypt if encrypted (E2E encryption)
                        response_data = decrypt_response(response_data, auth_token)

                        action = response_data.get('action')
                        if action:
                            selected_opts = response_data.get('selected_options', [])
                            stored_notif_id = response_data.get('notification_id', 'unknown')
                            log_debug(f"✓ Relay response found: action={action}, selected={selected_opts}")
                            log_debug(f"  stored_notification_id={stored_notif_id}")
                            return response_data
                    else:
                        log_debug(f"[Relay Poll] No response stored for this notification_id")
    except Exception as e:
        log_debug(f"Relay poll error: {e}")

    return None


def send_invalidation(notification_id: str, reason: str = 'terminal_response') -> bool:
    """Send invalidation to relay server to dismiss Watch notification.

    Called when user responds via terminal instead of Watch.
    This sends a silent push to Watch to mark the request as handled.

    Args:
        notification_id: The notification ID to invalidate
        reason: Reason for invalidation (default: 'terminal_response')

    Returns:
        True if successful, False otherwise.
    """
    auth_token = get_auth_token()
    if not auth_token:
        log_debug("No auth token found for invalidation")
        return False

    if not notification_id:
        log_debug("No notification_id for invalidation")
        return False

    url = f"{RELAY_URL}/invalidate"
    payload = {
        'auth_token': auth_token,
        'notification_id': notification_id,
        'reason': reason
    }

    try:
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, method='POST')
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                log_debug(f"✓ Invalidation sent for {notification_id[:8]}...")
                return True
            else:
                log_debug(f"Invalidation failed: status {resp.status}")
                return False
    except urllib.error.HTTPError as e:
        log_debug(f"Invalidation HTTP error: {e.code}")
        return False
    except Exception as e:
        log_debug(f"Invalidation error: {e}")
        return False


def wait_for_response(
    sequence_id: int,
    timeout: int = DEFAULT_PERMISSION_TIMEOUT,
    notification_id: str = ''
) -> dict | None:
    """Poll relay server for Watch response.

    RELAY-ONLY: CloudKit/iCloud polling removed 2026-01-02 (security fix).

    Args:
        sequence_id: Unique sequence for this request (for correlation)
        timeout: Total timeout in seconds
        notification_id: Unique notification ID for relay lookup

    Returns:
        Response dict if received, None on timeout
    """
    start_time = time.time()
    poll_count = 0

    log_debug(f"[seq={sequence_id}] Starting response wait (timeout={timeout}s, notification_id={notification_id[:8] if notification_id else 'none'}...)")

    while time.time() - start_time < timeout:
        poll_count += 1
        elapsed = time.time() - start_time

        # RELAY-ONLY: Poll relay server for Watch response
        # CloudKit/iCloud removed 2026-01-02 (security: public DB exposed auth tokens)
        response = check_relay_response(notification_id)
        if response:
            log_debug(f"[seq={sequence_id}] ✓ Relay response after {elapsed:.1f}s, {poll_count} polls")
            return response

        # LATENCY OPTIMIZATION: Adaptive polling intervals
        # - First 5s: 200ms (user likely responding quickly)
        # - 5-15s: 500ms (moderate wait)
        # - 15s+: 1000ms (user taking time, reduce overhead)
        if elapsed < 5:
            time.sleep(0.2)
        elif elapsed < 15:
            time.sleep(0.5)
        else:
            time.sleep(1.0)

    log_debug(f"[seq={sequence_id}] ⏱️ Timeout after {timeout}s, {poll_count} polls")
    return None


def output_decision(decision: str, reason: str = '') -> None:
    """Output hook decision to stdout for Claude Code.

    Uses the hookSpecificOutput format required by PermissionRequest hooks.
    """
    behavior = "allow" if decision == "allow" else "deny"

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {
                "behavior": behavior
            }
        }
    }

    if reason and behavior == "deny":
        output["hookSpecificOutput"]["decision"]["message"] = reason

    print(json.dumps(output), flush=True)


def handle_permission_request(data: dict) -> int:
    """Handle 'permission_request' hook - forward to Watch for approval.

    Sends tool permission prompt to Apple Watch and waits for user response.
    Uses periodic wake pushes to ensure iPhone processes Watch responses.
    If user approves/denies within timeout, returns that decision.
    If timeout, returns nothing (falls back to terminal prompt).
    """
    tool_name = data.get('tool_name', 'Unknown')
    tool_input = data.get('tool_input', {})
    session_id = data.get('session_id', 'unknown')
    cwd = data.get('cwd', '')
    project_name = Path(cwd).name if cwd else 'Unknown'

    # Handle AskUserQuestion specially - send question with options to Watch
    if tool_name == 'AskUserQuestion':
        log_debug(f"AskUserQuestion in PermissionRequest - handling with question options")
        return handle_ask_user_question(tool_input, session_id, project_name)

    log_debug(f"PermissionRequest: tool={tool_name}, session={session_id}")

    # Note: PermissionRequest hook only fires when permission is actually needed
    # No filtering required - Claude Code already filtered for us

    # Generate unique sequence ID for this request (for correlation)
    sequence_id = generate_sequence_id()

    # Build human-readable prompt based on tool type
    if tool_name == 'Write':
        file_path = tool_input.get('file_path', 'file')
        prompt = f"Allow Write to {Path(file_path).name}?"
    elif tool_name == 'Edit':
        file_path = tool_input.get('file_path', 'file')
        prompt = f"Allow Edit to {Path(file_path).name}?"
    elif tool_name == 'Bash':
        command = tool_input.get('command', '')[:40]
        prompt = f"Allow Bash: {command}?"
    elif tool_name == 'NotebookEdit':
        notebook_path = tool_input.get('notebook_path', 'notebook')
        prompt = f"Allow NotebookEdit to {Path(notebook_path).name}?"
    else:
        prompt = f"Allow {tool_name}?"

    # Generate unique notification ID for this request
    # This prevents stale approvals from being reused for different requests
    notification_id = str(uuid.uuid4())

    log_debug(f"[seq={sequence_id}] PermissionRequest: {prompt} (session={session_id}, notification={notification_id[:8]}...)")

    # 1. Send notification to Watch with action buttons
    send_result = send_notification(
        event='permission_request',
        message=prompt,
        session_id=session_id,
        project_name=project_name,
        requires_action=True,
        notification_id=notification_id
    )

    if send_result != 0:
        log_debug(f"[seq={sequence_id}] Failed to send notification, falling back to terminal")
        return 0  # No output = use terminal prompt

    # 2. Wait for Watch response via relay server
    log_debug(f"[seq={sequence_id}] Waiting for Watch response...")
    response = wait_for_response(
        sequence_id=sequence_id,
        timeout=DEFAULT_PERMISSION_TIMEOUT,
        notification_id=notification_id
    )

    # 3. Output decision via JSON (stdout) - this is how hooks communicate with Claude Code
    # Keystroke injection removed - it caused spurious characters in terminal
    if response:
        action = response.get('action', '').lower()
        if action == 'approve':
            output_decision('allow')
            log_debug(f"[seq={sequence_id}] ✓ User APPROVED via Watch")
        elif action == 'deny':
            output_decision('deny', 'Denied via Apple Watch')
            log_debug(f"[seq={sequence_id}] ✗ User DENIED via Watch")
        elif action == 'always_allow':
            output_decision('allow')
            log_debug(f"[seq={sequence_id}] ✓ User set ALWAYS ALLOW via Watch")
        else:
            log_debug(f"[seq={sequence_id}] Unknown action '{action}', no decision output")
            # No output = terminal prompt stays active
            # Send invalidation so Watch knows to dismiss this request
            send_invalidation(notification_id, 'unknown_action')
    else:
        log_debug(f"[seq={sequence_id}] No response received, falling back to terminal prompt")
        # No output = terminal prompt stays active
        # Send invalidation so Watch knows user will respond via terminal
        send_invalidation(notification_id, 'terminal_fallback')

    return 0


def handle_ask_user_question(tool_input: dict, session_id: str, project_name: str) -> int:
    """Handle AskUserQuestion tool - send question(s) with options to Watch.

    Supports both single and multi-question flows (1-4 questions).
    Extracts all questions and options from tool_input, sends to relay,
    waits for Watch response, and navigates terminal for each answer.
    """
    questions = tool_input.get('questions', [])
    if not questions:
        log_debug("No questions found in AskUserQuestion input")
        return 0

    # Generate unique IDs for this request
    notification_id = str(uuid.uuid4())
    sequence_id = generate_sequence_id()

    # Convert ALL questions to relay format
    relay_questions = []
    for idx, q in enumerate(questions):
        question_text = q.get('question', f'Question {idx + 1}')
        options = q.get('options', [])
        multi_select = q.get('multiSelect', False)
        header = q.get('header', None)

        # Convert options to relay format
        relay_options = []
        for opt in options:
            relay_options.append({
                'id': opt.get('label', '').lower().replace(' ', '_'),
                'label': opt.get('label', '?'),
                'description': opt.get('description', '')
            })

        relay_questions.append({
            'id': f"q{idx}",
            'question': question_text,
            'header': header,
            'options': relay_options,
            'multiSelect': multi_select
        })

    is_multi_question = len(relay_questions) > 1
    log_debug(f"AskUserQuestion: {len(relay_questions)} question(s), multi={is_multi_question}")

    # Send to relay with questions array
    if is_multi_question:
        # Multi-question flow - send full questions array
        success = send_questions_to_relay(
            questions=relay_questions,
            session_id=session_id,
            notification_id=notification_id
        )
    else:
        # Single question - use legacy format for backward compatibility
        first_q = relay_questions[0]
        success = send_question_to_relay(
            message=first_q['question'],
            session_id=session_id,
            question_options=first_q['options'],
            multi_select=first_q.get('multiSelect', False),
            notification_id=notification_id
        )

    if not success:
        log_debug(f"⚠️ Failed to send AskUserQuestion to Watch, falling back to terminal")
        return 0

    log_debug(f"✓ AskUserQuestion sent, waiting for Watch response...")

    # Wait for Watch response via relay server
    response = wait_for_response(
        sequence_id=sequence_id,
        timeout=DEFAULT_PERMISSION_TIMEOUT,
        notification_id=notification_id
    )

    if response:
        action = response.get('action', '')

        # Handle multi-question response (has 'answers' array)
        answers = response.get('answers', [])
        if answers and is_multi_question:
            log_debug(f"✓ Received multi-question answers: {len(answers)} answers")
            navigate_multi_question_answers(answers, questions)
            return 0

        # Handle single-question response (backward compatible)
        selected_options = response.get('selected_options', [])
        log_debug(f"✓ Received Watch answer: action={action}, selected={selected_options}")

        # For selectOption action, map selected label to option number
        if action == 'selectOption' and selected_options:
            selected_label = selected_options[0]
            options = questions[0].get('options', [])

            # Handle custom/voice input (Watch sends "__custom__" with message)
            if selected_label == '__custom__':
                custom_text = response.get('message', '')
                if custom_text:
                    log_debug(f"Voice input from Watch: '{custom_text}'")
                    # Use arrow key navigation for voice input
                    # This maps voice text to option and navigates with arrow keys
                    if inject_voice_response(custom_text, options):
                        log_debug(f"✓ Voice input successfully navigated to matching option")
                    else:
                        log_debug(f"⚠️ Voice navigation failed, falling back to terminal")
                        send_invalidation(notification_id, 'voice_navigation_failed')
                else:
                    log_debug(f"⚠️ __custom__ selected but no message text received")
                    # Send invalidation - custom input failed
                    send_invalidation(notification_id, 'custom_input_failed')
            else:
                # Predefined option tapped - use arrow navigation instead of typing number
                option_number = None
                for idx, opt in enumerate(options, 1):
                    if opt.get('label') == selected_label:
                        option_number = idx
                        break

                if option_number:
                    log_debug(f"Mapped '{selected_label}' → option {option_number}, using arrow navigation")
                    if navigate_to_option(option_number):
                        log_debug(f"✓ Arrow navigation selected option {option_number}")
                    else:
                        log_debug(f"⚠️ Arrow navigation failed for option {option_number}")
                        send_invalidation(notification_id, 'navigation_failed')
                else:
                    log_debug(f"⚠️ Could not map '{selected_label}' to option number")
                    # Send invalidation - mapping failed
                    send_invalidation(notification_id, 'option_mapping_failed')
        else:
            # Fallback to action as answer
            log_debug(f"Fallback to action: {action}")
            # Send invalidation - unexpected action
            send_invalidation(notification_id, 'unexpected_action')
    else:
        log_debug(f"No Watch response, falling back to terminal prompt")
        # Send invalidation so Watch knows user will respond via terminal
        send_invalidation(notification_id, 'terminal_fallback')

    return 0


def navigate_multi_question_answers(answers: list, questions: list) -> bool:
    """Navigate terminal UI for each answer in a multi-question flow.

    Claude Code's AskUserQuestion presents questions sequentially.
    For each answer, we navigate using arrow keys to select the option.

    Args:
        answers: List of answer dicts with questionId, selectedLabels, customText
        questions: Original questions list from tool_input

    Returns:
        True if all navigations succeeded, False if any failed.
    """
    log_debug(f"Navigating {len(answers)} multi-question answers...")

    for answer in answers:
        question_id = answer.get('questionId', '')
        selected_labels = answer.get('selectedLabels', [])
        custom_text = answer.get('customText', '')

        # Find the matching question to get its options
        question_idx = None
        for idx, q in enumerate(questions):
            # Match by index (q0, q1, etc) or by original id
            if question_id == f"q{idx}" or question_id == q.get('id', ''):
                question_idx = idx
                break

        if question_idx is None:
            log_debug(f"⚠️ Could not find question for answer: {question_id}")
            continue

        question = questions[question_idx]
        options = question.get('options', [])

        log_debug(f"Processing answer for question {question_idx + 1}: selected={selected_labels}")

        # Handle custom/voice input
        if selected_labels == ['__custom__'] and custom_text:
            log_debug(f"Voice input for Q{question_idx + 1}: '{custom_text}'")
            if inject_voice_response(custom_text, options):
                log_debug(f"✓ Voice navigation succeeded for Q{question_idx + 1}")
            else:
                log_debug(f"⚠️ Voice navigation failed for Q{question_idx + 1}")
        elif selected_labels:
            # For single-select, navigate to the selected option
            selected_label = selected_labels[0]
            option_number = None
            for idx, opt in enumerate(options, 1):
                if opt.get('label') == selected_label:
                    option_number = idx
                    break

            if option_number:
                log_debug(f"Navigating to option {option_number} for Q{question_idx + 1}")
                if navigate_to_option(option_number):
                    log_debug(f"✓ Selected option {option_number} for Q{question_idx + 1}")
                else:
                    log_debug(f"⚠️ Navigation failed for Q{question_idx + 1}")
            else:
                log_debug(f"⚠️ Could not map '{selected_label}' to option for Q{question_idx + 1}")
        else:
            log_debug(f"⚠️ No selection for Q{question_idx + 1}")

        # Small delay between questions to let Claude process each answer
        time.sleep(0.3)

    log_debug(f"✓ Multi-question navigation complete")
    return True


def send_questions_to_relay(
    questions: list,
    session_id: str,
    notification_id: str = ''
) -> bool:
    """Send multi-question notification directly to relay with questions array.

    This is used for AskUserQuestion with multiple questions (2-4).
    """
    auth_token = get_auth_token()
    if not auth_token:
        log_debug("No auth token found for questions notification")
        return False

    if not notification_id:
        notification_id = str(uuid.uuid4())

    # Build message from first question for notification banner
    first_q = questions[0] if questions else {}
    message = first_q.get('question', 'Multiple questions')[:100]
    if len(questions) > 1:
        message = f"{message} (+{len(questions) - 1} more)"

    payload = {
        'auth_token': auth_token,
        'event': 'question',
        'message': message,
        'session_id': session_id,
        'requires_action': True,
        'notification_id': notification_id,
        'questions': questions  # Full questions array for multi-question flow
    }

    try:
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{RELAY_URL}/notify",
            data=data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                log_debug(f"✓ Multi-question notification sent to relay ({len(questions)} questions)")
                return True
            else:
                log_debug(f"Relay returned status {resp.status}")
                return False

    except urllib.error.HTTPError as e:
        log_debug(f"Relay HTTP error: {e.code} - {e.read().decode()[:100]}")
        return False
    except Exception as e:
        log_debug(f"Failed to send questions to relay: {e}")
        return False


def send_question_to_relay(
    message: str,
    session_id: str,
    question_options: list,
    multi_select: bool = False,
    notification_id: str = ''
) -> bool:
    """Send question notification directly to relay with options.

    This bypasses the CLI to include question_options in the payload.
    """
    auth_token = get_auth_token()
    if not auth_token:
        log_debug("No auth token found for question notification")
        return False

    if not notification_id:
        notification_id = str(uuid.uuid4())

    payload = {
        'auth_token': auth_token,
        'event': 'question',
        'message': message[:500],
        'session_id': session_id,
        'requires_action': True,
        'notification_id': notification_id,
        'question_options': question_options,
        'allows_multi_select': multi_select  # Relay expects allows_multi_select
    }

    try:
        import urllib.request
        import urllib.error

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            f"{RELAY_URL}/notify",
            data=data,
            method='POST'
        )
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                log_debug(f"✓ Question notification sent to relay")
                return True
            else:
                log_debug(f"Relay returned status {resp.status}")
                return False

    except urllib.error.HTTPError as e:
        log_debug(f"Relay HTTP error: {e.code} - {e.read().decode()[:100]}")
        return False
    except Exception as e:
        log_debug(f"Failed to send question to relay: {e}")
        return False


def handle_pre_tool_use(data: dict) -> int:
    """Handle 'pre_tool_use' hook.

    NOTE: AskUserQuestion is now handled by handle_ask_user_question (called from
    handle_permission_request). Processing it here too would cause DOUBLE INPUT
    because both hooks fire for the same question.

    This hook is currently a no-op but kept for future pre-tool-use needs.
    """
    tool_name = data.get('tool_name', '')

    # AskUserQuestion is handled by permission_request hook to avoid double input
    if tool_name == 'AskUserQuestion':
        log_debug("PreToolUse: Skipping AskUserQuestion (handled by permission_request)")
        return 0

    # No other tools need pre_tool_use handling currently
    return 0


def handle_notification_debug(data: dict) -> int:
    """DEBUG: Log Notification hook data to understand what it provides."""
    log_debug(f"=== NOTIFICATION DEBUG ===")
    log_debug(f"Full data: {json.dumps(data, indent=2)[:1000]}")
    log_debug(f"Keys: {list(data.keys())}")
    log_debug(f"message: {data.get('message', 'N/A')[:200]}")
    log_debug(f"tool_name: {data.get('tool_name', 'N/A')}")
    log_debug(f"tool_input: {str(data.get('tool_input', 'N/A'))[:200]}")
    return 0


HANDLERS = {
    'stop': handle_stop,
    'notification': handle_notification,
    'notification_debug': handle_notification_debug,
    'session_start': handle_session_start,
    'session_end': handle_session_end,
    'subagent_stop': handle_subagent_stop,
    'permission_request': handle_permission_request,
    'pre_tool_use': handle_pre_tool_use,
}


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <hook_type>", file=sys.stderr)
        print(f"Hook types: {', '.join(ALLOWED_HOOKS)}", file=sys.stderr)
        return 1

    hook_type = sys.argv[1].lower().replace('-', '_')

    if hook_type not in ALLOWED_HOOKS:
        logger.error(f"Unknown hook type: {hook_type}")
        logger.error(f"Allowed: {', '.join(ALLOWED_HOOKS)}")
        return 1

    log_debug(f"=== Hook triggered: {hook_type} ===")

    try:
        data = parse_input()
        handler = HANDLERS.get(hook_type)

        if handler:
            return handler(data)
        else:
            logger.error(f"No handler for hook type: {hook_type}")
            return 1

    except ValueError as e:
        logger.error(f"Input error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Hook failed: {e}")
        import traceback
        log_debug(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(main())
