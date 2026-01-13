"""
EdgePulse Python SDK - Core monitoring and observability functionality.

This module provides decorators and utilities for monitoring function executions,
capturing timing data, errors, and sending telemetry to EdgePulse services.

Key properties:
- Fail-open by default: telemetry never breaks user code unless strict mode is enabled.
- API key is sent via HTTP header (not in payload).
- Optional background sending to minimize overhead.
- Retries with exponential backoff for transient failures.
- Configuration via EdgePulseConfig / configure() and environment variables.
"""

from __future__ import annotations

import dataclasses
import functools
import json
import logging
import os
import socket
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Mapping, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

_DEFAULT_URL = "https://edgepulse.jeremytrips.be/api/Invocation"
_ENV_API_KEY = "EDGEPULSE_PROJECT_KEY"
_ENV_URL = "EDGEPULSE_API_URL"
_ENV_DEBUG = "EDGEPULSE_DEBUG"


# ----------------------------
# Models
# ----------------------------


@dataclasses.dataclass(frozen=True)
class EdgePulseEventError:
    """Represents an error event that occurred during function execution."""

    message: str
    stack_trace: str


@dataclasses.dataclass(frozen=True)
class EdgePulseInvocation:
    """
    Represents a function invocation event.

    Note: API key is not included in payload; it is sent in HTTP headers.
    """

    function_name: str
    function_qualname: str
    module: str
    invoked_at: str
    status_code: int
    duration_ms: int
    error_event: Optional[EdgePulseEventError] = None
    is_debug: bool = False

    def to_json(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


# ----------------------------
# Configuration
# ----------------------------


@dataclasses.dataclass(frozen=True)
class EdgePulseConfig:
    """
    SDK configuration.

    enabled:
        If False, no telemetry is sent.
    strict:
        If True, configuration and telemetry failures may raise into user code.
        If False (default), telemetry is best-effort and never breaks user code.
    background:
        If True, telemetry is submitted to a background thread.
    is_debug:
        If True, invocations are marked as debug (notifications suppressed).
    """

    api_key: Optional[str] = None
    url: str = _DEFAULT_URL
    timeout_s: float = 10.0
    enabled: bool = True
    strict: bool = False
    background: bool = False
    is_debug: bool = False

    # retry policy
    max_retries: int = 2
    backoff_initial_s: float = 0.2
    backoff_multiplier: float = 2.0

    # headers
    auth_header_name: str = "Authorization"  # use "Authorization: Bearer <key>"
    auth_header_prefix: str = "Bearer"

    @staticmethod
    def from_env(
        *,
        enabled: Optional[bool] = None,
        strict: Optional[bool] = None,
        background: Optional[bool] = None,
        is_debug: Optional[bool] = None,
        timeout_s: Optional[float] = None,
        url: Optional[str] = None,
        max_retries: Optional[int] = None,
    ) -> "EdgePulseConfig":
        api_key = os.getenv(_ENV_API_KEY) or None
        env_url = os.getenv(_ENV_URL) or _DEFAULT_URL
        is_debug = is_debug or (os.getenv(_ENV_DEBUG, "0") in ("1", "true", "True"))
        return EdgePulseConfig(
            api_key=api_key,
            url=url or env_url,
            timeout_s=float(timeout_s) if timeout_s is not None else 10.0,
            enabled=bool(enabled) if enabled is not None else True,
            strict=bool(strict) if strict is not None else False,
            background=bool(background) if background is not None else False,
            is_debug=is_debug,
            max_retries=int(max_retries) if max_retries is not None else 2,
        )


# Global default config + background executor (optional)
_default_config: EdgePulseConfig = EdgePulseConfig.from_env()
_executor: Optional[ThreadPoolExecutor] = None


def configure(**kwargs: Any) -> EdgePulseConfig:
    """
    Configure the module-level default configuration.

    Example:
        configure(api_key="...", url="https://...", enabled=True, background=True)
    """
    global _default_config, _executor
    _default_config = dataclasses.replace(_default_config, **kwargs)

    # manage executor lifecycle based on background flag
    if _default_config.background and _executor is None:
        _executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="edgepulse")
    if not _default_config.background and _executor is not None:
        _executor.shutdown(wait=False)
        _executor = None

    return _default_config


