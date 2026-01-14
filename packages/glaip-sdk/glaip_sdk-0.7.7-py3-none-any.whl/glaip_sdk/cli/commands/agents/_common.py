"""Common helpers and group definition for agent commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

import click
from rich.console import Console

from glaip_sdk.branding import (
    ERROR_STYLE,
    HINT_PREFIX_STYLE,
    WARNING_STYLE,
)
from glaip_sdk.cli.constants import DEFAULT_AGENT_INSTRUCTION_PREVIEW_LIMIT
from glaip_sdk.config.constants import AGENT_CONFIG_FIELDS, DEFAULT_MODEL
from glaip_sdk.cli.context import get_ctx_value
from glaip_sdk.cli.display import (
    build_resource_result_data,
    handle_json_output,
    handle_rich_output,
    print_api_error,
)
from glaip_sdk.cli.hints import in_slash_mode
from glaip_sdk.cli.io import fetch_raw_resource_details
from glaip_sdk.cli.resolution import resolve_resource_reference
from glaip_sdk.cli.rich_helpers import markup_text
from glaip_sdk.cli.core.output import (
    output_result,
)
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.icons import ICON_AGENT
from glaip_sdk.utils import format_datetime, is_uuid

console = Console()

# Error message constants
AGENT_NOT_FOUND_ERROR = "Agent not found"


def _safe_agent_attribute(agent: Any, name: str) -> Any:
    """Return attribute value for ``name`` while filtering Mock sentinels."""
    try:
        value = getattr(agent, name)
    except Exception:
        return None

    if hasattr(value, "_mock_name"):
        return None
    return value


def _coerce_mapping_candidate(candidate: Any) -> dict[str, Any] | None:
    """Convert a mapping-like candidate to a plain dict when possible."""
    if candidate is None:
        return None
    if isinstance(candidate, Mapping):
        return dict(candidate)
    return None


def _call_agent_method(agent: Any, method_name: str) -> dict[str, Any] | None:
    """Attempt to call the named method and coerce its output to a dict."""
    method = getattr(agent, method_name, None)
    if not callable(method):
        return None
    try:
        candidate = method()
    except Exception:
        return None
    return _coerce_mapping_candidate(candidate)


def _coerce_agent_via_methods(agent: Any) -> dict[str, Any] | None:
    """Try standard serialisation helpers to produce a mapping."""
    for attr in ("model_dump", "dict", "to_dict"):
        mapping = _call_agent_method(agent, attr)
        if mapping is not None:
            return mapping
    return None


def _build_fallback_agent_mapping(agent: Any) -> dict[str, Any]:
    """Construct a minimal mapping from well-known agent attributes."""
    fallback_fields = (
        "id",
        "name",
        "instruction",
        "description",
        "model",
        "agent_config",
        *[field for field in AGENT_CONFIG_FIELDS if field not in ("name", "instruction", "model")],
        "tool_configs",
    )

    fallback: dict[str, Any] = {}
    for field in fallback_fields:
        value = _safe_agent_attribute(agent, field)
        if value is not None:
            fallback[field] = value

    return fallback or {"name": str(agent)}


def _prepare_agent_output(agent: Any) -> dict[str, Any]:
    """Build a JSON-serialisable mapping for CLI output."""
    method_mapping = _coerce_agent_via_methods(agent)
    if method_mapping is not None:
        return method_mapping

    intrinsic = _coerce_mapping_candidate(agent)
    if intrinsic is not None:
        return intrinsic

    return _build_fallback_agent_mapping(agent)


def _fetch_full_agent_details(client: Any, agent: Any) -> Any | None:
    """Fetch full agent details by ID to ensure all fields are populated."""
    try:
        agent_id = str(getattr(agent, "id", "")).strip()
        if agent_id:
            return client.agents.get_agent_by_id(agent_id)
    except Exception:
        # If fetching full details fails, continue with the resolved object
        pass
    return agent


def _normalise_model_name(value: Any) -> str | None:
    """Return a cleaned model name or None when not usable."""
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip()
        return cleaned or None
    if isinstance(value, bool):
        return None
    return str(value)


def _model_from_config(agent: Any) -> str | None:
    """Extract a usable model name from an agent's configuration mapping."""
    config = getattr(agent, "agent_config", None)
    if not config or not isinstance(config, dict):
        return None

    for key in ("lm_name", "model"):
        normalised = _normalise_model_name(config.get(key))
        if normalised:
            return normalised
    return None


