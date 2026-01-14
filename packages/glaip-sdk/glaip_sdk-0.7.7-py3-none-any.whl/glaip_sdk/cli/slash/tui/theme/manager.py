"""Theme manager for TUI applications."""

from __future__ import annotations

import logging
from enum import Enum
from typing import Literal

from glaip_sdk.cli.slash.tui.terminal import TerminalCapabilities
from glaip_sdk.cli.slash.tui.theme.catalog import default_theme_name_for_mode, get_builtin_theme
from glaip_sdk.cli.slash.tui.theme.tokens import ThemeTokens

logger = logging.getLogger(__name__)


class ThemeMode(str, Enum):
    """User-selectable theme mode."""

    AUTO = "auto"
    LIGHT = "light"
    DARK = "dark"


class ThemeManager:
    """Resolve active theme tokens from terminal state and user preferences."""

    def __init__(
        self,
        terminal: TerminalCapabilities,
        *,
        mode: ThemeMode | str = ThemeMode.AUTO,
        theme: str | None = None,
    ) -> None:
        """Initialize the theme manager."""
        self._terminal = terminal
        self._mode = self._coerce_mode(mode)
        self._theme = theme

    @property
    def mode(self) -> ThemeMode:
        """Return configured mode (auto/light/dark)."""
        return self._mode

    @property
    def effective_mode(self) -> Literal["light", "dark"]:
        """Return resolved light/dark mode."""
        if self._mode == ThemeMode.AUTO:
            return self._terminal.background_mode
        return "light" if self._mode == ThemeMode.LIGHT else "dark"

    @property
    def theme_name(self) -> str:
        """Return resolved theme name."""
        return self._theme or default_theme_name_for_mode(self.effective_mode)

    @property
    def tokens(self) -> ThemeTokens:
        """Return tokens for the resolved theme."""
        chosen = get_builtin_theme(self.theme_name)
        if chosen is not None:
            return chosen

        fallback_name = default_theme_name_for_mode(self.effective_mode)
        fallback = get_builtin_theme(fallback_name)
        if fallback is None:
            raise RuntimeError(f"Missing default theme: {fallback_name}")

        return fallback

    def set_mode(self, mode: ThemeMode | str) -> None:
        """Set auto/light/dark mode."""
        self._mode = self._coerce_mode(mode)

    def set_theme(self, theme: str | None) -> None:
        """Set explicit theme name (or None to use the default)."""
        self._theme = theme

    def _coerce_mode(self, mode: ThemeMode | str) -> ThemeMode:
        """Coerce a mode value to ThemeMode enum, defaulting to AUTO on invalid input."""
        if isinstance(mode, ThemeMode):
            return mode
        try:
            return ThemeMode(mode)
        except ValueError:
            logger.warning(f"Invalid theme mode '{mode}', defaulting to AUTO")
            return ThemeMode.AUTO
