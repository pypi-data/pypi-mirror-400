#!/usr/bin/env python3
"""Base types for HITL approval handling.

Authors:
    GLAIP SDK Team
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Protocol, runtime_checkable


class HITLDecision(str, Enum):
    """HITL decision types."""

    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"


@dataclass
class HITLRequest:
    """HITL approval request from SSE stream."""

    request_id: str
    tool_name: str
    tool_args: dict[str, Any]
    timeout_at: str  # ISO 8601, authoritative deadline
    timeout_seconds: int  # Informational, fallback only

    # Raw metadata for advanced use cases
    hitl_metadata: dict[str, Any]
    tool_metadata: dict[str, Any]


@dataclass
class HITLResponse:
    """HITL decision response."""

    decision: HITLDecision
    operator_input: str | None = None


@runtime_checkable
class HITLCallback(Protocol):
    """Protocol for HITL approval callbacks.

    Callbacks should complete within the computed callback timeout.
    Callbacks should handle exceptions internally or let them propagate.
    """

    def __call__(self, request: HITLRequest) -> HITLResponse:
        """Handle HITL approval request.

        Args:
            request: HITL request with tool info and metadata

        Returns:
            HITLResponse with decision and optional operator input

        Raises:
            Any exception will be caught, logged, and treated as REJECTED.
        """
        ...
