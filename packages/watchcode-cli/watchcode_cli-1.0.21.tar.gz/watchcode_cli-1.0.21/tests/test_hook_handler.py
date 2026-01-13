"""Tests for MacTools hook_handler.py module.

Tests the centralized hook handler for WatchCode Claude Code hooks.
"""

import json
import pytest
import sys
import io
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add MacTools (scripts) to path for import since hook_handler is in watchcode/scripts
sys.path.insert(0, str(Path(__file__).parent.parent / "watchcode" / "scripts"))
from hook_handler import (
    parse_input,
    validate_path,
    log_debug,
    output_decision,
    match_voice_to_option,
    handle_stop,
    handle_permission_request,
    handle_pre_tool_use,
    extract_transcript_data,
    decrypt_response,
    ALLOWED_HOOKS,
    MAX_INPUT_SIZE,
)


class TestParseInput:
    """Tests for parse_input function."""

    def test_parse_from_stdin(self, monkeypatch):
        """Parses JSON from stdin when available."""
        test_input = '{"session_id": "test-123", "tool_name": "Bash"}'
        stdin_mock = io.StringIO(test_input)
        stdin_mock.isatty = lambda: False
        monkeypatch.setattr('sys.stdin', stdin_mock)

        result = parse_input()

        assert result["session_id"] == "test-123"
        assert result["tool_name"] == "Bash"

    def test_parse_from_hook_input_env(self, monkeypatch):
        """Falls back to HOOK_INPUT env var when stdin is tty."""
        # Create a mock stdin that is a tty
        stdin_mock = io.StringIO('')
        stdin_mock.isatty = lambda: True
        monkeypatch.setattr('sys.stdin', stdin_mock)
        monkeypatch.setenv('HOOK_INPUT', '{"event": "stop"}')

        result = parse_input()

        assert result["event"] == "stop"

    def test_parse_empty_returns_empty_dict(self, monkeypatch):
        """Returns empty dict when no input available."""
        stdin_mock = io.StringIO('')
        stdin_mock.isatty = lambda: True
        monkeypatch.setattr('sys.stdin', stdin_mock)
        monkeypatch.delenv('HOOK_INPUT', raising=False)

        result = parse_input()

        assert result == {}

    def test_parse_rejects_oversized_input(self, monkeypatch):
        """Raises error for input exceeding size limit."""
        huge_input = '{"data": "' + 'x' * (MAX_INPUT_SIZE + 100) + '"}'
        stdin_mock = io.StringIO(huge_input)
        stdin_mock.isatty = lambda: False
        monkeypatch.setattr('sys.stdin', stdin_mock)

        with pytest.raises(ValueError, match="Input too large"):
            parse_input()

    def test_parse_invalid_json_raises(self, monkeypatch):
        """Raises error for invalid JSON."""
        stdin_mock = io.StringIO('not valid json')
        stdin_mock.isatty = lambda: False
        monkeypatch.setattr('sys.stdin', stdin_mock)

        with pytest.raises(ValueError, match="Invalid JSON"):
            parse_input()

    def test_parse_nested_json(self, monkeypatch):
        """Parses nested JSON structures correctly."""
        test_input = json.dumps({
            "tool_name": "Write",
            "tool_input": {
                "file_path": "/path/to/file.txt",
                "content": "test content"
            },
            "session_id": "session-123"
        })
        stdin_mock = io.StringIO(test_input)
        stdin_mock.isatty = lambda: False
        monkeypatch.setattr('sys.stdin', stdin_mock)

        result = parse_input()

        assert result["tool_name"] == "Write"
        assert result["tool_input"]["file_path"] == "/path/to/file.txt"


