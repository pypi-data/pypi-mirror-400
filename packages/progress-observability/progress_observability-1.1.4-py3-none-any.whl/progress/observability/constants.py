"""
Constants for Progress Observability Instrumentation

Contains environment variables and configuration constants used by the
Progress Observability instrumentation system.
"""

# Traceloop SDK environment variables that should be cleared to prevent conflicts
SDK_ENV_VARS = [
    "TRACELOOP_TELEMETRY",
    "TRACELOOP_BASE_URL", 
    "TRACELOOP_API_KEY",
    "TRACELOOP_HEADERS",
    "TRACELOOP_METRICS_ENDPOINT",
    "TRACELOOP_METRICS_HEADERS",
    "TRACELOOP_LOGGING_ENDPOINT", 
    "TRACELOOP_LOGGING_HEADERS"
]

# Observability environment variables
OBSERVABILITY_ENV_VARS = [
    "OBSERVABILITY_API_KEY",
    "OBSERVABILITY_ENDPOINT",
    "OBSERVABILITY_APP_NAME",
    "OBSERVABILITY_TRACE_CONTENT"
]

# Default configuration values
DEFAULTS = {
    "ENDPOINT": "https://collector.observability.progress.com:443"
}
