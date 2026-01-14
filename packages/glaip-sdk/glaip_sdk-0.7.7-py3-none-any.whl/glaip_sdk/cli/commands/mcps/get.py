"""Get MCP command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from glaip_sdk.branding import SUCCESS_STYLE, WARNING_STYLE
from glaip_sdk.cli.context import detect_export_format, output_flags
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.output import fetch_resource_for_export, format_datetime_fields, output_result
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.io import fetch_raw_resource_details
from glaip_sdk.cli.rich_helpers import print_markup
from glaip_sdk.utils.serialization import build_mcp_export_payload, write_resource_export
import sys

from ._common import _resolve_mcp, console, mcps_group


def _handle_mcp_export(
    ctx: Any,
    client: Any,
    mcp: Any,
    export_path: Path,
    no_auth_prompt: bool,
    auth_placeholder: str,
) -> None:
    """Handle MCP export to file with format detection and auth handling.

    Args:
        ctx: Click context for spinner management
        client: API client for fetching MCP details
        mcp: MCP object to export
        export_path: Target file path (format detected from extension)
        no_auth_prompt: Skip interactive secret prompts if True
        auth_placeholder: Placeholder text for missing secrets

    Note:
        Supports JSON (.json) and YAML (.yaml/.yml) export formats.
        In interactive mode, prompts for secret values.
        In non-interactive mode, uses placeholder values.
    """
    # Auto-detect format from file extension
    detected_format = detect_export_format(export_path)

    # Always export comprehensive data - re-fetch with full details
    mcp = fetch_resource_for_export(
        ctx,
        mcp,
        resource_type="MCP",
        get_by_id_func=client.mcps.get_mcp_by_id,
        console_override=console,
    )

    # Determine if we should prompt for secrets
    prompt_for_secrets = not no_auth_prompt and sys.stdin.isatty()

    # Warn user if non-interactive mode forces placeholder usage
    if not no_auth_prompt and not sys.stdin.isatty():
        print_markup(
            f"[{WARNING_STYLE}]⚠️  Non-interactive mode detected. Using placeholder values for secrets.[/]",
            console=console,
        )

    # Build and write export payload
    if prompt_for_secrets:
        # Interactive mode: no spinner during prompts
        export_payload = build_mcp_export_payload(
            mcp,
            prompt_for_secrets=prompt_for_secrets,
            placeholder=auth_placeholder,
            console=console,
        )
        with spinner_context(
            ctx,
            "[bold blue]Writing export file…[/bold blue]",
            console_override=console,
        ):
            write_resource_export(export_path, export_payload, detected_format)
    else:
        # Non-interactive mode: spinner for entire export process
        with spinner_context(
            ctx,
            "[bold blue]Exporting MCP configuration…[/bold blue]",
            console_override=console,
        ):
            export_payload = build_mcp_export_payload(
                mcp,
                prompt_for_secrets=prompt_for_secrets,
                placeholder=auth_placeholder,
                console=console,
            )
            write_resource_export(export_path, export_payload, detected_format)

    print_markup(
        f"[{SUCCESS_STYLE}]✅ Complete MCP configuration exported to: {export_path} (format: {detected_format})[/]",
        console=console,
    )


def _display_mcp_details(ctx: Any, client: Any, mcp: Any) -> None:
    """Display MCP details using raw API data or fallback to Pydantic model.

    Args:
        ctx: Click context containing output format preferences
        client: API client for fetching raw MCP data
        mcp: MCP object to display details for

    Note:
        Attempts to fetch raw API data first to preserve all fields.
        Falls back to Pydantic model data if raw data unavailable.
        Formats datetime fields for better readability.
    """
    # Try to fetch raw API data first to preserve ALL fields
    with spinner_context(
        ctx,
        "[bold blue]Fetching detailed MCP data…[/bold blue]",
        console_override=console,
    ):
        raw_mcp_data = fetch_raw_resource_details(client, mcp, "mcps")

    if raw_mcp_data:
        # Use raw API data - this preserves ALL fields
        formatted_data = format_datetime_fields(raw_mcp_data)

        output_result(
            ctx,
            formatted_data,
            title="MCP Details",
            panel_title=f"🔌 {raw_mcp_data.get('name', 'Unknown')}",
        )
    else:
        # Fall back to Pydantic model data
        console.print(f"[{WARNING_STYLE}]Falling back to Pydantic model data[/]")
        result_data = {
            "id": str(getattr(mcp, "id", "N/A")),
            "name": getattr(mcp, "name", "N/A"),
            "type": getattr(mcp, "type", "N/A"),
            "config": getattr(mcp, "config", "N/A"),
            "status": getattr(mcp, "status", "N/A"),
            "connection_status": getattr(mcp, "connection_status", "N/A"),
        }
        output_result(ctx, result_data, title=f"🔌 {mcp.name}")


@mcps_group.command()
@click.argument("mcp_ref")
@click.option(
    "--export",
    type=click.Path(dir_okay=False, writable=True),
    help="Export complete MCP configuration to file (format auto-detected from .json/.yaml extension)",
)
@click.option(
    "--no-auth-prompt",
    is_flag=True,
    help="Skip interactive secret prompts and use placeholder values.",
)
@click.option(
    "--auth-placeholder",
    default="<INSERT VALUE>",
    show_default=True,
    help="Placeholder text used when secrets are unavailable.",
)
@output_flags()
@click.pass_context
def get(
    ctx: Any,
    mcp_ref: str,
    export: str | None,
    no_auth_prompt: bool,
    auth_placeholder: str,
) -> None:
    r"""Get MCP details and optionally export configuration to file.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)
        export: Optional file path to export MCP configuration
        no_auth_prompt: Skip interactive secret prompts if True
        auth_placeholder: Placeholder text for missing secrets

    Raises:
        ClickException: If MCP not found or export fails

    \b
    Examples:
        aip mcps get my-mcp
        aip mcps get my-mcp --export mcp.json    # Export as JSON
        aip mcps get my-mcp --export mcp.yaml    # Export as YAML
    """
    try:
        client = get_client(ctx)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Handle export option
        if export:
            _handle_mcp_export(ctx, client, mcp, Path(export), no_auth_prompt, auth_placeholder)

        # Display MCP details
        _display_mcp_details(ctx, client, mcp)

    except Exception as e:
        raise click.ClickException(str(e)) from e
