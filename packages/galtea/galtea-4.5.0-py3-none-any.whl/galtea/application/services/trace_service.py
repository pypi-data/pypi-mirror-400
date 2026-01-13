import logging
from typing import Any, Dict, List, Optional, Union

from galtea.domain.models.trace import NodeType, Trace, TraceBase
from galtea.infrastructure.clients.http_client import Client
from galtea.utils.string import build_query_params, is_valid_id
from galtea.utils.trace_context import TraceContext


class TraceService:
    """Service for managing Traces - records of tool/function calls during inference.

    A Trace represents a single tool or function call that occurred during
    an inference result, capturing input, output, timing, and error information.
    """

    def __init__(self, client: Client):
        """Initialize the TraceService with the provided HTTP client.

        Args:
            client (Client): The HTTP client for making API requests.
        """
        self.__client: Client = client
        self.__logger: logging.Logger = logging.getLogger(__name__)

    def create(
        self,
        inference_result_id: str,
        name: str,
        node_type: Optional[NodeType] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> Trace:
        """Create a new trace for a tool/function call.

        Args:
            inference_result_id (str): The ID of the inference result this trace belongs to.
            name (str): The name of the tool or function that was called.
            node_type (str, optional): The type of node (TOOL, CHAIN, RETRIEVER, LLM, CUSTOM).
                For more details read: https://docs.galtea.ai/concepts/product/version/session/trace#node-types
            input_data (Dict[str, Any], optional): The input data passed to the tool.
            output_data (Dict[str, Any], optional): The output data returned by the tool.
            error (str, optional): Error message if the tool call failed.
            latency_ms (float, optional): The time in milliseconds the tool call took.
            metadata (Dict[str, Any], optional): Additional metadata about the trace.
            start_time (str, optional): ISO 8601 timestamp when the trace started.
            end_time (str, optional): ISO 8601 timestamp when the trace ended.

        Returns:
            Trace: The created trace object.

        Raises:
            ValueError: If inference_result_id is invalid or name is empty.
        """
        if not is_valid_id(inference_result_id):
            raise ValueError("The inference_result_id provided is not valid.")

        if not name or not isinstance(name, str) or not name.strip():
            raise ValueError("A valid name must be provided.")

        trace_base: TraceBase = TraceBase(
            inference_result_id=inference_result_id,
            name=name,
            node_type=node_type,
            input_data=input_data,
            output_data=output_data,
            error=error,
            latency_ms=latency_ms,
            metadata=metadata,
            start_time=start_time,
            end_time=end_time,
        )

        trace_base.model_validate(trace_base.model_dump())

        response = self.__client.post(
            "traces",
            json=trace_base.model_dump(by_alias=True, exclude_none=True),
        )

        return Trace(**response.json())

    def create_batch(self, traces: List[TraceBase]) -> List[Trace]:
        """Create multiple traces in a single API call.

        Args:
            traces (List[TraceBase]): List of trace objects to create.
                Timestamps should be ISO 8601 strings.

        Returns:
            List[Trace]: List of created trace objects.

        Raises:
            ValueError: If traces list is empty.
        """
        if not traces or not isinstance(traces, list):
            raise ValueError("A non-empty list of traces must be provided.")

        traces_payload: List[Dict[str, Any]] = [trace.model_dump(by_alias=True, exclude_none=True) for trace in traces]

        response = self.__client.post(
            "traces/batch",
            json={"traces": traces_payload},
        )

        return [Trace(**trace_data) for trace_data in response.json()]

    def get(self, trace_id: str) -> Trace:
        """Retrieve a trace by its ID.

        Args:
            trace_id (str): The ID of the trace to retrieve.

        Returns:
            Trace: The retrieved trace object.

        Raises:
            ValueError: If trace_id is invalid.
        """
        if not is_valid_id(trace_id):
            raise ValueError("A valid trace ID must be provided.")

        response = self.__client.get(f"traces/{trace_id}")
        return Trace(**response.json())

    def list(
        self,
        inference_result_id: Optional[Union[str, List[str]]] = None,
        session_id: Optional[Union[str, List[str]]] = None,
        node_types: Optional[List[str]] = None,
        names: Optional[List[str]] = None,
        sort_by_start_time: Optional[str] = None,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[Trace]:
        """List traces for given inference result(s).

        Args:
            inference_result_id (str | List[str], optional): The inference result ID or list of IDs
                to get traces from.
            session_id (str | List[str], optional): The session ID or list of IDs to filter traces.
            node_types (List[str], optional): The list of node types to filter traces by.
                For more details read: https://docs.galtea.ai/concepts/product/version/session/trace#node-types
            names (List[str], optional): The list of trace names to filter by.
            sort_by_start_time (str, optional): Sort by start_time. Valid values are 'asc' and 'desc'.
            offset (int, optional): Offset for pagination.
                This refers to the number of items to skip before starting to collect the result set.
                The default value is 0.
            limit (int, optional): Limit for pagination.
                This refers to the maximum number of items to collect in the result set.

        Returns:
            List[Trace]: List of trace objects.

        Raises:
            ValueError: If inference_result_id is invalid or sort_by_start_time is not 'asc' or 'desc'.
        """

        if inference_result_id is not None and not isinstance(inference_result_id, (str, list)):
            raise ValueError("The inference result ID must be a string or a list of strings.")

        if session_id is not None and not isinstance(session_id, (str, list)):
            raise ValueError("The session ID must be a string or a list of strings.")

        if (session_id is None and inference_result_id is None) or (session_id == [] and inference_result_id == []):
            raise ValueError("At least one of session_id or inference_result_id must be provided.")

        inference_result_ids: List[str] | None = (
            [inference_result_id] if isinstance(inference_result_id, str) else inference_result_id
        )
        session_ids: List[str] | None = [session_id] if isinstance(session_id, str) else session_id

        if sort_by_start_time is not None and sort_by_start_time not in ["asc", "desc"]:
            raise ValueError("Sort by start_time must be 'asc' or 'desc'.")

        query_params: str = build_query_params(
            inferenceResultIds=inference_result_ids,
            sessionIds=session_ids,
            nodeTypes=node_types,
            names=names,
            offset=offset,
            limit=limit,
            sort=["startTime", sort_by_start_time] if sort_by_start_time else None,
        )

        response = self.__client.get(f"traces?{query_params}")
        return [Trace(**trace_data) for trace_data in response.json()]

    def delete(self, trace_id: str) -> None:
        """Delete a trace by its ID.

        Args:
            trace_id (str): The ID of the trace to delete.

        Raises:
            ValueError: If trace_id is invalid.
        """
        if not is_valid_id(trace_id):
            raise ValueError("A valid trace ID must be provided.")

        self.__client.delete(f"traces/{trace_id}")

    def start_collection_context(self) -> None:
        """Initialize trace collection for the current context.

        This method starts a new trace collection session, generating a unique
        trace_id for correlating all spans within this trace. Should be called
        at the beginning of each inference execution.
        """
        TraceContext.start_collection()

    def get_all_from_context(self) -> List[Dict[str, Any]]:
        """Get all traces from the current context.

        Returns:
            List[Dict[str, Any]]: List of all trace dictionaries from the current context.
        """
        return TraceContext.get_traces()

    def get_current_id_from_context(self) -> Optional[str]:
        """Get the current active trace_id from the context.

        This returns the trace_id of the currently executing traced operation,
        which is useful for establishing parent-child relationships when
        manually adding traces.

        Returns:
            Optional[str]: The current trace_id, or None if no trace is active.
        """
        return TraceContext.get_current_trace_id()

    def generate_id(self) -> str:
        """Generate a unique trace ID.

        Returns:
            str: A unique trace ID in the format 'trace_<uuid>'.
        """
        return TraceContext._generate_id()

    def clear_context(self) -> None:
        """Clear and close all traces from the current context without saving.

        This method resets the trace context back to its initial state (None),
        effectively closing the trace collection session. Should be called to
        clean up traces after they have been saved or when trace collection
        needs to be aborted. After calling this, the context can be restarted
        with start_collection_context().
        """
        TraceContext.clear_traces()

    def add_to_context(
        self,
        name: str,
        node_type: Optional[str] = None,
        input_data: Optional[Dict[str, Any]] = None,
        output_data: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        latency_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> None:
        """Add a trace to the current context.

        Both trace_id and parent_trace_id are automatically populated:
        - trace_id: Auto-generated unique identifier
        - parent_trace_id: Set from the current active trace context

        Args:
            name (str): The name of the tool or function that was called.
            node_type (str, optional): The type of node (TOOL, CHAIN, RETRIEVER, LLM, CUSTOM).
                For more details read: https://docs.galtea.ai/concepts/product/version/session/trace#node-types
            input_data (Dict[str, Any], optional): The input data passed to the tool.
            output_data (Dict[str, Any], optional): The output data returned by the tool.
            error (str, optional): Error message if the tool call failed.
            latency_ms (float, optional): The time in milliseconds the tool call took.
            metadata (Dict[str, Any], optional): Additional metadata about the trace.
            start_time (str, optional): ISO 8601 timestamp when the trace started.
            end_time (str, optional): ISO 8601 timestamp when the trace ended.

        Example:
            >>> from datetime import datetime, timezone
            >>> start = datetime.now(timezone.utc).isoformat()
            >>> # ... perform operation ...
            >>> end = datetime.now(timezone.utc).isoformat()
            >>> galtea.traces.add_to_context(
            ...     name="my_operation",
            ...     node_type="TOOL",
            ...     start_time=start,
            ...     end_time=end,
            ... )
        """
        if not name:
            raise ValueError("A valid name must be provided.")

        trace_id = self.generate_id()
        parent_trace_id = self.get_current_id_from_context()
        TraceContext.add_trace(
            name=name,
            node_type=node_type,
            input_data=input_data,
            output_data=output_data,
            error=error,
            latency_ms=latency_ms,
            metadata=metadata,
            trace_id=trace_id,
            parent_trace_id=parent_trace_id,
            start_time=start_time,
            end_time=end_time,
        )

    def save_context(self, inference_result_id: str) -> None:
        """Save and close the collected traces from the current context for an inference result.

        This method performs the complete lifecycle closure of trace collection:
        1. Collects all traces from the current context
        2. Saves them to the API in a batch (if any traces exist)
        3. Clears and closes the trace context, resetting it to None

        The context is ALWAYS closed (cleared), regardless of whether traces were
        collected or saving succeeded. This ensures no traces remain in memory,
        prevents duplicate submissions on subsequent calls, and ensures a fresh
        state for new trace collection sessions. Errors during saving are logged
        but do not prevent the context from being closed.

        Args:
            inference_result_id (str): The ID of the inference result to associate traces with.
        """
        traces = self.get_all_from_context()
        if traces:
            try:
                trace_objects: List[TraceBase] = [
                    TraceBase(
                        inference_result_id=inference_result_id,
                        **trace_data,
                    )
                    for trace_data in traces
                ]
                self.create_batch(trace_objects)
                self.__logger.debug(f"Saved {len(traces)} traces for inference result {inference_result_id}")
            except Exception as e:
                self.__logger.error(f"Failed to save traces: {e!s}")
            finally:
                self.clear_context()
        else:
            self.clear_context()
