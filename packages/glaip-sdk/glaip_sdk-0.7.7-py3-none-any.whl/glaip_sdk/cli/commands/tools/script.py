"""Get tool script command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import json
from typing import Any

import click

from glaip_sdk.branding import ERROR_STYLE, SUCCESS_STYLE
from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.display import handle_json_output
from glaip_sdk.cli.rich_helpers import print_markup

from ._common import console, tools_group


@tools_group.command("script")
@click.argument("tool_id")
@output_flags()
@click.pass_context
def script(ctx: Any, tool_id: str) -> None:
    """Get tool script content."""
    try:
        client = get_client(ctx)
        with spinner_context(
            ctx,
            "[bold blue]Fetching tool script…[/bold blue]",
            console_override=console,
        ):
            script_content = client.get_tool_script(tool_id)

        if get_ctx_value(ctx, "view") == "json":
            click.echo(json.dumps({"script": script_content}, indent=2))
        else:
            console.print(f"[{SUCCESS_STYLE}]📜 Tool Script for '{tool_id}':[/]")
            console.print(script_content)

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            print_markup(f"[{ERROR_STYLE}]Error getting tool script: {e}[/]", console=console)
        raise click.ClickException(str(e)) from e
