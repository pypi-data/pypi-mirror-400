"""Terminal capability detection for TUI applications.

This module provides terminal capability detection including TTY status, ANSI support,
OSC 52 clipboard support, mouse support, truecolor support, and OSC 11 background
color detection for automatic theme selection.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import asyncio
import os
import re
import select
import sys
import time
from dataclasses import dataclass
from typing import Literal

# Windows compatibility: termios and tty may not be available
try:
    import termios
    import tty

    _TERMIOS_AVAILABLE = True
except ImportError:  # pragma: no cover
    # Platform-specific: Windows doesn't have termios/tty modules
    # This exception is only raised on Windows or systems without termios support
    # Testing would require complex module reloading and platform-specific test setup
    _TERMIOS_AVAILABLE = False


@dataclass
class TerminalCapabilities:
    """Terminal feature detection results.

    Attributes:
        tty: Whether stdout is a TTY.
        ansi: Whether ANSI escape sequences are supported.
        osc52: Whether OSC 52 (clipboard) is supported.
        osc11_bg: Raw RGB color string from OSC 11 query, or None if not detected.
        mouse: Whether mouse support is available.
        truecolor: Whether truecolor (24-bit) color is supported.
    """

    tty: bool
    ansi: bool
    osc52: bool
    osc11_bg: str | None
    mouse: bool
    truecolor: bool

    @property
    def background_mode(self) -> Literal["light", "dark"]:
        """Derive light/dark mode from OSC 11 background color.

        Returns:
            "light" if luminance > 0.5, "dark" otherwise. Defaults to "dark"
            if osc11_bg is None.
        """
        if self.osc11_bg is None:
            return "dark"

        rgb = _parse_color_response(self.osc11_bg)
        if rgb is None:
            return "dark"

        luminance = _calculate_luminance(rgb[0], rgb[1], rgb[2])
        return "light" if luminance > 0.5 else "dark"

    @classmethod
    async def detect(cls) -> TerminalCapabilities:
        """Detect terminal capabilities asynchronously with fast timeout.

        This method performs capability detection including OSC 11 background
        color detection with a 100ms timeout. The method completes quickly
        (< 100ms) as required by the roadmap. OSC 11 detection may return None
        if the terminal doesn't respond within the timeout; use
        detect_terminal_background() for full 1-second timeout when needed.

        Returns:
            TerminalCapabilities instance with detected capabilities.
        """
        tty_available = sys.stdout.isatty()
        term = os.environ.get("TERM", "")
        colorterm = os.environ.get("COLORTERM", "")

        # Basic capability detection
        ansi = tty_available and term not in ("dumb", "")
        osc52 = detect_osc52_support()
        mouse = tty_available and term not in ("dumb", "")
        truecolor = colorterm in ("truecolor", "24bit")

        # OSC 11 detection: use fast path (<100ms timeout)
        osc11_bg: str | None = await _detect_osc11_fast()

        return cls(
            tty=tty_available,
            ansi=ansi,
            osc52=osc52,
            osc11_bg=osc11_bg,
            mouse=mouse,
            truecolor=truecolor,
        )


async def detect_terminal_background() -> str | None:
    """Detect terminal background color using OSC 11 with full timeout.

    This function can be called separately to await OSC 11 detection with the
    full 1-second timeout. Useful for theme initialization where a slight delay
    is acceptable.

    Returns:
        Raw RGB color string from terminal, or None if detection fails or times out.
    """
    if not sys.stdout.isatty() or not sys.stdin.isatty():
        return None

    if not _TERMIOS_AVAILABLE:
        return None

    return await _detect_osc11_full()


async def _detect_osc11_fast() -> str | None:
    """Fast-path OSC 11 detection (used by detect())."""
    return await _detect_osc11_impl(timeout=0.1)


async def _detect_osc11_full() -> str | None:
    """Full-timeout OSC 11 detection (used by detect_terminal_background())."""
    return await _detect_osc11_impl(timeout=1.0)


def _read_osc11_char_with_timeout(start_time: float, timeout_seconds: float) -> str | None:
    """Read a single character from stdin with timeout.

    Args:
        start_time: Start time for timeout calculation.
        timeout_seconds: Maximum time to wait.

    Returns:
        Character read or None on timeout/error.
    """
    elapsed = time.time() - start_time
    if elapsed >= timeout_seconds:
        return None

    try:
        remaining = timeout_seconds - elapsed
        ready, _, _ = select.select([sys.stdin], [], [], min(0.1, remaining))
        if not ready:
            return None

        char = sys.stdin.read(1)
        return char if char else None
    except (OSError, ValueError):
        return None


def _check_osc11_complete(response_text: str, response_length: int) -> str | None:
    """Check if OSC 11 response is complete.

    Args:
        response_text: Current response text.
        response_length: Length of response characters.

    Returns:
        Matched color string if complete, None otherwise.
    """
    match = _match_osc11_response(response_text)
    if match:
        return match

    # If we see BEL (\x07) terminator, check one more time then give up
    if "\x07" in response_text and response_length >= 10:
        return None

    return None


def _read_osc11_response_sync(timeout_seconds: float) -> str | None:
    """Synchronously read OSC 11 response from stdin.

    This runs in a thread to avoid blocking the event loop.

    Args:
        timeout_seconds: Maximum time to wait.

    Returns:
        Color string or None.
    """
    response_chars: list[str] = []
    start_time = time.time()
    max_chars = 200  # Reasonable limit to prevent infinite loops

    while len(response_chars) < max_chars:
        elapsed = time.time() - start_time
        if elapsed >= timeout_seconds:
            return None

        char = _read_osc11_char_with_timeout(start_time, timeout_seconds)
        if char is None:
            # Check timeout again after failed read
            if time.time() - start_time >= timeout_seconds:
                return None
            continue

        response_chars.append(char)
        response_text = "".join(response_chars)

        result = _check_osc11_complete(response_text, len(response_chars))
        if result is not None:
            return result

    return None


async def _detect_osc11_impl(timeout: float) -> str | None:
    """Internal OSC 11 detection implementation.

    Args:
        timeout: Maximum time to wait for terminal response in seconds.

    Returns:
        Raw RGB color string, or None on timeout/error.
    """
    if not _TERMIOS_AVAILABLE:
        return None

    old_settings = None
    try:
        # Save terminal settings
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setraw(sys.stdin.fileno())

        # Send OSC 11 query
        sys.stdout.write("\x1b]11;?\x07")
        sys.stdout.flush()

        # Read response in a thread to avoid blocking
        try:
            result = await asyncio.wait_for(asyncio.to_thread(_read_osc11_response_sync, timeout), timeout=timeout)
            return result
        except TimeoutError:
            return None

    except Exception:
        return None
    finally:
        # Restore terminal settings
        if old_settings is not None:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
            except Exception:
                pass


def _match_osc11_response(text: str) -> str | None:
    """Extract OSC 11 color response from text.

    Args:
        text: Raw text from stdin.

    Returns:
        Color string (e.g., "rgb:RRRR/GGGG/BBBB") or None if not found.
    """
    # Match OSC 11 response: \x1b]11;...\x07
    match = re.search(r"\x1b\]11;([^\x07\x1b]+)", text)
    if match:
        return match.group(1)
    return None


def _parse_color_response(color_str: str) -> tuple[int, int, int] | None:
    """Parse RGB color from various terminal color formats.

    Supports:
    - rgb:RRRR/GGGG/BBBB (16-bit per channel)
    - rgb:RR/GG/BB (8-bit per channel)
    - #RRGGBB (hex)
    - rgb(R,G,B) (decimal)

    Args:
        color_str: Color string from terminal.

    Returns:
        Tuple of (R, G, B) values in 0-255 range, or None if parsing fails.
    """
    if not color_str:
        return None

    try:
        if color_str.startswith("rgb:"):
            # Format: rgb:RRRR/GGGG/BBBB (16-bit) or rgb:RR/GG/BB (8-bit)
            parts = color_str[4:].split("/")
            if len(parts) == 3:
                r_val = int(parts[0], 16)
                g_val = int(parts[1], 16)
                b_val = int(parts[2], 16)

                # Convert 16-bit to 8-bit: if hex string has 4 digits, it's 16-bit
                # and we take the high byte (>> 8). If 2 digits, it's already 8-bit.
                if len(parts[0]) == 4:  # 16-bit format
                    r_val = r_val >> 8
                if len(parts[1]) == 4:  # 16-bit format
                    g_val = g_val >> 8
                if len(parts[2]) == 4:  # 16-bit format
                    b_val = b_val >> 8

                return (r_val, g_val, b_val)

        elif color_str.startswith("#"):
            # Format: #RRGGBB
            if len(color_str) == 7:
                r = int(color_str[1:3], 16)
                g = int(color_str[3:5], 16)
                b = int(color_str[5:7], 16)
                return (r, g, b)

        elif color_str.startswith("rgb("):
            # Format: rgb(R,G,B)
            parts = color_str[4:-1].split(",")
            if len(parts) == 3:
                r = int(parts[0].strip())
                g = int(parts[1].strip())
                b = int(parts[2].strip())
                return (r, g, b)

    except (ValueError, IndexError):
        pass

    return None


def _calculate_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance from RGB values.

    Uses the relative luminance formula from WCAG:
    L = 0.299*R + 0.587*G + 0.114*B

    Args:
        r: Red component (0-255).
        g: Green component (0-255).
        b: Blue component (0-255).

    Returns:
        Luminance value normalized to 0.0-1.0 range.
    """
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _check_terminal_in_env(env_value: str, terminals: list[str]) -> bool:
    """Check if any terminal name appears in environment value.

    Args:
        env_value: Environment variable value to check.
        terminals: List of terminal names to search for.

    Returns:
        True if any terminal name is found in env_value.
    """
    return any(terminal in env_value for terminal in terminals)


def detect_osc52_support() -> bool:
    """Check if terminal likely supports OSC 52 (clipboard).

    Returns:
        True if terminal name suggests OSC 52 support.
    """
    term = os.environ.get("TERM", "").lower()
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    term_program_version = os.environ.get("TERM_PROGRAM_VERSION", "").lower()

    # Known terminals that support OSC 52
    osc52_terminals = [
        "iterm",
        "kitty",
        "alacritty",
        "wezterm",
        "vscode",
        "windows terminal",
        "mintty",  # Windows terminal emulator
    ]

    # Check TERM_PROGRAM first (most reliable)
    if term_program and _check_terminal_in_env(term_program, osc52_terminals):
        return True

    # Check TERM_PROGRAM_VERSION (VS Code uses this)
    if term_program_version and _check_terminal_in_env(term_program_version, osc52_terminals):
        return True

    # Check TERM (less reliable but sometimes works)
    if term and _check_terminal_in_env(term, osc52_terminals):
        return True

    return False
