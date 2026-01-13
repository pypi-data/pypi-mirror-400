"""
Comprehensive tests for EdgePulse Python SDK core module.

Tests cover:
- Models and serialization
- Configuration (environment variables, defaults, configure())
- HTTP client with retries and error handling
- Decorator functionality (success, errors, timing)
- Background sending
- Strict vs non-strict modes
- Authentication headers
"""

import json
import os
import time
import unittest
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, Mock, patch
from urllib.error import HTTPError, URLError

from Edgepulse.core import _auth_headers  # type: ignore[reportPrivateUsage]
from Edgepulse.core import _build_invocation  # type: ignore[reportPrivateUsage]
from Edgepulse.core import _redact_dict  # type: ignore[reportPrivateUsage]
from Edgepulse.core import _safe_send  # type: ignore[reportPrivateUsage]
from Edgepulse.core import _utc_now_iso  # type: ignore[reportPrivateUsage]
from Edgepulse.core import (
    EdgePulseConfig,
    EdgePulseEventError,
    EdgePulseInvocation,
    WebClient,
    configure,
    store_invocation,
    with_edgepulse,
)


class TestModels(unittest.TestCase):
    """Test data models."""

    def test_edge_pulse_event_error(self) -> None:
        """Test EdgePulseEventError model."""
        error: EdgePulseEventError = EdgePulseEventError(
            message="Test error",
            stack_trace="Traceback...",
        )
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.stack_trace, "Traceback...")

    def test_edge_pulse_invocation_to_json(self) -> None:
        """Test EdgePulseInvocation serialization."""
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test_func",
            function_qualname="module.test_func",
            module="test_module",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
            error_event=None,
        )

        result: Dict[str, Any] = invocation.to_json()
        self.assertEqual(result["function_name"], "test_func")
        self.assertEqual(result["function_qualname"], "module.test_func")
        self.assertEqual(result["module"], "test_module")
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["duration_ms"], 100)
        self.assertIsNone(result["error_event"])

    def test_edge_pulse_invocation_with_error(self) -> None:
        """Test EdgePulseInvocation with error event."""
        error: EdgePulseEventError = EdgePulseEventError(
            message="Test error",
            stack_trace="Traceback...",
        )
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test_func",
            function_qualname="test_func",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=500,
            duration_ms=50,
            error_event=error,
        )

        result: Dict[str, Any] = invocation.to_json()
        self.assertEqual(result["status_code"], 500)
        self.assertIsNotNone(result["error_event"])
        self.assertEqual(result["error_event"]["message"], "Test error")
        self.assertEqual(result["error_event"]["stack_trace"], "Traceback...")


class TestConfiguration(unittest.TestCase):
    """Test configuration management."""

    old_api_key: Optional[str]
    old_url: Optional[str]

    def setUp(self) -> None:
        """Clear environment variables before each test."""
        self.old_api_key = os.environ.pop("EDGEPULSE_PROJECT_KEY", None)
        self.old_url = os.environ.pop("EDGEPULSE_API_URL", None)

    def tearDown(self) -> None:
        """Restore environment variables after each test."""
        if self.old_api_key:
            os.environ["EDGEPULSE_PROJECT_KEY"] = self.old_api_key
        if self.old_url:
            os.environ["EDGEPULSE_API_URL"] = self.old_url

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        config: EdgePulseConfig = EdgePulseConfig()
        self.assertIsNone(config.api_key)
        self.assertEqual(config.url, "https://edgepulse.jeremytrips.be/api/Invocation")
        self.assertEqual(config.timeout_s, 10.0)
        self.assertTrue(config.enabled)
        self.assertFalse(config.strict)
        self.assertFalse(config.background)
        self.assertEqual(config.max_retries, 2)
        self.assertEqual(config.backoff_initial_s, 0.2)
        self.assertEqual(config.backoff_multiplier, 2.0)

    def test_config_from_env_with_api_key(self) -> None:
        """Test configuration from environment variables."""
        os.environ["EDGEPULSE_PROJECT_KEY"] = "test-api-key"
        os.environ["EDGEPULSE_API_URL"] = "https://example.com/api"

        config: EdgePulseConfig = EdgePulseConfig.from_env()
        self.assertEqual(config.api_key, "test-api-key")
        self.assertEqual(config.url, "https://example.com/api")

    def test_config_from_env_override_url(self) -> None:
        """Test URL override in from_env."""
        os.environ["EDGEPULSE_API_URL"] = "https://example.com/api"

        config: EdgePulseConfig = EdgePulseConfig.from_env(
            url="https://override.com/api"
        )
        self.assertEqual(config.url, "https://override.com/api")

    def test_config_from_env_options(self) -> None:
        """Test configuration options from from_env."""
        config: EdgePulseConfig = EdgePulseConfig.from_env(
            enabled=False,
            strict=True,
            background=True,
            timeout_s=5.0,
            max_retries=3,
        )
        self.assertFalse(config.enabled)
        self.assertTrue(config.strict)
        self.assertTrue(config.background)
        self.assertEqual(config.timeout_s, 5.0)
        self.assertEqual(config.max_retries, 3)

    def test_configure_global(self) -> None:
        """Test configure() updates global config."""
        new_config: EdgePulseConfig = configure(
            api_key="new-key",
            url="https://new.com/api",
            enabled=True,
            strict=False,
        )
        self.assertEqual(new_config.api_key, "new-key")
        self.assertEqual(new_config.url, "https://new.com/api")
        self.assertTrue(new_config.enabled)
        self.assertFalse(new_config.strict)