# ----------------------------
# Transport
# ----------------------------


def _redact_dict(
    d: Mapping[str, Any],
    *,
    redact_keys: Tuple[str, ...] = ("authorization", "api_key", "key", "token"),
) -> Dict[str, Any]:
    """Shallow redaction helper for logging."""
    out: Dict[str, Any] = {}
    for k, v in d.items():
        if any(rk in k.lower() for rk in redact_keys):
            out[k] = "[REDACTED]"
        else:
            out[k] = v
    return out


class WebClient:
    """HTTP client for sending data to EdgePulse services."""

    def __init__(self, url: str, timeout_s: float = 10.0) -> None:
        self.url = url
        self.timeout_s = timeout_s

    def post_json(
        self,
        *,
        data: Dict[str, Any],
        headers: Dict[str, str],
        max_retries: int,
        backoff_initial_s: float,
        backoff_multiplier: float,
    ) -> bool:
        """
        Send POST request with JSON body. Returns True on success (2xx), False otherwise.
        Retries transient failures (timeouts, URLError, 5xx) with exponential backoff.
        """
        encoded = json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )

        attempt = 0
        backoff = max(0.0, backoff_initial_s)

        while True:
            attempt += 1
            req = Request(
                self.url,
                data=encoded,
                headers={"Content-Type": "application/json", **headers},
                method="POST",
            )

            try:
                with urlopen(req, timeout=self.timeout_s) as resp:
                    status = getattr(resp, "status", None) or 200
                    if 200 <= int(status) < 300:
                        logger.debug("EdgePulse POST succeeded (status=%s).", status)
                        return True

                    # Non-2xx without exception (possible with urllib)
                    logger.warning(
                        "EdgePulse POST returned non-2xx (status=%s).", status
                    )
                    if int(status) >= 500 and attempt <= (max_retries + 1):
                        time.sleep(backoff)
                        backoff *= backoff_multiplier
                        continue
                    return False

            except HTTPError as e:
                status = getattr(e, "code", None)
                body = ""
                try:
                    body = e.read().decode(errors="replace")
                except Exception:
                    body = "<unreadable>"
                logger.warning(
                    "EdgePulse HTTPError (status=%s reason=%s body=%s).",
                    status,
                    getattr(e, "reason", None),
                    body[:500],
                )

                if (
                    status is not None
                    and int(status) >= 500
                    and attempt <= (max_retries + 1)
                ):
                    time.sleep(backoff)
                    backoff *= backoff_multiplier
                    continue
                return False

            except (URLError, socket.timeout) as e:
                logger.warning(
                    "EdgePulse network error (%s).", getattr(e, "reason", str(e))
                )
                if attempt <= (max_retries + 1):
                    time.sleep(backoff)
                    backoff *= backoff_multiplier
                    continue
                return False

            except Exception as e:
                logger.exception("EdgePulse unexpected transport error: %s", e)
                return False


# ----------------------------
# Invocation building + sending
# ----------------------------


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_invocation(
    *,
    func: Callable[..., Any],
    invoked_at: str,
    status_code: int,
    duration_ms: int,
    error_event: Optional[EdgePulseEventError],
    is_debug: bool = False,
    function_name_override: Optional[str] = None,
) -> EdgePulseInvocation:
    func_name = function_name_override or getattr(func, "__name__", "unknown")
    return EdgePulseInvocation(
        function_name=func_name,
        function_qualname=function_name_override
        or getattr(func, "__qualname__", getattr(func, "__name__", "unknown")),
        module=getattr(func, "__module__", "unknown"),
        invoked_at=invoked_at,
        status_code=status_code,
        duration_ms=int(duration_ms),
        error_event=error_event,
        is_debug=is_debug,
    )


def _auth_headers(cfg: EdgePulseConfig) -> Dict[str, str]:
    if not cfg.api_key:
        return {}
    if cfg.auth_header_name.lower() == "authorization":
        return {cfg.auth_header_name: f"{cfg.auth_header_prefix} {cfg.api_key}".strip()}
    return {cfg.auth_header_name: cfg.api_key}


