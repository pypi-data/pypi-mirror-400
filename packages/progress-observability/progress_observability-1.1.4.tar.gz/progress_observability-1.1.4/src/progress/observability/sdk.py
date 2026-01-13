"""
Progress Observability - Zero-intrusion AI agent telemetry

Provides granular control over AI agent tracing with zero code changes required
to existing agent implementations. Simply add one line at the beginning of your
agent code to enable comprehensive telemetry.

Quick Start:
    
    from progress.observability.instrumentation import Observability
    
    # Basic initialization
    Observability.instrument(
        app_name="my-agent-app",
        endpoint='https://collector.observability.progress.com:443',
        api_key="<YOUR_API_KEY>",
    )


"""

import sys
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from typing import Any, Dict, Optional, Set
from urllib.parse import urlparse

from .enums import ObservabilityInstruments
from .helpers import init_environment, setup_api_key_headers, patch_traceloop_modules, clear_sdk_env_vars
from .model_fix_processor import ModelFixProcessor
from .exceptions import (
    EndpointValidationError,
    InvalidPortError,
    MissingHostError,
    MissingPortError,
    NonNumericPortError,
    UnsupportedSchemeError,
    InvalidHostError,
)

patch_traceloop_modules()
clear_sdk_env_vars()

from traceloop.sdk import Traceloop


