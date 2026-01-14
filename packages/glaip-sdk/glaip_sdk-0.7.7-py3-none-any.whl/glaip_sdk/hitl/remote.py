#!/usr/bin/env python3
"""Remote HITL approval handler with threading and error recovery.

Authors:
    GLAIP SDK Team
"""

import logging
import os
import threading
import time
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from collections.abc import Callable

import httpx

from glaip_sdk.exceptions import APIError
from glaip_sdk.hitl.base import (
    HITLCallback,
    HITLDecision,
    HITLRequest,
    HITLResponse,
)

if TYPE_CHECKING:
    from glaip_sdk.client.base import BaseClient

logger = logging.getLogger(__name__)


class RemoteHITLHandler:
    """Handler for remote HITL approval requests.

    Executes callbacks in background threads to avoid blocking SSE stream.
    Includes timeout enforcement and error handling.

    Thread Safety:
        This handler is thread-safe for concurrent HITL events. Callbacks
        execute in daemon threads. Use wait_for_pending_decisions() after
        stream completion to ensure all decisions are posted.

    Environment Variables:
        GLAIP_HITL_AUTO_APPROVE: Set to "true" to auto-approve all requests.

    Example:
        >>> def my_approver(request: HITLRequest) -> HITLResponse:
        ...     print(f"Approve {request.tool_name}?")
        ...     return HITLResponse(decision=HITLDecision.APPROVED)
        >>>
        >>> handler = RemoteHITLHandler(callback=my_approver, client=client)
        >>> client.agents.run_agent(agent_id, message, hitl_handler=handler)
    """

    def __init__(
        self,
        callback: HITLCallback | None = None,
        *,
        client: "BaseClient",
        auto_approve: bool | None = None,
        max_retries: int = 3,
        on_unrecoverable_error: Callable[[str, Exception], None] | None = None,
    ):
        """Initialize remote HITL handler.

        Args:
            callback: Function to invoke for approval decisions.
                If None and auto_approve=False, HITL events will be rejected.
            client: BaseClient instance for posting decisions.
            auto_approve: Override GLAIP_HITL_AUTO_APPROVE env var.
            max_retries: Max retries for POST /agents/hitl/decision (default: 3)
            on_unrecoverable_error: Optional callback invoked when both the
                approval callback and fallback rejection POST fail. Receives
                (request_id, exception) for custom alerting/logging.
        """
        self._callback = callback
        self._client = client
        self._max_retries = max_retries
        self._on_unrecoverable_error = on_unrecoverable_error

        # Thread tracking for synchronization
        self._active_threads: list[threading.Thread] = []
        self._threads_lock = threading.Lock()

        # Auto-approve from env or explicit override
        if auto_approve is None:
            auto_approve = os.getenv("GLAIP_HITL_AUTO_APPROVE", "").lower() == "true"
        self._auto_approve = auto_approve

        # Warn if no decision mechanism
        if not auto_approve and callback is None:
            logger.warning(
                "RemoteHITLHandler: No callback provided and auto_approve=False. "
                "HITL requests will be rejected. Set GLAIP_HITL_AUTO_APPROVE=true "
                "or provide a callback."
            )

    def handle_hitl_event(self, event: dict) -> None:
        """Process HITL event from SSE stream.

        Runs in background thread to avoid blocking stream.

        Args:
            event: SSE event dict with metadata.hitl and metadata.tool_info
        """
        # Validate event structure
        try:
            request = self._parse_hitl_request(event)
        except (KeyError, ValueError) as e:
            logger.error(f"Invalid HITL event structure: {e}")
            logger.debug(f"Event data: {event}")
            return

        # Execute in background thread to avoid blocking stream
        thread = threading.Thread(
            target=self._process_approval,
            args=(request,),
            daemon=True,
            name=f"hitl-{request.request_id[:8]}",
        )
        thread.start()

        # Track active threads for synchronization.
        cleanup_snapshot: list[threading.Thread] | None = None
        with self._threads_lock:
            self._active_threads.append(thread)
            if len(self._active_threads) > 10:
                cleanup_snapshot = list(self._active_threads)

        # Clean up finished threads outside the lock when the list grows.
        if cleanup_snapshot is not None:
            dead_threads = [t for t in cleanup_snapshot if not t.is_alive()]
            if dead_threads:
                with self._threads_lock:
                    self._active_threads = [t for t in self._active_threads if t not in dead_threads]

    def _parse_hitl_request(self, event: dict) -> HITLRequest:
        """Parse SSE event into HITLRequest.

        Raises:
            KeyError: If required fields missing
            ValueError: If data invalid
        """
        metadata = event.get("metadata", {})
        hitl_meta = metadata.get("hitl", {})
        tool_info = metadata.get("tool_info", {})

        # Validate required fields
        request_id = hitl_meta.get("request_id")
        if not request_id:
            raise ValueError("Missing request_id in HITL metadata")

        return HITLRequest(
            request_id=request_id,
            tool_name=tool_info.get("name", "unknown"),
            tool_args=tool_info.get("args", {}),
            timeout_at=hitl_meta.get("timeout_at", ""),
            timeout_seconds=hitl_meta.get("timeout_seconds", 180),
            hitl_metadata=hitl_meta,
            tool_metadata=tool_info,
        )

    def _process_approval(self, request: HITLRequest) -> None:
        """Process approval in background thread.

        Handles callback execution, timeout, errors, and POST retry.
        """
        try:
            # Get decision
            response = self._get_decision(request)

            # Post to backend with retry
            self._post_decision_with_retry(request.request_id, response)

        except APIError as e:
            # Handle client errors (4xx) - non-retryable
            if e.status_code and 400 <= e.status_code < 500:
                logger.warning(f"Non-retryable HITL decision error for {request.request_id}: {e}")
                return

            logger.error(
                f"HITL processing failed for {request.request_id}: {e}",
                exc_info=True,
            )
            self._handle_approval_failure(request, e)

        except Exception as e:
            logger.error(
                f"HITL processing failed for {request.request_id}: {e}",
                exc_info=True,
            )
            self._handle_approval_failure(request, e)

    def _handle_approval_failure(self, request: HITLRequest, error: Exception) -> None:
        """Handle failure during approval processing by attempting fallback rejection.

        Args:
            request: The HITL request that failed.
            error: The exception that occurred during processing.
        """
        # Try to post rejection as fallback
        try:
            fallback = HITLResponse(
                decision=HITLDecision.REJECTED,
                operator_input=f"Error: {str(error)[:100]}",
            )
            self._post_decision_with_retry(request.request_id, fallback)
        except Exception as post_err:
            logger.error(f"Failed to post fallback rejection: {post_err}")

            # Invoke error callback if provided
            if self._on_unrecoverable_error:
                try:
                    self._on_unrecoverable_error(request.request_id, post_err)
                except Exception as cb_err:
                    logger.error(f"Error callback failed: {cb_err}")

    def _get_decision(self, request: HITLRequest) -> HITLResponse:
        """Get approval decision via auto-approve or callback.

        Raises:
            Exception: If callback fails
        """
        # Auto-approve path
        if self._auto_approve:
            logger.info(f"Auto-approving HITL request {request.request_id}")
            return HITLResponse(
                decision=HITLDecision.APPROVED,
                operator_input="auto-approved",
            )

        # Callback path
        if self._callback:
            return self._execute_callback(request)

        # No callback, no auto-approve -> reject
        logger.warning(f"No approval mechanism, rejecting {request.request_id}")
        return HITLResponse(
            decision=HITLDecision.REJECTED,
            operator_input="No approval handler configured",
        )

    def _execute_callback(self, request: HITLRequest) -> HITLResponse:
        """Execute callback with timeout and error handling.

        Args:
            request: HITL request to process

        Returns:
            HITLResponse from callback or rejection on error
        """
        try:
            # Apply timeout: 80% of remaining backend time (20% buffer)
            timeout = self._compute_callback_timeout(request)

            # Run callback with timeout
            response = self._run_callback_with_timeout(
                request,
                timeout_seconds=timeout,
            )

            # Validate return type
            if not isinstance(response, HITLResponse):
                logger.error(
                    f"HITL callback returned invalid type {type(response)} "
                    f"for {request.request_id}, expected HITLResponse"
                )
                return HITLResponse(
                    decision=HITLDecision.REJECTED,
                    operator_input="Callback returned invalid response type",
                )

            logger.info(f"HITL callback returned {response.decision} for {request.request_id}")
            return response

        except TimeoutError:
            logger.error(
                f"HITL callback timeout ({timeout}s) for request {request.request_id} (tool: {request.tool_name})"
            )
            return HITLResponse(
                decision=HITLDecision.REJECTED,
                operator_input="Callback timeout",
            )
        except Exception as e:
            logger.error(
                f"HITL callback failed for {request.request_id}: {e}",
                exc_info=True,
            )
            return HITLResponse(
                decision=HITLDecision.REJECTED,
                operator_input=f"Callback error: {str(e)[:100]}",
            )

    def _run_callback_with_timeout(
        self,
        request: HITLRequest,
        timeout_seconds: int,
    ) -> HITLResponse:
        """Run callback with timeout using threading.

        Args:
            request: HITL request
            timeout_seconds: Max execution time

        Returns:
            HITLResponse from callback

        Raises:
            TimeoutError: If callback exceeds timeout
            Exception: If callback raises
        """
        result = [None]  # Mutable container for thread result
        exception = [None]

        def wrapper():
            try:
                result[0] = self._callback(request)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=wrapper, daemon=True)
        thread.start()
        thread.join(timeout=timeout_seconds)

        if thread.is_alive():
            # Timeout - thread still running
            logger.warning(f"Callback timeout after {timeout_seconds}s for {request.request_id}")
            raise TimeoutError(f"Callback exceeded {timeout_seconds}s")

        if exception[0]:
            raise exception[0]

        if result[0] is None:
            raise ValueError("Callback returned None instead of HITLResponse")

        return result[0]

    def _compute_callback_timeout(self, request: HITLRequest) -> int:
        """Compute callback timeout using timeout_at as the source of truth.

        Args:
            request: HITL request with timeout information

        Returns:
            Timeout in seconds (minimum 5s)
        """
        fallback_seconds = max(5, int(request.timeout_seconds * 0.8))
        try:
            # Try ISO format first with Z suffix
            if request.timeout_at.endswith("Z"):
                deadline = datetime.fromisoformat(request.timeout_at.replace("Z", "+00:00"))
            else:
                # Try parsing as-is (may include timezone info)
                deadline = datetime.fromisoformat(request.timeout_at)

            now = datetime.now(timezone.utc)
            remaining = max(0, int((deadline - now).total_seconds()))
            return max(5, int(remaining * 0.8))
        except (TypeError, ValueError, AttributeError) as e:
            logger.debug(
                f"Failed to parse timeout_at '{request.timeout_at}': {e}, using fallback timeout of {fallback_seconds}s"
            )
            return fallback_seconds

    def _post_decision_with_retry(
        self,
        request_id: str,
        response: HITLResponse,
    ) -> None:
        """Post decision to backend with retry logic.

        Only retries on server errors (5xx) and network errors.
        Client errors (4xx) fail immediately as they won't succeed on retry.
        404/409 are treated as already resolved.

        Args:
            request_id: HITL request ID
            response: Decision response

        Raises:
            Exception: If all retries fail
        """
        payload = self._build_decision_payload(request_id, response)
        last_error = None

        for attempt in range(1, self._max_retries + 1):
            try:
                result = self._client._request("POST", "/agents/hitl/decision", json=payload)
                logger.info(
                    f"HITL decision posted successfully for {request_id} (attempt {attempt}/{self._max_retries})"
                )
                logger.debug(f"Response: {result}")
                return  # Success

            except APIError as e:
                last_error = e
                if self._handle_api_error(e, request_id, attempt):
                    return  # Request already resolved

            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Network error (attempt {attempt}/{self._max_retries}): {e}")

            except Exception as e:
                # Unexpected errors - don't retry
                logger.error(f"Unexpected error posting decision: {e}")
                raise

            # Retry delay only if not last attempt
            if attempt < self._max_retries:
                time.sleep(attempt)  # Linear backoff: 1s, 2s, 3s

        # All retries failed
        self._log_retry_exhausted(request_id, last_error)
        raise last_error

    def _build_decision_payload(self, request_id: str, response: HITLResponse) -> dict[str, Any]:
        """Build payload for decision POST request."""
        payload = {
            "request_id": request_id,
            "decision": response.decision.value,
        }

        if response.operator_input:
            payload["operator_input"] = response.operator_input

        return payload

    def _handle_api_error(self, error: APIError, request_id: str, attempt: int) -> bool:
        """Handle API error and determine if request is already resolved.

        Args:
            error: The API error to handle
            request_id: The HITL request ID
            attempt: Current attempt number

        Returns:
            True if request is already resolved (404/409), False otherwise

        Raises:
            APIError: If error is not retryable
        """
        status_code = error.status_code or 0
        RETRYABLE_STATUS_CODES = {500, 502, 503, 504}

        # 404/409 indicate the request is already resolved
        if status_code in (404, 409):
            logger.info(f"Request already resolved ({status_code}) for {request_id}")
            return True

        # Don't retry client errors (4xx)
        if 400 <= status_code < 500:
            logger.warning(f"Non-retryable error {status_code} for {request_id}: {error}")
            raise error

        # Retry server errors (5xx)
        if status_code not in RETRYABLE_STATUS_CODES:
            logger.warning(f"Unexpected status {status_code}, not retrying")
            raise error

        logger.warning(f"Server error {status_code} (attempt {attempt}/{self._max_retries}): {error}")
        return False

    def _log_retry_exhausted(self, request_id: str, last_error: Exception | None) -> None:
        """Log that retry attempts have been exhausted."""
        logger.error(f"Failed to post HITL decision for {request_id} after {self._max_retries} attempts: {last_error}")

    def wait_for_pending_decisions(self, timeout: float = 30) -> None:
        """Wait for all pending HITL decision posts to complete.

        Call this after SSE stream ends to ensure all background
        threads finish posting decisions before returning from run_agent().

        Uses adaptive timeout redistribution: when threads complete early,
        their remaining time is redistributed to remaining threads.

        Args:
            timeout: Maximum seconds to wait for all threads (default: 30)

        Raises:
            ValueError: If timeout is not positive
        """
        if timeout <= 0:
            raise ValueError("timeout must be positive")

        with self._threads_lock:
            threads_to_wait = self._active_threads.copy()

        if not threads_to_wait:
            return

        deadline = time.monotonic() + timeout
        remaining_threads = list(threads_to_wait)

        while remaining_threads:
            time_left = deadline - time.monotonic()
            if time_left <= 0:
                break

            per_thread_timeout = time_left / len(remaining_threads)
            next_round: list[threading.Thread] = []

            for thread in remaining_threads:
                thread.join(timeout=per_thread_timeout)
                if thread.is_alive():
                    logger.warning(f"HITL thread {thread.name} still running after {per_thread_timeout:.1f}s timeout")
                    next_round.append(thread)

            if len(next_round) == len(remaining_threads):
                # Break to avoid a tight loop when joins return immediately.
                break

            remaining_threads = next_round

        # Clean up finished threads
        with self._threads_lock:
            still_alive = [t for t in self._active_threads if t.is_alive()]
            if still_alive:
                logger.error(
                    f"{len(still_alive)} HITL threads did not complete within timeout. "
                    "Decisions may not have been posted."
                )
            self._active_threads = still_alive
