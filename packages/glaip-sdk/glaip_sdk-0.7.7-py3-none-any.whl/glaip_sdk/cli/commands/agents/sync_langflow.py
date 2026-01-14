"""Sync LangFlow agents command.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from typing import Any

import click

from glaip_sdk.cli.context import get_ctx_value, output_flags
from glaip_sdk.cli.display import handle_json_output, handle_rich_output
from glaip_sdk.cli.core.context import get_client
from glaip_sdk.cli.rich_helpers import markup_text

from ._common import _handle_command_exception, agents_group

from glaip_sdk.branding import SUCCESS_STYLE


@agents_group.command()
@click.option(
    "--base-url",
    help="Custom LangFlow server base URL (overrides LANGFLOW_BASE_URL env var)",
)
@click.option("--api-key", help="Custom LangFlow API key (overrides LANGFLOW_API_KEY env var)")
@output_flags()
@click.pass_context
def sync_langflow(ctx: Any, base_url: str | None, api_key: str | None) -> None:
    r"""Sync agents with LangFlow server flows.

    This command fetches all flows from the configured LangFlow server and
    creates/updates corresponding agents in the platform.

    The LangFlow server configuration can be provided via:
    - Command options (--base-url, --api-key)
    - Environment variables (LANGFLOW_BASE_URL, LANGFLOW_API_KEY)

    \b
    Examples:
        aip agents sync-langflow
        aip agents sync-langflow --base-url https://my-langflow.com --api-key my-key
    """
    try:
        client = get_client(ctx)

        # Perform the sync
        result = client.sync_langflow_agents(base_url=base_url, api_key=api_key)

        # Handle output format
        handle_json_output(ctx, result)

        # Show success message for non-JSON output
        if get_ctx_value(ctx, "view") != "json":
            # Extract some useful info from the result
            success_count = result.get("data", {}).get("created_count", 0) + result.get("data", {}).get(
                "updated_count", 0
            )
            total_count = result.get("data", {}).get("total_processed", 0)

            handle_rich_output(
                ctx,
                markup_text(
                    f"[{SUCCESS_STYLE}]✅ Successfully synced {success_count} LangFlow agents "
                    f"({total_count} total processed)[/]"
                ),
            )

    except Exception as e:
        _handle_command_exception(ctx, e)
