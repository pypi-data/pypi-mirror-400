"""Tool CLI commands package.

This package contains tool management commands split by operation.
The package is the canonical import surface.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# pylint: disable=duplicate-code
from glaip_sdk.cli.commands.tools._common import tools_group, _resolve_tool, console
from glaip_sdk.cli.commands.tools.create import create  # noqa: E402
from glaip_sdk.cli.commands.tools.delete import delete  # noqa: E402
from glaip_sdk.cli.commands.tools.get import get  # noqa: E402
from glaip_sdk.cli.commands.tools.list import list_tools  # noqa: E402
from glaip_sdk.cli.commands.tools.script import script  # noqa: E402
from glaip_sdk.cli.commands.tools.update import update  # noqa: E402

# Import helper functions from create module for backward compatibility
from glaip_sdk.cli.commands.tools.create import (  # noqa: E402
    _check_duplicate_name,
    _create_tool_from_file,
    _extract_internal_name,
    _handle_import_file,
    _parse_tags,
    _validate_name_match,
)

# Import core functions for test compatibility
from glaip_sdk.cli.core.context import get_client  # noqa: E402
from glaip_sdk.cli.core.output import (  # noqa: E402
    output_list,
    output_result,
)
from glaip_sdk.cli.core.rendering import spinner_context  # noqa: E402

# Import IO functions for test compatibility
from glaip_sdk.cli.io import (  # noqa: E402
    fetch_raw_resource_details,
    load_resource_from_file_with_validation,
)

# Alias for backward compatibility (used in create.py)
load_resource_from_file = load_resource_from_file_with_validation

__all__ = [
    "tools_group",
    "create",
    "delete",
    "get",
    "list_tools",
    "script",
    "update",
    "_check_duplicate_name",
    "_create_tool_from_file",
    "_extract_internal_name",
    "_handle_import_file",
    "_parse_tags",
    "_resolve_tool",
    "_validate_name_match",
    "console",
    "get_client",
    "output_list",
    "output_result",
    "spinner_context",
    "fetch_raw_resource_details",
    "load_resource_from_file_with_validation",
    "load_resource_from_file",
]
