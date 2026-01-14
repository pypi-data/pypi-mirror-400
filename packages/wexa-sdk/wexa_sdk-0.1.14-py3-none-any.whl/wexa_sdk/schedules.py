from __future__ import annotations
from typing import TypedDict, Optional, Dict, Any

from .core.http import HttpClient


class CoworkerScheduleCreateBody(TypedDict):
    coworker_id: str
    goal: Dict[str, Any]
    template: str
    display_template: str
    schedule: int


class CoworkerScheduleUpdateBody(TypedDict, total=False):
    goal: Dict[str, Any]
    template: str
    display_template: str
    schedule: int


class Schedules:
    def __init__(self, http: HttpClient):
        self.http = http

    def list_coworker_schedules(
        self,
        coworker_id: str | None,
        *,
        projectID: str,
        limit: int = 20,
        page_no: int = 1,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search_key: Optional[str] = None,
    ):
        """
        Get schedules.
        GET /schedules/coworker?projectID=...&limit=...&page_no=...&coworker_id=...&status=...&type=...&search_key=...

        Retrieve Coworker Schedule by ID.

        Use this endpoint to retrieve the schedule details of a specific AI Coworker within your 
        Wexa.ai environment by its unique coworker_id. This allows you to view the planned execution 
        times and frequencies of the coworker's tasks, enabling better planning and coordination 
        of automation workflows.

        Args:
            coworker_id: The unique identifier of the coworker (optional)
            projectID: The unique identifier of the project (required)
            limit: Maximum number of schedules to return (optional, default: 20)
            page_no: Page number for pagination (optional, default: 1)
            status: Optional status filter (optional)
            type: Optional type filter (optional)
            search_key: Optional search key for filtering schedules (optional)

        Returns:
            List of schedule details for the coworker, containing planned execution times, 
            frequencies, and other relevant schedule information.

        Example:
            >>> schedules = client.schedules.list_coworker_schedules(
            ...     coworker_id="68067c49c517ff5238533ccf",
            ...     projectID="68dcb579121a635f13002bf7",
            ...     limit=15,
            ...     page_no=1
            ... )
        """
        params: Dict[str, Any] = {"projectID": projectID, "limit": limit, "page_no": page_no}
        if coworker_id:
            params["coworker_id"] = coworker_id
        if status is not None:
            params["status"] = status
        if type is not None:
            params["type"] = type
        if search_key is not None:
            params["search_key"] = search_key
        return self.http.request("GET", "/schedules/coworker", params=params)

    def create_coworker_schedule(self, *, projectID: str, body: CoworkerScheduleCreateBody):
        """
        Create coworker schedule.
        POST /schedule/coworker?projectID=...

        Schedule an AI Coworker Task.

        Use this endpoint to schedule a specific task for an AI Coworker in your Wexa.ai environment. 
        Scheduling tasks allows you to automate actions at precise times, ensuring timely execution 
        of workflows and enhancing operational efficiency.

        Args:
            projectID: The unique identifier of the project (required)
            body: Schedule creation body containing:
                - coworker_id: The unique identifier of the coworker (required)
                - goal: The goal/objective for the scheduled task (required)
                - template: The template for the task (required)
                - display_template: The display template (required)
                - schedule: The schedule configuration (required)

        Returns:
            Created schedule object containing metadata about the scheduled task.

        Example:
            >>> schedule_body = {
            ...     "coworker_id": "6901c586eedc9fe81f0105ee",
            ...     "goal": {"action": "process_data"},
            ...     "template": "template_string",
            ...     "display_template": "display_template_string",
            ...     "schedule": 3600
            ... }
            >>> schedule = client.schedules.create_coworker_schedule(
            ...     projectID="68dcb579121a635f13002bf7",
            ...     body=schedule_body
            ... )
        """
        params = {"projectID": projectID}
        return self.http.request("POST", "/schedule/coworker", params=params, json=body)

    def get_coworker_schedule(self, id: str):
        """
        Get schedule coworker by its id.
        GET /schedule/coworker/{id}

        Retrieve Scheduled Task for a Specific AI Coworker.

        Use this endpoint to retrieve the scheduled task details for a specific AI Coworker 
        identified by its unique schedule_id. This allows you to view the planned execution times, 
        goals, and configurations associated with the coworker's scheduled tasks.

        Args:
            id: The unique identifier of the schedule (required)

        Returns:
            Scheduled task details including planned execution times, goals, and configurations.

        Example:
            >>> schedule = client.schedules.get_coworker_schedule(id="schedule-id-123")
        """
        return self.http.request("GET", f"/schedule/coworker/{id}")

    def update_coworker_schedule(self, id: str, *, projectID: str, body: CoworkerScheduleUpdateBody):
        """
        Update schedule by its id.
        PATCH /schedule/coworker/{id}?projectID=...

        Update a Scheduled Task for an AI Coworker.

        Use this endpoint to update the details of a scheduled task for a specific AI Coworker 
        identified by its unique id. This allows you to modify the execution time, goal, or other 
        configurations associated with the coworker's scheduled task.

        Args:
            id: The unique identifier of the schedule (required)
            projectID: The unique identifier of the project (required)
            body: Schedule update body containing:
                - goal: The goal/objective for the scheduled task (optional)
                - template: The template for the task (optional)
                - display_template: The display template (optional)
                - schedule: The schedule configuration (optional)

        Returns:
            Updated schedule object containing metadata about the scheduled task.

        Example:
            >>> update_body = {
            ...     "goal": {"action": "updated_process_data"},
            ...     "template": "updated_template_string",
            ...     "display_template": "updated_display_template_string",
            ...     "schedule": 7200
            ... }
            >>> schedule = client.schedules.update_coworker_schedule(
            ...     id="schedule-id-123",
            ...     projectID="68dcb579121a635f13002bf7",
            ...     body=update_body
            ... )
        """
        params = {"projectID": projectID}
        return self.http.request("PATCH", f"/schedule/coworker/{id}", params=params, json=body)

    def delete_coworker_schedule(self, id: str, *, projectID: str):
        """
        Delete schedule by its id.
        DELETE /schedule/coworker/{id}?projectID=...

        Delete a Scheduled Task for an AI Coworker.

        Use this endpoint to delete a scheduled task associated with a specific AI Coworker by its 
        unique id. This operation removes the scheduled task from the system, preventing it from 
        executing in the future.

        Args:
            id: The unique identifier of the schedule (required)
            projectID: The unique identifier of the project (required)

        Returns:
            Deletion confirmation or status indicating the scheduled task has been removed.

        Example:
            >>> client.schedules.delete_coworker_schedule(
            ...     id="schedule-id-123",
            ...     projectID="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"projectID": projectID}
        return self.http.request("DELETE", f"/schedule/coworker/{id}", params=params)


