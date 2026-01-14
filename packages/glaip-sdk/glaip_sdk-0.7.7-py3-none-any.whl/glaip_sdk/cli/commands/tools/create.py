"""Create tool command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import click

from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.core.context import get_client, handle_best_effort_check
from glaip_sdk.cli.core.rendering import spinner_context
from glaip_sdk.cli.display import (
    display_api_error,
    display_creation_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.io import load_resource_from_file_with_validation as load_resource_from_file
from glaip_sdk.utils.import_export import merge_import_with_cli_args

from ._common import console, tools_group


def _extract_internal_name(code: str) -> str:
    """Extract plugin class name attribute from tool code."""
    m = re.search(r'^\s*name\s*:\s*str\s*=\s*"([^"]+)"', code, re.M)
    if not m:
        m = re.search(r'^\s*name\s*=\s*"([^"]+)"', code, re.M)
    if not m:
        raise click.ClickException(
            "Could not find plugin 'name' attribute in the tool file. "
            'Ensure your plugin class defines e.g. name: str = "my_tool".'
        )
    return m.group(1)


def _validate_name_match(provided: str | None, internal: str) -> str:
    """Validate provided --name against internal name; return effective name."""
    if provided and provided != internal:
        raise click.ClickException(
            f"--name '{provided}' does not match plugin internal name '{internal}'. "
            "Either update the code or pass a matching --name."
        )
    return provided or internal


def _check_duplicate_name(client: Any, tool_name: str) -> None:
    """Raise if a tool with the same name already exists."""

    def _check_duplicate() -> None:
        existing = client.find_tools(name=tool_name)
        if existing:
            raise click.ClickException(
                f"A tool named '{tool_name}' already exists. "
                "Please change your plugin's 'name' to a unique value, then re-run."
            )

    handle_best_effort_check(_check_duplicate)


def _parse_tags(tags: str | None) -> list[str]:
    """Return a cleaned list of tag strings from a comma-separated input."""
    return [t.strip() for t in (tags.split(",") if tags else []) if t.strip()]


def _handle_import_file(
    import_file: str | None,
    name: str | None,
    description: str | None,
    tags: str | None,
) -> dict[str, Any]:
    """Handle import file logic and merge with CLI arguments."""
    if import_file:
        import_data = load_resource_from_file(Path(import_file), "tool")

        # Merge CLI args with imported data
        cli_args = {
            "name": name,
            "description": description,
            "tags": tags,
        }

        return merge_import_with_cli_args(import_data, cli_args)
    else:
        # No import file - use CLI args directly
        return {
            "name": name,
            "description": description,
            "tags": tags,
        }


def _create_tool_from_file(
    client: Any,
    file_path: str,
    name: str | None,
    description: str | None,
    tags: str | None,
) -> Any:
    """Create tool from file upload."""
    with open(file_path, encoding="utf-8") as f:
        code_content = f.read()

    internal_name = _extract_internal_name(code_content)
    tool_name = _validate_name_match(name, internal_name)
    _check_duplicate_name(client, tool_name)

    # Upload the plugin code as-is (no rewrite)
    return client.create_tool_from_code(
        name=tool_name,
        code=code_content,
        framework="langchain",  # Always langchain
        description=description,
        tags=_parse_tags(tags) if tags else None,
    )


def _validate_creation_parameters(
    file: str | None,
    import_file: str | None,
) -> None:
    """Validate required parameters for tool creation."""
    if not file and not import_file:
        raise click.ClickException("A tool file must be provided. Use --file to specify the tool file to upload.")


@tools_group.command()
@click.argument("file_arg", required=False, type=click.Path(exists=True))
@click.option(
    "--file",
    type=click.Path(exists=True),
    help="Tool file to upload",
)
@click.option(
    "--name",
    help="Tool name (extracted from script if file provided)",
)
@click.option(
    "--description",
    help="Tool description (extracted from script if file provided)",
)
@click.option(
    "--tags",
    help="Comma-separated tags for the tool",
)
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Import tool configuration from JSON file",
)
@output_flags()
@click.pass_context
def create(
    ctx: Any,
    file_arg: str | None,
    file: str | None,
    name: str | None,
    description: str | None,
    tags: str | None,
    import_file: str | None,
) -> None:
    r"""Create a new tool.

    \b
    Examples:
        aip tools create tool.py  # Create from file
        aip tools create --import tool.json  # Create from exported configuration
    """
    try:
        client = get_client(ctx)

        # Allow positional file argument for better DX (matches examples)
        if not file and file_arg:
            file = file_arg

        # Handle import file and merge with CLI arguments
        merged_data = _handle_import_file(import_file, name, description, tags)

        # Extract merged values
        name = merged_data.get("name")
        description = merged_data.get("description")
        tags_raw = merged_data.get("tags")
        # Convert tags to string format (for _create_tool_from_file which expects str | None)
        # Import data may have tags as list, CLI provides string
        if isinstance(tags_raw, list):
            tags = ",".join(str(tag).strip() for tag in tags_raw) if tags_raw else None
        else:
            tags = tags_raw  # Already string or None

        # Validate required parameters
        _validate_creation_parameters(file, import_file)

        # Create tool from file (either direct file or import file)
        with spinner_context(
            ctx,
            "[bold blue]Creating tool…[/bold blue]",
            console_override=console,
        ):
            tool = _create_tool_from_file(client, file, name, description, tags)

        # Handle JSON output
        handle_json_output(ctx, tool.model_dump())

        # Handle Rich output
        creation_method = "file upload (custom)"
        rich_panel = display_creation_success(
            "Tool",
            tool.name,
            tool.id,
            Framework=getattr(tool, "framework", "N/A"),
            Type=getattr(tool, "tool_type", "N/A"),
            Description=getattr(tool, "description", "No description"),
            Method=creation_method,
        )
        handle_rich_output(ctx, rich_panel)

    except Exception as e:
        handle_json_output(ctx, error=e)
        if get_ctx_value(ctx, "view") != "json":
            display_api_error(e, "tool creation")
        raise click.ClickException(str(e)) from e
