"""Human-in-the-Loop (HITL) utilities for glaip-sdk.

This package provides utilities for HITL approval workflows in both local
and remote agent execution modes.

For local development, LocalPromptHandler is automatically injected when
agent_config.hitl_enabled is True. No manual setup required.

For remote execution, use RemoteHITLHandler to handle HITL events programmatically.

Authors:
    Putu Ravindra Wiguna (putu.r.wiguna@gdplabs.id)
    GLAIP SDK Team
"""

from typing import TYPE_CHECKING, Any

# These don't require aip_agents, so import them directly
from glaip_sdk.hitl.base import HITLCallback, HITLDecision, HITLRequest, HITLResponse
from glaip_sdk.hitl.callback import PauseResumeCallback
from glaip_sdk.hitl.remote import RemoteHITLHandler

if TYPE_CHECKING:
    from glaip_sdk.hitl.local import LocalPromptHandler

__all__ = [
    "LocalPromptHandler",
    "PauseResumeCallback",
    "HITLCallback",
    "HITLDecision",
    "HITLRequest",
    "HITLResponse",
    "RemoteHITLHandler",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy import for LocalPromptHandler.

    This defers the import of aip_agents until LocalPromptHandler is actually accessed,
    preventing ImportError when aip-agents is not installed but HITL is not being used.
    """
    if name == "LocalPromptHandler":
        from glaip_sdk.hitl.local import LocalPromptHandler  # noqa: PLC0415

        globals()["LocalPromptHandler"] = LocalPromptHandler
        return LocalPromptHandler
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
