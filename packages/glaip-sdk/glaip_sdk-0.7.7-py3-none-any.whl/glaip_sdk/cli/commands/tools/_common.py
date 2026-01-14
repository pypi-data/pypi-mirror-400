"""Common helpers and group definition for tool commands.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click
from rich.console import Console

from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.resolution import resolve_resource_reference

console = Console()


@click.group(name="tools", no_args_is_help=True)
def tools_group() -> None:
    """Tool management operations."""
    pass


def _resolve_tool(ctx: Any, client: Any, ref: str, select: int | None = None) -> Any | None:
    """Resolve a tool by ID or name, handling ambiguous matches interactively.

    This function provides tool-specific resolution logic. It uses
    resolve_resource_reference to find tools by UUID or name, with interactive
    selection when multiple matches are found.

    Args:
        ctx: Click context for CLI operations.
        client: API client instance.
        ref: Tool reference (UUID string or name).
        select: Pre-selected index for non-interactive mode (1-based).

    Returns:
        Tool object if found, None otherwise.
    """
    # Configure tool-specific resolution with standard fuzzy matching
    get_by_id = client.get_tool
    find_by_name = client.find_tools
    return resolve_resource_reference(
        ctx,
        client,
        ref,
        "tool",
        get_by_id,
        find_by_name,
        "Tool",
        select=select,
    )


def _get_tool_by_id_with_spinner(ctx: Any, tool_id: str) -> Any:
    """Get tool by ID with spinner context and error handling.

    Args:
        ctx: Click context.
        tool_id: Tool ID to fetch.

    Returns:
        Tool object.

    Raises:
        click.ClickException: If tool not found.
    """
    client = get_client(ctx)
    try:
        with spinner_context(
            ctx,
            "[bold blue]Fetching tool…[/bold blue]",
            console_override=console,
        ):
            return client.get_tool_by_id(tool_id)
    except Exception as e:
        raise click.ClickException(f"Tool with ID '{tool_id}' not found: {e}") from e
