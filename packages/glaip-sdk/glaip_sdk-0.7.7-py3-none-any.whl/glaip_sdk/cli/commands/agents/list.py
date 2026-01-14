"""List agents command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import os
from typing import Any

import click

from glaip_sdk.branding import ACCENT_STYLE, INFO, SUCCESS, WARNING_STYLE
from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import display_agent_run_suggestions, handle_rich_output
from glaip_sdk.cli.core.output import coerce_to_row, output_list
from glaip_sdk.cli.core.prompting import _fuzzy_pick_for_resources
from glaip_sdk.cli.core.rendering import with_client_and_spinner
from glaip_sdk.icons import ICON_AGENT

from ._common import _display_agent_details, agents_group, console


@agents_group.command(name="list")
@click.option("--simple", is_flag=True, help="Show simple table without interactive picker")
@click.option("--type", "agent_type", help="Filter by agent type (config, code, a2a, langflow)")
@click.option("--framework", help="Filter by framework (langchain, langgraph, google_adk)")
@click.option("--name", help="Filter by partial name match (case-insensitive)")
@click.option("--version", help="Filter by exact version match")
@click.option(
    "--sync-langflow",
    is_flag=True,
    help="Sync with LangFlow server before listing (only applies when filtering by langflow type)",
)
@output_flags()
@click.pass_context
def list_agents(
    ctx: Any,
    simple: bool,
    agent_type: str | None,
    framework: str | None,
    name: str | None,
    version: str | None,
    sync_langflow: bool,
) -> None:
    """List agents with optional filtering."""
    try:
        with with_client_and_spinner(
            ctx,
            "[bold blue]Fetching agents…[/bold blue]",
            console_override=console,
        ) as client:
            # Query agents with specified filters
            filter_params = {
                "agent_type": agent_type,
                "framework": framework,
                "name": name,
                "version": version,
                "sync_langflow_agents": sync_langflow,
            }
            agents = client.agents.list_agents(**filter_params)

        # Define table columns: (data_key, header, style, width)
        columns = [
            ("id", "ID", "dim", 36),
            ("name", "Name", ACCENT_STYLE, None),
            ("type", "Type", WARNING_STYLE, None),
            ("framework", "Framework", INFO, None),
            ("version", "Version", SUCCESS, None),
        ]

        # Transform function for safe attribute access
        def transform_agent(agent: Any) -> dict[str, Any]:
            """Transform an agent object to a display row dictionary.

            Args:
                agent: Agent object to transform.

            Returns:
                Dictionary with id, name, type, framework, and version fields.
            """
            row = coerce_to_row(agent, ["id", "name", "type", "framework", "version"])
            # Ensure id is always a string
            row["id"] = str(row["id"])
            return row

        # Use fuzzy picker for interactive agent selection and details (default behavior)
        # Skip if --simple flag is used, a name filter is applied, or non-rich output is requested
        ctx_obj = ctx.obj if isinstance(getattr(ctx, "obj", None), dict) else {}
        current_view = ctx_obj.get("view")
        interactive_enabled = (
            not simple
            and name is None
            and current_view not in {"json", "plain", "md"}
            and console.is_terminal
            and os.isatty(1)
            and len(agents) > 0
        )

        # Track picker attempt so the fallback table doesn't re-open the palette
        picker_attempted = False
        if interactive_enabled:
            picker_attempted = True
            picked_agent = _fuzzy_pick_for_resources(agents, "agent", "")
            if picked_agent:
                _display_agent_details(ctx, client, picked_agent)
                # Show run suggestions via centralized display helper
                handle_rich_output(ctx, display_agent_run_suggestions(picked_agent))
                return

        # Show simple table (either --simple flag or non-interactive)
        output_list(
            ctx,
            agents,
            f"{ICON_AGENT} Available Agents",
            columns,
            transform_agent,
            skip_picker=(
                not interactive_enabled
                or picker_attempted
                or simple
                or any(param is not None for param in (agent_type, framework, name, version))
            ),
            use_pager=False,
        )

    except Exception as e:
        raise click.ClickException(str(e)) from e
