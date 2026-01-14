"""Toast notification helpers for Textual TUIs.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import Enum


class ToastVariant(str, Enum):
    """Toast message variant."""

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


DEFAULT_TOAST_DURATIONS_SECONDS: dict[ToastVariant, float] = {
    ToastVariant.SUCCESS: 2.0,
    ToastVariant.INFO: 3.0,
    ToastVariant.WARNING: 3.0,
    ToastVariant.ERROR: 5.0,
}


@dataclass(frozen=True, slots=True)
class ToastState:
    """Immutable toast payload."""

    message: str
    variant: ToastVariant
    duration_seconds: float


class ToastBus:
    """Single-toast state holder with auto-dismiss."""

    def __init__(self) -> None:
        """Initialize the bus."""
        self._state: ToastState | None = None
        self._dismiss_task: asyncio.Task[None] | None = None

    @property
    def state(self) -> ToastState | None:
        """Return the current toast state."""
        return self._state

    def show(
        self,
        message: str,
        variant: ToastVariant | str = ToastVariant.INFO,
        *,
        duration_seconds: float | None = None,
    ) -> None:
        """Set toast state and schedule auto-dismiss."""
        resolved_variant = self._coerce_variant(variant)
        resolved_duration = (
            DEFAULT_TOAST_DURATIONS_SECONDS[resolved_variant] if duration_seconds is None else float(duration_seconds)
        )

        self._state = ToastState(
            message=message,
            variant=resolved_variant,
            duration_seconds=resolved_duration,
        )

        self._cancel_dismiss_task()

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            raise RuntimeError(
                "Cannot schedule toast auto-dismiss: no running event loop. "
                "ToastBus.show() must be called from within an async context."
            ) from None

        self._dismiss_task = loop.create_task(self._auto_dismiss(resolved_duration))

    def clear(self) -> None:
        """Clear the current toast."""
        self._cancel_dismiss_task()
        self._state = None

    def copy_success(self, label: str | None = None) -> None:
        """Show clipboard success toast."""
        message = "Copied to clipboard" if not label else f"Copied {label} to clipboard"
        self.show(message=message, variant=ToastVariant.SUCCESS)

    def copy_failed(self) -> None:
        """Show clipboard failure toast."""
        self.show(
            message="Clipboard unavailable. Text printed below",
            variant=ToastVariant.WARNING,
        )

    def _coerce_variant(self, variant: ToastVariant | str) -> ToastVariant:
        if isinstance(variant, ToastVariant):
            return variant
        try:
            return ToastVariant(variant)
        except ValueError:
            return ToastVariant.INFO

    def _cancel_dismiss_task(self) -> None:
        if self._dismiss_task is None:
            return
        if not self._dismiss_task.done():
            self._dismiss_task.cancel()
        self._dismiss_task = None

    async def _auto_dismiss(self, duration_seconds: float) -> None:
        try:
            await asyncio.sleep(duration_seconds)
        except asyncio.CancelledError:
            return

        self._state = None
        self._dismiss_task = None
