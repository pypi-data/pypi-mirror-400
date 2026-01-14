"""Textual UI helpers for slash commands."""

from glaip_sdk.cli.slash.tui.clipboard import ClipboardAdapter, ClipboardResult
from glaip_sdk.cli.slash.tui.context import TUIContext
from glaip_sdk.cli.slash.tui.keybind_registry import (
    Keybind,
    KeybindRegistry,
    format_key_sequence,
    parse_key_sequence,
)
from glaip_sdk.cli.slash.tui.toast import ToastBus, ToastVariant
from glaip_sdk.cli.slash.tui.remote_runs_app import (
    RemoteRunsTextualApp,
    RemoteRunsTUICallbacks,
    run_remote_runs_textual,
)
from glaip_sdk.cli.slash.tui.terminal import TerminalCapabilities, detect_terminal_background

__all__ = [
    "TUIContext",
    "ToastBus",
    "ToastVariant",
    "TerminalCapabilities",
    "detect_terminal_background",
    "RemoteRunsTextualApp",
    "RemoteRunsTUICallbacks",
    "run_remote_runs_textual",
    "KeybindRegistry",
    "Keybind",
    "parse_key_sequence",
    "format_key_sequence",
    "ClipboardAdapter",
    "ClipboardResult",
]
