#!/usr/bin/env python3
"""Schedule DTO models for AIP SDK.

These models represent API payloads and responses. They are intentionally DTO-only
and do not contain runtime behavior.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from glaip_sdk.models.agent_runs import RunStatus


class ScheduleConfig(BaseModel):
    """Cron-like schedule configuration matching backend ScheduleConfig.

    All fields accept cron-style values:
    - Specific values: "0", "9", "1"
    - Wildcards: "*"
    - Intervals: "*/5", "*/2"
    - Ranges: "1-5", "9-17"
    - Lists: "1,3,5"

    Note: day_of_week uses 0-6 where 0=Monday.
    """

    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"

    model_config = ConfigDict(from_attributes=True)

    def to_cron_string(self) -> str:
        """Convert to standard cron string format.

        Returns:
            Cron string in format "minute hour day_of_month month day_of_week"
        """
        return f"{self.minute} {self.hour} {self.day_of_month} {self.month} {self.day_of_week}"

    @classmethod
    def from_cron_string(cls, cron: str) -> "ScheduleConfig":
        """Parse a cron string into ScheduleConfig.

        Args:
            cron: Cron string in format "minute hour day_of_month month day_of_week"

        Returns:
            ScheduleConfig instance

        Raises:
            ValueError: If cron string doesn't have exactly 5 fields
        """
        parts = cron.split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron string: expected 5 fields, got {len(parts)}")
        return cls(
            minute=parts[0],
            hour=parts[1],
            day_of_month=parts[2],
            month=parts[3],
            day_of_week=parts[4],
        )


class ScheduleMetadata(BaseModel):
    """Metadata embedded in schedule responses.

    Contains the agent association, input text, and cron configuration.
    """

    agent_id: str
    input: str
    schedule: ScheduleConfig

    model_config = ConfigDict(from_attributes=True)


class ScheduleResponse(BaseModel):
    """Schedule response DTO.

    Attributes:
        id: Schedule ID.
        next_run_time: Next run time as returned by the API.
        time_until_next_run: Human-readable duration until next run.
        metadata: Schedule metadata.
        created_at: Creation timestamp.
        updated_at: Update timestamp.
        agent_id: Agent ID derived from metadata.
        input: Input text derived from metadata.
        schedule_config: ScheduleConfig derived from metadata.
    """

    id: str
    next_run_time: str | None = None
    time_until_next_run: str | None = None
    metadata: ScheduleMetadata | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def agent_id(self) -> str | None:
        """Get the agent ID from metadata."""
        return self.metadata.agent_id if self.metadata else None

    @property
    def input(self) -> str | None:
        """Get the scheduled input text from metadata."""
        return self.metadata.input if self.metadata else None

    @property
    def schedule_config(self) -> ScheduleConfig | None:
        """Get the schedule configuration from metadata."""
        return self.metadata.schedule if self.metadata else None

    def __repr__(self) -> str:
        """Return a readable representation of the schedule."""
        parts = [f"ScheduleResponse(id={self.id!r}"]
        if self.next_run_time:
            parts.append(f"next_run_time={self.next_run_time!r}")
        if self.time_until_next_run:
            parts.append(f"time_until_next_run={self.time_until_next_run!r}")
        if self.agent_id:
            parts.append(f"agent_id={self.agent_id!r}")
        if self.created_at:
            parts.append(f"created_at={self.created_at!r}")
        return ", ".join(parts) + ")"

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.__repr__()


# Type alias for SSE event dictionaries
ScheduleRunOutputChunk = dict[str, Any]


class ScheduleRunResponse(BaseModel):
    """Schedule run response DTO."""

    id: str
    agent_id: str
    schedule_id: str | None = None  # May be None for non-scheduled runs
    status: RunStatus  # Backend uses lowercase.
    run_type: str | None = None  # "schedule" for scheduled runs
    started_at: datetime | None = None
    completed_at: datetime | None = None
    input: str | None = None  # Input used for the execution.
    config: ScheduleConfig | dict[str, str] | None = None  # Schedule config used.
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    @property
    def duration(self) -> str | None:
        """Calculate the duration of the run.

        Returns:
            Formatted duration string (HH:MM:SS) or None if incomplete
        """
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            total_seconds = int(delta.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return None

    def __repr__(self) -> str:
        """Return a readable representation of the run."""
        parts = [f"ScheduleRunResponse(id={self.id!r}"]
        parts.append(f"status={self.status!r}")
        if self.started_at:
            parts.append(f"started_at={self.started_at.isoformat()!r}")
        if self.duration:
            parts.append(f"duration={self.duration!r}")
        return ", ".join(parts) + ")"

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.__repr__()


class ScheduleRunResult(BaseModel):
    """Full output payload for a schedule run.

    Maps to the backend's AgentRunWithOutputResponse which includes
    run metadata plus the output stream.
    """

    id: str
    agent_id: str
    schedule_id: str | None = None
    status: RunStatus
    run_type: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    input: str | None = None  # Input used for the execution.
    config: ScheduleConfig | dict[str, str] | None = None  # Schedule config used.
    output: list[ScheduleRunOutputChunk] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True, extra="ignore")

    def __repr__(self) -> str:
        """Return a readable representation of the result."""
        output_count = len(self.output) if self.output else 0
        return f"ScheduleRunResult(id={self.id!r}, status={self.status!r}, output_chunks={output_count})"

    def __str__(self) -> str:
        """Return a readable string representation."""
        return self.__repr__()
