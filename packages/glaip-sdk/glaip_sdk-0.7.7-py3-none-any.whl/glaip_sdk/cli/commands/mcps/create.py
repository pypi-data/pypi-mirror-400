"""Create MCP command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import display_creation_success, handle_json_output, handle_rich_output
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.config.constants import DEFAULT_MCP_TYPE

from ._common import (
    _handle_cli_error,
    _load_import_ready_payload,
    _merge_import_payload,
    console,
    mcps_group,
)


@mcps_group.command()
@click.option("--name", help="MCP name")
@click.option("--transport", help="MCP transport protocol")
@click.option("--description", help="MCP description")
@click.option(
    "--config",
    help="JSON configuration string or @file reference (e.g., @config.json)",
)
@click.option(
    "--auth",
    "--authentication",
    "auth",
    help="JSON authentication object or @file reference (e.g., @auth.json)",
)
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Import MCP configuration from JSON or YAML export",
)
@output_flags()
@click.pass_context
def create(
    ctx: Any,
    name: str | None,
    transport: str | None,
    description: str | None,
    config: str | None,
    auth: str | None,
    import_file: str | None,
) -> None:
    r"""Create a new MCP with specified configuration.

    You can create an MCP by providing all parameters via CLI options, or by
    importing from a file and optionally overriding specific fields.

    Args:
        ctx: Click context containing output format preferences
        name: MCP name (required unless provided via --import)
        transport: MCP transport protocol (required unless provided via --import)
        description: Optional MCP description
        config: JSON configuration string or @file reference
        auth: JSON authentication object or @file reference
        import_file: Optional path to import configuration from export file.
            CLI options override imported values.

    Raises:
        ClickException: If JSON parsing fails or API request fails

    \b
    Examples:
        Create from CLI options:
            aip mcps create --name my-mcp --transport http --config '{"url": "https://api.example.com"}'

        Import from file:
            aip mcps create --import mcp-export.json

        Import with overrides:
            aip mcps create --import mcp-export.json --name new-name --transport sse
    """
    try:
        # Get API client instance for MCP operations
        api_client = get_client(ctx)

        # Process import file if specified, otherwise use None
        import_payload = _load_import_ready_payload(import_file) if import_file is not None else None

        merged_payload, missing_fields = _merge_import_payload(
            import_payload,
            cli_name=name,
            cli_transport=transport,
            cli_description=description,
            cli_config=config,
            cli_auth=auth,
        )

        if missing_fields:
            raise click.ClickException(
                "Missing required fields after combining import and CLI values: " + ", ".join(missing_fields)
            )

        effective_name = merged_payload["name"]
        effective_transport = merged_payload["transport"]
        effective_description = merged_payload.get("description")
        effective_config = merged_payload.get("config") or {}
        effective_auth = merged_payload.get("authentication")
        mcp_metadata = merged_payload.get("mcp_metadata")

        with spinner_context(
            ctx,
            "[bold blue]Creating MCP…[/bold blue]",
            console_override=console,
        ):
            # Use SDK client method to create MCP
            create_kwargs: dict[str, Any] = {
                "transport": effective_transport,
            }
            if effective_auth:
                create_kwargs["authentication"] = effective_auth
            if mcp_metadata is not None:
                create_kwargs["mcp_metadata"] = mcp_metadata

            mcp = api_client.mcps.create_mcp(
                name=effective_name,
                description=effective_description,
                config=effective_config,
                **create_kwargs,
            )

        # Handle JSON output
        handle_json_output(ctx, mcp.model_dump())

        # Handle Rich output
        rich_panel = display_creation_success(
            "MCP",
            mcp.name,
            mcp.id,
            Type=getattr(mcp, "type", DEFAULT_MCP_TYPE),
            Transport=getattr(mcp, "transport", effective_transport),
            Description=effective_description or "No description",
        )
        handle_rich_output(ctx, rich_panel)

    except Exception as e:
        _handle_cli_error(ctx, e, "MCP creation")
