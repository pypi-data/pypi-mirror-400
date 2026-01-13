"""
EdgePulse Python SDK

A Python SDK for monitoring function executions and sending telemetry data
to EdgePulse services for observability and performance tracking.
"""

from .core import (
    EdgePulseEventError,
    EdgePulseInvocation,
    WebClient,
    store_invocation,
    with_edgepulse,
)

__version__ = "0.1.0"
__author__ = "EdgePulse Team"
__email__ = "support@edgepulse.com"

__all__ = [
    "with_edgepulse",
    "EdgePulseInvocation",
    "EdgePulseEventError",
    "WebClient",
    "store_invocation",
]
