"""Update tool command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.branding import SUCCESS_STYLE, WARNING_STYLE
from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.display import display_api_error, display_update_success, handle_json_output, handle_rich_output
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.rich_helpers import markup_text

from ._common import _get_tool_by_id_with_spinner, console, tools_group
from .create import _parse_tags


@tools_group.command()
@click.argument("tool_id")
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="New tool file for code update (custom tools only)",
)
@click.option("--description", help="New description")
@click.option("--tags", help="Comma-separated tags")
@output_flags()
@click.pass_context
def update(
    ctx: Any,
    tool_id: str,
    file: str | None,
    description: str | None,
    tags: str | None,
) -> None:
    """Update a tool (code or metadata)."""
    try:
        client = get_client(ctx)

        # Get tool by ID (no ambiguity handling needed)
        tool = _get_tool_by_id_with_spinner(ctx, tool_id)

        update_kwargs: dict[str, Any] = {}
        if description is not None:
            update_kwargs["description"] = description
        if tags:
            update_kwargs["tags"] = _parse_tags(tags)

        if file:
            # Update code via file upload (custom tools only)
            if tool.tool_type != "custom":
                raise click.ClickException(
                    "File updates are only supported for custom tools. "
                    f"Tool '{tool.name}' is of type '{tool.tool_type}'."
                )
            with spinner_context(
                ctx,
                "[bold blue]Uploading new tool code…[/bold blue]",
                console_override=console,
            ):
                updated_tool = client.tools.update_tool_via_file(
                    tool.id,
                    file,
                    framework=tool.framework,
                    **update_kwargs,
                )
            handle_rich_output(
                ctx,
                markup_text(f"[{SUCCESS_STYLE}]✓[/] Tool code updated from {file}"),
            )
        elif update_kwargs:
            # Update metadata only (native tools only)
            if tool.tool_type != "native":
                raise click.ClickException(
                    "Metadata updates are only supported for native tools. "
                    f"Tool '{tool.name}' is of type '{tool.tool_type}'."
                )
            with spinner_context(
                ctx,
                "[bold blue]Updating tool metadata…[/bold blue]",
                console_override=console,
            ):
                updated_tool = client.tools.update_tool(tool, **update_kwargs)
            handle_rich_output(ctx, markup_text(f"[{SUCCESS_STYLE}]✓[/] Tool metadata updated"))
        else:
            handle_rich_output(ctx, markup_text(f"[{WARNING_STYLE}]No updates specified[/]"))
            return

        handle_json_output(ctx, updated_tool.model_dump())
        handle_rich_output(ctx, display_update_success("Tool", updated_tool.name))

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            display_api_error(e, "tool update")
        raise click.ClickException(str(e)) from e
