"""Shared formatting helpers for CLI commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import json
from typing import Any


def _is_sensitive_data(val: Any) -> bool:
    """Check if value contains sensitive authentication data.

    Args:
        val: Value to check for sensitive information

    Returns:
        True if the value appears to contain sensitive data
    """
    if not isinstance(val, dict):
        return False

    sensitive_patterns = {"token", "password", "secret", "key", "credential"}
    return any(pattern in str(k).lower() for k in val.keys() for pattern in sensitive_patterns)


def _redact_sensitive_dict(val: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive fields from a dictionary.

    Args:
        val: Dictionary to redact

    Returns:
        Redacted dictionary
    """
    redacted = val.copy()
    sensitive_patterns = {"token", "password", "secret", "key", "credential"}
    for k in redacted.keys():
        if any(pattern in k.lower() for pattern in sensitive_patterns):
            redacted[k] = "<REDACTED>"
    return redacted


def _format_dict_value(val: dict[str, Any]) -> str:
    """Format a dictionary value for display.

    Args:
        val: Dictionary to format

    Returns:
        Formatted string representation
    """
    if _is_sensitive_data(val):
        redacted = _redact_sensitive_dict(val)
        return json.dumps(redacted, indent=2)
    return json.dumps(val, indent=2)


def _format_preview_value(val: Any) -> str:
    """Format a value for display in update preview with sensitive data redaction.

    Args:
        val: Value to format

    Returns:
        Formatted string representation of the value
    """
    if val is None:
        return "[dim]None[/dim]"
    if isinstance(val, dict):
        return _format_dict_value(val)
    if isinstance(val, str):
        return f'"{val}"' if val else '""'
    return str(val)


def _format_empty_override_warnings(empty_fields: list[str]) -> list[str]:
    """Format warning lines for empty CLI overrides.

    Args:
        empty_fields: List of field names with empty string overrides

    Returns:
        List of formatted warning lines
    """
    if not empty_fields:
        return []

    warnings = ["\n[yellow]⚠️  Warning: Empty values provided via CLI will override import values[/yellow]"]
    warnings.extend(f"- [yellow]{field}: will be set to empty string[/yellow]" for field in empty_fields)
    return warnings
