"""
Trace context management using context variables for thread-safe and async-safe trace collection.

This module provides utilities for collecting traces (tool/function calls) during
agent execution. It uses Python's contextvars to ensure trace isolation between
parallel simulations and async operations.
"""

import contextvars
import inspect
import uuid
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

from galtea.domain.models.trace import NodeType

# Type variable for generic function decoration
F = TypeVar("F", bound=Callable[..., Any])


class TraceContext:
    """Manages trace collection using context variables for thread/async safety.

    This class provides static methods to control trace collection during agent
    execution. Traces are stored in a context variable, ensuring that each
    simulation (even when running in parallel) maintains its own isolated trace list.

    Example:
        ```python
        # Start collecting traces
        TraceContext.start_collection()

        # Traces are added (usually via @trace_tool decorator)
        TraceContext.add_trace(
            name="fetch_data",
            input_data={"query": "example"},
            output_data={"result": "data"},
            latency_ms=150.5,
        )

        # Get all collected traces
        traces = TraceContext.get_traces()

        # Clear traces when done
        TraceContext.clear_traces()
        ```
    """

    _allowed_node_types = [node_type.value for node_type in NodeType]

    # Context variable to store the current trace list (class-level for encapsulation)
    _current_traces: contextvars.ContextVar[Optional[List[Dict[str, Any]]]] = contextvars.ContextVar(
        "current_traces",
        default=None,
    )

    # Context variable to store the current active trace_id (for parent-child hierarchy)
    _current_trace_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
        "current_trace_id",
        default=None,
    )

    @staticmethod
    def _generate_id() -> str:
        """Generate a unique ID for trace hierarchy.

        Returns:
            str: A 32-character hexadecimal string for trace ID compatibility.
        """
        return "trace_" + uuid.uuid4().hex

    @staticmethod
    def start_collection() -> None:
        """Start collecting traces for the current context.

        This method initializes an empty trace list for the current context.
        Should be called at the beginning of each simulation turn.
        """
        TraceContext._current_traces.set([])
        TraceContext._current_trace_id.set(None)

    @staticmethod
    def get_current_trace_id() -> Optional[str]:
        """Get the current active trace_id.

        Returns:
            Optional[str]: The current trace_id, or None if no trace is active.
        """
        return TraceContext._current_trace_id.get()

    @staticmethod
    def set_current_trace_id(trace_id: Optional[str]) -> None:
        """Set the current active trace_id.

        Args:
            trace_id (Optional[str]): The trace_id to set as current.
        """
        TraceContext._current_trace_id.set(trace_id)

    @staticmethod
    def add_trace(
        name: str,
        node_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        parent_trace_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> None:
        """Add a trace to the current context.

        This method is safe to call even if trace collection has not been started.
        If collection is not active (traces is None), the trace will be silently ignored.

        Args:
            name (str): The name of the tool or function that was called.
            node_type (str, optional): The type of node (TOOL, CHAIN, RETRIEVER, LLM, CUSTOM).
            input_data (Dict[str, Any], optional): The input data passed to the tool.
            output_data (Dict[str, Any], optional): The output data returned by the tool.
            error (str, optional): Error message if the tool call failed.
            latency_ms (float, optional): The time in milliseconds the tool call took.
            metadata (Dict[str, Any], optional): Additional metadata about the trace.
            trace_id (str, optional): Unique identifier for this trace. Auto-generated if not provided.
            parent_trace_id (str, optional): The trace_id of the parent trace. None for root traces.
            start_time (str, optional): ISO 8601 timestamp when the trace started.
            end_time (str, optional): ISO 8601 timestamp when the trace ended.
        """
        traces: Optional[List[Dict[str, Any]]] = TraceContext._current_traces.get()
        if traces is not None:
            actual_trace_id: str = trace_id or TraceContext._generate_id()

            actual_latency_ms: Optional[float] = latency_ms
            if actual_latency_ms is None and start_time is not None and end_time is not None:
                try:
                    start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
                    end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                    actual_latency_ms = (end_dt - start_dt).total_seconds() * 1000
                except (ValueError, TypeError):
                    pass

            traces.append(
                {
                    "id": actual_trace_id,
                    "parent_trace_id": parent_trace_id,
                    "name": name,
                    "node_type": node_type,
                    "start_time": start_time,
                    "end_time": end_time,
                    "input_data": input_data,
                    "output_data": output_data,
                    "error": error,
                    "latency_ms": actual_latency_ms,
                    "metadata": metadata,
                }
            )

    @staticmethod
    def get_traces() -> List[Dict[str, Any]]:
        """Get all traces from the current context.

        Returns:
            List[Dict[str, Any]]: List of trace dictionaries collected in the current context.
                Returns an empty list if trace collection has not been started.
        """
        traces: Optional[List[Dict[str, Any]]] = TraceContext._current_traces.get()
        return traces if traces is not None else []

    @staticmethod
    def clear_traces() -> None:
        """Clear traces from the current context.

        This method should be called after traces have been saved to prevent
        memory leaks. Sets all context variables back to None.
        """
        TraceContext._current_traces.set(None)
        TraceContext._current_trace_id.set(None)

    @staticmethod
    def is_collecting() -> bool:
        """Check if trace collection is currently active.

        Returns:
            bool: True if trace collection has been started, False otherwise.
        """
        return TraceContext._current_traces.get() is not None


def trace(
    name: Optional[Union[str, Callable[..., Any]]] = None,
    node_type: Optional[str] = None,
) -> Union[Callable[[F], F], F]:
    """Decorator to automatically trace function calls with node type classification.

    This decorator wraps a function to automatically capture trace information
    including the function name, node type, input arguments, output result,
    any errors, and execution time.

    The trace will only be recorded if trace collection is active
    (i.e., TraceContext.start_collection() has been called).

    Args:
        name (str, optional): Custom name for the trace. If not provided,
            defaults to the function name.
        node_type (str, optional): The type of node being traced. Valid values:
            - "TOOL": For tool/function calls (default)
            - "TOOL": For tool/function calls
            - "CHAIN": For chain operations
            - "RETRIEVER": For retrieval operations
            - "LLM": For language model operations
            - "CUSTOM": For custom operations
            - "RETRIEVER": For retrieval operations

    Returns:
        A decorator function that wraps the target function with tracing.

    Raises:
        ValueError: If node_type is not one of the valid NodeType values.

    Example:
        ```python
        import galtea
        from galtea.domain.models.trace import NodeType

        class MyAgent(galtea.Agent):
            @galtea.trace  # Uses function name as trace name
            def fetch_data(self, query: str) -> dict:
                # Tool call automatically traced
                return {"data": "result"}

            @galtea.trace("weather_chain_call", node_type="CHAIN")
            def call(self, input_data: galtea.AgentInput) -> galtea.AgentResponse:
                data = self.fetch_data(input_data.last_user_message_str())
                return galtea.AgentResponse(content=str(data))
        ```

    Supports both synchronous and asynchronous functions.
    """
    # Handle @trace without parentheses (function passed directly as name)
    if callable(name):
        func = name
        return _create_trace_wrapper(func, func.__name__, node_type)

    if node_type and node_type not in NodeType:
        raise ValueError(
            f"Invalid node_type: '{node_type}'. Must be one of {NodeType}. "
            f"Use NodeType enum from galtea.domain.models.trace for type safety."
        )

    def decorator(func: F) -> F:
        trace_name: str = name or func.__name__
        return _create_trace_wrapper(func, trace_name, node_type)

    return decorator


def _create_trace_wrapper(func: F, trace_name: str, node_type: Optional[str]) -> F:
    """Create a trace wrapper for a function.

    Args:
        func: The function to wrap.
        trace_name: The name to use for the trace.
        node_type: The type of node being traced.

    Returns:
        The wrapped function with tracing enabled.
    """
    sig: inspect.Signature = inspect.signature(func)

    def _build_input_data(
        args: tuple[Any, ...],
        kwargs: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Build input data dict with parameter names mapped to values."""
        try:
            bound: inspect.BoundArguments = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            input_data: Dict[str, Any] = dict(bound.arguments)
            input_data.pop("self", None)
            input_data.pop("cls", None)
            return input_data if input_data else None
        except TypeError:
            return {"args": args, "kwargs": kwargs} if args or kwargs else None

    def _record_trace(
        args: tuple[Any, ...],
        kwargs: Dict[str, Any],
        result: Any,
        error: Optional[str],
        start_time: str,
        trace_id: str,
        parent_trace_id: Optional[str],
    ) -> None:
        end_time: str = datetime.now(timezone.utc).isoformat()
        start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        latency_ms: float = (end_dt - start_dt).total_seconds() * 1000
        input_data: Optional[Dict[str, Any]] = _build_input_data(args, kwargs)

        TraceContext.add_trace(
            name=trace_name,
            node_type=node_type,
            input_data=input_data,
            output_data={"result": result} if result is not None else None,
            error=error,
            latency_ms=latency_ms,
            trace_id=trace_id,
            parent_trace_id=parent_trace_id,
            start_time=start_time,
            end_time=end_time,
        )

    if inspect.iscoroutinefunction(func):

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            parent_trace_id: Optional[str] = TraceContext.get_current_trace_id()
            trace_id: str = TraceContext._generate_id()
            TraceContext.set_current_trace_id(trace_id)

            start_time: str = datetime.now(timezone.utc).isoformat()
            error: Optional[str] = None
            result: Any = None
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                _record_trace(args, kwargs, result, error, start_time, trace_id, parent_trace_id)
                TraceContext.set_current_trace_id(parent_trace_id)

        return async_wrapper  # type: ignore[return-value]

    else:

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            parent_trace_id: Optional[str] = TraceContext.get_current_trace_id()
            trace_id: str = TraceContext._generate_id()
            TraceContext.set_current_trace_id(trace_id)

            start_time: str = datetime.now(timezone.utc).isoformat()
            error: Optional[str] = None
            result: Any = None
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = str(e)
                raise
            finally:
                _record_trace(args, kwargs, result, error, start_time, trace_id, parent_trace_id)
                TraceContext.set_current_trace_id(parent_trace_id)

        return sync_wrapper  # type: ignore[return-value]
