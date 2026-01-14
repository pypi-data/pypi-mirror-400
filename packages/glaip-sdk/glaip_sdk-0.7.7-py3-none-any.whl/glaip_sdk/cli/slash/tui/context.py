"""Shared context for all TUI components.

This module provides the TUIContext dataclass, which serves as the Python equivalent
of OpenCode's nested provider pattern. It provides a single container for all TUI
services and state that can be injected into components.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from glaip_sdk.cli.slash.tui.terminal import TerminalCapabilities
from glaip_sdk.cli.slash.tui.theme import ThemeManager

if TYPE_CHECKING:
    from glaip_sdk.cli.slash.tui.toast import ToastBus


@dataclass
class TUIContext:
    """Shared context for all TUI components (Python equivalent of OpenCode's providers).

    This context provides access to all TUI services and state. Components that will
    be implemented in later phases are typed as Optional and will be None initially.

    Attributes:
        terminal: Terminal capability detection results.
        keybinds: Central keybind registry (Phase 3).
        theme: Theme manager for light/dark mode and color tokens (Phase 2).
        toasts: Toast notification bus (Phase 4).
        clipboard: Clipboard adapter with OSC 52 support (Phase 4).
    """

    terminal: TerminalCapabilities
    keybinds: object | None = None
    theme: ThemeManager | None = None
    toasts: ToastBus | None = None
    clipboard: object | None = None

    @classmethod
    async def create(cls) -> TUIContext:
        """Create a TUIContext instance with detected terminal capabilities.

        This factory method detects terminal capabilities asynchronously and
        returns a populated TUIContext instance. Other components (keybinds,
        theme, toasts, clipboard) will be set incrementally as they are created.

        Returns:
            TUIContext instance with terminal capabilities detected.
        """
        terminal = await TerminalCapabilities.detect()
        theme_name = os.getenv("AIP_TUI_THEME") or None
        theme = ThemeManager(terminal, theme=theme_name)
        return cls(terminal=terminal, theme=theme)
