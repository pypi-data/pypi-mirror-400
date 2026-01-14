"""Schedule request payload builders for AIP SDK.

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
"""

from dataclasses import dataclass
from typing import Any

from glaip_sdk.models.schedule import ScheduleConfig


@dataclass
class ScheduleListParams:
    """Parameters for listing schedules.

    Args:
        limit: Maximum number of schedules to return (1-100, default 50)
        page: Page number for pagination (default 1)
        agent_id: Filter schedules by agent ID
    """

    limit: int | None = None
    page: int | None = None
    agent_id: str | None = None

    def to_query_params(self) -> dict[str, Any]:
        """Convert to query parameters dictionary.

        Returns:
            Dictionary of non-None parameters for the API request
        """
        params: dict[str, Any] = {}
        if self.limit is not None:
            params["limit"] = self.limit
        if self.page is not None:
            params["page"] = self.page
        if self.agent_id is not None:
            params["agent_id"] = self.agent_id
        return params


def normalize_schedule(
    schedule: ScheduleConfig | dict[str, str] | str | None,
) -> dict[str, str] | None:
    """Normalize schedule input to a dictionary for API requests.

    Accepts multiple input formats for user convenience:
    - ScheduleConfig: Pydantic model with cron fields
    - dict: Dictionary with cron fields (minute, hour, etc.)
    - str: Cron string like "0 9 * * 1-5"
    - None: Returns None

    Args:
        schedule: Schedule in various formats

    Returns:
        Dictionary suitable for API request or None

    Raises:
        ValueError: If cron string format is invalid
        TypeError: If schedule is an unsupported type

    Examples:
        >>> normalize_schedule(ScheduleConfig(minute="0", hour="9"))
        {'minute': '0', 'hour': '9', 'day_of_month': '*', 'month': '*', 'day_of_week': '*'}

        >>> normalize_schedule({"minute": "0", "hour": "9"})
        {'minute': '0', 'hour': '9', 'day_of_month': '*', 'month': '*', 'day_of_week': '*'}

        >>> normalize_schedule("0 9 * * 1-5")
        {'minute': '0', 'hour': '9', 'day_of_month': '*', 'month': '*', 'day_of_week': '1-5'}
    """
    if schedule is None:
        return None

    if isinstance(schedule, ScheduleConfig):
        return schedule.model_dump()

    if isinstance(schedule, dict):
        # Validate and merge with defaults
        return ScheduleConfig(**schedule).model_dump()

    if isinstance(schedule, str):
        # Parse cron string
        config = ScheduleConfig.from_cron_string(schedule)
        return config.model_dump()

    raise TypeError(f"schedule must be ScheduleConfig, dict, or str, got {type(schedule).__name__}")
