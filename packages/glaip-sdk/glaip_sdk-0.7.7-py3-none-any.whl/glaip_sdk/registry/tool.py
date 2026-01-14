"""Tool registry for glaip_sdk.

This module provides a ToolRegistry that caches deployed tools
to avoid redundant API calls when deploying agents with tools.

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from glaip_sdk.registry.base import BaseRegistry

if TYPE_CHECKING:
    from glaip_sdk.tools import Tool

logger = logging.getLogger(__name__)


class ToolRegistry(BaseRegistry["Tool"]):
    """Registry for tools.

    Resolves tool references to glaip_sdk.models.Tool objects.
    Caches results to avoid redundant API calls and duplicate uploads.

    Handles:
        - Tool classes (LangChain BaseTool subclasses) → upload, cache, return Tool
        - glaip_sdk.models.Tool → return as-is (uses tool.id)
        - String names → lookup on platform, cache, return Tool

    Attributes:
        _cache: Internal cache mapping names to Tool objects.

    Example:
        >>> registry = get_tool_registry()
        >>> tool = registry.resolve(WebSearchTool)
        >>> print(tool.id)
    """

    def _get_name_from_model_fields(self, ref: type) -> str | None:
        """Extract name from Pydantic model_fields if available."""
        model_fields = getattr(ref, "model_fields", {})
        if "name" not in model_fields:
            return None
        field_info = model_fields["name"]
        default = getattr(field_info, "default", None)
        return default if isinstance(default, str) else None

    def _get_string_attr(self, obj: Any, attr: str) -> str | None:
        """Get attribute if it's a string, otherwise None."""
        value = getattr(obj, attr, None)
        return value if isinstance(value, str) else None

    def _extract_name_from_instance(self, ref: Any) -> str | None:
        """Extract name from a non-type instance.

        Args:
            ref: The instance to extract name from.

        Returns:
            The extracted name, or None if not found.
        """
        if isinstance(ref, type):
            return None
        return self._get_string_attr(ref, "name")

    def _extract_name_from_class(self, ref: Any) -> str | None:
        """Extract name from a class.

        Args:
            ref: The class to extract name from.

        Returns:
            The extracted name, or None if not found.
        """
        if not isinstance(ref, type):
            return None
        return self._get_string_attr(ref, "name") or self._get_name_from_model_fields(ref)

    def _extract_name(self, ref: Any) -> str:
        """Extract tool name from a reference.

        Args:
            ref: A tool class, instance, dict, or string name.

        Returns:
            The extracted tool name.

        Raises:
            ValueError: If name cannot be extracted from the reference.
        """
        # Lazy import to avoid circular dependency: Tool -> ToolRegistry -> Tool
        from glaip_sdk.tools.base import Tool  # noqa: PLC0415

        if isinstance(ref, str):
            return ref

        # Tool instance (from Tool.from_langchain() or Tool.from_native())
        if isinstance(ref, Tool):
            return ref.get_name()

        # Dict from API response - extract name or id
        if isinstance(ref, dict):
            return ref.get("name") or ref.get("id") or ""

        # Tool instance (not a class) with name attribute
        name = self._extract_name_from_instance(ref)
        if name:
            return name

        # Tool class - try direct attribute first, then model_fields
        name = self._extract_name_from_class(ref)
        if name:
            return name

        raise ValueError(f"Cannot extract name from: {ref}")

    def _cache_tool(self, tool: Tool, name: str) -> None:
        """Cache a tool by name and ID if available.

        Args:
            tool: The tool to cache.
            name: The tool name.
        """
        self._cache[name] = tool
        if hasattr(tool, "id") and tool.id:
            self._cache[tool.id] = tool

    def _resolve_native_platform_tool(self, name: str, tool_class: type | None = None) -> Tool:
        """Find a native tool on the platform and cache it.

        Args:
            name: The tool name to look up.
            tool_class: Optional local implementation to preserve.

        Returns:
            The resolved Tool object.

        Raises:
            ValueError: If the tool is not found on the platform.
        """
        from glaip_sdk.utils.discovery import find_tool  # noqa: PLC0415

        logger.info("Looking up native tool: %s", name)
        tool = find_tool(name)
        if tool:
            # Preserve local implementation if provided
            if tool_class:
                tool.tool_class = tool_class
            self._cache_tool(tool, name)
            return tool

        raise ValueError(
            f"Native tool '{name}' not found on platform. Ensure the tool is deployed or check for name mismatches."
        )

    def _resolve_tool_instance(self, ref: Any, name: str) -> Tool | None:
        """Resolve a ToolClass instance.

        Args:
            ref: The ToolClass instance to resolve.
            name: The extracted tool name.

        Returns:
            The resolved tool, or None if not a ToolClass instance.
        """
        # Lazy imports to avoid circular dependency: Tool -> ToolRegistry -> Tool
        from glaip_sdk.tools.base import Tool as ToolClass  # noqa: PLC0415
        from glaip_sdk.tools.base import ToolType  # noqa: PLC0415

        # Use try/except to handle mocked Tool class in tests
        try:
            is_tool_instance = isinstance(ref, ToolClass)
        except TypeError:
            return None

        if not is_tool_instance:
            return None

        # If Tool has an ID, it's already deployed - return as-is
        if ref.id is not None:
            logger.debug("Caching already deployed tool: %s", name)
            self._cache_tool(ref, name)
            return ref

        # Tool.from_native() - look up on platform
        if ref.tool_type == ToolType.NATIVE:
            return self._resolve_native_platform_tool(name, tool_class=getattr(ref, "tool_class", None))

        # Tool.from_langchain() - resolve the inner tool_class (promoted or uploaded)
        if ref.tool_class is not None:
            return self._resolve_custom_tool(ref.tool_class, name)

        # Unresolvable Tool instance - neither native nor has tool_class
        raise ValueError(
            f"Cannot resolve Tool instance: {ref}. "
            f"Tool has no id, is not NATIVE type, and has no tool_class. "
            f"Ensure Tool is created via Tool.from_native() or Tool.from_langchain()."
        )

    def _resolve_deployed_tool(self, ref: Any, name: str) -> Tool | None:
        """Resolve an already deployed tool (has id/name attributes).

        Args:
            ref: The tool reference to resolve.
            name: The extracted tool name.

        Returns:
            The resolved tool, or None if not a deployed tool.
        """
        # Already deployed tool (not a ToolClass, but has id/name)
        # This handles API response objects and backward compatibility
        if not (hasattr(ref, "id") and hasattr(ref, "name") and not isinstance(ref, type)):
            return None

        if ref.id is not None:
            logger.debug("Caching already deployed tool: %s", name)
            # Use _cache_tool to cache by both name and ID for consistency
            self._cache_tool(ref, name)
            return ref

        # Tool without ID (backward compatibility) - look up on platform
        return self._resolve_native_platform_tool(name)

    def _resolve_custom_tool(self, ref: Any, name: str) -> Tool | None:
        """Resolve a custom tool class, promoting aip_agents.tools classes to NATIVE.

        This method handles two main paths:
        1. **Promotion**: If the tool class is from `aip_agents.tools`, it is automatically
           promoted to a `NATIVE` tool type. It then performs a platform lookup to link it
           with the deployed native tool while preserving the local `tool_class` for local execution.
        2. **Upload**: If it is a standard LangChain tool, it is uploaded to the platform
           as a custom tool.

        Args:
            ref: The tool reference (usually a class) to resolve.
            name: The extracted tool name.

        Returns:
            The resolved tool, or None if not a custom tool.
        """
        # aip_agents tools are automatically promoted to NATIVE
        if self._is_aip_agents_tool(ref):
            from glaip_sdk.utils.tool_detection import get_tool_name  # noqa: PLC0415

            # Get name from class attribute or field
            tool_name = get_tool_name(ref)
            if tool_name is None:
                raise ValueError(f"Tool class {ref.__name__} has no 'name' attribute")

            return self._resolve_native_platform_tool(tool_name, tool_class=ref)

        if not self._is_custom_tool(ref):
            return None

        # Regular custom tools - upload to platform
        from glaip_sdk.utils.sync import update_or_create_tool  # noqa: PLC0415

        logger.info("Uploading custom tool: %s", name)
        tool = update_or_create_tool(ref)

        # Cache the resolved tool
        self._cache_tool(tool, name)
        if hasattr(tool, "id") and tool.id:
            self._cache[tool.id] = tool

        return tool

    def _resolve_dict_tool(self, ref: Any, name: str) -> Tool | None:
        """Resolve a tool from a dict (API response).

        Args:
            ref: The dict to resolve.
            name: The extracted tool name.

        Returns:
            The resolved tool, or None if not a dict.
        """
        # Lazy imports to avoid circular dependency
        from glaip_sdk.tools.base import Tool as ToolClass  # noqa: PLC0415

        if not isinstance(ref, dict):
            return None

        tool_id = ref.get("id")
        if tool_id:
            tool = ToolClass(id=tool_id, name=ref.get("name", ""))
            # Use _cache_tool to cache by both name and ID for consistency
            self._cache_tool(tool, name)
            return tool
        raise ValueError(f"Tool dict missing 'id': {ref}")

    def _resolve_string_tool(self, ref: Any, name: str) -> Tool | None:
        """Resolve a tool from a string name.

        Args:
            ref: The string to resolve.
            name: The extracted tool name.

        Returns:
            The resolved tool, or None if not a string.
        """
        if not isinstance(ref, str):
            return None

        return self._resolve_native_platform_tool(name)

    def _resolve_and_cache(self, ref: Any, name: str) -> Tool:
        """Resolve tool reference - upload if class, find if string/native.

        Args:
            ref: The tool reference to resolve.
            name: The extracted tool name.

        Returns:
            The resolved glaip_sdk.models.Tool object.

        Raises:
            ValueError: If tool cannot be resolved.
        """
        # Try each resolution strategy in order
        resolvers = [
            self._resolve_tool_instance,
            self._resolve_deployed_tool,
            self._resolve_custom_tool,
            self._resolve_dict_tool,
            self._resolve_string_tool,
        ]

        for resolver in resolvers:
            result = resolver(ref, name)
            if result is not None:
                return result

        raise ValueError(f"Could not resolve tool reference: {ref}")

    def _is_aip_agents_tool(self, ref: Any) -> bool:
        """Check if reference is an aip-agents tool.

        Args:
            ref: The reference to check.

        Returns:
            True if ref is from aip_agents.tools package.
        """
        try:
            from glaip_sdk.utils.tool_detection import (  # noqa: PLC0415
                is_aip_agents_tool,
            )
        except ImportError:
            return False

        return is_aip_agents_tool(ref)

    def _is_custom_tool(self, ref: Any) -> bool:
        """Check if reference is a custom tool class/instance.

        Args:
            ref: The reference to check.

        Returns:
            True if ref is a custom tool that needs uploading.
        """
        try:
            from glaip_sdk.utils.tool_detection import (  # noqa: PLC0415
                is_langchain_tool,
            )

            is_tool = is_langchain_tool(ref)
        except ImportError:
            is_tool = hasattr(ref, "args_schema") or hasattr(ref, "_run")
            if is_tool:
                logger.warning("tool_detection module missing; identifying tool via fallback attributes.")

        # aip_agents tools are NOT custom - they're native
        if is_tool and self._is_aip_agents_tool(ref):
            return False

        return is_tool

    def resolve(self, ref: Any) -> Tool:
        """Resolve a tool reference to a platform Tool object.

        Overrides base resolve to handle SDK tools differently.

        Args:
            ref: The tool reference to resolve.

        Returns:
            The resolved glaip_sdk.models.Tool object.
        """
        # Check if it's a Tool instance (not a class)
        if hasattr(ref, "id") and hasattr(ref, "name") and not isinstance(ref, type):
            # If Tool has an ID, it's already deployed - return as-is
            if ref.id is not None:
                name = self._extract_name(ref)
                if name not in self._cache:
                    # Use _cache_tool to cache by both name and ID for consistency
                    self._cache_tool(ref, name)
                return ref
            # Tool without ID (e.g., from Tool.from_native()) - needs platform lookup
            # Fall through to normal resolution

        return super().resolve(ref)


class _ToolRegistrySingleton:
    """Singleton holder for ToolRegistry to avoid global statement."""

    _instance: ToolRegistry | None = None

    @classmethod
    def get_instance(cls) -> ToolRegistry:
        """Get or create the singleton instance.

        Returns:
            The global ToolRegistry instance.
        """
        if cls._instance is None:
            cls._instance = ToolRegistry()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None


def get_tool_registry() -> ToolRegistry:
    """Get the singleton ToolRegistry instance.

    Returns a global ToolRegistry that caches tools across the session.

    Returns:
        The global ToolRegistry instance.

    Example:
        >>> from glaip_sdk.registry import get_tool_registry
        >>> registry = get_tool_registry()
        >>> tool = registry.resolve("web_search")
    """
    return _ToolRegistrySingleton.get_instance()
