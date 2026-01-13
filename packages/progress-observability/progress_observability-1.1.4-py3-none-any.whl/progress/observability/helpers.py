"""
Helper functions for Progress Observability instrumentation
"""

import os
import sys
from typing import Optional, Dict, Any
from .constants import SDK_ENV_VARS

class ObservabilityTelemetry:
    """Helper class for Progress Observability"""
    
    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ObservabilityTelemetry, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self._telemetry_enabled = False
        self._posthog = None
        self._curr_anon_id = None
    
    def _anon_id(self) -> str:
        return "disabled"
    
    def _context(self) -> Dict[str, Any]:
        return {}
    
    def capture(self, event: str, event_properties: Dict[str, Any] = {}) -> None:
        pass
    
    def log_exception(self, exception: Exception) -> None:
        pass
    
    def feature_enabled(self, key: str) -> bool:
        return False


def patch_traceloop_modules() -> None:
    """Patch Traceloop modules with Observability implementations"""
    sys.modules['traceloop.sdk.telemetry'] = type(sys)('telemetry')
    sys.modules['traceloop.sdk.telemetry'].Telemetry = ObservabilityTelemetry

    # Patch Traceloop with Progress Observability's default span processor
    from traceloop.sdk import Traceloop
    Traceloop.get_default_span_processor = staticmethod(observability_get_default_span_processor)


def clear_sdk_env_vars() -> None:
    """Clear all sdk* environment variables to prevent conflicts"""
    for var in SDK_ENV_VARS:
        if var in os.environ:
            del os.environ[var]


def is_http_endpoint(endpoint: Optional[str]) -> bool:
    """Check if endpoint is HTTP/HTTPS (vs gRPC)"""
    return bool(endpoint) and (
        endpoint.startswith("http://") or endpoint.startswith("https://")
    )


def observability_get_default_span_processor(
    disable_batch: bool = False,
    api_endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    headers: Optional[Dict[str, Any]] = None,
    exporter: Optional[Any] = None
) -> Any:
    """Observability version of get_default_span_processor with dual auth headers"""
    from traceloop.sdk.tracing.tracing import get_default_span_processor
    
    if headers is None:
        if api_key is None:
            api_key = os.getenv("OBSERVABILITY_API_KEY")

        # Only add headers for HTTP endpoints
        if is_http_endpoint(api_endpoint):
            headers = {
                "Authorization": f"Bearer {api_key}",
                "X-Api-Key": api_key
            }
        else:
            headers = {}  # No headers for gRPC endpoints
    
    if api_endpoint is None:
        api_endpoint = os.getenv("OBSERVABILITY_ENDPOINT")
    
    return get_default_span_processor(api_key, disable_batch, api_endpoint, headers, exporter)


def init_environment(app_name: str, endpoint: Optional[str], api_key: Optional[str], trace_content: Optional[bool]) -> tuple[str, Optional[str], Optional[str]]:
    """Initialize environment variables with Observability overrides"""
    endpoint = os.getenv("OBSERVABILITY_ENDPOINT") or endpoint
    api_key = os.getenv("OBSERVABILITY_API_KEY") or api_key
    app_name = os.getenv("OBSERVABILITY_APP_NAME") or app_name
    
    # Handle trace_content from environment variable or parameter
    env_trace_content = os.getenv("OBSERVABILITY_TRACE_CONTENT")
    if env_trace_content is not None:
        trace_content_value = env_trace_content.lower() in ('true', '1', 'yes')
    elif trace_content is not None:
        trace_content_value = trace_content
    else:
        trace_content_value = True
    
    # Set TRACELOOP_TRACE_CONTENT for the underlying SDK only if false (default is true)
    if not trace_content_value:
        os.environ['TRACELOOP_TRACE_CONTENT'] = 'false'
    
    import logging

    # Disable metrics exporter - OBSERVABILITY focuses on spans/traces only
    if 'OTEL_METRICS_EXPORTER' not in os.environ:
        os.environ['OTEL_METRICS_EXPORTER'] = 'none'

    # Suppress metrics exporter 404 errors (underlying SDK doesn't fully respect the env var)
    logger = logging.getLogger("opentelemetry.exporter.otlp.proto.http.metric_exporter")
    logger.disabled = True

    # Validate endpoint format if provided
    if endpoint and not (endpoint.startswith("http://") or endpoint.startswith("https://") or ":" in endpoint):
        raise ValueError(f"Invalid endpoint format: {endpoint}")
        
    return app_name, endpoint, api_key
def setup_api_key_headers(api_key: str, endpoint: Optional[str], init_kwargs: Dict[str, Any], kwargs: Dict[str, Any]) -> None:
    """Setup API key validation and authentication headers"""
    # Validate API key format
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("API key must be a non-empty string")
    
    # Only add headers for HTTP endpoints
    if is_http_endpoint(endpoint):
        headers = kwargs.get("headers", {})
        if isinstance(headers, dict):
            headers["Authorization"] = f"Bearer {api_key}"
            headers["X-Api-Key"] = api_key
        else:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "X-Api-Key": api_key
            }
        init_kwargs["headers"] = headers
