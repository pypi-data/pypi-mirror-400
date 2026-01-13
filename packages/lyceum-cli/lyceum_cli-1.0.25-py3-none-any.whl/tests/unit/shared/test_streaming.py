"""Tests for streaming utilities."""

import json
from unittest.mock import MagicMock, patch

import pytest

from lyceum.shared.streaming import (
    StatusLine,
    check_execution_status,
    normalize_newlines,
    stream_execution_output,
    strip_ansi_codes,
)


class TestStripAnsiCodes:
    """Tests for strip_ansi_codes function."""

    def test_removes_color_codes(self):
        text = "\x1b[31mRed text\x1b[0m"
        assert strip_ansi_codes(text) == "Red text"

    def test_removes_multiple_color_codes(self):
        text = "\x1b[1m\x1b[31mBold Red\x1b[0m Normal"
        assert strip_ansi_codes(text) == "Bold Red Normal"

    def test_preserves_plain_text(self):
        text = "Plain text without codes"
        assert strip_ansi_codes(text) == text

    def test_handles_empty_string(self):
        assert strip_ansi_codes("") == ""

    def test_handles_nested_codes(self):
        text = "\x1b[38;5;196mExtended color\x1b[0m"
        assert strip_ansi_codes(text) == "Extended color"


class TestNormalizeNewlines:
    """Tests for normalize_newlines function."""

    def test_collapses_double_newlines(self):
        assert normalize_newlines("a\n\nb") == "a\nb"

    def test_collapses_triple_newlines(self):
        assert normalize_newlines("a\n\n\nb") == "a\nb"

    def test_preserves_single_newlines(self):
        assert normalize_newlines("a\nb\nc") == "a\nb\nc"

    def test_handles_mixed_newlines(self):
        text = "a\nb\n\n\nc\nd"
        assert normalize_newlines(text) == "a\nb\nc\nd"

    def test_handles_empty_string(self):
        assert normalize_newlines("") == ""

    def test_handles_only_newlines(self):
        assert normalize_newlines("\n\n\n") == "\n"


class TestStatusLine:
    """Tests for StatusLine class."""

    def test_start_stop_lifecycle(self):
        status = StatusLine()
        status.start()
        assert status._live is not None
        status.stop()
        assert status._live is None

    def test_multiple_stops_no_error(self):
        status = StatusLine()
        status.start()
        status.stop()
        status.stop()  # Should not raise

    def test_context_manager(self):
        with StatusLine() as status:
            assert status._live is not None
        assert status._live is None

    def test_update_message(self):
        status = StatusLine()
        status.start()
        status.update("Loading...")  # Should not raise
        assert status._current_status == "Loading..."
        status.stop()

    def test_update_without_start(self):
        status = StatusLine()
        status.update("Test")  # Should not raise even without start
        assert status._current_status == "Test"

    def test_stop_without_start(self):
        status = StatusLine()
        status.stop()  # Should not raise


class TestStreamExecutionOutput:
    """Tests for stream_execution_output function."""

    @patch("lyceum.shared.streaming.httpx.stream")
    @patch("lyceum.shared.streaming.config")
    def test_success_with_output(
        self,
        mock_config,
        mock_httpx_stream,
        setup_httpx_stream,
        mock_execution_id,
    ):
        from tests.unit.external.compute.execution.test_data import (
            SAMPLE_SSE_JOB_FINISHED,
            SAMPLE_SSE_OUTPUT_EVENT,
        )

        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"
        mock_httpx_stream.return_value = setup_httpx_stream(
            events=[SAMPLE_SSE_OUTPUT_EVENT, SAMPLE_SSE_JOB_FINISHED]
        )

        result = stream_execution_output(mock_execution_id, "http://stream.url")
        assert result is True

    @patch("lyceum.shared.streaming.httpx.stream")
    @patch("lyceum.shared.streaming.config")
    def test_failure_with_nonzero_exit(
        self,
        mock_config,
        mock_httpx_stream,
        setup_httpx_stream,
        mock_execution_id,
    ):
        from tests.unit.external.compute.execution.test_data import SAMPLE_SSE_JOB_FAILED

        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"
        mock_httpx_stream.return_value = setup_httpx_stream(events=[SAMPLE_SSE_JOB_FAILED])

        result = stream_execution_output(mock_execution_id, "http://stream.url")
        assert result is False

    @patch("lyceum.shared.streaming.httpx.stream")
    @patch("lyceum.shared.streaming.config")
    def test_http_error_response(
        self,
        mock_config,
        mock_httpx_stream,
        mock_execution_id,
    ):
        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_context = MagicMock()
        mock_context.__enter__.return_value = mock_response
        mock_context.__exit__.return_value = None
        mock_httpx_stream.return_value = mock_context

        result = stream_execution_output(mock_execution_id, "http://stream.url")
        assert result is False

    @patch("lyceum.shared.streaming.httpx.stream")
    @patch("lyceum.shared.streaming.config")
    def test_uses_default_url_when_not_provided(
        self,
        mock_config,
        mock_httpx_stream,
        setup_httpx_stream,
        mock_execution_id,
    ):
        from tests.unit.external.compute.execution.test_data import SAMPLE_SSE_JOB_FINISHED

        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"
        mock_httpx_stream.return_value = setup_httpx_stream(events=[SAMPLE_SSE_JOB_FINISHED])

        stream_execution_output(mock_execution_id)

        # Check that the default URL was constructed
        call_args = mock_httpx_stream.call_args
        assert mock_execution_id in call_args[0][1]


class TestCheckExecutionStatus:
    """Tests for check_execution_status function."""

    @patch("lyceum.shared.streaming.httpx.get")
    @patch("lyceum.shared.streaming.config")
    def test_completed_status(self, mock_config, mock_httpx_get, mock_execution_id):
        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "completed"}
        mock_httpx_get.return_value = mock_response

        result = check_execution_status(mock_execution_id)
        assert result is True

    @patch("lyceum.shared.streaming.httpx.get")
    @patch("lyceum.shared.streaming.config")
    def test_failed_user_status(self, mock_config, mock_httpx_get, mock_execution_id):
        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "failed_user", "errors": "Error msg"}
        mock_httpx_get.return_value = mock_response

        result = check_execution_status(mock_execution_id)
        assert result is False

    @patch("lyceum.shared.streaming.httpx.get")
    @patch("lyceum.shared.streaming.config")
    def test_failed_system_status(self, mock_config, mock_httpx_get, mock_execution_id):
        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "failed_system"}
        mock_httpx_get.return_value = mock_response

        result = check_execution_status(mock_execution_id)
        assert result is False

    @patch("lyceum.shared.streaming.httpx.get")
    @patch("lyceum.shared.streaming.config")
    def test_timeout_status(self, mock_config, mock_httpx_get, mock_execution_id):
        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "timeout"}
        mock_httpx_get.return_value = mock_response

        result = check_execution_status(mock_execution_id)
        assert result is False

    @patch("lyceum.shared.streaming.httpx.get")
    @patch("lyceum.shared.streaming.config")
    def test_cancelled_status(self, mock_config, mock_httpx_get, mock_execution_id):
        mock_config.api_key = "test-key"
        mock_config.base_url = "https://api.lyceum.dev"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "cancelled"}
        mock_httpx_get.return_value = mock_response

        result = check_execution_status(mock_execution_id)
        assert result is False
