"""Schedule client for AIP SDK.

Authors:
    Christian Trisno Sen Long Chen (christian.t.s.l.chen@gdplabs.id)
    Putu Ravindra Wiguna (putu.r.wiguna@gdplabs.id)
"""

from typing import TYPE_CHECKING, Any

from glaip_sdk.client._schedule_payloads import ScheduleListParams, normalize_schedule
from glaip_sdk.client.base import BaseClient
from glaip_sdk.exceptions import APIError, NotFoundError
from glaip_sdk.models.agent_runs import RunStatus
from glaip_sdk.models.schedule import (
    ScheduleConfig,
    ScheduleResponse,
    ScheduleRunResponse,
    ScheduleRunResult,
)
from glaip_sdk.schedules import (
    Schedule,
    ScheduleListResult,
    ScheduleRun,
    ScheduleRunListResult,
)

if TYPE_CHECKING:
    from glaip_sdk.models import Agent


class ScheduleClient(BaseClient):
    """Client for managing agent schedules.

    Provides CRUD operations for scheduled agent executions.
    Schedules allow agents to run automatically at specified times
    using cron-like configurations.

    Example:
        >>> from glaip_sdk import Client
        >>> from glaip_sdk.models.schedule import ScheduleConfig
        >>>
        >>> client = Client()
        >>> # List all schedules
        >>> result = client.schedules.list()
        >>> for schedule in result:
        ...     print(f"{schedule.id}: {schedule.next_run_time}")
        >>>
        >>> # Get a specific schedule
        >>> schedule = client.schedules.get("schedule-id")
        >>>
        >>> # Create a schedule for an agent
        >>> schedule = client.schedules.create(
        ...     agent_id="agent-id",
        ...     input="Generate daily report",
        ...     schedule=ScheduleConfig(minute="0", hour="9", day_of_week="1-5")
        ... )
        >>>
        >>> # Update a schedule
        >>> schedule = client.schedules.update(
        ...     schedule_id="schedule-id",
        ...     input="Updated report input"
        ... )
        >>>
        >>> # Delete a schedule
        >>> client.schedules.delete("schedule-id")
    """

    def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
        agent_id: str | None = None,
    ) -> ScheduleListResult:
        """List schedules with optional filtering and pagination.

        Args:
            limit: Maximum number of schedules to return (1-100)
            page: Page number for pagination
            agent_id: Filter schedules by agent ID

        Returns:
            ScheduleListResult containing schedules and pagination metadata
        """
        params = ScheduleListParams(limit=limit, page=page, agent_id=agent_id)

        response = self._request_with_envelope(
            "GET",
            "/agents/schedules",
            params=params.to_query_params(),
        )

        # Parse schedules from response data
        schedules = [
            Schedule.from_response(ScheduleResponse.model_validate(item), client=self)
            for item in (response.get("data") or [])
        ]

        return ScheduleListResult(
            items=schedules,
            total=response.get("total"),
            page=response.get("page"),
            limit=response.get("limit"),
            has_next=response.get("has_next"),
            has_prev=response.get("has_prev"),
        )

    def get(self, schedule_id: str) -> Schedule:
        """Get a schedule by ID.

        Args:
            schedule_id: The schedule ID to retrieve

        Returns:
            Schedule instance

        Raises:
            NotFoundError: If schedule is not found
            AuthenticationError: If API key is invalid
            APIError: If the API request fails
        """
        data = self._request("GET", f"/agents/schedules/{schedule_id}")

        if data is None:
            raise NotFoundError(f"Schedule not found: {schedule_id}")
        return Schedule.from_response(ScheduleResponse.model_validate(data), client=self)

    def create(
        self,
        *,
        agent_id: str,
        input: str,
        schedule: ScheduleConfig | dict[str, str] | str,
    ) -> Schedule:
        """Create a new schedule for an agent.

        Args:
            agent_id: The agent ID to schedule
            input: Input text for scheduled execution
            schedule: Schedule configuration (ScheduleConfig, dict, or cron string)

        Returns:
            Created Schedule instance

        Raises:
            ValueError: If schedule format is invalid
            NotFoundError: If agent is not found
            ValidationError: If schedule configuration is invalid
            AuthenticationError: If API key is invalid
            APIError: If the API request fails
        """
        schedule_dict = normalize_schedule(schedule)
        if schedule_dict is None:
            raise ValueError("schedule is required")

        payload = {
            "input": input,
            "schedule": schedule_dict,
        }

        response = self._request("POST", f"/agents/{agent_id}/schedule", json=payload)

        # Response contains schedule_id, fetch the full schedule
        schedule_id = response.get("schedule_id")
        if not schedule_id:
            raise APIError("Missing schedule_id in create response")

        return self.get(schedule_id)

    def update(
        self,
        schedule_id: str,
        *,
        input: str | None = None,
        schedule: ScheduleConfig | dict[str, str] | str | None = None,
    ) -> Schedule:
        """Update an existing schedule.

        Args:
            schedule_id: The schedule ID to update
            input: New input text for scheduled execution
            schedule: New schedule configuration (ScheduleConfig, dict, or cron string)

        Returns:
            Updated Schedule instance

        Raises:
            NotFoundError: If schedule is not found
            ValueError: If schedule config is required but not provided
            ValidationError: If schedule configuration is invalid
            AuthenticationError: If API key is invalid
            APIError: If the API request fails

        Note:
            Updates use explicit replacement (not merge). The SDK normalizes partial
            schedule dicts by filling missing cron fields with "*". This is intentional
            for predictability - what you provide is what you get (plus wildcard defaults).
            If the current schedule metadata is missing and no schedule parameter is
            provided, a ValueError is raised.
        """
        # Get current schedule to merge with updates
        current = self.get(schedule_id)

        # Handle input - ensure we have valid input data
        if current.input is None and input is None:
            raise ValueError(
                f"Schedule {schedule_id} has missing input metadata and no input parameter provided. "
                "Please provide an input value to update this schedule."
            )

        # Handle schedule config - ensure we have complete schedule data
        if current.schedule_config is None and schedule is None:
            raise ValueError(
                f"Schedule {schedule_id} has missing metadata and no schedule parameter provided. "
                "Please provide a full schedule configuration to update this schedule."
            )

        current_input = current.input or ""
        current_schedule = current.schedule_config.model_dump() if current.schedule_config else {}

        payload: dict[str, Any] = {
            "input": input if input is not None else current_input,
            "schedule": normalize_schedule(schedule) or current_schedule,
        }

        data = self._request("PUT", f"/agents/schedules/{schedule_id}", json=payload)
        return Schedule.from_response(ScheduleResponse.model_validate(data), client=self)

    def delete(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id: The schedule ID to delete

        Raises:
            NotFoundError: If schedule is not found
            AuthenticationError: If API key is invalid
            APIError: If the API request fails
        """
        self._request("DELETE", f"/agents/schedules/{schedule_id}")

    def list_runs(
        self,
        agent_id: str,
        *,
        schedule_id: str | None = None,
        status: RunStatus | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> ScheduleRunListResult:
        """List runs for an agent, optionally filtered by schedule ID.

        Args:
            agent_id: The agent ID to list runs for
            schedule_id: Optional schedule ID to filter by
            status: Optional status filter
            limit: Maximum number of runs to return (1-100)
            page: Page number for pagination

        Returns:
            ScheduleRunListResult containing runs and pagination metadata
        """
        params: dict[str, Any] = {"run_type": "schedule"}
        if schedule_id is not None:
            params["schedule_id"] = schedule_id
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if page is not None:
            params["page"] = page

        response = self._request_with_envelope(
            "GET",
            f"/agents/{agent_id}/runs",
            params=params,
        )

        # Parse runs from response data
        runs = [
            ScheduleRun.from_response(ScheduleRunResponse.model_validate(item), client=self)
            for item in (response.get("data") or [])
        ]

        return ScheduleRunListResult(
            items=runs,
            total=response.get("total"),
            page=response.get("page"),
            limit=response.get("limit"),
            has_next=response.get("has_next"),
            has_prev=response.get("has_prev"),
        )

    def get_run_result(self, agent_id: str, run_id: str) -> ScheduleRunResult:
        """Get the full output payload for an agent run.

        Args:
            agent_id: The agent ID the run belongs to
            run_id: The run ID to retrieve

        Returns:
            ScheduleRunResult containing run details and optional output
        """
        data = self._request("GET", f"/agents/{agent_id}/runs/{run_id}")
        return ScheduleRunResult.model_validate(data)


class AgentScheduleManager:
    """Facade for agent-scoped schedule operations.

    Provides a convenient interface for managing schedules through
    an Agent instance, automatically scoping operations to that agent.

    Example:
        >>> agent = client.get_agent_by_id("agent-id")
        >>> # List schedules for this agent
        >>> schedules = agent.schedule.list()
        >>> # Create a schedule for this agent
        >>> schedule = agent.schedule.create(
        ...     input="Daily task",
        ...     schedule="0 9 * * 1-5"
        ... )
    """

    def __init__(self, agent: "Agent", client: ScheduleClient) -> None:
        """Initialize the schedule manager.

        Args:
            agent: The agent to manage schedules for
            client: The ScheduleClient for API operations
        """
        self._agent = agent
        self._client = client

    def list(
        self,
        *,
        limit: int | None = None,
        page: int | None = None,
    ) -> ScheduleListResult:
        """List schedules for this agent.

        Args:
            limit: Maximum number of schedules to return (1-100)
            page: Page number for pagination

        Returns:
            ScheduleListResult containing schedules for this agent
        """
        return self._client.list(limit=limit, page=page, agent_id=self._agent.id)

    def create(
        self,
        *,
        input: str,
        schedule: ScheduleConfig | dict[str, str] | str,
    ) -> Schedule:
        """Create a schedule for this agent.

        Args:
            input: Input text for scheduled execution
            schedule: Schedule configuration (ScheduleConfig, dict, or cron string)

        Returns:
            Created Schedule instance
        """
        return self._client.create(
            agent_id=self._agent.id,
            input=input,
            schedule=schedule,
        )

    def get(self, schedule_id: str) -> Schedule:
        """Get a schedule by ID.

        Args:
            schedule_id: The schedule ID to retrieve

        Returns:
            Schedule instance

        Raises:
            NotFoundError: If schedule is not found
        """
        return self._client.get(schedule_id)

    def update(
        self,
        schedule_id: str,
        *,
        input: str | None = None,
        schedule: ScheduleConfig | dict[str, str] | str | None = None,
    ) -> Schedule:
        """Update a schedule.

        Args:
            schedule_id: The schedule ID to update
            input: New input text for scheduled execution
            schedule: New schedule configuration

        Returns:
            Updated Schedule instance
        """
        return self._client.update(schedule_id, input=input, schedule=schedule)

    def delete(self, schedule_id: str) -> None:
        """Delete a schedule.

        Args:
            schedule_id: The schedule ID to delete
        """
        self._client.delete(schedule_id)

    def list_runs(
        self,
        schedule_id: str | None = None,
        *,
        status: RunStatus | None = None,
        limit: int | None = None,
        page: int | None = None,
    ) -> ScheduleRunListResult:
        """List runs for this agent.

        Args:
            schedule_id: Optional schedule ID to filter by
            status: Optional status filter
            limit: Maximum number of runs to return (1-100)
            page: Page number for pagination

        Returns:
            ScheduleRunListResult containing runs for this agent
        """
        return self._client.list_runs(
            self._agent.id,
            schedule_id=schedule_id,
            status=status,
            limit=limit,
            page=page,
        )
