"""Shared utilities for tool type detection.

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

from __future__ import annotations

import ast
import importlib
import inspect
import pkgutil
from functools import lru_cache
from typing import Any

# Constants for frequently used strings to avoid duplication (S1192)
_NAME = "name"
_AIP_AGENTS_TOOLS = "aip_agents.tools"
_BASE_TOOL = "BaseTool"

# Internal map to store all discovered tools in the session
_DISCOVERED_TOOLS: dict[str, type] | None = None


def _should_skip_module(module_name: str) -> bool:
    """Check if module should be skipped during tool discovery."""
    short_name = module_name.rsplit(".", 1)[-1]
    return short_name.startswith("_") or "test" in short_name


def _get_pydantic_field_default(cls: type, attr_name: str, field_name: str) -> str | None:
    """Extract default value from a Pydantic field."""
    try:
        fields = getattr(cls, attr_name, {})
        field = fields.get(field_name)
        # Broad exception handling needed because:
        # - model_fields/__fields__ might be a descriptor that raises AttributeError
        # - field.default might raise during access
        # - Various Pydantic internals can raise unexpected exceptions
        if field and hasattr(field, "default") and isinstance(field.default, str):
            return field.default
    except Exception:  # pylint: disable=broad-except
        pass
    return None


def _get_name_from_pydantic_v2(cls: type) -> str | None:
    """Extract name from Pydantic v2 model_fields."""
    return _get_pydantic_field_default(cls, "model_fields", _NAME)


def _get_name_from_pydantic_v1(cls: type) -> str | None:
    """Extract name from Pydantic v1 __fields__."""
    return _get_pydantic_field_default(cls, "__fields__", _NAME)


def get_tool_name(ref: Any) -> str | None:
    """Extract tool name from a tool class or instance.

    Handles LangChain BaseTool (Pydantic v1/v2) and standard classes.

    Args:
        ref: Tool class or instance.

    Returns:
        The extracted tool name, or None if not found.
    """
    if ref is None:
        return None

    # 1. Try instance 'name' attribute
    if not isinstance(ref, type):
        try:
            name = getattr(ref, _NAME, None)
            if isinstance(name, str):
                return name
        except Exception:  # pylint: disable=broad-except
            pass

    cls = ref if isinstance(ref, type) else type(ref)

    # 2. Try class 'model_fields' (Pydantic v2)
    # Check Pydantic v2 first for forward compatibility
    name = _get_name_from_pydantic_v2(cls)
    if name:
        return name

    # 3. Try class '__fields__' (Pydantic v1)
    name = _get_name_from_pydantic_v1(cls)
    if name:
        return name

    # 4. Try direct class attribute
    if hasattr(cls, _NAME):
        try:
            name_attr = getattr(cls, _NAME)
            if isinstance(name_attr, str):
                return name_attr
        except Exception:  # pylint: disable=broad-except
            pass

    return None


def _check_langchain_standard(ref: Any) -> bool:
    """Perform standard isinstance/issubclass check for LangChain tool."""
    try:
        from langchain_core.tools import BaseTool  # noqa: PLC0415

        # Check if BaseTool is actually a type to avoid TypeError in issubclass/isinstance
        if isinstance(BaseTool, type):
            if isinstance(ref, type) and issubclass(ref, BaseTool):
                return True
            if isinstance(ref, BaseTool):
                return True
    except (ImportError, TypeError):
        pass
    return False


def _check_langchain_fallback(ref: Any) -> bool:
    """Perform name-based fallback check for LangChain tool (robust for mocks).

    This fallback handles cases where:
    - BaseTool is mocked in tests
    - BaseTool is re-imported through internal modules (e.g., runner)
    - isinstance/issubclass checks fail due to module reloading
    """
    try:
        cls = ref if isinstance(ref, type) else getattr(ref, "__class__", None)
        if cls and hasattr(cls, "__mro__"):
            for c in cls.__mro__:
                c_name = getattr(c, "__name__", None)
                c_module = getattr(c, "__module__", "")
                if c_name == _BASE_TOOL and ("langchain" in c_module or "runner" in c_module):
                    return True
    except (AttributeError, TypeError):
        pass
    return False


def is_langchain_tool(ref: Any) -> bool:
    """Check if ref is a LangChain BaseTool class or instance.

    Shared by:
    - ToolRegistry._is_custom_tool() (for upload detection)
    - LangChainToolAdapter._is_langchain_tool() (for adaptation)

    Args:
        ref: Object to check.

    Returns:
        True if ref is a LangChain BaseTool class or instance.
    """
    if ref is None:
        return False

    # 1. Standard check (preferred)
    if _check_langchain_standard(ref):
        return True

    # 2. Name-based check (robust fallback for mocks and re-imports)
    return _check_langchain_fallback(ref)


def is_aip_agents_tool(ref: Any) -> bool:
    """Check if ref is an aip-agents tool class or instance.

    Args:
        ref: Object to check.

    Returns:
        True if ref is from aip_agents.tools package.
    """
    try:
        # Check class module
        if isinstance(ref, type):
            return ref.__module__.startswith(_AIP_AGENTS_TOOLS)

        # Check instance class
        if hasattr(ref, "__class__"):
            return ref.__class__.__module__.startswith(_AIP_AGENTS_TOOLS)

        return False
    except (AttributeError, TypeError):
        return False


def _get_discovered_classes_from_module(module: Any) -> list[type]:
    """Extract BaseTool subclasses from a module."""
    discovered_classes = []
    for attr_name in dir(module):
        if attr_name.startswith("_"):
            continue

        try:
            attr = getattr(module, attr_name)
            if inspect.isclass(attr) and is_langchain_tool(attr):
                # Ensure it's not the BaseTool class itself
                if getattr(attr, "__name__", None) != _BASE_TOOL:
                    discovered_classes.append(attr)
        except Exception:  # pylint: disable=broad-except
            continue
    return discovered_classes


def _import_and_map_module(module_name: str, tools_map: dict[str, type]) -> None:
    """Import a single module and extract its tools."""
    try:
        module = importlib.import_module(module_name)
        classes = _get_discovered_classes_from_module(module)
        for tool_class in classes:
            name = get_tool_name(tool_class)
            if name:
                tools_map[name] = tool_class
    except Exception:  # pylint: disable=broad-except
        # Broad catch to skip broken modules during discovery
        pass


def _walk_and_map_package(package: Any, tools_map: dict[str, type]) -> None:
    """Walk through a package and map all tools found."""
    try:
        # Walk packages using the package's path and name
        for _, module_name, _ in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
            if _should_skip_module(module_name):
                continue  # pragma: no cover

            _import_and_map_module(module_name, tools_map)
    except Exception:  # pylint: disable=broad-except
        # Broad catch for walk_packages failure
        pass


def _get_all_aip_agents_tools() -> dict[str, type]:
    """Discover and map all tools in aip_agents.tools (once per session)."""
    global _DISCOVERED_TOOLS  # pylint: disable=global-statement
    if _DISCOVERED_TOOLS is None:
        _DISCOVERED_TOOLS = {}
        try:
            package = importlib.import_module(_AIP_AGENTS_TOOLS)
            if hasattr(package, "__path__"):
                _walk_and_map_package(package, _DISCOVERED_TOOLS)
        except (ImportError, AttributeError):
            pass
    return _DISCOVERED_TOOLS


@lru_cache(maxsize=128)
def find_aip_agents_tool_class(name: str) -> type | None:
    """Find and return a native tool class by tool name.

    Searches aip_agents.tools submodules for BaseTool subclasses
    with matching 'name' attribute. Uses caching to improve performance.

    Note:
        Results are discovered once per session and cached. If tools are
        dynamically added to the path after the first call, they may not
        be discovered until the session restarts.

    Args:
        name (str): The tool name to search for (e.g., "google_serper").

    Returns:
        type|None: The discovered tool class, or None if not found.

    Examples:
        >>> find_aip_agents_tool_class("google_serper")
        <class 'aip_agents.tools.web_search.serper_tool.GoogleSerperTool'>

        >>> find_aip_agents_tool_class("nonexistent")
        None
    """
    return _get_all_aip_agents_tools().get(name)


def clear_discovery_cache() -> None:
    """Clear the tool discovery cache (internal use for testing)."""
    global _DISCOVERED_TOOLS  # pylint: disable=global-statement
    _DISCOVERED_TOOLS = None
    find_aip_agents_tool_class.cache_clear()


def is_tool_plugin_decorator(decorator: ast.expr) -> bool:
    """Check if an AST decorator node is @tool_plugin.

    Shared by:
    - ToolBundler._has_tool_plugin_decorator() (for bundling)
    - ImportResolver._is_tool_plugin_decorator() (for import resolution)

    Args:
        decorator: AST decorator expression node to check.

    Returns:
        True if decorator is @tool_plugin.
    """
    if isinstance(decorator, ast.Name) and decorator.id == "tool_plugin":
        return True
    if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name) and decorator.func.id == "tool_plugin":
        return True
    return False
