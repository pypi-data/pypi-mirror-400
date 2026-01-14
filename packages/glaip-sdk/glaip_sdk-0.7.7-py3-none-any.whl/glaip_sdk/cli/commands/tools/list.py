"""List tools command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.branding import ACCENT_STYLE, INFO
from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.output import coerce_to_row, output_list
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.icons import ICON_TOOL

from ._common import console, tools_group


@tools_group.command(name="list")
@output_flags()
@click.option(
    "--type",
    "tool_type",
    help="Filter tools by type (e.g., custom, native)",
    type=str,
    required=False,
)
@click.pass_context
def list_tools(ctx: Any, tool_type: str | None) -> None:
    """List all tools."""
    try:
        client = get_client(ctx)
        with spinner_context(
            ctx,
            "[bold blue]Fetching tools…[/bold blue]",
            console_override=console,
        ):
            tools = client.list_tools(tool_type=tool_type)

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", ACCENT_STYLE, None),
            ("framework", "Framework", INFO, None),
        ]

        # Transform function for safe dictionary access
        def transform_tool(tool: Any) -> dict[str, Any]:
            """Transform a tool object to a display row dictionary.

            Args:
                tool: Tool object to transform.

            Returns:
                Dictionary with id, name, and framework fields.
            """
            row = coerce_to_row(tool, ["id", "name", "framework"])
            # Ensure id is always a string
            row["id"] = str(row["id"])
            return row

        output_list(ctx, tools, f"{ICON_TOOL} Available Tools", columns, transform_tool)

    except Exception as e:
        raise click.ClickException(str(e)) from e
