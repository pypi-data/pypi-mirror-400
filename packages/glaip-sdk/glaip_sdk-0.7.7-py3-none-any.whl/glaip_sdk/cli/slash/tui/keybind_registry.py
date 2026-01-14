"""Keybinding registry helpers for TUI applications."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

DEFAULT_LEADER = "ctrl+x"
_LEADER_TOKEN = "<leader>"

_MODIFIER_ORDER = ("ctrl", "alt", "shift", "meta")
_MODIFIER_SYNONYMS = {
    "control": "ctrl",
    "ctl": "ctrl",
    "cmd": "meta",
    "command": "meta",
    "option": "alt",
    "return": "enter",
}

_KEY_SYNONYMS = {
    "esc": "escape",
}

_KEY_DISPLAY = {
    "escape": "Esc",
    "enter": "Enter",
    "space": "Space",
    "tab": "Tab",
    "backspace": "Backspace",
}


@dataclass(frozen=True, slots=True)
class Keybind:
    """A registered keybinding."""

    action: str
    sequence: tuple[str, ...]
    description: str
    category: str | None = None

    def __repr__(self) -> str:
        """Return a readable representation of the keybind."""
        return (
            f"Keybind(action={self.action!r}, sequence={self.sequence}, "
            f"description={self.description!r}, category={self.category!r})"
        )


class KeybindRegistry:
    """Central registry of keybindings and associated metadata."""

    def __init__(self, *, leader: str = DEFAULT_LEADER) -> None:
        """Initialize the registry."""
        normalized = _normalize_chord(leader)
        self._leader = normalized or DEFAULT_LEADER
        self._keybinds: dict[str, Keybind] = {}

    @property
    def leader(self) -> str:
        """Return the normalized leader chord."""
        return self._leader

    def register(
        self,
        *,
        action: str,
        key: str,
        description: str,
        category: str | None = None,
    ) -> Keybind:
        """Register a keybinding for an action."""
        if action in self._keybinds:
            raise ValueError(f"Action already registered: {action}")

        sequence = parse_key_sequence(key)
        keybind = Keybind(action=action, sequence=sequence, description=description, category=category)
        self._keybinds[action] = keybind
        return keybind

    def get(self, action: str) -> Keybind | None:
        """Return keybind for action, if present."""
        return self._keybinds.get(action)

    def actions(self) -> list[str]:
        """Return sorted list of registered actions."""
        return sorted(self._keybinds)

    def matches(self, action: str, sequence: str | Iterable[str]) -> bool:
        """Return True if the provided sequence matches the action's keybind."""
        keybind = self._keybinds.get(action)
        if keybind is None:
            return False

        candidate = _coerce_sequence(sequence)
        return candidate == keybind.sequence

    def format(self, action: str) -> str:
        """Return a human-readable sequence for an action."""
        keybind = self._keybinds.get(action)
        if keybind is None:
            return ""

        return format_key_sequence(keybind.sequence, leader=self._leader)


def parse_key_sequence(key: str) -> tuple[str, ...]:
    """Parse a key sequence string into normalized tokens."""
    tokens = [token for token in key.strip().split() if token]
    normalized: list[str] = []

    for token in tokens:
        if token.lower() == _LEADER_TOKEN:
            normalized.append(_LEADER_TOKEN)
            continue

        chord = _normalize_chord(token)
        if chord:
            normalized.append(chord)

    return tuple(normalized)


def format_key_sequence(sequence: tuple[str, ...], *, leader: str = DEFAULT_LEADER) -> str:
    """Format a normalized sequence into a display string."""
    rendered: list[str] = []

    for token in sequence:
        if token == _LEADER_TOKEN:
            rendered.append(_format_token(leader))
            continue
        rendered.append(_format_token(token))

    return " ".join(rendered)


def _coerce_sequence(sequence: str | Iterable[str]) -> tuple[str, ...]:
    if isinstance(sequence, str):
        return parse_key_sequence(sequence)

    tokens: list[str] = []
    for token in sequence:
        if not token:
            continue
        if token.lower() == _LEADER_TOKEN:
            tokens.append(_LEADER_TOKEN)
            continue
        chord = _normalize_chord(token)
        if chord:
            tokens.append(chord)

    return tuple(tokens)


def _normalize_chord(chord: str) -> str:
    """Normalize a key chord string to canonical form.

    Normalization rules:
    - Converts separators: both '-' and '+' are normalized to '+'
    - Handles synonyms: 'control'/'ctl' -> 'ctrl', 'cmd'/'command' -> 'meta', 'option' -> 'alt'
    - Deduplicates modifiers: 'ctrl+ctrl+l' -> 'ctrl+l'
    - Orders modifiers: ctrl < alt < shift < meta (unknown modifiers sort last)
    - Case-insensitive: 'Ctrl+L' == 'ctrl+l' == 'CTRL-L'

    Args:
        chord: Key chord string (e.g., "Ctrl+L", "ctrl-l", "CTRL+CTRL+L")

    Returns:
        Normalized chord string (e.g., "ctrl+l") or empty string if invalid.
    """
    parts = [part for part in chord.replace("-", "+").split("+") if part.strip()]
    if not parts:
        return ""

    normalized_parts = [_normalize_key_part(part) for part in parts]
    if len(normalized_parts) == 1:
        return normalized_parts[0]

    modifiers, key = normalized_parts[:-1], normalized_parts[-1]

    seen: set[str] = set()
    unique_mods: list[str] = []
    for mod in modifiers:
        if mod in seen:
            continue
        seen.add(mod)
        unique_mods.append(mod)

    unique_mods.sort(key=_modifier_sort_key)
    return "+".join([*unique_mods, key])


def _normalize_key_part(part: str) -> str:
    token = part.strip().lower()
    token = _MODIFIER_SYNONYMS.get(token, token)
    return _KEY_SYNONYMS.get(token, token)


def _modifier_sort_key(modifier: str) -> int:
    try:
        return _MODIFIER_ORDER.index(modifier)
    except ValueError:
        return len(_MODIFIER_ORDER)


def _format_token(token: str) -> str:
    if "+" in token:
        return _format_chord(token)

    return _KEY_DISPLAY.get(token, token)


def _format_chord(chord: str) -> str:
    parts = chord.split("+")
    modifiers, key = parts[:-1], parts[-1]

    rendered_mods: list[str] = []
    for mod in modifiers:
        if mod == "ctrl":
            rendered_mods.append("Ctrl")
        elif mod == "alt":
            rendered_mods.append("Alt")
        elif mod == "shift":
            rendered_mods.append("Shift")
        elif mod == "meta":
            rendered_mods.append("Meta")
        else:
            rendered_mods.append(mod.title())

    rendered_key = _KEY_DISPLAY.get(key, key)
    if len(rendered_key) == 1 and rendered_key.isalpha():
        rendered_key = rendered_key.upper()

    return "+".join([*rendered_mods, rendered_key])
