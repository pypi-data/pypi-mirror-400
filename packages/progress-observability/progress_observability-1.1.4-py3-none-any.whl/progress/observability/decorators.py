"""
Progress Observability Decorators - Unified telemetry decorators for AI agents

Provides convenient decorators for instrumenting agent functions, workflows,
tasks, and tools with Progress Observability telemetry.
"""

import functools
import inspect
from typing import Optional, TypeVar, Callable, Awaitable, Union, Dict, Any

from opentelemetry import trace
from opentelemetry.trace import SpanKind, Status, StatusCode


class ObservabilitySpanKind:
    """
    Observability span kind values for distinguishing different operation types.

    These custom span kinds complement OpenTelemetry standard semantic conventions
    to provide domain-specific categorization for AI agent operations.
    """
    TASK = "task"
    WORKFLOW = "workflow"
    AGENT = "agent"
    TOOL = "tool"


R = TypeVar("R")
F = TypeVar("F", bound=Callable[..., Union[R, Awaitable[R]]])

# Get tracer instance
tracer = trace.get_tracer("progress.observability")


def _create_span_wrapper(
    func: F,
    span_name: Optional[str],
    span_kind: str,
    version: Optional[int],
    additional_attributes: Optional[Dict[str, Any]] = None,
) -> F:
    """
    Create a span wrapper for a function with OpenTelemetry standard semantic conventions.

    Args:
        func: Function to wrap
        span_name: Name for the span (if None, derived from function)
        span_kind: Observability span kind value
        version: Optional version number
        additional_attributes: Optional additional attributes to add

    Returns:
        Wrapped function with telemetry
    """
    # Get function name and namespace
    func_name = func.__name__
    namespace = None

    # Try to get class name if this is a method
    if hasattr(func, '__qualname__') and '.' in func.__qualname__:
        parts = func.__qualname__.rsplit('.', 1)
        if len(parts) == 2:
            namespace = parts[0]

    # Determine span name
    if span_name is None:
        span_name = f"{namespace}.{func_name}" if namespace else func_name

    # Build base attributes using OpenTelemetry standard semantic conventions
    base_attributes = {
        'code.function': func_name,
        'observability.span.kind': span_kind,
    }

    if namespace:
        base_attributes['code.namespace'] = namespace

    if version is not None:
        base_attributes['service.version'] = str(version)

    if additional_attributes:
        base_attributes.update(additional_attributes)

    # Handle async functions
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with tracer.start_as_current_span(
                span_name,
                kind=SpanKind.INTERNAL,
                attributes=base_attributes,
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return async_wrapper  # type: ignore

    # Handle sync functions
    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        with tracer.start_as_current_span(
            span_name,
            kind=SpanKind.INTERNAL,
            attributes=base_attributes,
        ) as span:
            try:
                result = func(*args, **kwargs)
                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as e:
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.record_exception(e)
                raise
    return sync_wrapper  # type: ignore


def task(
    name: Optional[str] = None,
    version: Optional[int] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator for instrumenting task functions with Progress Observability telemetry.

    Uses OpenTelemetry standard semantic conventions for attributes:
    - code.function: Function name
    - code.namespace: Class name (if method)
    - service.version: Version number
    - observability.span.kind: Set to "task"

    Args:
        name: Optional name override for the task span
        version: Optional version number for the task
        attributes: Optional additional attributes to add to the span

    Returns:
        Decorated function with telemetry instrumentation

    Examples:
        @task()
        def my_task():
            pass

        @task(name="custom_task", version=1)
        async def async_task():
            pass
    """
    def decorator(func: F) -> F:
        return _create_span_wrapper(
            func,
            name,
            ObservabilitySpanKind.TASK,
            version,
            attributes,
        )
    return decorator


def workflow(
    name: Optional[str] = None,
    version: Optional[int] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator for instrumenting workflow functions with Progress Observability telemetry.

    Uses OpenTelemetry standard semantic conventions for attributes:
    - code.function: Function name
    - code.namespace: Class name (if method)
    - service.version: Version number
    - observability.span.kind: Set to "workflow"

    Args:
        name: Optional name override for the workflow span
        version: Optional version number for the workflow
        attributes: Optional additional attributes to add to the span

    Returns:
        Decorated function with telemetry instrumentation

    Examples:
        @workflow()
        def my_workflow():
            pass

        @workflow(name="data_processing", version=2)
        async def process_data():
            pass
    """
    def decorator(func: F) -> F:
        return _create_span_wrapper(
            func,
            name,
            ObservabilitySpanKind.WORKFLOW,
            version,
            attributes,
        )
    return decorator


def agent(
    name: Optional[str] = None,
    version: Optional[int] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator for instrumenting agent functions with Progress Observability telemetry.

    Uses OpenTelemetry standard semantic conventions for attributes:
    - code.function: Function name
    - code.namespace: Class name (if method)
    - service.version: Version number
    - observability.span.kind: Set to "agent"

    Args:
        name: Optional name override for the agent span
        version: Optional version number for the agent
        attributes: Optional additional attributes to add to the span

    Returns:
        Decorated function with telemetry instrumentation

    Examples:
        @agent()
        def my_agent():
            pass

        @agent(name="chat_agent", version=1)
        async def chat_with_user():
            pass
    """
    def decorator(func: F) -> F:
        return _create_span_wrapper(
            func,
            name,
            ObservabilitySpanKind.AGENT,
            version,
            attributes,
        )
    return decorator


def tool(
    name: Optional[str] = None,
    version: Optional[int] = None,
    attributes: Optional[Dict[str, Any]] = None,
) -> Callable[[F], F]:
    """
    Decorator for instrumenting tool functions with Progress Observability telemetry.

    Uses OpenTelemetry standard semantic conventions for attributes:
    - code.function: Function name
    - code.namespace: Class name (if method)
    - service.version: Version number
    - observability.span.kind: Set to "tool"

    Args:
        name: Optional name override for the tool span
        version: Optional version number for the tool
        attributes: Optional additional attributes to add to the span

    Returns:
        Decorated function with telemetry instrumentation

    Examples:
        @tool()
        def my_tool():
            pass

        @tool(name="web_search", version=1)
        async def search_web(query: str):
            pass
    """
    def decorator(func: F) -> F:
        return _create_span_wrapper(
            func,
            name,
            ObservabilitySpanKind.TOOL,
            version,
            attributes,
        )
    return decorator