class Observability:
    """
    Progress Observability - Zero-intrusion AI agent telemetry

    Provides granular control over AI agent tracing with zero code changes required
    to existing agent implementations. Simply add one line at the beginning of your
    agent code to enable comprehensive telemetry.
    """

    _initialized = False
    _model_fix_processor = None  # Store for debugging access
    SDK = Traceloop

    @staticmethod
    def _validate_endpoint(endpoint: Optional[str]) -> None:
        """
        Validate the endpoint URL format and components.
        
        Args:
            endpoint: The endpoint URL to validate
            
        Raises:
            EndpointValidationError: If the endpoint is invalid
        """
        if endpoint is None or endpoint == "":
            # Empty string and None are allowed (will use defaults)
            return
            
        try:
            parsed = urlparse(endpoint)
        except Exception as e:
            raise EndpointValidationError(f"Failed to parse endpoint '{endpoint}': {e}")
        
        # Check scheme
        if parsed.scheme not in ("http", "https"):
            raise UnsupportedSchemeError(parsed.scheme or "missing")
        
        # Check host
        if not parsed.hostname:
            raise MissingHostError(endpoint)
        
        # Check for spaces in hostname
        if " " in parsed.hostname:
            raise InvalidHostError(parsed.hostname)
        
        # Check port
        try:
            port = parsed.port
        except ValueError as ve:
            # Handle port out of range or non-numeric port
            msg = str(ve)
            if "out of range" in msg:
                # Extract port from netloc
                port_part = parsed.netloc.split(":")[-1]
                raise InvalidPortError(port_part)
            else:
                port_part = parsed.netloc.split(":")[-1]
                raise NonNumericPortError(port_part)

        if port is None:
            # Check if there's a colon without a port number
            if ":" in parsed.netloc and not parsed.netloc.endswith(":"):
                port_part = parsed.netloc.split(":")[-1]
                if port_part and not port_part.isdigit():
                    raise NonNumericPortError(port_part)
            elif parsed.netloc.endswith(":"):
                raise MissingPortError(endpoint)
        else:
            if port < 1 or port > 65535:
                raise InvalidPortError(str(port))

    @staticmethod
    def _build_init_kwargs(
        *,
        app_name: Optional[str],
        api_key: Optional[str],
        endpoint: Optional[str],
        instruments: Optional[Set[ObservabilityInstruments]],
        block_instruments: Optional[Set[ObservabilityInstruments]],
        disable_batch: bool,
        resource_attributes: Optional[Dict[str, Any]],
        extra_kwargs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build keyword arguments for the underlying SDK.init call.

        Converts Observability enums to Traceloop values, applies batching and
        resource attributes, configures API key headers when provided, and
        merges any additional kwargs.
        
        Args:
            app_name: Application name for telemetry identification
            api_key: Optional API key for authentication
            endpoint: Optional collector endpoint URL
            instruments: Optional set of instruments to enable
            block_instruments: Optional set of instruments to block
            disable_batch: Whether to disable batching (default True)
            resource_attributes: Optional additional resource attributes
            extra_kwargs: Additional kwargs from caller (highest precedence)
            
        Returns:
            Dictionary of keyword arguments ready for SDK.init()
        """

        # Convert ObservabilityInstruments to Traceloop instruments
        traceloop_instruments = (
            {instrument.value for instrument in instruments}
            if instruments
            else None
        )
        traceloop_block_instruments = (
            {instrument.value for instrument in block_instruments}
            if block_instruments
            else None
        )

        init_kwargs: Dict[str, Any] = {
            "app_name": app_name,
            "disable_batch": disable_batch,
            "telemetry_enabled": False
        }
        
        if api_key:
            init_kwargs["api_key"] = api_key
        if endpoint:
            init_kwargs["api_endpoint"] = endpoint
            
        if traceloop_instruments:
            init_kwargs["instruments"] = traceloop_instruments
        if traceloop_block_instruments:
            init_kwargs["block_instruments"] = traceloop_block_instruments

        if api_key:
            # configure headers for exporters if api_key is provided
            setup_api_key_headers(api_key, endpoint, init_kwargs, extra_kwargs)

        if resource_attributes:
            init_kwargs["resource_attributes"] = dict(resource_attributes)

        # Merge additional kwargs last so callers can override defaults
        init_kwargs.update(extra_kwargs)
        return init_kwargs

    @classmethod
    def instrument(
        cls,
        app_name: str = sys.argv[0],
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        instruments: Optional[Set[ObservabilityInstruments]] = None,
        block_instruments: Optional[Set[ObservabilityInstruments]] = None,
        disable_batch: bool = True,
        trace_content: Optional[bool] = None,
        resource_attributes: Optional[Dict[str, Any]] = None,
        debug: bool = False,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Observability with granular control over what gets traced.

        Args:
            app_name: Application name for telemetry identification
            endpoint: Collector endpoint URL
            api_key: Collector API key for authentication
            instruments: Set of ObservabilityInstruments to enable for tracing
            block_instruments: Set of ObservabilityInstruments to exclude from tracing
            disable_batch: Send traces immediately vs batching
            trace_content: Whether to log prompts/completions (default True, can also use OBSERVABILITY_TRACE_CONTENT env var)
            resource_attributes: Additional resource attributes for traces
            debug: Enable verbose debugging output (can also use OBSERVABILITY_DEBUG env var)
            **kwargs: Additional parameters passed to underlying SDK
        """

        # Always allow re-initialization to support different instrument configurations
        # The underlying traceloop SDK will handle duplicate initialization safely

        # Validate endpoint before processing
        cls._validate_endpoint(endpoint)

        app_name, endpoint, api_key = init_environment(app_name, endpoint, api_key, trace_content)

        # Create the model fix processor with debug mode
        model_fix_processor = ModelFixProcessor(debug=debug)
        cls._model_fix_processor = model_fix_processor

        # Just pass the method directly - you can set breakpoints inside on_end()
        if 'span_postprocess_callback' not in kwargs:
            kwargs['span_postprocess_callback'] = model_fix_processor.on_end
                
        init_kwargs = cls._build_init_kwargs(
            app_name=app_name,
            api_key=api_key,
            endpoint=endpoint,
            instruments=instruments,
            block_instruments=block_instruments,
            disable_batch=disable_batch,
            resource_attributes=resource_attributes,
            extra_kwargs=kwargs,
        )

        # Suppress SDK init output to keep user console clean
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            cls.SDK.init(**init_kwargs)

        cls._initialized = True

    @classmethod
    def shutdown(cls, timeout_millis: int = 30000) -> bool:
        """
        Shutdown Progress Observability instrumentation and clean up resources.

        This method performs a shutdown of the tracing infrastructure:
        - Shuts down the TracerProvider and all associated span processors
        - Ensures all pending spans are exported before shutdown
        - Prevents further telemetry collection
        - Resets initialization state

        Args:
            timeout_millis: Maximum time to wait for shutdown completion in milliseconds.
                          Defaults to 30000ms (30 seconds) as per OpenTelemetry spec.

        Returns:
            bool: True if shutdown completed successfully within timeout,
                  False if shutdown failed or timed out.

        Note:
            This method should be called only once per Observability instance.
            After shutdown, subsequent calls to instrument() will reinitialize
            the instrumentation.
        """
        if not cls._initialized:
            return True

        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider

            tracer_provider = trace.get_tracer_provider()

            if isinstance(tracer_provider, TracerProvider):
                tracer_provider.shutdown()
                cls._initialized = False
                return True
            else:
                cls._initialized = False
                return True
        except Exception as e:
            print(f"Error during Observability shutdown: {e}", file=sys.stderr)
            cls._initialized = False
            return False
 
