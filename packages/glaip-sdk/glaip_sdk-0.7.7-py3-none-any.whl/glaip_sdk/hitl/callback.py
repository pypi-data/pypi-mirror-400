"""Pause/resume callback for HITL renderer control.

This module provides PauseResumeCallback which allows HITL prompt handlers
to control the live renderer without directly coupling to the renderer implementation.

Author:
    Putu Ravindra Wiguna (putu.r.wiguna@gdplabs.id)
"""

from typing import Any


class PauseResumeCallback:
    """Simple callback object for pausing/resuming the live renderer.

    This allows the LocalPromptHandler to control the renderer without
    directly coupling to the renderer implementation.
    """

    def __init__(self) -> None:
        """Initialize the callback."""
        self._renderer: Any | None = None

    def set_renderer(self, renderer: Any) -> None:
        """Set the renderer instance.

        Args:
            renderer: RichStreamRenderer instance with pause_live() and resume_live() methods.
        """
        self._renderer = renderer

    def pause(self) -> None:
        """Pause the live renderer before prompting."""
        if self._renderer and hasattr(self._renderer, "_shutdown_live"):
            self._renderer._shutdown_live()

    def resume(self) -> None:
        """Resume the live renderer after prompting."""
        if self._renderer and hasattr(self._renderer, "_ensure_live"):
            self._renderer._ensure_live()


__all__ = ["PauseResumeCallback"]
