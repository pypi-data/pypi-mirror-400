"""Agent CLI commands package.

This package contains agent management commands split by operation.
The package is the canonical import surface.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# pylint: disable=duplicate-code
# Import from submodules
from glaip_sdk.cli.commands.agents._common import (  # noqa: E402
    AGENT_NOT_FOUND_ERROR,
    _get_agent_for_update,
    _resolve_agent,
    agents_group,
    _coerce_mapping_candidate,
    _display_agent_details,
    _emit_verbose_guidance,
    _fetch_full_agent_details,
    _get_agent_model_name,
    _get_language_model_display_name,
    _model_from_config,
    _prepare_agent_output,
    _resolve_resources_by_name,
    console,
)
from glaip_sdk.cli.commands.agents.create import create  # noqa: E402
from glaip_sdk.cli.commands.agents.delete import delete  # noqa: E402
from glaip_sdk.cli.commands.agents.get import get  # noqa: E402
from glaip_sdk.cli.commands.agents.list import list_agents  # noqa: E402
from glaip_sdk.cli.commands.agents.run import run, _maybe_attach_transcript_toggle  # noqa: E402
from glaip_sdk.cli.commands.agents.sync_langflow import sync_langflow  # noqa: E402
from glaip_sdk.cli.commands.agents.update import update  # noqa: E402

# Import core functions for test compatibility
from glaip_sdk.cli.core.context import get_client  # noqa: E402
from glaip_sdk.cli.core.rendering import with_client_and_spinner  # noqa: E402

# Import display functions for test compatibility
from glaip_sdk.cli.display import (  # noqa: E402
    handle_json_output,
    handle_rich_output,
)

# Import core output functions for test compatibility
from glaip_sdk.cli.core.output import (  # noqa: E402
    handle_resource_export,
    output_list,
)

# Import rendering functions for test compatibility
from glaip_sdk.cli.core.rendering import (  # noqa: E402
    build_renderer,
)

# Import display functions for test compatibility
from glaip_sdk.cli.display import (  # noqa: E402
    display_agent_run_suggestions,
)

# Import rich helpers for test compatibility
from glaip_sdk.cli.rich_helpers import (  # noqa: E402
    markup_text,
)

# Import transcript functions for test compatibility
from glaip_sdk.cli.transcript import (  # noqa: E402
    maybe_launch_post_run_viewer,
    store_transcript_for_session,
)

# Import IO functions for test compatibility
from glaip_sdk.cli.io import (  # noqa: E402
    fetch_raw_resource_details,
)

# Import utils for test compatibility
from glaip_sdk.utils import (  # noqa: E402
    is_uuid,
)

__all__ = [
    "AGENT_NOT_FOUND_ERROR",
    "agents_group",
    "create",
    "delete",
    "get",
    "list_agents",
    "run",
    "sync_langflow",
    "update",
    "_get_agent_for_update",
    "_resolve_agent",
    "_coerce_mapping_candidate",
    "_display_agent_details",
    "_emit_verbose_guidance",
    "_fetch_full_agent_details",
    "_get_agent_model_name",
    "_get_language_model_display_name",
    "_model_from_config",
    "_prepare_agent_output",
    "_resolve_resources_by_name",
    "_maybe_attach_transcript_toggle",
    "get_client",
    "with_client_and_spinner",
    "console",
    "handle_json_output",
    "handle_rich_output",
    "output_list",
    "handle_resource_export",
    "build_renderer",
    "display_agent_run_suggestions",
    "markup_text",
    "maybe_launch_post_run_viewer",
    "store_transcript_for_session",
    "fetch_raw_resource_details",
    "is_uuid",
]