class TestValidatePath:
    """Tests for validate_path function."""

    def test_validates_existing_path(self, tmp_path):
        """Returns resolved path for existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        result = validate_path(str(test_file))

        assert result == test_file

    def test_validates_directory_path(self, tmp_path):
        """Returns resolved path for existing directory."""
        result = validate_path(str(tmp_path))

        assert result == tmp_path

    def test_blocks_path_traversal(self, tmp_path):
        """Blocks path traversal attempts."""
        allowed_base = tmp_path / "allowed"
        allowed_base.mkdir()

        # Try to escape to parent
        result = validate_path(str(tmp_path / "allowed" / ".." / "secret"), allowed_base)

        assert result is None

    def test_returns_none_for_empty_path(self):
        """Returns None for empty path."""
        result = validate_path("")
        assert result is None

    def test_returns_none_for_none_path(self):
        """Returns None for None input."""
        result = validate_path(None)
        assert result is None

    def test_expands_home_directory(self):
        """Expands ~ to home directory."""
        result = validate_path("~")

        assert result is not None
        assert result == Path.home()

    def test_allows_valid_nested_path(self, tmp_path):
        """Allows valid nested path under allowed base."""
        allowed_base = tmp_path / "allowed"
        allowed_base.mkdir()
        nested = allowed_base / "sub" / "file.txt"
        nested.parent.mkdir(parents=True)
        nested.write_text("test")

        result = validate_path(str(nested), allowed_base)

        assert result == nested


class TestOutputDecision:
    """Tests for output_decision function."""

    def test_outputs_allow_decision(self, capsys):
        """Outputs correct JSON for allow decision."""
        output_decision('allow')

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["hookSpecificOutput"]["hookEventName"] == "PermissionRequest"
        assert output["hookSpecificOutput"]["decision"]["behavior"] == "allow"

    def test_outputs_deny_decision_with_reason(self, capsys):
        """Outputs correct JSON for deny decision with message."""
        output_decision('deny', 'User denied on Watch')

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["hookSpecificOutput"]["decision"]["behavior"] == "deny"
        assert output["hookSpecificOutput"]["decision"]["message"] == "User denied on Watch"

    def test_deny_without_reason_has_no_message(self, capsys):
        """Deny without reason omits message key."""
        output_decision('deny')

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["hookSpecificOutput"]["decision"]["behavior"] == "deny"
        assert "message" not in output["hookSpecificOutput"]["decision"]

    def test_allow_ignores_reason(self, capsys):
        """Allow decision ignores reason parameter."""
        output_decision('allow', 'Should be ignored')

        captured = capsys.readouterr()
        output = json.loads(captured.out)

        assert output["hookSpecificOutput"]["decision"]["behavior"] == "allow"
        assert "message" not in output["hookSpecificOutput"]["decision"]


class TestMatchVoiceToOption:
    """Tests for match_voice_to_option function."""

    @pytest.fixture
    def options(self):
        """Standard options for testing."""
        return [
            {"label": "Allow"},
            {"label": "Deny"},
            {"label": "Always Allow"}
        ]

    def test_matches_direct_number(self, options):
        """Matches direct number input."""
        assert match_voice_to_option("1", options) == 1
        assert match_voice_to_option("2", options) == 2
        assert match_voice_to_option("3", options) == 3

    def test_matches_number_words(self, options):
        """Matches spelled-out numbers."""
        assert match_voice_to_option("one", options) == 1
        assert match_voice_to_option("two", options) == 2
        assert match_voice_to_option("three", options) == 3

    def test_matches_ordinal_words(self, options):
        """Matches ordinal number words."""
        assert match_voice_to_option("first", options) == 1
        assert match_voice_to_option("second", options) == 2
        assert match_voice_to_option("third", options) == 3

    def test_matches_ordinal_abbreviations(self, options):
        """Matches ordinal abbreviations like 1st, 2nd."""
        assert match_voice_to_option("1st", options) == 1
        assert match_voice_to_option("2nd", options) == 2
        assert match_voice_to_option("3rd", options) == 3

    def test_matches_exact_label(self, options):
        """Matches exact label (case-insensitive)."""
        assert match_voice_to_option("Allow", options) == 1
        assert match_voice_to_option("deny", options) == 2
        assert match_voice_to_option("ALWAYS ALLOW", options) == 3

    def test_matches_partial_label(self, options):
        """Matches partial label."""
        assert match_voice_to_option("always", options) == 3

    def test_matches_label_in_voice(self, options):
        """Matches when label is contained in voice text."""
        assert match_voice_to_option("option allow please", options) == 1
        assert match_voice_to_option("I want to deny", options) == 2

    def test_defaults_to_first_on_no_match(self, options):
        """Defaults to option 1 when no match found."""
        assert match_voice_to_option("nonsense", options) == 1
        assert match_voice_to_option("asdfghjkl", options) == 1

    def test_handles_out_of_range_number(self, options):
        """Defaults to 1 for out-of-range numbers."""
        assert match_voice_to_option("99", options) == 1
        assert match_voice_to_option("0", options) == 1
        assert match_voice_to_option("-1", options) == 1

    def test_handles_empty_options(self):
        """Handles empty options list gracefully."""
        assert match_voice_to_option("1", []) == 1
        assert match_voice_to_option("allow", []) == 1

    def test_handles_options_without_label(self):
        """Handles options missing label key."""
        options = [{"id": "opt1"}, {"id": "opt2"}]
        assert match_voice_to_option("1", options) == 1
        assert match_voice_to_option("2", options) == 2


class TestHandleStop:
    """Tests for handle_stop function."""

    @patch('hook_handler.send_notification')
    @patch('hook_handler.extract_transcript_data')
    def test_handle_stop_sends_notification(self, mock_extract, mock_send):
        """handle_stop sends notification with correct event."""
        mock_extract.return_value = ("User request", "Task completed successfully")
        mock_send.return_value = 0

        data = {
            "session_id": "test-session",
            "transcript_path": "/tmp/transcript.jsonl",
            "cwd": "/Users/test/project"
        }

        result = handle_stop(data)

        assert result == 0
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["event"] == "stop"
        assert call_kwargs["session_id"] == "test-session"
        assert call_kwargs["project_name"] == "project"

    @patch('hook_handler.send_notification')
    @patch('hook_handler.extract_transcript_data')
    def test_handle_stop_uses_summary(self, mock_extract, mock_send):
        """handle_stop uses transcript summary in notification."""
        long_response = "A" * 300
        mock_extract.return_value = ("User prompt", long_response)
        mock_send.return_value = 0

        data = {"session_id": "test", "transcript_path": "/tmp/t.jsonl", "cwd": "/proj"}

        handle_stop(data)

        call_kwargs = mock_send.call_args[1]
        # Message should be truncated to 200 chars plus "..."
        assert len(call_kwargs["message"]) == 203
        assert call_kwargs["message"].endswith("...")

    @patch('hook_handler.send_notification')
    @patch('hook_handler.extract_transcript_data')
    def test_handle_stop_fallback_message(self, mock_extract, mock_send):
        """handle_stop uses fallback message when no transcript data."""
        mock_extract.return_value = ("", "")
        mock_send.return_value = 0

        data = {"session_id": "test", "transcript_path": "", "cwd": ""}

        handle_stop(data)

        call_kwargs = mock_send.call_args[1]
        assert call_kwargs["message"] == "Task completed"


class TestHandlePermissionRequest:
    """Tests for handle_permission_request function."""

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_approve(self, mock_send, mock_wait, mock_invalidate, capsys):
        """Outputs allow on approve response."""
        mock_send.return_value = 0
        mock_wait.return_value = {"action": "approve"}

        data = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
            "session_id": "test-session",
            "cwd": "/tmp/project"
        }

        result = handle_permission_request(data)

        assert result == 0
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["hookSpecificOutput"]["decision"]["behavior"] == "allow"

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_deny(self, mock_send, mock_wait, mock_invalidate, capsys):
        """Outputs deny on deny response."""
        mock_send.return_value = 0
        mock_wait.return_value = {"action": "deny"}

        data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/etc/passwd"},
            "session_id": "test-session",
            "cwd": "/tmp"
        }

        result = handle_permission_request(data)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["hookSpecificOutput"]["decision"]["behavior"] == "deny"
        assert "Watch" in output["hookSpecificOutput"]["decision"]["message"]

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_always_allow(self, mock_send, mock_wait, mock_invalidate, capsys):
        """Outputs allow on always_allow response."""
        mock_send.return_value = 0
        mock_wait.return_value = {"action": "always_allow"}

        data = {
            "tool_name": "Bash",
            "tool_input": {"command": "npm install"},
            "session_id": "test-session",
            "cwd": "/project"
        }

        result = handle_permission_request(data)

        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert output["hookSpecificOutput"]["decision"]["behavior"] == "allow"

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_timeout(self, mock_send, mock_wait, mock_invalidate, capsys):
        """No output on timeout (falls back to terminal)."""
        mock_send.return_value = 0
        mock_wait.return_value = None  # Timeout
        mock_invalidate.return_value = True

        data = {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
            "session_id": "test-session"
        }

        result = handle_permission_request(data)

        assert result == 0
        captured = capsys.readouterr()
        # No JSON output means terminal prompt is used
        assert captured.out.strip() == ""
        # Invalidation should be sent
        mock_invalidate.assert_called_once()

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_notification_fails(self, mock_send, mock_wait, mock_invalidate, capsys):
        """Returns 0 and no output when notification fails."""
        mock_send.return_value = 1  # Failed

        data = {
            "tool_name": "Bash",
            "tool_input": {"command": "echo test"},
            "session_id": "test-session"
        }

        result = handle_permission_request(data)

        assert result == 0
        captured = capsys.readouterr()
        assert captured.out.strip() == ""
        mock_wait.assert_not_called()

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_builds_write_prompt(self, mock_send, mock_wait, mock_invalidate):
        """Builds human-readable prompt for Write tool."""
        mock_send.return_value = 0
        mock_wait.return_value = {"action": "approve"}

        data = {
            "tool_name": "Write",
            "tool_input": {"file_path": "/path/to/newfile.txt"},
            "session_id": "test"
        }

        handle_permission_request(data)

        call_kwargs = mock_send.call_args[1]
        assert "Write" in call_kwargs["message"]
        assert "newfile.txt" in call_kwargs["message"]

    @patch('hook_handler.send_invalidation')
    @patch('hook_handler.wait_for_response')
    @patch('hook_handler.send_notification')
    def test_permission_request_builds_bash_prompt(self, mock_send, mock_wait, mock_invalidate):
        """Builds human-readable prompt for Bash tool."""
        mock_send.return_value = 0
        mock_wait.return_value = {"action": "approve"}

        data = {
            "tool_name": "Bash",
            "tool_input": {"command": "npm install lodash"},
            "session_id": "test"
        }

        handle_permission_request(data)

        call_kwargs = mock_send.call_args[1]
        assert "Bash" in call_kwargs["message"]
        assert "npm install" in call_kwargs["message"]


class TestHandlePreToolUse:
    """Tests for handle_pre_tool_use function."""

    def test_skips_askuserquestion(self):
        """Skips AskUserQuestion to avoid double handling."""
        data = {
            "tool_name": "AskUserQuestion",
            "tool_input": {"questions": [{"question": "Test?"}]}
        }

        result = handle_pre_tool_use(data)

        assert result == 0

    def test_returns_zero_for_other_tools(self):
        """Returns 0 for non-AskUserQuestion tools (no-op)."""
        data = {
            "tool_name": "Bash",
            "tool_input": {"command": "ls"}
        }

        result = handle_pre_tool_use(data)

        assert result == 0


class TestExtractTranscriptData:
    """Tests for extract_transcript_data function."""

    def test_extracts_from_valid_transcript(self, tmp_path):
        """Extracts user prompt and assistant response from valid transcript."""
        transcript = tmp_path / "transcript.jsonl"
        entries = [
            {"type": "user", "message": {"content": [{"type": "text", "text": "Please create a hello world script"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "I'll create that for you."}]}},
        ]
        transcript.write_text("\n".join(json.dumps(e) for e in entries))

        user_prompt, response = extract_transcript_data(str(transcript))

        assert "hello world" in user_prompt
        assert "create" in response

    def test_returns_empty_for_missing_file(self):
        """Returns empty strings for missing transcript file."""
        user_prompt, response = extract_transcript_data("/nonexistent/path.jsonl")

        assert user_prompt == ""
        assert response == ""

    def test_returns_empty_for_empty_path(self):
        """Returns empty strings for empty path."""
        user_prompt, response = extract_transcript_data("")

        assert user_prompt == ""
        assert response == ""

    def test_skips_short_followup_messages(self, tmp_path):
        """Skips short follow-up messages like 'yes' or 'ok'."""
        transcript = tmp_path / "transcript.jsonl"
        entries = [
            {"type": "user", "message": {"content": [{"type": "text", "text": "Please implement user authentication"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "I'll do that."}]}},
            {"type": "user", "message": {"content": [{"type": "text", "text": "yes"}]}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": "Done!"}]}},
        ]
        transcript.write_text("\n".join(json.dumps(e) for e in entries))

        user_prompt, response = extract_transcript_data(str(transcript))

        # Should get the substantial request, not "yes"
        assert "authentication" in user_prompt


class TestAllowedHooks:
    """Tests for ALLOWED_HOOKS constant."""

    def test_allowed_hooks_contains_expected(self):
        """ALLOWED_HOOKS contains all expected hook types."""
        expected = {'stop', 'notification', 'session_start', 'session_end',
                    'subagent_stop', 'permission_request', 'pre_tool_use'}

        assert expected.issubset(ALLOWED_HOOKS)

    def test_hook_type_normalization(self):
        """Hook types are lowercase with underscores."""
        for hook in ALLOWED_HOOKS:
            assert hook == hook.lower()
            assert '-' not in hook


class TestLogDebug:
    """Tests for log_debug function."""

    def test_log_debug_creates_file(self, tmp_path, monkeypatch):
        """log_debug creates debug log file."""
        debug_log = tmp_path / "hook_debug.log"
        monkeypatch.setattr('hook_handler.DEBUG_LOG', debug_log)

        log_debug("Test message")

        assert debug_log.exists()
        content = debug_log.read_text()
        assert "Test message" in content

    def test_log_debug_appends(self, tmp_path, monkeypatch):
        """log_debug appends to existing file."""
        debug_log = tmp_path / "hook_debug.log"
        debug_log.write_text("Existing content\n")
        monkeypatch.setattr('hook_handler.DEBUG_LOG', debug_log)

        log_debug("New message")

        content = debug_log.read_text()
        assert "Existing content" in content
        assert "New message" in content

    def test_log_debug_handles_errors_silently(self, monkeypatch):
        """log_debug silently handles errors (e.g., permission denied)."""
        # Use a path that doesn't exist and can't be created
        monkeypatch.setattr('hook_handler.DEBUG_LOG', Path("/nonexistent/dir/log.txt"))

        # Should not raise
        log_debug("Test message")


class TestMaxInputSize:
    """Tests for MAX_INPUT_SIZE constant."""

    def test_max_input_size_is_reasonable(self):
        """MAX_INPUT_SIZE should be 1MB."""
        assert MAX_INPUT_SIZE == 1024 * 1024


class TestDecryptResponse:
    """Tests for decrypt_response function (E2E encryption)."""

    def test_decrypt_plaintext_response_passthrough(self):
        """Plaintext responses should be returned as-is."""
        plaintext_response = {
            "action": "approve",
            "timestamp": "2026-01-03T12:00:00Z",
            "selected_options": ["Yes"]
        }

        result = decrypt_response(plaintext_response, "ABCD1234EFGH")

        assert result == plaintext_response
        assert result["action"] == "approve"

    def test_decrypt_encrypted_response(self):
        """Encrypted responses should be decrypted correctly."""
        # First encrypt a response using the crypto module
        from watchcode.crypto import encrypt

        auth_token = "TESTTOKEN123"
        original_response = {
            "action": "deny",
            "timestamp": "2026-01-03T12:00:00Z",
            "message": "Not allowed"
        }

        encrypted = encrypt(original_response, auth_token)

        # Now decrypt it
        result = decrypt_response(encrypted, auth_token)

        assert result["action"] == "deny"
        assert result["timestamp"] == "2026-01-03T12:00:00Z"
        assert result["message"] == "Not allowed"

    def test_decrypt_response_wrong_key_returns_original(self):
        """Wrong key should return original encrypted data (graceful fallback)."""
        from watchcode.crypto import encrypt

        auth_token = "CORRECTTOKEN"
        wrong_token = "WRONGTOKEN12"

        original = {"action": "approve"}
        encrypted = encrypt(original, auth_token)

        # Decrypt with wrong token - should return original encrypted data
        result = decrypt_response(encrypted, wrong_token)

        # Should return original encrypted payload (decryption failed gracefully)
        assert "v" in result or "action" in result

    def test_decrypt_response_with_selected_options(self):
        """Encrypted responses with selected_options should decrypt correctly."""
        from watchcode.crypto import encrypt

        auth_token = "OPTIONTOKEN1"
        original = {
            "action": "selectOption",
            "selected_options": ["Option A", "Option B"],
            "timestamp": "2026-01-03T12:00:00Z"
        }

        encrypted = encrypt(original, auth_token)

        result = decrypt_response(encrypted, auth_token)

        assert result["action"] == "selectOption"
        assert result["selected_options"] == ["Option A", "Option B"]

    def test_decrypt_response_with_voice_message(self):
        """Encrypted responses with voice message should decrypt correctly."""
        from watchcode.crypto import encrypt

        auth_token = "VOICETOKEN12"
        original = {
            "action": "selectOption",
            "selected_options": ["__custom__"],
            "message": "Custom voice input text",
            "timestamp": "2026-01-03T12:00:00Z"
        }

        encrypted = encrypt(original, auth_token)

        result = decrypt_response(encrypted, auth_token)

        assert result["action"] == "selectOption"
        assert result["message"] == "Custom voice input text"

    def test_decrypt_response_empty_dict(self):
        """Empty response should be returned as-is."""
        result = decrypt_response({}, "ABCD1234EFGH")
        assert result == {}

    def test_decrypt_response_missing_v_field(self):
        """Response with nonce/ciphertext but no v should be treated as plaintext."""
        response = {
            "nonce": "test",
            "ciphertext": "test",
            "action": "approve"
        }

        result = decrypt_response(response, "ABCD1234EFGH")

        # Should return as-is since v field is missing
        assert result["action"] == "approve"

    def test_decrypt_response_wrong_version(self):
        """Response with unsupported version should return original."""
        response = {
            "v": 99,
            "nonce": "dGVzdA==",
            "ciphertext": "dGVzdA=="
        }

        result = decrypt_response(response, "ABCD1234EFGH")

        # Should return original since version is unsupported
        assert result["v"] == 99
