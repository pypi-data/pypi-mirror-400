"""Delete tool command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.display import (
    display_api_error,
    display_confirmation_prompt,
    display_deletion_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.core.rendering import spinner_context

from ._common import _get_tool_by_id_with_spinner, console, tools_group


@tools_group.command()
@click.argument("tool_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx: Any, tool_id: str, yes: bool) -> None:
    """Delete a tool."""
    try:
        # Get tool by ID (no ambiguity handling needed)
        tool = _get_tool_by_id_with_spinner(ctx, tool_id)

        # Confirm deletion via centralized display helper
        if not yes and not display_confirmation_prompt("Tool", tool.name):
            return

        with spinner_context(
            ctx,
            "[bold blue]Deleting tool…[/bold blue]",
            console_override=console,
        ):
            tool.delete()

        handle_json_output(
            ctx,
            {
                "success": True,
                "message": f"Tool '{tool.name}' deleted",
            },
        )
        handle_rich_output(ctx, display_deletion_success("Tool", tool.name))

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            display_api_error(e, "tool deletion")
        raise click.ClickException(str(e)) from e
