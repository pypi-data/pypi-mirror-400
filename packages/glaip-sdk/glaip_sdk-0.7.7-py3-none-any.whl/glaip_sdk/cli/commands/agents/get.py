"""Get agent command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import display_agent_run_suggestions, handle_rich_output
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.output import handle_resource_export

from ._common import _display_agent_details, _resolve_agent, agents_group, console


@agents_group.command()
@click.argument("agent_ref")
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@click.option(
    "--export",
    type=click.Path(dir_okay=False, writable=True),
    help="Export complete agent configuration to file (format auto-detected from .json/.yaml extension)",
)
@click.option(
    "--instruction-preview",
    type=int,
    default=0,
    show_default=True,
    help="Instruction preview length when printing instructions (0 shows full prompt).",
)
@output_flags()
@click.pass_context
def get(
    ctx: Any,
    agent_ref: str,
    select: int | None,
    export: str | None,
    instruction_preview: int,
) -> None:
    r"""Get agent details.

    \b
    Examples:
        aip agents get my-agent
        aip agents get my-agent --export agent.json    # Exports complete configuration as JSON
        aip agents get my-agent --export agent.yaml    # Exports complete configuration as YAML
    """
    try:
        # Initialize API client for agent retrieval
        api_client = get_client(ctx)

        # Resolve agent reference using questionary interface for better UX
        agent = _resolve_agent(ctx, api_client, agent_ref, select, interface_preference="questionary")

        if not agent:
            raise click.ClickException(f"Agent '{agent_ref}' not found")

        # Handle export option if requested
        if export:
            handle_resource_export(
                ctx,
                agent,
                Path(export),
                resource_type="agent",
                get_by_id_func=api_client.agents.get_agent_by_id,
                console_override=console,
            )

        # Display full agent details using the standardized helper
        _display_agent_details(
            ctx,
            api_client,
            agent,
            instruction_preview_limit=instruction_preview,
        )

        # Show run suggestions via centralized display helper
        handle_rich_output(ctx, display_agent_run_suggestions(agent))

    except click.ClickException:
        raise
    except Exception as e:
        raise click.ClickException(str(e)) from e
