from enum import Enum
from typing import Any, Dict, Optional

from galtea.utils.from_camel_case_base_model import FromCamelCaseBaseModel


class NodeType(str, Enum):
    """Enum representing the types of nodes in the agentic system."""

    TOOL = "TOOL"
    CHAIN = "CHAIN"
    RETRIEVER = "RETRIEVER"
    LLM = "LLM"
    CUSTOM = "CUSTOM"


class TraceBase(FromCamelCaseBaseModel):
    """Base model for creating traces.

    A trace represents a single tool or function call during an inference,
    capturing input, output, timing, and error information.
    """

    inference_result_id: str
    name: str
    id: Optional[str] = None
    node_type: Optional[NodeType] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    latency_ms: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    parent_trace_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


class Trace(TraceBase):
    """Complete trace model returned from API.

    Includes all fields from TraceBase plus server-generated fields
    like id, created_at, and deleted_at.
    """

    created_at: str
    deleted_at: Optional[str] = None
