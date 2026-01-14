"""Local agent execution runners.

This module provides runners for executing glaip-sdk agents locally
without requiring the AIP backend server. The primary runner is
LangGraphRunner which uses the aip-agents library.

To use local execution, install with the [local] extra:
    pip install "glaip-sdk[local]"

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)

Example:
    >>> from glaip_sdk.runner import get_default_runner
    >>> from glaip_sdk.agents import Agent
    >>>
    >>> agent = Agent(name="my-agent", instruction="You are helpful.")
    >>> runner = get_default_runner()
    >>> result = runner.run(agent, "Hello!")
"""

from typing import TYPE_CHECKING, Any

from glaip_sdk.runner.deps import (
    LOCAL_RUNTIME_AVAILABLE,
    check_local_runtime_available,
    get_local_runtime_missing_message,
)

# Default runner instance
_default_runner: Any | None = None


def get_default_runner() -> Any:
    """Get the default runner instance for local agent execution.

    Returns:
        The default LangGraphRunner instance.

    Raises:
        RuntimeError: If local runtime dependencies are not available.
    """
    global _default_runner

    if not check_local_runtime_available():
        raise RuntimeError(get_local_runtime_missing_message())

    if _default_runner is None:
        # Lazy import to avoid requiring aip-agents when runner is not used
        from glaip_sdk.runner.langgraph import LangGraphRunner  # noqa: PLC0415

        _default_runner = LangGraphRunner()

    return _default_runner


if TYPE_CHECKING:
    from glaip_sdk.runner.langgraph import LangGraphRunner

__all__ = [
    "LOCAL_RUNTIME_AVAILABLE",
    "LangGraphRunner",
    "check_local_runtime_available",
    "get_default_runner",
    "get_local_runtime_missing_message",
]


def __getattr__(name: str) -> Any:
    """Lazy import for LangGraphRunner to avoid requiring aip-agents when not used."""
    if name == "LangGraphRunner":
        from glaip_sdk.runner.langgraph import LangGraphRunner  # noqa: PLC0415

        globals()["LangGraphRunner"] = LangGraphRunner
        return LangGraphRunner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
