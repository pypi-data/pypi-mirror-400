"""
Wedata Header Provider Plugin for MLflow

This module implements a request header provider that adds headers
to all Wedata MLflow tracking requests.
"""

import sys
import os
from typing import Dict

try:
    # NOTE: MLflow is a runtime dependency of this plugin. We keep a fallback to
    # allow importing this package in environments where mlflow isn't installed
    # (e.g. minimal linting or doc builds).
    from mlflow.tracking.request_header.abstract_request_header_provider import (  # type: ignore[import-not-found]
        RequestHeaderProvider,
    )
except ModuleNotFoundError:  # pragma: no cover
    class RequestHeaderProvider:  # type: ignore[misc]
        """Fallback base class when MLflow is not available."""

        def in_context(self) -> bool:  # noqa: D401
            return True

        def request_headers(self) -> Dict[str, str]:
            return {}

_DEBUG_ENV_VAR = "WEDATA_MLFLOW_HEADER_PLUGIN_DEBUG"
_MLFLOW_SERVICE_IP_ENV_VAR = "MLFLOW_SERVICE_IP"
_MLFLOW_SERVICE_PORT_ENV_VAR = "MLFLOW_SERVICE_PORT"
_MLFLOW_SERVICE_IP_HEADER_KEY = "X-Target-Service-IP"
_MLFLOW_SERVICE_PORT_HEADER_KEY = "X-Target-Service-PORT"

def _is_debug_enabled() -> bool:
    """Return True if debug mode is enabled via environment variable."""
    raw = os.environ.get(_DEBUG_ENV_VAR, "")
    return str(raw).strip().lower() in {"1", "true", "yes", "y", "on"}


def _looks_sensitive_header_key(key: str) -> bool:
    k = key.lower()
    return any(token in k for token in ("authorization", "token", "secret", "password", "key", "cookie"))


def _mask_value(value: str, *, keep_prefix: int = 3, keep_suffix: int = 2) -> str:
    """Mask a string value to avoid leaking secrets in debug logs."""
    s = "" if value is None else str(value)
    if len(s) <= (keep_prefix + keep_suffix + 3):
        return "***"
    return f"{s[:keep_prefix]}***{s[-keep_suffix:]}"


def _format_headers_for_log(headers: Dict[str, str]) -> Dict[str, str]:
    """Return a sanitized copy of headers for logging."""
    sanitized: Dict[str, str] = {}
    for k, v in headers.items():
        sanitized[k] = _mask_value(v) if _looks_sensitive_header_key(k) else str(v)
    return sanitized


def _debug_print(message: str) -> None:
    """Print debug message to stderr when debug mode is enabled."""
    if not _is_debug_enabled():
        return
    print(f"[wedata-mlflow-header-plugin][debug] {message}", file=sys.stderr)


class WedataRequestHeaderProvider(RequestHeaderProvider):
    """
    Provides custom headers for MLflow tracking requests.
    
    This provider adds the following headers:
    - X-Target-Service-IP: Target service IP address
    - X-Target-Service-PORT: Target service port
    
    The values can be configured via environment variables:
    - MLFLOW_SERVICE_IP (default: "127.0.0.1")
    - MLFLOW_SERVICE_PORT (default: "5000")
    """

    def in_context(self) -> bool:
        """
        Check if this provider should be active.
        
        Returns:
            bool: Always returns True to ensure headers are added to all requests
        """
        return True

    def request_headers(self) -> Dict[str, str]:
        """
        Generate the custom headers for MLflow requests.
        
        Returns:
            Dict[str, str]: Dictionary containing the custom headers
        """
        # Get values from environment variables with defaults
        service_ip = os.environ.get(_MLFLOW_SERVICE_IP_ENV_VAR)
        service_port = os.environ.get(_MLFLOW_SERVICE_PORT_ENV_VAR)

        _debug_print(
            "Resolving headers from environment: "
            f"{_MLFLOW_SERVICE_IP_ENV_VAR}={service_ip!r}, "
            f"{_MLFLOW_SERVICE_PORT_ENV_VAR}={service_port!r}"
        )

        headers = {}

        if service_ip and service_port:
            headers[_MLFLOW_SERVICE_IP_HEADER_KEY] = service_ip
            headers[_MLFLOW_SERVICE_PORT_HEADER_KEY] = service_port
        else:
            _debug_print("No service IP or port found, skipping adding headers")

        _debug_print(f"Returning request headers: {_format_headers_for_log(headers)}")
        return headers

