"""Agent response payload types.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# pylint: disable=duplicate-code
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class AgentListResult:
    """Structured response for list_agents that retains pagination metadata."""

    items: list[Any] = field(default_factory=list)
    total: int | None = None
    page: int | None = None
    limit: int | None = None
    has_next: bool | None = None
    has_prev: bool | None = None
    message: str | None = None

    def __len__(self) -> int:  # pragma: no cover - simple delegation
        """Return the number of items in the result list."""
        return len(self.items)

    def __iter__(self):  # pragma: no cover - simple delegation
        """Return an iterator over the items in the result list."""
        return iter(self.items)

    def __getitem__(self, index: int) -> Any:  # pragma: no cover - simple delegation
        """Get an item from the result list by index.

        Args:
            index: Index of the item to retrieve.

        Returns:
            The item at the specified index.
        """
        return self.items[index]