def _get_agent_model_name(agent: Any) -> str | None:
    """Extract model name from agent configuration."""
    config_model = _model_from_config(agent)
    if config_model:
        return config_model

    normalised_attr = _normalise_model_name(getattr(agent, "model", None))
    if normalised_attr:
        return normalised_attr

    return DEFAULT_MODEL


def _resolve_resources_by_name(
    _client: Any, items: tuple[str, ...], resource_type: str, find_func: Any, label: str
) -> list[str]:
    """Resolve resource names/IDs to IDs, handling ambiguity.

    Args:
        client: API client
        items: Tuple of resource names/IDs
        resource_type: Type of resource ("tool" or "agent")
        find_func: Function to find resources by name
        label: Label for error messages

    Returns:
        List of resolved resource IDs
    """
    out = []
    for ref in items or ():
        if is_uuid(ref):
            out.append(ref)
            continue

        matches = find_func(name=ref)
        if not matches:
            raise click.ClickException(f"{label} not found: {ref}")
        if len(matches) > 1:
            raise click.ClickException(f"Multiple {resource_type}s named '{ref}'. Use ID instead.")
        out.append(str(matches[0].id))
    return out


def _split_comma_separated_refs(items: tuple[str, ...] | None) -> tuple[str, ...]:
    """Expand comma-separated CLI values into a flat tuple.

    Click ``multiple=True`` options can be provided as repeated flags (``--tools t1 --tools t2``)
    or as a single comma-separated value (``--tools t1,t2``). Keep both forms working.
    """
    if not items:
        return ()

    resolved: list[str] = []
    for item in items:
        if item is None:
            continue
        for part in str(item).split(","):
            cleaned = part.strip()
            if cleaned:
                resolved.append(cleaned)
    return tuple(resolved)


def _fetch_and_format_raw_agent_data(client: Any, agent: Any) -> dict | None:
    """Fetch raw agent data and format it for display."""
    try:
        raw_agent_data = fetch_raw_resource_details(client, agent, "agents")
        if not raw_agent_data:
            return None

        # Format dates for better display
        formatted_data = raw_agent_data.copy()
        if "created_at" in formatted_data:
            formatted_data["created_at"] = format_datetime(formatted_data["created_at"])
        if "updated_at" in formatted_data:
            formatted_data["updated_at"] = format_datetime(formatted_data["updated_at"])

        return formatted_data
    except Exception:
        return None


def _format_fallback_agent_data(client: Any, agent: Any) -> dict:
    """Format fallback agent data using Pydantic model."""
    full_agent = _fetch_full_agent_details(client, agent)

    # Define fields to extract
    fields = [
        "id",
        "name",
        "type",
        "framework",
        "version",
        "description",
        "instruction",
        "created_at",
        "updated_at",
        "metadata",
        "language_model_id",
        "agent_config",
        "tools",
        "agents",
        "mcps",
        "a2a_profile",
        "tool_configs",
    ]

    result_data = build_resource_result_data(full_agent, fields)

    # Handle missing instruction
    if result_data.get("instruction") in ["N/A", None, ""]:
        result_data["instruction"] = "-"

    # Format dates for better display
    for date_field in ["created_at", "updated_at"]:
        if result_data.get(date_field) and result_data[date_field] not in ["N/A", None]:
            result_data[date_field] = format_datetime(result_data[date_field])

    return result_data


def _clamp_instruction_preview_limit(limit: int | None) -> int:
    """Normalise preview limit; 0 disables trimming."""
    default = DEFAULT_AGENT_INSTRUCTION_PREVIEW_LIMIT
    if limit is None:  # pragma: no cover
        return default
    try:
        limit_value = int(limit)
    except (TypeError, ValueError):  # pragma: no cover - defensive parsing
        return default

    if limit_value <= 0:
        return 0

    return limit_value


