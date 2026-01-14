"""Clipboard adapter for TUI copy actions."""

from __future__ import annotations

import base64
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any
from collections.abc import Callable

from glaip_sdk.cli.slash.tui.terminal import TerminalCapabilities, detect_osc52_support


class ClipboardMethod(str, Enum):
    """Supported clipboard backends."""

    OSC52 = "osc52"
    PBCOPY = "pbcopy"
    XCLIP = "xclip"
    XSEL = "xsel"
    WL_COPY = "wl-copy"
    CLIP = "clip"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class ClipboardResult:
    """Result of a clipboard operation."""

    success: bool
    method: ClipboardMethod
    message: str


_SUBPROCESS_COMMANDS: dict[ClipboardMethod, list[str]] = {
    ClipboardMethod.PBCOPY: ["pbcopy"],
    ClipboardMethod.XCLIP: ["xclip", "-selection", "clipboard"],
    ClipboardMethod.XSEL: ["xsel", "--clipboard", "--input"],
    ClipboardMethod.WL_COPY: ["wl-copy"],
    ClipboardMethod.CLIP: ["clip"],
}


class ClipboardAdapter:
    """Cross-platform clipboard access with OSC 52 fallback."""

    def __init__(
        self,
        *,
        terminal: TerminalCapabilities | None = None,
        method: ClipboardMethod | None = None,
    ) -> None:
        """Initialize the adapter."""
        self._terminal = terminal
        self._method = method or self._detect_method()

    @property
    def method(self) -> ClipboardMethod:
        """Return the detected clipboard backend."""
        return self._method

    def copy(self, text: str, *, writer: Callable[[str], Any] | None = None) -> ClipboardResult:
        """Copy text to clipboard using the best available method.

        Args:
            text: Text to copy.
            writer: Optional function to write OSC 52 sequence (e.g., self.app.console.write).
                   Defaults to sys.stdout.write if not provided.
        """
        if self._method == ClipboardMethod.OSC52:
            return self._copy_osc52(text, writer=writer)

        command = _SUBPROCESS_COMMANDS.get(self._method)
        if command is None:
            return self._copy_osc52(text, writer=writer)

        result = self._copy_subprocess(command, text)
        if not result.success:
            return self._copy_osc52(text, writer=writer)

        return result

    def _detect_method(self) -> ClipboardMethod:
        if self._terminal.osc52 if self._terminal else detect_osc52_support():
            return ClipboardMethod.OSC52

        system = platform.system()
        if system == "Darwin":
            return self._detect_darwin_method()
        if system == "Linux":
            return self._detect_linux_method()
        if system == "Windows":
            return self._detect_windows_method()
        return ClipboardMethod.NONE

    def _detect_darwin_method(self) -> ClipboardMethod:
        return ClipboardMethod.PBCOPY if shutil.which("pbcopy") else ClipboardMethod.NONE

    def _detect_linux_method(self) -> ClipboardMethod:
        if not os.getenv("DISPLAY") and not os.getenv("WAYLAND_DISPLAY"):
            return ClipboardMethod.NONE

        for cmd, method in (
            ("xclip", ClipboardMethod.XCLIP),
            ("xsel", ClipboardMethod.XSEL),
            ("wl-copy", ClipboardMethod.WL_COPY),
        ):
            if shutil.which(cmd):
                return method
        return ClipboardMethod.NONE

    def _detect_windows_method(self) -> ClipboardMethod:
        return ClipboardMethod.CLIP if shutil.which("clip") else ClipboardMethod.NONE

    def _copy_osc52(self, text: str, *, writer: Callable[[str], Any] | None = None) -> ClipboardResult:
        encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
        sequence = f"\x1b]52;c;{encoded}\x07"
        try:
            if writer:
                writer(sequence)
            else:
                sys.stdout.write(sequence)
                sys.stdout.flush()
        except Exception as exc:
            return ClipboardResult(False, ClipboardMethod.OSC52, str(exc))

        return ClipboardResult(True, ClipboardMethod.OSC52, "Copied to clipboard")

    def _copy_subprocess(self, cmd: list[str], text: str) -> ClipboardResult:
        try:
            completed = subprocess.run(
                cmd,
                input=text.encode("utf-8"),
                check=False,
            )
        except OSError as exc:
            return ClipboardResult(False, self._method, str(exc))

        if completed.returncode == 0:
            return ClipboardResult(True, self._method, "Copied to clipboard")

        return ClipboardResult(False, self._method, f"Command failed: {completed.returncode}")
