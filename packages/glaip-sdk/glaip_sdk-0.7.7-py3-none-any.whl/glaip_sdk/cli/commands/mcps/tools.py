"""List MCP tools command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from glaip_sdk.branding import ACCENT_STYLE, INFO
from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.output import output_list
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.display import handle_json_output
from glaip_sdk.cli.io import load_resource_from_file_with_validation
from glaip_sdk.cli.mcp_validators import validate_mcp_config_structure
from glaip_sdk.icons import ICON_TOOL

from ._common import _resolve_mcp, console, mcps_group

MAX_DESCRIPTION_LEN = 50


def _get_tools_from_config(ctx: Any, client: Any, config_file: str) -> tuple[list[dict[str, Any]], str]:
    """Get tools from MCP config file.

    Args:
        ctx: Click context
        client: GlaIP client instance
        config_file: Path to config file

    Returns:
        Tuple of (tools list, title string)
    """
    config_data = load_resource_from_file_with_validation(Path(config_file), "MCP config")

    # Validate config structure
    transport = config_data.get("transport")
    if "config" not in config_data:
        raise click.ClickException("Invalid MCP config: missing 'config' section in the file.")
    config_data["config"] = validate_mcp_config_structure(
        config_data["config"],
        transport=transport,
        source=config_file,
    )

    # Get tools from config without saving
    with spinner_context(
        ctx,
        "[bold blue]Fetching tools from config…[/bold blue]",
        console_override=console,
    ):
        tools = client.mcps.get_mcp_tools_from_config(config_data)

    title = f"{ICON_TOOL} Tools from config: {Path(config_file).name}"
    return tools, title


def _get_tools_from_mcp(ctx: Any, client: Any, mcp_ref: str | None) -> tuple[list[dict[str, Any]], str]:
    """Get tools from saved MCP.

    Args:
        ctx: Click context
        client: GlaIP client instance
        mcp_ref: MCP reference (ID or name)

    Returns:
        Tuple of (tools list, title string)
    """
    mcp = _resolve_mcp(ctx, client, mcp_ref)

    with spinner_context(
        ctx,
        "[bold blue]Fetching MCP tools…[/bold blue]",
        console_override=console,
    ):
        tools = client.mcps.get_mcp_tools(mcp.id)

    title = f"{ICON_TOOL} Tools from MCP: {mcp.name}"
    return tools, title


def _output_tool_names(ctx: Any, tools: list[dict[str, Any]]) -> None:
    """Output only tool names.

    Args:
        ctx: Click context
        tools: List of tool dictionaries
    """
    view = get_ctx_value(ctx, "view", "rich")
    tool_names = [tool.get("name", "N/A") for tool in tools]

    if view == "json":
        handle_json_output(ctx, tool_names)
    elif view == "plain":
        if tool_names:
            for name in tool_names:
                console.print(name, markup=False)
            console.print(f"Total: {len(tool_names)} tools", markup=False)
        else:
            console.print("No tools found", markup=False)
    else:
        if tool_names:
            for name in tool_names:
                console.print(name)
            console.print(f"[dim]Total: {len(tool_names)} tools[/dim]")
        else:
            console.print("[yellow]No tools found[/yellow]")


def _transform_tool(tool: dict[str, Any]) -> dict[str, Any]:
    """Transform a tool dictionary to a display row dictionary.

    Args:
        tool: Tool dictionary to transform.

    Returns:
        Dictionary with name and description fields.
    """
    description = tool.get("description", "N/A")
    if len(description) > MAX_DESCRIPTION_LEN:
        description = description[: MAX_DESCRIPTION_LEN - 3] + "..."
    return {
        "name": tool.get("name", "N/A"),
        "description": description,
    }


def _output_tools_table(ctx: Any, tools: list[dict[str, Any]], title: str) -> None:
    """Output tools in table format.

    Args:
        ctx: Click context
        tools: List of tool dictionaries
        title: Table title
    """
    columns = [
        ("name", "Name", ACCENT_STYLE, None),
        ("description", "Description", INFO, 50),
    ]

    output_list(
        ctx,
        tools,
        title,
        columns,
        _transform_tool,
    )


def _validate_tool_command_args(mcp_ref: str | None, config_file: str | None) -> None:
    """Validate that exactly one of mcp_ref or config_file is provided.

    Args:
        mcp_ref: MCP reference (ID or name)
        config_file: Path to config file

    Raises:
        ClickException: If validation fails
    """
    if not mcp_ref and not config_file:
        raise click.ClickException(
            "Either MCP_REF or --from-config must be provided.\n"
            "Examples:\n"
            "  aip mcps tools <MCP_ID>\n"
            "  aip mcps tools --from-config mcp-config.json"
        )
    if mcp_ref and config_file:
        raise click.ClickException(
            "Cannot use both MCP_REF and --from-config at the same time.\n"
            "Use either:\n"
            "  aip mcps tools <MCP_ID>\n"
            "  aip mcps tools --from-config mcp-config.json"
        )


@mcps_group.command("tools")
@click.argument("mcp_ref", required=False)
@click.option(
    "--from-config",
    "--config",
    "config_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Get tools from MCP config file without saving to DB (JSON or YAML)",
)
@click.option(
    "--names-only",
    is_flag=True,
    help="Show only tool names (useful for allowed_tools config)",
)
@output_flags()
@click.pass_context
def list_tools(ctx: Any, mcp_ref: str | None, config_file: str | None, names_only: bool) -> None:
    """List tools available from a specific MCP or config file.

    Args:
        ctx: Click context containing output format preferences
        mcp_ref: MCP reference (ID or name) - required if --from-config not used
        config_file: Path to MCP config file - alternative to mcp_ref
        names_only: Show only tool names instead of full table

    Raises:
        ClickException: If MCP not found or tools fetch fails

    Examples:
        Get tools from saved MCP:
            aip mcps tools <MCP_ID>

        Get tools from config file (without saving to DB):
            aip mcps tools --from-config mcp-config.json

        Get just tool names for allowed_tools config:
            aip mcps tools <MCP_ID> --names-only
    """
    try:
        _validate_tool_command_args(mcp_ref, config_file)
        client = get_client(ctx)

        if config_file:
            tools, title = _get_tools_from_config(ctx, client, config_file)
        else:
            tools, title = _get_tools_from_mcp(ctx, client, mcp_ref)

        if names_only:
            _output_tool_names(ctx, tools)
        else:
            _output_tools_table(ctx, tools, title)

    except Exception as e:
        raise click.ClickException(str(e)) from e