def _build_instruction_preview(value: Any, limit: int) -> tuple[Any, bool]:
    """Return a trimmed preview for long instruction strings."""
    if not isinstance(value, str) or limit <= 0:  # pragma: no cover
        return value, False

    if len(value) <= limit:
        return value, False

    trimmed_value = value[:limit].rstrip()
    preview = f"{trimmed_value}\n\n... (preview trimmed)"
    return preview, True


def _prepare_agent_details_payload(
    data: dict[str, Any],
    *,
    instruction_preview_limit: int,
) -> tuple[dict[str, Any], bool]:
    """Return payload ready for rendering plus trim indicator."""
    payload = deepcopy(data)
    trimmed = False
    if instruction_preview_limit > 0:
        preview, trimmed = _build_instruction_preview(payload.get("instruction"), instruction_preview_limit)
        if trimmed:
            payload["instruction"] = preview
    return payload, trimmed


def _show_instruction_trim_hint(
    ctx: Any,
    *,
    trimmed: bool,
    preview_limit: int,
) -> None:
    """Render hint describing how to expand or collapse the instruction preview."""
    if not trimmed or preview_limit <= 0:
        return

    view = get_ctx_value(ctx, "view", "rich") if ctx is not None else "rich"
    if view != "rich":  # pragma: no cover - non-rich view handling
        return

    suffix = f"[dim](preview: {preview_limit:,} chars)[/]"
    if in_slash_mode(ctx):
        console.print(
            f"[{HINT_PREFIX_STYLE}]Tip:[/] Use '/details' again to toggle between trimmed and full prompts {suffix}"
        )
        return

    console.print(  # pragma: no cover - fallback hint rendering
        f"[{HINT_PREFIX_STYLE}]Tip:[/] Run 'aip agents get <agent> --instruction-preview <n>' "
        f"to control prompt preview length {suffix}"
    )


def _display_agent_details(
    ctx: Any,
    client: Any,
    agent: Any,
    *,
    instruction_preview_limit: int | None = None,
) -> None:
    """Display full agent details using raw API data to preserve ALL fields."""
    if agent is None:
        handle_rich_output(ctx, markup_text(f"[{ERROR_STYLE}]❌ No agent provided[/]"))
        return

    preview_limit = _clamp_instruction_preview_limit(instruction_preview_limit)
    trimmed_instruction = False

    # Try to fetch and format raw agent data first
    with spinner_context(
        ctx,
        "[bold blue]Loading agent details…[/bold blue]",
        console_override=console,
    ):
        formatted_data = _fetch_and_format_raw_agent_data(client, agent)

    if formatted_data:
        # Use raw API data - this preserves ALL fields including account_id
        panel_title = f"{ICON_AGENT} {formatted_data.get('name', 'Unknown')}"
        payload, trimmed_instruction = _prepare_agent_details_payload(
            formatted_data,
            instruction_preview_limit=preview_limit,
        )
        output_result(
            ctx,
            payload,
            title=panel_title,
        )
    else:
        # Fall back to Pydantic model data if raw fetch fails
        handle_rich_output(
            ctx,
            markup_text(f"[{WARNING_STYLE}]Falling back to Pydantic model data[/]"),
        )

        with spinner_context(
            ctx,
            "[bold blue]Preparing fallback agent details…[/bold blue]",
            console_override=console,
        ):
            result_data = _format_fallback_agent_data(client, agent)

        # Display using output_result
        payload, trimmed_instruction = _prepare_agent_details_payload(
            result_data,
            instruction_preview_limit=preview_limit,
        )
        output_result(
            ctx,
            payload,
            title="Agent Details",
        )

    _show_instruction_trim_hint(
        ctx,
        trimmed=trimmed_instruction,
        preview_limit=preview_limit,
    )


@click.group(name="agents", no_args_is_help=True)
def agents_group() -> None:
    """Agent management operations."""
    pass


