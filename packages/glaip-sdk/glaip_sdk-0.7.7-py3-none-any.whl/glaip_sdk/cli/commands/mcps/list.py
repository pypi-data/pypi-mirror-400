"""List MCPs command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.branding import ACCENT_STYLE, INFO
from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.core.output import coerce_to_row, output_list
from glaip_sdk.cli.core.rendering import with_client_and_spinner

from ._common import console, mcps_group


@mcps_group.command(name="list")
@output_flags()
@click.pass_context
def list_mcps(ctx: Any) -> None:
    """List all MCPs in a formatted table.

    Args:
        ctx: Click context containing output format preferences

    Raises:
        ClickException: If API request fails
    """
    try:
        with with_client_and_spinner(
            ctx,
            "[bold blue]Fetching MCPs…[/bold blue]",
            console_override=console,
        ) as client:
            mcps = client.mcps.list_mcps()

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", ACCENT_STYLE, None),
            ("config", "Config", INFO, None),
        ]

        # Transform function for safe dictionary access
        def transform_mcp(mcp: Any) -> dict[str, Any]:
            """Transform an MCP object to a display row dictionary.

            Args:
                mcp: MCP object to transform.

            Returns:
                Dictionary with id, name, and config fields.
            """
            row = coerce_to_row(mcp, ["id", "name", "config"])
            # Ensure id is always a string
            row["id"] = str(row["id"])
            # Truncate config field for display
            if row["config"] != "N/A":
                row["config"] = str(row["config"])[:50] + "..." if len(str(row["config"])) > 50 else str(row["config"])
            return row

        output_list(ctx, mcps, "🔌 Available MCPs", columns, transform_mcp)

    except Exception as e:
        raise click.ClickException(str(e)) from e
