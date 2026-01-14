#!/usr/bin/env python3
"""HITL REST client for manual approval operations.

Authors:
    GLAIP SDK Team
"""

from typing import Any

from glaip_sdk.client.base import BaseClient
from glaip_sdk.hitl.base import HITLDecision


class HITLClient(BaseClient):
    """Client for HITL REST endpoints.

    Use for manual approval workflows separate from agent runs.

    Example:
        >>> # List pending approvals
        >>> pending = client.hitl.list_pending()
        >>>
        >>> # Approve a request
        >>> client.hitl.approve(
        ...     request_id="bc4d0a77-7800-470e-a91c-7fd663a66b4d",
        ...     operator_input="Verified and approved",
        ... )
    """

    def approve(
        self,
        request_id: str,
        operator_input: str | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Approve a HITL request.

        Args:
            request_id: HITL request ID from SSE stream
            operator_input: Optional notes/reason for approval
            run_id: Optional client-side run correlation ID

        Returns:
            Response dict: {"status": "ok", "message": "..."}
        """
        return self._post_decision(
            request_id,
            HITLDecision.APPROVED,
            operator_input,
            run_id,
        )

    def reject(
        self,
        request_id: str,
        operator_input: str | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Reject a HITL request.

        Args:
            request_id: HITL request ID
            operator_input: Optional reason for rejection
            run_id: Optional run correlation ID

        Returns:
            Response dict
        """
        return self._post_decision(
            request_id,
            HITLDecision.REJECTED,
            operator_input,
            run_id,
        )

    def skip(
        self,
        request_id: str,
        operator_input: str | None = None,
        run_id: str | None = None,
    ) -> dict[str, Any]:
        """Skip a HITL request.

        Args:
            request_id: HITL request ID
            operator_input: Optional notes
            run_id: Optional run correlation ID

        Returns:
            Response dict
        """
        return self._post_decision(
            request_id,
            HITLDecision.SKIPPED,
            operator_input,
            run_id,
        )

    def _post_decision(
        self,
        request_id: str,
        decision: HITLDecision,
        operator_input: str | None,
        run_id: str | None,
    ) -> dict[str, Any]:
        """Post HITL decision to backend."""
        payload = {
            "request_id": request_id,
            "decision": decision.value,
        }

        if operator_input:
            payload["operator_input"] = operator_input
        if run_id:
            payload["run_id"] = run_id

        return self._request("POST", "/agents/hitl/decision", json=payload)

    def list_pending(self) -> list[dict[str, Any]]:
        """List all pending HITL requests.

        Returns:
            List of pending request dicts with metadata:
            [
                {
                    "request_id": "...",
                    "tool": "...",
                    "arguments": {...},
                    "created_at": "...",
                    "agent_id": "...",
                    "hitl_metadata": {...},
                },
                ...
            ]
        """
        return self._request("GET", "/agents/hitl/pending")