def _resolve_agent(
    ctx: Any,
    client: Any,
    ref: str,
    select: int | None = None,
    interface_preference: str = "fuzzy",
) -> Any | None:
    """Resolve an agent by ID or name, supporting fuzzy and questionary interfaces.

    This function provides agent-specific resolution with flexible UI options.
    It wraps resolve_resource_reference with agent-specific configuration, allowing
    users to choose between fuzzy search and traditional questionary selection.

    Args:
        ctx: Click context for CLI command execution.
        client: AIP SDK client instance.
        ref: Agent identifier (UUID or name string).
        select: Pre-selected index for non-interactive resolution (1-based).
        interface_preference: UI preference - "fuzzy" for search or "questionary" for list.

    Returns:
        Agent object when found, None when resolution fails.
    """
    # Configure agent-specific resolution parameters
    resolution_config = {
        "resource_type": "agent",
        "get_by_id": client.agents.get_agent_by_id,
        "find_by_name": client.agents.find_agents,
        "label": "Agent",
    }
    # Use agent-specific resolution with flexible interface preference
    return resolve_resource_reference(
        ctx,
        client,
        ref,
        resolution_config["resource_type"],
        resolution_config["get_by_id"],
        resolution_config["find_by_name"],
        resolution_config["label"],
        select=select,
        interface_preference=interface_preference,
    )


def _get_agent_for_update(client: Any, agent_id: str) -> Any:
    """Resolve an agent reference for update operations."""
    try:
        return client.agents.get_agent_by_id(agent_id)
    except Exception:
        # Fall back to name-based resolution below.
        pass

    try:
        matches = client.agents.find_agents(name=agent_id)
    except Exception as e:
        raise click.ClickException(f"Agent not found: {agent_id} ({e})") from e

    match_list: list[Any]
    if matches is None:
        match_list = []
    elif isinstance(matches, list):
        match_list = matches
    else:
        try:
            match_list = list(matches)
        except TypeError:
            match_list = []

    if not match_list:
        raise click.ClickException(f"Agent not found: {agent_id}")
    if len(match_list) > 1:
        raise click.ClickException(f"Multiple agents named '{agent_id}'. Use ID instead.")
    return match_list[0]


def _running_in_slash_mode(ctx: Any) -> bool:
    """Return True if the command is executing inside the slash session."""
    ctx_obj = getattr(ctx, "obj", None)
    return isinstance(ctx_obj, dict) and bool(ctx_obj.get("_slash_session"))


def _emit_verbose_guidance(ctx: Any) -> None:
    """Explain the modern alternative to the deprecated --verbose flag."""
    if _running_in_slash_mode(ctx):
        message = (
            "[dim]Tip:[/] Verbose streaming has been retired in the command palette. Run the agent normally and open "
            "the post-run viewer (Ctrl+T) to inspect the transcript."
        )
    else:
        message = (
            "[dim]Tip:[/] `--verbose` is no longer supported. Re-run without the flag and toggle the post-run viewer "
            "(Ctrl+T) for detailed output."
        )
    handle_rich_output(ctx, markup_text(message))


def _get_language_model_display_name(agent: Any, model: str | None) -> str:
    """Get display name for the language model."""
    lm_display = getattr(agent, "model", None)
    if not lm_display:
        cfg = getattr(agent, "agent_config", {}) or {}
        lm_display = cfg.get("lm_name") or cfg.get("model") or model or f"{DEFAULT_MODEL} (backend default)"
    return lm_display


def _handle_command_exception(ctx: Any, e: Exception) -> None:
    """Handle exceptions during command execution with consistent error handling."""
    if isinstance(e, click.ClickException):
        if get_ctx_value(ctx, "view") == "json":
            handle_json_output(ctx, error=Exception(AGENT_NOT_FOUND_ERROR))
        raise

    handle_json_output(ctx, error=e)
    if get_ctx_value(ctx, "view") != "json":
        print_api_error(e)
    raise click.exceptions.Exit(1) from e


def _handle_click_exception_for_json(ctx: Any, exc: click.ClickException) -> None:
    """Handle ClickException with JSON output support, then re-raise.

    This helper extracts the common pattern used in agent commands for handling
    ClickExceptions with JSON output support.

    Args:
        ctx: Click context.
        exc: The ClickException to handle.

    Raises:
        click.ClickException: Always re-raises the exception after handling JSON output.
    """
    # Handle JSON output for ClickExceptions if view is JSON
    if get_ctx_value(ctx, "view") == "json":
        handle_json_output(ctx, error=Exception(AGENT_NOT_FOUND_ERROR))
    # Re-raise ClickExceptions without additional processing
    raise exc
