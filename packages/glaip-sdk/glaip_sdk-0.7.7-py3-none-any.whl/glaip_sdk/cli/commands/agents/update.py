"""Update agent command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import (
    display_agent_run_suggestions,
    display_update_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.core.context import get_client

from ._common import (
    _get_agent_for_update,
    _handle_click_exception_for_json,
    _handle_command_exception,
    _prepare_agent_output,
    _resolve_resources_by_name,
    _split_comma_separated_refs,
    agents_group,
)


@agents_group.command()
@click.argument("agent_id")
@click.option("--name", help="New agent name")
@click.option("--instruction", help="New instruction")
@click.option("--tools", multiple=True, help="New tool names or IDs")
@click.option("--agents", multiple=True, help="New sub-agent names")
@click.option("--mcps", multiple=True, help="New MCP names or IDs")
@click.option("--timeout", type=int, help="New timeout value")
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Import agent configuration from JSON file",
)
@output_flags()
@click.pass_context
def update(
    ctx: Any,
    agent_id: str,
    name: str | None,
    instruction: str | None,
    tools: tuple[str, ...] | None,
    agents: tuple[str, ...] | None,
    mcps: tuple[str, ...] | None,
    timeout: float | None,
    import_file: str | None,
) -> None:
    r"""Update an existing agent.

    \b
    Examples:
        aip agents update my-agent --instruction "New instruction"
        aip agents update my-agent --import agent.json
    """
    try:
        client = get_client(ctx)
        tools = _split_comma_separated_refs(tools)
        agents = _split_comma_separated_refs(agents)
        mcps = _split_comma_separated_refs(mcps)

        has_updates = bool(import_file) or any(
            [
                name is not None,
                instruction is not None,
                bool(tools),
                bool(agents),
                bool(mcps),
                timeout is not None,
            ]
        )
        if not has_updates:
            raise click.ClickException("No update fields specified")

        agent = _get_agent_for_update(client, agent_id)

        resolved_tools = _resolve_resources_by_name(client, tools, "tool", client.find_tools, "Tool") if tools else None
        resolved_agents = (
            _resolve_resources_by_name(client, agents, "agent", client.find_agents, "Agent") if agents else None
        )
        resolved_mcps = _resolve_resources_by_name(client, mcps, "mcp", client.find_mcps, "MCP") if mcps else None

        updated_agent = client.agents.update_agent(
            agent.id,
            file=import_file,
            name=name,
            instruction=instruction,
            tools=resolved_tools,
            agents=resolved_agents,
            mcps=resolved_mcps,
            timeout=timeout,
        )

        handle_json_output(ctx, _prepare_agent_output(updated_agent))
        handle_rich_output(ctx, display_update_success("Agent", updated_agent.name))
        handle_rich_output(ctx, display_agent_run_suggestions(updated_agent))

    except click.ClickException as e:
        _handle_click_exception_for_json(ctx, e)
    except Exception as e:
        _handle_command_exception(ctx, e)
