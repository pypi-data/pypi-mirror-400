"""Get tool command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from glaip_sdk.branding import WARNING_STYLE
from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.output import format_datetime_fields, handle_resource_export, output_result
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.io import fetch_raw_resource_details
from glaip_sdk.icons import ICON_TOOL

from ._common import _resolve_tool, console, tools_group


@tools_group.command()
@click.argument("tool_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@click.option(
    "--export",
    type=click.Path(dir_okay=False, writable=True),
    help="Export complete tool configuration to file (format auto-detected from .json/.yaml extension)",
)
@output_flags()
@click.pass_context
def get(ctx: Any, tool_ref: str, select: int | None, export: str | None) -> None:
    r"""Get tool details.

    \b
    Examples:
        aip tools get my-tool
        aip tools get my-tool --export tool.json    # Exports complete configuration as JSON
        aip tools get my-tool --export tool.yaml    # Exports complete configuration as YAML
    """
    try:
        client = get_client(ctx)

        # Resolve tool with ambiguity handling
        tool = _resolve_tool(ctx, client, tool_ref, select)

        # Handle export option
        if export:
            handle_resource_export(
                ctx,
                tool,
                Path(export),
                resource_type="tool",
                get_by_id_func=client.get_tool_by_id,
                console_override=console,
            )

        # Try to fetch raw API data first to preserve ALL fields
        with spinner_context(
            ctx,
            "[bold blue]Fetching detailed tool data…[/bold blue]",
            console_override=console,
        ):
            raw_tool_data = fetch_raw_resource_details(client, tool, "tools")

        if raw_tool_data:
            # Use raw API data - this preserves ALL fields
            # Format dates for better display (minimal postprocessing)
            formatted_data = format_datetime_fields(raw_tool_data)

            # Display using output_result with raw data
            output_result(
                ctx,
                formatted_data,
                title="Tool Details",
                panel_title=f"{ICON_TOOL} {raw_tool_data.get('name', 'Unknown')}",
            )
        else:
            # Fall back to original method if raw fetch fails
            console.print(f"[{WARNING_STYLE}]Falling back to Pydantic model data[/]")

            # Create result data with all available fields from backend
            result_data = {
                "id": str(getattr(tool, "id", "N/A")),
                "name": getattr(tool, "name", "N/A"),
                "tool_type": getattr(tool, "tool_type", "N/A"),
                "framework": getattr(tool, "framework", "N/A"),
                "version": getattr(tool, "version", "N/A"),
                "description": getattr(tool, "description", "N/A"),
            }

            output_result(
                ctx,
                result_data,
                title="Tool Details",
                panel_title=f"{ICON_TOOL} {tool.name}",
            )

    except Exception as e:
        raise click.ClickException(str(e)) from e
