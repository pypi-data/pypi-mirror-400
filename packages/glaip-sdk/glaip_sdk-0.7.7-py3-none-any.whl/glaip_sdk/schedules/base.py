"""Schedule runtime resources.

This module contains class-based runtime resources for schedules.

The runtime resources:
- Are not Pydantic models.
- Are returned from public client APIs.
- Delegate API operations to a bound ScheduleClient.

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from glaip_sdk.models.agent_runs import RunStatus
from glaip_sdk.models.schedule import (
    ScheduleConfig,
    ScheduleMetadata,
    ScheduleResponse,
    ScheduleRunResponse,
    ScheduleRunResult,
)

if TYPE_CHECKING:  # pragma: no cover
    from glaip_sdk.client.schedules import ScheduleClient

_SCHEDULE_CLIENT_REQUIRED_MSG = "No client available. Use client.schedules.get() to get a client-connected schedule."
_SCHEDULE_RUN_CLIENT_REQUIRED_MSG = (
    "No client available. Use client.schedules.list_runs() to get a client-connected schedule run."
)


class Schedule:
    """Runtime schedule resource.

    Attributes:
        id (str): The schedule ID.
        next_run_time (str | None): Next run time as returned by the API.
        time_until_next_run (str | None): Human readable duration until next run.
        metadata (ScheduleMetadata | None): Schedule metadata.
        created_at (datetime | None): Creation timestamp.
        updated_at (datetime | None): Update timestamp.
    """

    def __init__(
        self,
        *,
        id: str,
        next_run_time: str | None = None,
        time_until_next_run: str | None = None,
        metadata: ScheduleMetadata | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        _client: ScheduleClient | None = None,
    ) -> None:
        """Initialize a runtime Schedule."""
        self.id = id
        self.next_run_time = next_run_time
        self.time_until_next_run = time_until_next_run
        self.metadata = metadata
        self.created_at = created_at
        self.updated_at = updated_at
        self._client = _client

    @classmethod
    def from_response(cls, response: ScheduleResponse, *, client: ScheduleClient) -> Schedule:
        """Build a runtime Schedule from a DTO response.

        Args:
            response: Parsed schedule response DTO.
            client: ScheduleClient to bind.

        Returns:
            Runtime Schedule.
        """
        return cls(
            id=response.id,
            next_run_time=response.next_run_time,
            time_until_next_run=response.time_until_next_run,
            metadata=response.metadata,
            created_at=response.created_at,
            updated_at=response.updated_at,
            _client=client,
        )

    @property
    def agent_id(self) -> str | None:
        """Agent ID derived from metadata."""
        return self.metadata.agent_id if self.metadata else None

    @property
    def input(self) -> str | None:
        """Input text derived from metadata."""
        return self.metadata.input if self.metadata else None

    @property
    def schedule_config(self) -> ScheduleConfig | None:
        """Schedule configuration derived from metadata."""
        return self.metadata.schedule if self.metadata else None

    def update(
        self,
        *,
        input: str | None = None,
        schedule: ScheduleConfig | dict[str, str] | str | None = None,
    ) -> Schedule:
        """Update this schedule."""
        if self._client is None:
            raise RuntimeError(_SCHEDULE_CLIENT_REQUIRED_MSG)
        return self._client.update(self.id, input=input, schedule=schedule)

    def delete(self) -> None:
        """Delete this schedule."""
        if self._client is None:
            raise RuntimeError(_SCHEDULE_CLIENT_REQUIRED_MSG)
        self._client.delete(self.id)

    def list_runs(
        self,
        *,
        status: RunStatus | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> ScheduleRunListResult:
        """List runs for this schedule."""
        if self._client is None:
            raise RuntimeError(_SCHEDULE_CLIENT_REQUIRED_MSG)
        if self.agent_id is None:
            raise ValueError("Schedule has no agent_id")
        return self._client.list_runs(
            self.agent_id,
            schedule_id=self.id,
            status=status,
            limit=limit,
            page=page,
        )

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        parts: list[str] = [f"id={self.id!r}"]
        if self.agent_id is not None:
            parts.append(f"agent_id={self.agent_id!r}")
        if self.next_run_time is not None:
            parts.append(f"next_run_time={self.next_run_time!r}")
        if self.time_until_next_run is not None:
            parts.append(f"time_until_next_run={self.time_until_next_run!r}")
        if self.created_at is not None:
            parts.append(f"created_at={self.created_at!r}")
        return f"Schedule({', '.join(parts)})"

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.__repr__()


class ScheduleRun:
    """Runtime schedule run resource."""

    def __init__(
        self,
        *,
        id: str,
        agent_id: str,
        schedule_id: str | None = None,
        status: RunStatus,
        run_type: str | None = None,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
        input: str | None = None,
        config: ScheduleConfig | dict[str, str] | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        _client: ScheduleClient | None = None,
    ) -> None:
        """Initialize a runtime ScheduleRun."""
        self.id = id
        self.agent_id = agent_id
        self.schedule_id = schedule_id
        self.status = status
        self.run_type = run_type
        self.started_at = started_at
        self.completed_at = completed_at
        self.input = input
        self.config = config
        self.created_at = created_at
        self.updated_at = updated_at
        self._client = _client

    @classmethod
    def from_response(cls, response: ScheduleRunResponse, *, client: ScheduleClient) -> ScheduleRun:
        """Build a runtime ScheduleRun from a DTO response."""
        return cls(
            id=response.id,
            agent_id=response.agent_id,
            schedule_id=response.schedule_id,
            status=response.status,
            run_type=response.run_type,
            started_at=response.started_at,
            completed_at=response.completed_at,
            input=response.input,
            config=response.config,
            created_at=response.created_at,
            updated_at=response.updated_at,
            _client=client,
        )

    def get_result(self) -> ScheduleRunResult:
        """Retrieve the full output payload for this run."""
        if self._client is None:
            raise RuntimeError(_SCHEDULE_RUN_CLIENT_REQUIRED_MSG)
        if self.agent_id is None:
            raise ValueError("Schedule run has no agent_id")
        return self._client.get_run_result(self.agent_id, self.id)

    @property
    def duration(self) -> str | None:
        """Formatted duration (HH:MM:SS) when both timestamps are available."""
        if not self.started_at or not self.completed_at:
            return None

        total_seconds = int((self.completed_at - self.started_at).total_seconds())
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def __repr__(self) -> str:
        """Return a developer-friendly representation."""
        parts: list[str] = [f"id={self.id!r}", f"status={self.status!r}"]
        if self.started_at is not None:
            parts.append(f"started_at={self.started_at.isoformat()!r}")
        duration = self.duration
        if duration is not None:
            parts.append(f"duration={duration!r}")
        return f"ScheduleRun({', '.join(parts)})"

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.__repr__()


@dataclass
class ScheduleListResult:
    """Paginated list wrapper for runtime schedules."""

    items: list[Schedule]
    total: int | None = field(default=None)
    page: int | None = field(default=None)
    limit: int | None = field(default=None)
    has_next: bool | None = field(default=None)
    has_prev: bool | None = field(default=None)

    def __iter__(self):
        """Iterate over schedules."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of schedules in this page."""
        return self.items.__len__()

    def __getitem__(self, index: int) -> Schedule:
        """Return the schedule at the given index."""
        return self.items[index]


@dataclass
class ScheduleRunListResult:
    """Paginated list wrapper for runtime schedule runs."""

    items: list[ScheduleRun]
    total: int | None = field(default=None)
    page: int | None = field(default=None)
    limit: int | None = field(default=None)
    has_next: bool | None = field(default=None)
    has_prev: bool | None = field(default=None)

    def __iter__(self):
        """Iterate over schedule runs."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of runs in this page."""
        return self.items.__len__()

    def __getitem__(self, index: int) -> ScheduleRun:
        """Return the run at the given index."""
        return self.items[index]
