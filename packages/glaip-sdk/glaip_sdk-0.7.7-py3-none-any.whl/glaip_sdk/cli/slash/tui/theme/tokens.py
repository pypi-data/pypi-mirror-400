"""Theme token definitions for TUI applications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ThemeModeLiteral = Literal["light", "dark"]


@dataclass(frozen=True, slots=True)
class ThemeTokens:
    """Color token set for a built-in theme."""

    name: str
    mode: ThemeModeLiteral

    primary: str
    secondary: str
    accent: str

    background: str
    background_panel: str

    text: str
    text_muted: str

    success: str
    warning: str
    error: str
    info: str

    def as_dict(self) -> dict[str, str]:
        """Return color tokens as a plain dictionary.

        Returns only color tokens (primary, secondary, accent, background, etc.),
        excluding metadata fields (name, mode). This is intentional for use cases
        like Textual TCSS mapping where only color values are needed.

        Returns:
            Dictionary mapping color token names to hex color strings.
        """
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "background_panel": self.background_panel,
            "text": self.text,
            "text_muted": self.text_muted,
            "success": self.success,
            "warning": self.warning,
            "error": self.error,
            "info": self.info,
        }
