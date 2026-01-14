"""MCP CLI commands package.

This package contains MCP management commands split by operation.
The package is the canonical import surface.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# pylint: disable=duplicate-code
from glaip_sdk.cli.commands.mcps._common import (  # noqa: E402
    mcps_group,
    _resolve_mcp,
    console,
    _load_import_ready_payload,
    _merge_import_payload,
    _strip_server_only_fields,
    _coerce_cli_string,
    _collect_cli_overrides,
    _merge_config_field,
    _merge_auth_field,
    _get_config_transport,
    _generate_update_preview,
)
from glaip_sdk.cli.commands.mcps.connect import connect  # noqa: E402
from glaip_sdk.cli.commands.mcps.create import create  # noqa: E402
from glaip_sdk.cli.commands.mcps.delete import delete  # noqa: E402
from glaip_sdk.cli.commands.mcps.get import get  # noqa: E402
from glaip_sdk.cli.commands.mcps.list import list_mcps  # noqa: E402
from glaip_sdk.cli.commands.mcps.tools import list_tools, _get_tools_from_config  # noqa: E402
from glaip_sdk.cli.commands.mcps.update import update  # noqa: E402

# Import core functions for test compatibility
from glaip_sdk.cli.core.context import get_client  # noqa: E402
from glaip_sdk.cli.core.output import (  # noqa: E402
    output_list,
    output_result,
)
from glaip_sdk.cli.core.rendering import (  # noqa: E402
    spinner_context,
    with_client_and_spinner,
)

# Import validators for test compatibility
from glaip_sdk.cli.mcp_validators import (  # noqa: E402
    validate_mcp_auth_structure,
    validate_mcp_config_structure,
)

# Import import/export utilities for test compatibility
from glaip_sdk.utils.import_export import convert_export_to_import_format  # noqa: E402
from glaip_sdk.cli.io import load_resource_from_file_with_validation  # noqa: E402

# Import shared formatters for test compatibility
from glaip_sdk.cli.commands.shared.formatters import (  # noqa: E402
    _format_dict_value,
    _redact_sensitive_dict,
    _is_sensitive_data,
)

__all__ = [
    "mcps_group",
    "connect",
    "create",
    "delete",
    "get",
    "list_mcps",
    "list_tools",
    "update",
    "_resolve_mcp",
    "console",
    "_load_import_ready_payload",
    "_merge_import_payload",
    "_strip_server_only_fields",
    "_coerce_cli_string",
    "_collect_cli_overrides",
    "_merge_config_field",
    "_merge_auth_field",
    "_get_config_transport",
    "_generate_update_preview",
    "_get_tools_from_config",
    "_format_dict_value",
    "_redact_sensitive_dict",
    "_is_sensitive_data",
    "get_client",
    "output_list",
    "output_result",
    "spinner_context",
    "with_client_and_spinner",
    "validate_mcp_auth_structure",
    "validate_mcp_config_structure",
    "convert_export_to_import_format",
    "load_resource_from_file_with_validation",
]
