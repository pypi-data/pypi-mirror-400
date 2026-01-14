"""Run agent command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import json
from typing import Any

import click

from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.display import handle_json_output
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.core.rendering import build_renderer
from glaip_sdk.cli.transcript import maybe_launch_post_run_viewer, store_transcript_for_session
from glaip_sdk.cli.rich_helpers import print_markup
from glaip_sdk.config.constants import DEFAULT_AGENT_RUN_TIMEOUT
from glaip_sdk.exceptions import AgentTimeoutError
from glaip_sdk.utils.rendering.renderer.toggle import TranscriptToggleController

from ._common import (
    _emit_verbose_guidance,
    _get_agent_model_name,
    _handle_command_exception,
    _resolve_agent,
    _running_in_slash_mode,
    _safe_agent_attribute,
    agents_group,
    console,
)

from glaip_sdk.branding import SUCCESS_STYLE


def _validate_run_input(input_option: str | None, input_text: str | None) -> str:
    """Validate and determine the final input text for agent run."""
    final_input_text = input_option if input_option else input_text

    if not final_input_text:
        raise click.ClickException("Input text is required. Use either positional argument or --input option.")

    return final_input_text


def _parse_chat_history(chat_history: str | None) -> list[dict[str, Any]] | None:
    """Parse chat history JSON if provided."""
    if not chat_history:
        return None

    try:
        return json.loads(chat_history)
    except json.JSONDecodeError as err:
        raise click.ClickException("Invalid JSON in chat history") from err


def _setup_run_renderer(ctx: Any, save: str | None, verbose: bool) -> Any:
    """Set up renderer and working console for agent run."""
    tty_enabled = bool(get_ctx_value(ctx, "tty", True))
    return build_renderer(
        ctx,
        save_path=save,
        verbose=verbose,
        _tty_enabled=tty_enabled,
    )


def _maybe_attach_transcript_toggle(ctx: Any, renderer: Any) -> None:
    """Attach transcript toggle controller when interactive TTY is available."""
    if renderer is None:
        return

    console_obj = getattr(renderer, "console", None)
    if console_obj is None or not getattr(console_obj, "is_terminal", False):
        return

    tty_enabled = bool(get_ctx_value(ctx, "tty", True))
    if not tty_enabled:
        return

    controller = TranscriptToggleController(enabled=True)
    renderer.transcript_controller = controller


def _prepare_run_kwargs(
    agent: Any,
    final_input_text: str,
    files: list[str] | None,
    parsed_chat_history: list[dict[str, Any]] | None,
    renderer: Any,
    tty_enabled: bool,
) -> dict[str, Any]:
    """Prepare kwargs for agent run."""
    run_kwargs = {
        "agent_id": agent.id,
        "message": final_input_text,
        "files": list(files),
        "agent_name": agent.name,
        "tty": tty_enabled,
    }

    if parsed_chat_history:
        run_kwargs["chat_history"] = parsed_chat_history

    if renderer is not None:
        run_kwargs["renderer"] = renderer

    return run_kwargs


def _handle_run_output(ctx: Any, result: Any, renderer: Any) -> None:
    """Handle output formatting for agent run results."""
    printed_by_renderer = bool(renderer)
    selected_view = get_ctx_value(ctx, "view", "rich")

    if not printed_by_renderer:
        if selected_view == "json":
            handle_json_output(ctx, {"output": result})
        elif selected_view == "md":
            click.echo(f"# Assistant\n\n{result}")
        elif selected_view == "plain":
            click.echo(result)


def _save_run_transcript(save: str | None, result: Any, working_console: Any) -> None:
    """Save transcript to file if requested."""
    if not save:
        return

    ext = (save.rsplit(".", 1)[-1] or "").lower()
    if ext == "json":
        save_data = {
            "output": result or "",
            "full_debug_output": getattr(working_console, "get_captured_output", lambda: "")(),
            "timestamp": "captured during agent execution",
        }
        content = json.dumps(save_data, indent=2)
    else:
        full_output = getattr(working_console, "get_captured_output", lambda: "")()
        if full_output:
            content = f"# Agent Debug Log\n\n{full_output}\n\n---\n\n## Final Result\n\n{result or ''}\n"
        else:
            content = f"# Assistant\n\n{result or ''}\n"

    with open(save, "w", encoding="utf-8") as f:
        f.write(content)
    print_markup(f"[{SUCCESS_STYLE}]Full debug output saved to: {save}[/]", console=console)


@agents_group.command()
@click.argument("agent_ref")
@click.argument("input_text", required=False)
@click.option("--select", type=int, help="Choose among ambiguous matches (1-based)")
@click.option("--input", "input_option", help="Input text for the agent")
@click.option("--chat-history", help="JSON string of chat history")
@click.option(
    "--timeout",
    default=DEFAULT_AGENT_RUN_TIMEOUT,
    type=int,
    help="Agent execution timeout in seconds (default: 300s)",
)
@click.option(
    "--save",
    type=click.Path(dir_okay=False, writable=True),
    help="Save transcript to file (md or json)",
)
@click.option(
    "--file",
    "files",
    multiple=True,
    type=click.Path(exists=True),
    help="Attach file(s)",
)
@click.option(
    "--verbose/--no-verbose",
    default=False,
    help="Show detailed SSE events during streaming",
)
@output_flags()
@click.pass_context
def run(
    ctx: Any,
    agent_ref: str,
    select: int | None,
    input_text: str | None,
    input_option: str | None,
    chat_history: str | None,
    timeout: float | None,
    save: str | None,
    files: tuple[str, ...] | None,
    verbose: bool,
) -> None:
    r"""Run an agent with input text.

    Usage: aip agents run <agent_ref> <input_text> [OPTIONS]

    \b
    Examples:
        aip agents run my-agent "Hello world"
        aip agents run agent-123 "Process this data" --timeout 600
        aip agents run my-agent --input "Hello world"  # Legacy style
    """
    final_input_text = _validate_run_input(input_option, input_text)

    if verbose:
        _emit_verbose_guidance(ctx)
        return

    try:
        client = get_client(ctx)
        agent = _resolve_agent(ctx, client, agent_ref, select, interface_preference="fuzzy")

        parsed_chat_history = _parse_chat_history(chat_history)
        renderer, working_console = _setup_run_renderer(ctx, save, verbose)
        _maybe_attach_transcript_toggle(ctx, renderer)

        try:
            client.timeout = float(timeout)
        except Exception:  # pragma: no cover  # Defensive - timeout is int per Click, so float() always succeeds
            pass

        run_kwargs = _prepare_run_kwargs(
            agent,
            final_input_text,
            files,
            parsed_chat_history,
            renderer,
            bool(get_ctx_value(ctx, "tty", True)),
        )

        result = client.agents.run_agent(**run_kwargs, timeout=timeout)

        slash_mode = _running_in_slash_mode(ctx)
        agent_id = str(_safe_agent_attribute(agent, "id") or "") or None
        agent_name = _safe_agent_attribute(agent, "name")
        model_hint = _get_agent_model_name(agent)

        transcript_context = store_transcript_for_session(
            ctx,
            renderer,
            final_result=result,
            agent_id=agent_id,
            agent_name=agent_name,
            model=model_hint,
            source="slash" if slash_mode else "cli",
        )

        _handle_run_output(ctx, result, renderer)
        _save_run_transcript(save, result, working_console)
        maybe_launch_post_run_viewer(
            ctx,
            transcript_context,
            console=console,
            slash_mode=slash_mode,
        )

    except AgentTimeoutError as e:
        error_msg = str(e)
        handle_json_output(ctx, error=Exception(error_msg))
        raise click.ClickException(error_msg) from e
    except Exception as e:
        _handle_command_exception(ctx, e)
