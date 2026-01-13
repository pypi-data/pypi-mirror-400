"""
Observability custom exceptions for validation and error handling.
"""


class ObservabilityError(Exception):
    """Base exception class for Progress Observability instrumentation errors."""
    pass


class EndpointValidationError(ObservabilityError):
    """Raised when an invalid endpoint is provided."""
    pass


class InvalidPortError(EndpointValidationError):
    """Raised when an invalid port number is provided in the endpoint."""
    def __init__(self, port: str, message: str = None):
        if message is None:
            message = f"Invalid port number '{port}'. Port must be between 1 and 65535."
        super().__init__(message)


class MissingHostError(EndpointValidationError):
    """Raised when the host is missing from the endpoint URL."""
    def __init__(self, endpoint: str, message: str = None):
        if message is None:
            message = f"Missing host in endpoint '{endpoint}'. Expected format: http://hostname:port"
        super().__init__(message)


class MissingPortError(EndpointValidationError):
    """Raised when the port is missing from the endpoint URL."""
    def __init__(self, endpoint: str, message: str = None):
        if message is None:
            message = f"Missing port in endpoint '{endpoint}'. Expected format: http://hostname:port"
        super().__init__(message)


class NonNumericPortError(EndpointValidationError):
    """Raised when the port is not a valid numeric value."""
    def __init__(self, port: str, message: str = None):
        if message is None:
            message = f"Port '{port}' must be a numeric value between 1 and 65535."
        super().__init__(message)


class UnsupportedSchemeError(EndpointValidationError):
    """Raised when an unsupported URL scheme is used (only http/https are supported)."""
    def __init__(self, scheme: str, message: str = None):
        if message is None:
            message = f"Unsupported URL scheme '{scheme}'. Only 'http' and 'https' are supported."
        super().__init__(message)


class InvalidHostError(EndpointValidationError):
    """Raised when the host contains invalid characters (e.g., spaces)."""
    def __init__(self, host: str, message: str = None):
        if message is None:
            message = f"Invalid host '{host}'. Host cannot contain spaces or invalid characters."
        super().__init__(message)