def _safe_send(
    invocation: EdgePulseInvocation,
    cfg: EdgePulseConfig,
    client: Optional[WebClient] = None,
) -> None:
    """
    Best-effort send. Never raises unless cfg.strict is True.
    """
    if not cfg.enabled:
        return

    if not cfg.api_key:
        msg = (
            f"{_ENV_API_KEY} environment variable is not set and no api_key configured."
        )
        if cfg.strict:
            raise ValueError(msg)
        logger.debug("EdgePulse disabled (missing api key): %s", msg)
        return

    try:
        client = client or WebClient(cfg.url, timeout_s=cfg.timeout_s)
        headers = _auth_headers(cfg)

        # Avoid logging secrets/payload
        logger.debug(
            "EdgePulse sending invocation (url=%s headers=%s function=%s status=%s duration_ms=%s).",
            cfg.url,
            _redact_dict(headers),
            invocation.function_qualname,
            invocation.status_code,
            invocation.duration_ms,
        )

        ok = client.post_json(
            data=invocation.to_json(),
            headers=headers,
            max_retries=cfg.max_retries,
            backoff_initial_s=cfg.backoff_initial_s,
            backoff_multiplier=cfg.backoff_multiplier,
        )
        if not ok:
            msg = "EdgePulse send failed (non-fatal)."
            if cfg.strict:
                raise RuntimeError(msg)
            logger.debug(msg)

    except Exception as e:
        if cfg.strict:
            raise
        logger.debug("EdgePulse send suppressed exception: %s", e, exc_info=True)


def store_invocation(
    invocation: EdgePulseInvocation,
    *,
    cfg: Optional[EdgePulseConfig] = None,
    client: Optional[WebClient] = None,
) -> None:
    """
    Store an invocation event by sending it to EdgePulse services.

    Honors cfg.background:
      - False: send inline
      - True: submit to a background thread (best-effort)
    """
    cfg = cfg or _default_config

    if cfg.background:
        if _executor is None:
            # if user toggled env-only background without calling configure()
            configure(background=True)
        if _executor is not None:
            _executor.submit(_safe_send, invocation, cfg, client)
            return

    _safe_send(invocation, cfg, client)


# ----------------------------
# Decorator (sync)
# ----------------------------


def with_edgepulse(
    func: Optional[Callable[..., Any]] = None,
    *,
    cfg: Optional[EdgePulseConfig] = None,
    function_name: Optional[str] = None,
) -> Callable[..., Any]:
    """
    Decorator to monitor function executions with EdgePulse.

    Usage:
        @with_edgepulse
        def f(): ...

        @with_edgepulse(function_name="custom_name")
        def f(): ...

    Args:
        func: The function to decorate (automatically passed when used without parentheses).
        cfg: Optional EdgePulseConfig to override default configuration.
        function_name: Optional custom name to use for the function in telemetry.
                      If not provided, uses the actual function name.

    Notes:
      - Telemetry is best-effort and will not break user code unless strict=True.
    """
    cfg_final = cfg or _default_config

    def decorate(target: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(target)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            invoked_at = _utc_now_iso()
            t0 = time.perf_counter()
            try:
                result = target(*args, **kwargs)
                duration_ms = int((time.perf_counter() - t0) * 1000)
                inv = _build_invocation(
                    func=target,
                    invoked_at=invoked_at,
                    status_code=200,
                    duration_ms=duration_ms,
                    error_event=None,
                    is_debug=cfg_final.is_debug,
                    function_name_override=function_name,
                )
                store_invocation(inv, cfg=cfg_final)
                return result
            except Exception as e:
                duration_ms = int((time.perf_counter() - t0) * 1000)
                err = EdgePulseEventError(
                    message=str(e), stack_trace=traceback.format_exc()
                )
                inv = _build_invocation(
                    func=target,
                    invoked_at=invoked_at,
                    status_code=500,
                    duration_ms=duration_ms,
                    error_event=err,
                    is_debug=cfg_final.is_debug,
                    function_name_override=function_name,
                )
                store_invocation(inv, cfg=cfg_final)
                raise

        return wrapper

    return decorate(func) if func is not None else decorate