class TestWebClient(unittest.TestCase):
    """Test HTTP client functionality."""

    def test_web_client_init(self) -> None:
        """Test WebClient initialization."""
        client: WebClient = WebClient("https://example.com/api", timeout_s=5.0)
        self.assertEqual(client.url, "https://example.com/api")
        self.assertEqual(client.timeout_s, 5.0)

    @patch("Edgepulse.core.urlopen")
    def test_post_json_success(self, mock_urlopen: MagicMock) -> None:
        """Test successful POST request."""
        mock_response: MagicMock = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        client: WebClient = WebClient("https://example.com/api")
        result: bool = client.post_json(
            data={"test": "data"},
            headers={"Authorization": "Bearer test"},
            max_retries=2,
            backoff_initial_s=0.1,
            backoff_multiplier=2.0,
        )

        self.assertTrue(result)
        mock_urlopen.assert_called_once()

    @patch("Edgepulse.core.urlopen")
    def test_post_json_http_error_4xx(self, mock_urlopen: MagicMock) -> None:
        """Test HTTP 4xx error (no retry)."""
        mock_urlopen.side_effect = HTTPError(
            url="https://example.com/api",
            code=400,
            msg="Bad Request",
            hdrs={},  # type: ignore[arg-type]
            fp=BytesIO(b'{"error": "bad request"}'),
        )

        client: WebClient = WebClient("https://example.com/api")
        result: bool = client.post_json(
            data={"test": "data"},
            headers={},
            max_retries=2,
            backoff_initial_s=0.01,
            backoff_multiplier=2.0,
        )

        self.assertFalse(result)
        # Should only try once for 4xx errors
        self.assertEqual(mock_urlopen.call_count, 1)

    @patch("Edgepulse.core.time.sleep")
    @patch("Edgepulse.core.urlopen")
    def test_post_json_http_error_5xx_retry(
        self, mock_urlopen: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """Test HTTP 5xx error triggers retry."""
        mock_urlopen.side_effect = HTTPError(
            url="https://example.com/api",
            code=500,
            msg="Internal Server Error",
            hdrs={},  # type: ignore[arg-type]
            fp=BytesIO(b"Server error"),
        )

        client: WebClient = WebClient("https://example.com/api")
        result: bool = client.post_json(
            data={"test": "data"},
            headers={},
            max_retries=2,
            backoff_initial_s=0.1,
            backoff_multiplier=2.0,
        )

        self.assertFalse(result)
        # Should try max_retries + 1 times (initial + retries)
        self.assertGreaterEqual(mock_urlopen.call_count, 3)
        # Should sleep between retries
        self.assertGreaterEqual(mock_sleep.call_count, 2)

    @patch("Edgepulse.core.time.sleep")
    @patch("Edgepulse.core.urlopen")
    def test_post_json_url_error_retry(
        self, mock_urlopen: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """Test URLError triggers retry."""
        mock_urlopen.side_effect = URLError("Connection refused")

        client: WebClient = WebClient("https://example.com/api")
        result: bool = client.post_json(
            data={"test": "data"},
            headers={},
            max_retries=2,
            backoff_initial_s=0.1,
            backoff_multiplier=2.0,
        )

        self.assertFalse(result)
        # Should try max_retries + 1 times (initial + retries)
        self.assertGreaterEqual(mock_urlopen.call_count, 3)
        self.assertGreaterEqual(mock_sleep.call_count, 2)

    @patch("Edgepulse.core.time.sleep")
    @patch("Edgepulse.core.urlopen")
    def test_post_json_retry_then_success(
        self, mock_urlopen: MagicMock, mock_sleep: MagicMock
    ) -> None:
        """Test retry succeeds after initial failure."""
        mock_response: MagicMock = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        # Fail first, then succeed
        mock_urlopen.side_effect = [
            URLError("Connection refused"),
            mock_response,
        ]

        client: WebClient = WebClient("https://example.com/api")
        result: bool = client.post_json(
            data={"test": "data"},
            headers={},
            max_retries=2,
            backoff_initial_s=0.1,
            backoff_multiplier=2.0,
        )

        self.assertTrue(result)
        self.assertGreaterEqual(mock_urlopen.call_count, 2)
        self.assertGreaterEqual(mock_sleep.call_count, 1)

    @patch("Edgepulse.core.urlopen")
    def test_post_json_unexpected_exception(self, mock_urlopen: MagicMock) -> None:
        """Test unexpected exception is caught."""
        mock_urlopen.side_effect = Exception("Unexpected error")

        client: WebClient = WebClient("https://example.com/api")
        result: bool = client.post_json(
            data={"test": "data"},
            headers={},
            max_retries=2,
            backoff_initial_s=0.01,
            backoff_multiplier=2.0,
        )

        self.assertFalse(result)
        # Should not retry on unexpected exceptions
        self.assertEqual(mock_urlopen.call_count, 1)


class TestHelpers(unittest.TestCase):
    """Test helper functions."""

    def test_utc_now_iso(self) -> None:
        """Test UTC timestamp generation."""
        timestamp: str = _utc_now_iso()
        # Should be valid ISO format
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_build_invocation(self) -> None:
        """Test invocation building."""

        def test_func() -> None:
            pass

        inv: EdgePulseInvocation = _build_invocation(
            func=test_func,
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
            error_event=None,
        )

        self.assertEqual(inv.function_name, "test_func")
        # qualname includes the full path
        self.assertIn("test_func", inv.function_qualname)
        self.assertEqual(inv.status_code, 200)
        self.assertEqual(inv.duration_ms, 100)

    def test_build_invocation_with_function_name_override(self) -> None:
        """Test invocation building with custom function name."""

        def test_func() -> None:
            pass

        inv: EdgePulseInvocation = _build_invocation(
            func=test_func,
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
            error_event=None,
            function_name_override="custom_function_name",
        )

        # Should use the override name instead of actual function name
        self.assertEqual(inv.function_name, "custom_function_name")
        self.assertEqual(inv.function_qualname, "custom_function_name")
        self.assertEqual(inv.status_code, 200)
        self.assertEqual(inv.duration_ms, 100)

    def test_auth_headers_with_authorization(self) -> None:
        """Test auth headers with Authorization header."""
        config: EdgePulseConfig = EdgePulseConfig(api_key="test-key")
        headers: Dict[str, str] = _auth_headers(config)
        self.assertEqual(headers, {"Authorization": "Bearer test-key"})

    def test_auth_headers_without_key(self) -> None:
        """Test auth headers without API key."""
        config: EdgePulseConfig = EdgePulseConfig(api_key=None)
        headers: Dict[str, str] = _auth_headers(config)
        self.assertEqual(headers, {})

    def test_auth_headers_custom_header(self) -> None:
        """Test auth headers with custom header name."""
        config: EdgePulseConfig = EdgePulseConfig(
            api_key="test-key",
            auth_header_name="X-API-Key",
        )
        headers: Dict[str, str] = _auth_headers(config)
        self.assertEqual(headers, {"X-API-Key": "test-key"})

    def test_redact_dict(self) -> None:
        """Test dictionary redaction for logging."""
        data: Dict[str, str] = {
            "Authorization": "Bearer secret",
            "api_key": "secret-key",
            "safe_value": "not-secret",
        }
        redacted: Dict[str, Any] = _redact_dict(data)
        self.assertEqual(redacted["Authorization"], "[REDACTED]")
        self.assertEqual(redacted["api_key"], "[REDACTED]")
        self.assertEqual(redacted["safe_value"], "not-secret")


class TestSafeSend(unittest.TestCase):
    """Test safe send functionality."""

    old_api_key: Optional[str]

    def setUp(self) -> None:
        """Clear environment before each test."""
        self.old_api_key = os.environ.pop("EDGEPULSE_PROJECT_KEY", None)

    def tearDown(self) -> None:
        """Restore environment after each test."""
        if self.old_api_key:
            os.environ["EDGEPULSE_PROJECT_KEY"] = self.old_api_key

    def test_safe_send_disabled(self) -> None:
        """Test safe send with disabled config."""
        config: EdgePulseConfig = EdgePulseConfig(enabled=False, api_key="test")
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        # Should not raise
        _safe_send(invocation, config)

    def test_safe_send_missing_api_key_non_strict(self) -> None:
        """Test safe send with missing API key in non-strict mode."""
        config: EdgePulseConfig = EdgePulseConfig(
            enabled=True, strict=False, api_key=None
        )
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        # Should not raise in non-strict mode
        _safe_send(invocation, config)

    def test_safe_send_missing_api_key_strict(self) -> None:
        """Test safe send with missing API key in strict mode."""
        config: EdgePulseConfig = EdgePulseConfig(
            enabled=True, strict=True, api_key=None
        )
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        # Should raise in strict mode
        with self.assertRaises(ValueError):
            _safe_send(invocation, config)

    @patch("Edgepulse.core.WebClient")
    def test_safe_send_success(self, mock_client_class: MagicMock) -> None:
        """Test successful safe send."""
        mock_client: Mock = Mock()
        mock_client.post_json.return_value = True
        mock_client_class.return_value = mock_client

        config: EdgePulseConfig = EdgePulseConfig(enabled=True, api_key="test-key")
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        _safe_send(invocation, config)
        mock_client.post_json.assert_called_once()

    @patch("Edgepulse.core.WebClient")
    def test_safe_send_failure_non_strict(self, mock_client_class: MagicMock) -> None:
        """Test failed send in non-strict mode."""
        mock_client: Mock = Mock()
        mock_client.post_json.return_value = False
        mock_client_class.return_value = mock_client

        config: EdgePulseConfig = EdgePulseConfig(
            enabled=True, strict=False, api_key="test-key"
        )
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        # Should not raise in non-strict mode
        _safe_send(invocation, config)

    @patch("Edgepulse.core.WebClient")
    def test_safe_send_failure_strict(self, mock_client_class: MagicMock) -> None:
        """Test failed send in strict mode."""
        mock_client: Mock = Mock()
        mock_client.post_json.return_value = False
        mock_client_class.return_value = mock_client

        config: EdgePulseConfig = EdgePulseConfig(
            enabled=True, strict=True, api_key="test-key"
        )
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        # Should raise in strict mode
        with self.assertRaises(RuntimeError):
            _safe_send(invocation, config)


class TestDecorator(unittest.TestCase):
    """Test @with_edgepulse decorator."""

    def setUp(self) -> None:
        """Set up environment for tests."""
        os.environ["EDGEPULSE_PROJECT_KEY"] = "test-key"
        configure(enabled=True, background=False, api_key="test-key")

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_success(self, mock_store: MagicMock) -> None:
        """Test decorator on successful function execution."""

        @with_edgepulse
        def test_func() -> str:
            return "success"

        result: str = test_func()

        self.assertEqual(result, "success")
        mock_store.assert_called_once()

        # Check invocation details
        inv: EdgePulseInvocation = mock_store.call_args[0][0]
        self.assertEqual(inv.function_name, "test_func")
        self.assertEqual(inv.status_code, 200)
        self.assertIsNone(inv.error_event)
        self.assertGreaterEqual(inv.duration_ms, 0)

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_with_args(self, mock_store: MagicMock) -> None:
        """Test decorator with function arguments."""

        @with_edgepulse
        def test_func(a: int, b: int, c: Optional[int] = None) -> int:
            return a + b + (c or 0)

        result: int = test_func(1, 2, c=3)

        self.assertEqual(result, 6)
        mock_store.assert_called_once()

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_error(self, mock_store: MagicMock) -> None:
        """Test decorator on function that raises exception."""

        @with_edgepulse
        def test_func() -> None:
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            test_func()

        mock_store.assert_called_once()

        # Check invocation details
        inv: EdgePulseInvocation = mock_store.call_args[0][0]
        self.assertEqual(inv.function_name, "test_func")
        self.assertEqual(inv.status_code, 500)
        self.assertIsNotNone(inv.error_event)
        assert inv.error_event is not None  # Type guard for mypy
        self.assertEqual(inv.error_event.message, "Test error")
        self.assertIn("ValueError", inv.error_event.stack_trace)

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_timing(self, mock_store: MagicMock) -> None:
        """Test decorator captures timing correctly."""

        @with_edgepulse
        def test_func() -> str:
            time.sleep(0.1)
            return "done"

        test_func()

        inv: EdgePulseInvocation = mock_store.call_args[0][0]
        # Should be at least 100ms
        self.assertGreaterEqual(inv.duration_ms, 90)

    def test_decorator_with_custom_config(self) -> None:
        """Test decorator with custom configuration."""
        custom_config: EdgePulseConfig = EdgePulseConfig(
            enabled=False,
            api_key="custom-key",
        )

        @with_edgepulse(cfg=custom_config)
        def test_func() -> str:
            return "success"

        # Should not raise even though sending is disabled
        result: str = test_func()
        self.assertEqual(result, "success")

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_preserves_function_metadata(self, mock_store: MagicMock) -> None:
        """Test decorator preserves function name and docstring."""

        @with_edgepulse
        def test_func() -> str:
            """Test docstring."""
            return "success"

        self.assertEqual(test_func.__name__, "test_func")
        self.assertEqual(test_func.__doc__, "Test docstring.")

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_with_custom_function_name(self, mock_store: MagicMock) -> None:
        """Test decorator with custom function name."""

        @with_edgepulse(function_name="custom_handler")
        def test_func() -> str:
            return "success"

        result: str = test_func()

        self.assertEqual(result, "success")
        mock_store.assert_called_once()

        # Check invocation details
        inv: EdgePulseInvocation = mock_store.call_args[0][0]
        self.assertEqual(inv.function_name, "custom_handler")
        self.assertEqual(inv.function_qualname, "custom_handler")
        self.assertEqual(inv.status_code, 200)
        self.assertIsNone(inv.error_event)

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_with_custom_function_name_on_error(
        self, mock_store: MagicMock
    ) -> None:
        """Test decorator with custom function name when function raises error."""

        @with_edgepulse(function_name="custom_error_handler")
        def test_func() -> None:
            raise ValueError("Test error")

        with self.assertRaises(ValueError):
            test_func()

        mock_store.assert_called_once()

        # Check invocation details
        inv: EdgePulseInvocation = mock_store.call_args[0][0]
        self.assertEqual(inv.function_name, "custom_error_handler")
        self.assertEqual(inv.function_qualname, "custom_error_handler")
        self.assertEqual(inv.status_code, 500)
        self.assertIsNotNone(inv.error_event)
        assert inv.error_event is not None  # Type guard for mypy
        self.assertEqual(inv.error_event.message, "Test error")

    @patch("Edgepulse.core.store_invocation")
    def test_decorator_custom_name_with_config(self, mock_store: MagicMock) -> None:
        """Test decorator with both custom function name and config."""
        custom_config: EdgePulseConfig = EdgePulseConfig(
            enabled=True,
            api_key="custom-key",
        )

        @with_edgepulse(cfg=custom_config, function_name="api_v2_handler")
        def test_func(x: int) -> int:
            return x * 2

        result: int = test_func(5)

        self.assertEqual(result, 10)
        mock_store.assert_called_once()

        # Check invocation details
        inv: EdgePulseInvocation = mock_store.call_args[0][0]
        self.assertEqual(inv.function_name, "api_v2_handler")
        self.assertEqual(inv.function_qualname, "api_v2_handler")
        self.assertEqual(inv.status_code, 200)


class TestStoreInvocation(unittest.TestCase):
    """Test store_invocation function."""

    def setUp(self) -> None:
        """Set up for tests."""
        configure(enabled=True, background=False, api_key="test-key")

    @patch("Edgepulse.core._safe_send")
    def test_store_invocation_inline(self, mock_send: MagicMock) -> None:
        """Test store_invocation sends inline when background=False."""
        config: EdgePulseConfig = EdgePulseConfig(
            enabled=True, background=False, api_key="test-key"
        )
        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        store_invocation(invocation, cfg=config)

        mock_send.assert_called_once()

    @patch("Edgepulse.core._executor")
    def test_store_invocation_background(self, mock_executor: MagicMock) -> None:
        """Test store_invocation submits to background when background=True."""
        mock_executor_instance: Mock = Mock()
        mock_executor.return_value = mock_executor_instance

        # Configure background mode
        configure(background=True, api_key="test-key")

        invocation: EdgePulseInvocation = EdgePulseInvocation(
            function_name="test",
            function_qualname="test",
            module="test",
            invoked_at="2024-01-01T00:00:00Z",
            status_code=200,
            duration_ms=100,
        )

        with patch("Edgepulse.core._executor", mock_executor_instance):
            store_invocation(invocation)
            mock_executor_instance.submit.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end functionality."""

    def setUp(self) -> None:
        """Set up environment."""
        os.environ["EDGEPULSE_PROJECT_KEY"] = "test-key"
        configure(enabled=True, background=False, api_key="test-key")

    @patch("Edgepulse.core.urlopen")
    def test_end_to_end_success(self, mock_urlopen: MagicMock) -> None:
        """Test end-to-end flow with successful function execution."""
        mock_response: MagicMock = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        @with_edgepulse
        def my_function(x: int, y: int) -> int:
            return x + y

        result: int = my_function(2, 3)

        self.assertEqual(result, 5)
        mock_urlopen.assert_called_once()

        # Verify request details
        call_args: Any = mock_urlopen.call_args
        request: Any = call_args[0][0]

        # Check headers
        self.assertIn("Authorization", request.headers)
        self.assertEqual(request.headers["Authorization"], "Bearer test-key")
        self.assertEqual(request.headers["Content-type"], "application/json")

        # Check payload
        payload: Dict[str, Any] = json.loads(request.data.decode("utf-8"))
        self.assertEqual(payload["function_name"], "my_function")
        self.assertEqual(payload["status_code"], 200)
        self.assertIsNone(payload["error_event"])

    @patch("Edgepulse.core.urlopen")
    def test_end_to_end_error(self, mock_urlopen: MagicMock) -> None:
        """Test end-to-end flow with function error."""
        mock_response: MagicMock = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        @with_edgepulse
        def my_function() -> None:
            raise RuntimeError("Something went wrong")

        with self.assertRaises(RuntimeError):
            my_function()

        mock_urlopen.assert_called_once()

        # Check payload
        call_args: Any = mock_urlopen.call_args
        request: Any = call_args[0][0]
        payload: Dict[str, Any] = json.loads(request.data.decode("utf-8"))

        self.assertEqual(payload["status_code"], 500)
        self.assertIsNotNone(payload["error_event"])
        self.assertEqual(payload["error_event"]["message"], "Something went wrong")
        self.assertIn("RuntimeError", payload["error_event"]["stack_trace"])

    @patch("Edgepulse.core.urlopen")
    def test_fail_open_behavior(self, mock_urlopen: MagicMock) -> None:
        """Test fail-open behavior: telemetry errors don't break user code."""
        # Simulate network failure
        mock_urlopen.side_effect = URLError("Network error")

        configure(enabled=True, strict=False, api_key="test-key")

        @with_edgepulse
        def my_function() -> str:
            return "success"

        # Should still succeed despite telemetry failure
        result: str = my_function()
        self.assertEqual(result, "success")

    @patch("Edgepulse.core.urlopen")
    def test_end_to_end_custom_function_name(self, mock_urlopen: MagicMock) -> None:
        """Test end-to-end flow with custom function name."""
        mock_response: MagicMock = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        @with_edgepulse(function_name="payment_processor_v2")
        def process_payment(amount: int) -> int:
            return amount * 2

        result: int = process_payment(100)

        self.assertEqual(result, 200)
        mock_urlopen.assert_called_once()

        # Verify request payload contains custom function name
        call_args: Any = mock_urlopen.call_args
        request: Any = call_args[0][0]
        payload: Dict[str, Any] = json.loads(request.data.decode("utf-8"))

        # Custom name should be in the payload, not the actual function name
        self.assertEqual(payload["function_name"], "payment_processor_v2")
        self.assertEqual(payload["function_qualname"], "payment_processor_v2")
        self.assertEqual(payload["status_code"], 200)
        self.assertIsNone(payload["error_event"])


if __name__ == "__main__":
    unittest.main()
