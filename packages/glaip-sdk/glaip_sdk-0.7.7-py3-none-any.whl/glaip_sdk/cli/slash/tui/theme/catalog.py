"""Built-in theme catalog for TUI applications.

This module implements Phase 2 of the TUI Theme System spec, providing a foundational
set of 12 color tokens (primary, secondary, accent, background, background_panel, text,
text_muted, success, warning, error, info). Additional tokens (e.g., diff.added,
syntax.*, backgroundElevated, textDim) will be added in future phases per the spec's
"100+ color tokens" requirement.
"""

from __future__ import annotations

from glaip_sdk.cli.slash.tui.theme.tokens import ThemeModeLiteral, ThemeTokens

_BUILTIN_THEMES: dict[str, ThemeTokens] = {
    "gl-dark": ThemeTokens(
        name="gl-dark",
        mode="dark",
        primary="#6EA8FE",
        secondary="#ADB5BD",
        accent="#C77DFF",
        background="#0B0F19",
        background_panel="#111827",
        text="#E5E7EB",
        text_muted="#9CA3AF",
        success="#34D399",
        warning="#FBBF24",
        error="#F87171",
        info="#60A5FA",
    ),
    "gl-light": ThemeTokens(
        name="gl-light",
        mode="light",
        primary="#1D4ED8",
        secondary="#4B5563",
        accent="#7C3AED",
        background="#FFFFFF",
        background_panel="#F3F4F6",
        text="#111827",
        text_muted="#4B5563",
        success="#059669",
        warning="#B45309",
        error="#B91C1C",
        info="#1D4ED8",
    ),
    "gl-high-contrast": ThemeTokens(
        name="gl-high-contrast",
        mode="dark",
        # High-contrast theme uses uniform colors (#FFFFFF on #000000) to maximize
        # contrast for accessibility. Semantic distinctions (success/warning/error)
        # are intentionally uniform to prioritize maximum readability over color
        # coding, per accessibility best practices for high-contrast modes.
        primary="#FFFFFF",
        secondary="#FFFFFF",
        accent="#FFFFFF",
        background="#000000",
        background_panel="#000000",
        text="#FFFFFF",
        text_muted="#FFFFFF",
        success="#FFFFFF",
        warning="#FFFFFF",
        error="#FFFFFF",
        info="#FFFFFF",
    ),
}


def get_builtin_theme(name: str) -> ThemeTokens | None:
    """Return a built-in theme by name."""
    return _BUILTIN_THEMES.get(name)


def list_builtin_themes() -> list[str]:
    """List available built-in theme names."""
    return sorted(_BUILTIN_THEMES)


def default_theme_name_for_mode(mode: ThemeModeLiteral) -> str:
    """Return the default theme name for the given light/dark mode."""
    return "gl-light" if mode == "light" else "gl-dark"
