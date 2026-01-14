"""Delete MCP command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import (
    display_confirmation_prompt,
    display_deletion_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context

from ._common import _handle_cli_error, _resolve_mcp, console, mcps_group


@mcps_group.command()
@click.argument("mcp_ref")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx: Any, mcp_ref: str, yes: bool) -> None:
    """Delete an MCP after confirmation.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name)
        yes: Skip confirmation prompt if True

    Raises:
        ClickException: If MCP not found or deletion fails

    Note:
        Requires confirmation unless --yes flag is provided.
        Deletion is permanent and cannot be undone.
    """
    try:
        client = get_client(ctx)

        # Resolve MCP using helper function
        mcp = _resolve_mcp(ctx, client, mcp_ref)

        # Confirm deletion
        if not yes and not display_confirmation_prompt("MCP", mcp.name):
            return

        with spinner_context(
            ctx,
            "[bold blue]Deleting MCP…[/bold blue]",
            console_override=console,
        ):
            client.mcps.delete_mcp(mcp.id)

        handle_json_output(
            ctx,
            {
                "success": True,
                "message": f"MCP '{mcp.name}' deleted",
            },
        )
        handle_rich_output(ctx, display_deletion_success("MCP", mcp.name))

    except Exception as e:
        _handle_cli_error(ctx, e, "MCP deletion")
