"""Common helpers and group definition for MCP commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click
from rich.console import Console

from glaip_sdk.cli.context import get_ctx_value
from glaip_sdk.cli.display import display_api_error, handle_json_output
from glaip_sdk.cli.io import load_resource_from_file_with_validation
from glaip_sdk.cli.mcp_validators import validate_mcp_auth_structure, validate_mcp_config_structure
from glaip_sdk.cli.parsers.json_input import parse_json_input
from glaip_sdk.cli.resolution import resolve_resource_reference
from glaip_sdk.cli.rich_helpers import print_markup
from glaip_sdk.cli.commands.shared.formatters import _format_empty_override_warnings, _format_preview_value
from glaip_sdk.utils.import_export import convert_export_to_import_format

console = Console()


@click.group(name="mcps", no_args_is_help=True)
def mcps_group() -> None:
    """MCP management operations.

    Provides commands for creating, listing, updating, deleting, and managing
    Model Context Protocol (MCP) configurations.
    """
    pass


def _resolve_mcp(ctx: Any, client: Any, ref: str, select: int | None = None) -> Any | None:
    """Resolve an MCP server by ID or name, with interactive selection support.

    This function provides MCP-specific resolution logic. It delegates to
    resolve_resource_reference for MCP-specific resolution, supporting UUID
    lookups and name-based fuzzy matching.

    Args:
        ctx: Click context for command execution.
        client: API client for backend operations.
        ref: MCP identifier (UUID or name string).
        select: Optional selection index when multiple MCPs match (1-based).

    Returns:
        MCP instance if resolution succeeds, None if not found.

    Raises:
        click.ClickException: When resolution fails or selection is invalid.
    """
    # Configure MCP-specific resolution functions
    mcp_client = client.mcps
    get_by_id_func = mcp_client.get_mcp_by_id
    find_by_name_func = mcp_client.find_mcps
    # Use MCP-specific resolution with standard fuzzy matching
    return resolve_resource_reference(
        ctx,
        client,
        ref,
        "mcp",
        get_by_id_func,
        find_by_name_func,
        "MCP",
        select=select,
    )


def _strip_server_only_fields(import_data: dict[str, Any]) -> dict[str, Any]:
    """Remove fields that should not be forwarded during import-driven creation.

    Args:
        import_data: Raw import payload loaded from disk.

    Returns:
        A shallow copy of the data with server-managed fields removed.
    """
    cleaned = dict(import_data)
    for key in (
        "id",
        "type",
        "status",
        "connection_status",
        "created_at",
        "updated_at",
    ):
        cleaned.pop(key, None)
    return cleaned


def _load_import_ready_payload(import_file: str) -> dict[str, Any]:
    """Load and normalise an imported MCP definition for create operations.

    Args:
        import_file: Path to an MCP export file (JSON or YAML).

    Returns:
        Normalised import payload ready for CLI/REST usage.

    Raises:
        click.ClickException: If the file cannot be parsed or validated.
    """
    raw_data = load_resource_from_file_with_validation(Path(import_file), "MCP")
    import_data = convert_export_to_import_format(raw_data)
    import_data = _strip_server_only_fields(import_data)

    transport = import_data.get("transport")

    if "config" in import_data:
        import_data["config"] = validate_mcp_config_structure(
            import_data["config"],
            transport=transport,
            source="import file",
        )

    if "authentication" in import_data:
        import_data["authentication"] = validate_mcp_auth_structure(
            import_data["authentication"],
            source="import file",
        )

    return import_data


def _coerce_cli_string(value: str | None) -> str | None:
    """Normalise CLI string values so blanks are treated as missing.

    Args:
        value: User-provided string option.

    Returns:
        The stripped string, or ``None`` when the value is blank/whitespace-only.
    """
    if value is None:
        return None
    trimmed = value.strip()
    # Treat whitespace-only strings as None
    return trimmed if trimmed else None


def _merge_config_field(
    merged_base: dict[str, Any],
    cli_config: str | None,
    final_transport: str | None,
) -> None:
    """Merge config field with validation.

    Args:
        merged_base: Base payload to update in-place.
        cli_config: Raw CLI JSON string for config.
        final_transport: Transport type for validation.

    Raises:
        click.ClickException: If config JSON parsing or validation fails.
    """
    if cli_config is not None:
        parsed_config = parse_json_input(cli_config)
        merged_base["config"] = validate_mcp_config_structure(
            parsed_config,
            transport=final_transport,
            source="--config",
        )
    elif "config" not in merged_base or merged_base["config"] is None:
        merged_base["config"] = {}


def _merge_auth_field(
    merged_base: dict[str, Any],
    cli_auth: str | None,
) -> None:
    """Merge authentication field with validation.

    Args:
        merged_base: Base payload to update in-place.
        cli_auth: Raw CLI JSON string for authentication.

    Raises:
        click.ClickException: If auth JSON parsing or validation fails.
    """
    if cli_auth is not None:
        parsed_auth = parse_json_input(cli_auth)
        merged_base["authentication"] = validate_mcp_auth_structure(
            parsed_auth,
            source="--auth",
        )
    elif "authentication" not in merged_base:
        merged_base["authentication"] = None


def _merge_import_payload(
    import_data: dict[str, Any] | None,
    *,
    cli_name: str | None,
    cli_transport: str | None,
    cli_description: str | None,
    cli_config: str | None,
    cli_auth: str | None,
) -> tuple[dict[str, Any], list[str]]:
    """Merge import data with CLI overrides while tracking missing fields.

    Args:
        import_data: Normalised payload loaded from file (if provided).
        cli_name: Name supplied via CLI option.
        cli_transport: Transport supplied via CLI option.
        cli_description: Description supplied via CLI option.
        cli_config: Raw CLI JSON string for config.
        cli_auth: Raw CLI JSON string for authentication.

    Returns:
        A tuple of (merged_payload, missing_required_fields).

    Raises:
        click.ClickException: If config/auth JSON parsing or validation fails.
    """
    merged_base = import_data.copy() if import_data else {}

    # Merge simple string fields using truthy CLI overrides
    for field, cli_value in (
        ("name", _coerce_cli_string(cli_name)),
        ("transport", _coerce_cli_string(cli_transport)),
        ("description", _coerce_cli_string(cli_description)),
    ):
        if cli_value is not None:
            merged_base[field] = cli_value

    # Determine final transport before validating config
    final_transport = merged_base.get("transport")

    # Merge config and authentication with validation
    _merge_config_field(merged_base, cli_config, final_transport)
    _merge_auth_field(merged_base, cli_auth)

    # Validate required fields
    missing_fields = []
    for required in ("name", "transport"):
        value = merged_base.get(required)
        if not isinstance(value, str) or not value.strip():
            missing_fields.append(required)

    return merged_base, missing_fields


def _validate_import_payload_fields(import_payload: dict[str, Any]) -> bool:
    """Validate that import payload contains updatable fields.

    Args:
        import_payload: Import payload to validate

    Returns:
        True if payload has updatable fields, False otherwise
    """
    updatable_fields = {"name", "transport", "description", "config", "authentication"}
    has_updatable = any(field in import_payload for field in updatable_fields)

    if not has_updatable:
        available_fields = set(import_payload.keys())
        print_markup(
            "[yellow]⚠️  No updatable fields found in import file.[/yellow]\n"
            f"[dim]Found fields: {', '.join(sorted(available_fields))}[/dim]\n"
            f"[dim]Updatable fields: {', '.join(sorted(updatable_fields))}[/dim]"
        )
    return has_updatable


def _get_config_transport(
    transport: str | None,
    import_payload: dict[str, Any] | None,
    mcp: Any,
) -> str | None:
    """Get the transport value for config validation.

    Args:
        transport: CLI transport flag
        import_payload: Optional import payload
        mcp: Current MCP object

    Returns:
        Transport value or None
    """
    if import_payload:
        return transport or import_payload.get("transport")
    return transport or getattr(mcp, "transport", None)


def _collect_cli_overrides(
    name: str | None,
    transport: str | None,
    description: str | None,
    config: str | None,
    auth: str | None,
) -> dict[str, Any]:
    """Collect CLI flags that were explicitly provided.

    Args:
        name: CLI name flag
        transport: CLI transport flag
        description: CLI description flag
        config: CLI config flag
        auth: CLI auth flag

    Returns:
        Dictionary of provided CLI overrides
    """
    cli_overrides = {}
    if name is not None:
        cli_overrides["name"] = name
    if transport is not None:
        cli_overrides["transport"] = transport
    if description is not None:
        cli_overrides["description"] = description
    if config is not None:
        cli_overrides["config"] = config
    if auth is not None:
        cli_overrides["auth"] = auth
    return cli_overrides


def _handle_cli_error(ctx: Any, error: Exception, operation: str) -> None:
    """Render CLI error once and exit with non-zero status."""
    handle_json_output(ctx, error=error)
    if get_ctx_value(ctx, "view") != "json":
        display_api_error(error, operation)
    ctx.exit(1)


def _parse_and_validate_config_auth(
    update_dict: dict[str, Any],
    config: str | None,
    auth: str | None,
    transport: str | None,
    import_payload: dict[str, Any] | None,
    mcp: Any,
) -> None:
    """Parse and validate config and auth CLI options, updating dict in-place.

    Args:
        update_dict: Dictionary to update with parsed config/auth
        config: Config option string
        auth: Auth option string
        transport: Transport option for config validation
        import_payload: Import payload dictionary or None
        mcp: Current MCP object
    """
    if config is not None:
        parsed_config = parse_json_input(config)
        config_transport = _get_config_transport(transport, import_payload, mcp)
        update_dict["config"] = validate_mcp_config_structure(
            parsed_config,
            transport=config_transport,
            source="--config",
        )
    if auth is not None:
        parsed_auth = parse_json_input(auth)
        update_dict["authentication"] = validate_mcp_auth_structure(parsed_auth, source="--auth")


def _generate_update_preview(mcp: Any, update_data: dict[str, Any], cli_overrides: dict[str, Any]) -> str:
    """Generate formatted preview of changes for user confirmation.

    Args:
        mcp: Current MCP object
        update_data: Data that will be sent in update request
        cli_overrides: CLI flags that were explicitly provided

    Returns:
        Formatted preview string showing old→new values
    """
    lines = [f"\n[bold]The following fields will be updated for MCP '{mcp.name}':[/bold]\n"]

    empty_overrides = []

    # Show each field that will be updated
    for field, new_value in update_data.items():
        old_value = getattr(mcp, field, None)

        # Track empty CLI overrides
        if field in cli_overrides and cli_overrides[field] == "":
            empty_overrides.append(field)

        old_display = _format_preview_value(old_value)
        new_display = _format_preview_value(new_value)

        lines.append(f"- [cyan]{field}[/cyan]: {old_display} → {new_display}")

    # Add warnings for empty CLI overrides
    lines.extend(_format_empty_override_warnings(empty_overrides))

    return "\n".join(lines)


def _validate_update_inputs(
    name: str | None,
    transport: str | None,
    description: str | None,
    config: str | None,
    auth: str | None,
    import_file: str | None,
) -> None:
    """Validate that at least one update method is provided.

    Args:
        name: MCP name option
        transport: Transport option
        description: Description option
        config: Config option
        auth: Auth option
        import_file: Import file option

    Raises:
        ClickException: If no update fields are specified
    """
    cli_flags_provided = any(v is not None for v in [name, transport, description, config, auth])
    if not import_file and not cli_flags_provided:
        raise click.ClickException(
            "No update fields specified. Use --import or one of: --name, --transport, --description, --config, --auth"
        )


def _handle_update_preview_and_confirmation(
    import_payload: dict[str, Any] | None,
    y: bool,
    mcp: Any,
    update_data: dict[str, Any],
    name: str | None,
    transport: str | None,
    description: str | None,
    config: str | None,
    auth: str | None,
) -> bool:
    """Handle preview display and user confirmation for import-based updates.

    Args:
        import_payload: Import payload dictionary or None
        y: Skip confirmation flag
        mcp: Current MCP object
        update_data: Data that will be sent in update request
        name: MCP name option
        transport: Transport option
        description: Description option
        config: Config option
        auth: Auth option

    Returns:
        True if update should proceed, False if cancelled
    """
    if import_payload and not y:
        cli_overrides = _collect_cli_overrides(name, transport, description, config, auth)
        preview = _generate_update_preview(mcp, update_data, cli_overrides)
        print_markup(preview)

        if not click.confirm("\nContinue with update?", default=False):
            print_markup("[yellow]Update cancelled.[/yellow]")
            return False
    return True
