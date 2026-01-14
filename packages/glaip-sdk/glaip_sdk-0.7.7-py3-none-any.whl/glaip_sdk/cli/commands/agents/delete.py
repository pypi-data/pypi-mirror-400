"""Delete agent command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import (
    display_confirmation_prompt,
    display_deletion_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.core.context import get_client

from ._common import (
    _handle_click_exception_for_json,
    _handle_command_exception,
    agents_group,
)


@agents_group.command()
@click.argument("agent_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation")
@output_flags()
@click.pass_context
def delete(ctx: Any, agent_id: str, yes: bool) -> None:
    """Delete an agent."""
    try:
        client = get_client(ctx)

        # Get agent by ID (no ambiguity handling needed)
        try:
            agent = client.agents.get_agent_by_id(agent_id)
        except Exception as e:
            raise click.ClickException(f"Agent with ID '{agent_id}' not found: {e}") from e

        # Confirm deletion when not forced
        if not yes:
            if not display_confirmation_prompt("Agent", agent.name):
                return

        client.agents.delete_agent(agent.id)

        handle_json_output(
            ctx,
            {
                "success": True,
                "message": f"Agent '{agent.name}' deleted",
            },
        )
        handle_rich_output(ctx, display_deletion_success("Agent", agent.name))

    except click.ClickException as e:
        _handle_click_exception_for_json(ctx, e)
    except Exception as e:
        _handle_command_exception(ctx, e)
