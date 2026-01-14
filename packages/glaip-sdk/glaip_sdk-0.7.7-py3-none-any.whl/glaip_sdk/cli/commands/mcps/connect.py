"""Connect to MCP command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import json
from typing import Any

import click

from glaip_sdk.branding import SUCCESS, SUCCESS_STYLE, WARNING_STYLE
from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.display import handle_json_output
from glaip_sdk.cli.rich_helpers import print_markup
from glaip_sdk.rich_components import AIPPanel

from ._common import console, mcps_group


@mcps_group.command("connect")
@click.option(
    "--from-file",
    "config_file",
    required=True,
    help="MCP config JSON file",
)
@output_flags()
@click.pass_context
def connect(ctx: Any, config_file: str) -> None:
    """Test MCP connection using a configuration file.

    Args:
        ctx: Click context containing output format preferences
        config_file: Path to MCP configuration JSON file

    Raises:
        ClickException: If config file invalid or connection test fails

    Note:
        Loads MCP configuration from JSON file and tests connectivity.
        Displays success or failure with connection details.
    """
    try:
        client = get_client(ctx)

        # Load MCP config from file
        with open(config_file) as f:
            config = json.load(f)

        view = get_ctx_value(ctx, "view", "rich")
        if view != "json":
            print_markup(
                f"[{WARNING_STYLE}]Connecting to MCP with config from {config_file}...[/]",
                console=console,
            )

        # Test connection using config
        with spinner_context(
            ctx,
            "[bold blue]Connecting to MCP…[/bold blue]",
            console_override=console,
        ):
            result = client.mcps.test_mcp_connection_from_config(config)

        view = get_ctx_value(ctx, "view", "rich")
        if view == "json":
            handle_json_output(ctx, result)
        else:
            success_panel = AIPPanel(
                f"[{SUCCESS_STYLE}]✓[/] MCP connection successful!\n\n[bold]Result:[/bold] {result}",
                title="🔌 Connection",
                border_style=SUCCESS,
            )
            console.print(success_panel)

    except Exception as e:
        raise click.ClickException(str(e)) from e
