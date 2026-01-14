"""Create agent command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import output_flags
from glaip_sdk.cli.display import (
    display_agent_run_suggestions,
    display_creation_success,
    handle_json_output,
    handle_rich_output,
)
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.config.constants import DEFAULT_AGENT_RUN_TIMEOUT, DEFAULT_MODEL
from glaip_sdk.cli.validators import (
    validate_agent_instruction_cli as validate_agent_instruction,
    validate_agent_name_cli as validate_agent_name,
    validate_timeout_cli as validate_timeout,
)
from glaip_sdk.utils.validation import coerce_timeout

from ._common import (
    _get_language_model_display_name,
    _handle_command_exception,
    _prepare_agent_output,
    _resolve_resources_by_name,
    _split_comma_separated_refs,
    agents_group,
)


def _handle_successful_creation(ctx: Any, agent: Any, model: str | None) -> None:
    """Handle successful agent creation output."""
    handle_json_output(ctx, _prepare_agent_output(agent))

    lm_display = _get_language_model_display_name(agent, model)

    handle_rich_output(
        ctx,
        display_creation_success(
            "Agent",
            agent.name,
            agent.id,
            Model=lm_display,
            Type=getattr(agent, "type", "config"),
            Framework=getattr(agent, "framework", "langchain"),
            Version=getattr(agent, "version", "1.0"),
        ),
    )
    handle_rich_output(ctx, display_agent_run_suggestions(agent))


def _handle_creation_exception(ctx: Any, e: Exception) -> None:
    """Handle exceptions during agent creation."""
    _handle_command_exception(ctx, e)


@agents_group.command()
@click.option("--name", help="Agent name")
@click.option("--instruction", help="Agent instruction (prompt)")
@click.option(
    "--model",
    help=f"Language model to use (e.g., {DEFAULT_MODEL}, default: {DEFAULT_MODEL})",
)
@click.option("--tools", multiple=True, help="Tool names or IDs to attach")
@click.option("--agents", multiple=True, help="Sub-agent names or IDs to attach")
@click.option("--mcps", multiple=True, help="MCP names or IDs to attach")
@click.option(
    "--timeout",
    default=DEFAULT_AGENT_RUN_TIMEOUT,
    type=int,
    help="Agent execution timeout in seconds (default: 300s)",
)
@click.option(
    "--import",
    "import_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Import agent configuration from JSON file",
)
@output_flags()
@click.pass_context
def create(
    ctx: Any,
    name: str,
    instruction: str,
    model: str | None,
    tools: tuple[str, ...] | None,
    agents: tuple[str, ...] | None,
    mcps: tuple[str, ...] | None,
    timeout: float | None,
    import_file: str | None,
) -> None:
    r"""Create a new agent.

    \b
    Examples:
        aip agents create --name "My Agent" --instruction "You are a helpful assistant"
        aip agents create --import agent.json
    """
    try:
        client = get_client(ctx)

        if import_file is None:
            if not name:
                raise click.ClickException("Agent name is required (--name or --import)")
            if not instruction:
                raise click.ClickException("Agent instruction is required (--instruction or --import)")

        if name is not None:
            name = validate_agent_name(name)
        if instruction is not None:
            instruction = validate_agent_instruction(instruction)

        timeout_value = coerce_timeout(timeout)
        if timeout_value is not None:
            timeout_value = validate_timeout(timeout_value)
        if import_file is None and timeout_value == DEFAULT_AGENT_RUN_TIMEOUT:
            timeout_value = None

        tools = _split_comma_separated_refs(tools)
        agents = _split_comma_separated_refs(agents)
        mcps = _split_comma_separated_refs(mcps)

        # Resolve resources
        resolved_tools = _resolve_resources_by_name(client, tools, "tool", client.find_tools, "Tool")
        resolved_agents = _resolve_resources_by_name(client, agents, "agent", client.find_agents, "Agent")
        resolved_mcps = _resolve_resources_by_name(client, mcps, "mcp", client.find_mcps, "MCP")

        agent = client.agents.create_agent(
            file=import_file,
            name=name,
            instruction=instruction,
            model=model,
            tools=resolved_tools or None,
            agents=resolved_agents or None,
            mcps=resolved_mcps or None,
            timeout=timeout_value,
        )

        # Handle successful creation
        _handle_successful_creation(ctx, agent, model)

    except Exception as e:
        _handle_creation_exception(ctx, e)
