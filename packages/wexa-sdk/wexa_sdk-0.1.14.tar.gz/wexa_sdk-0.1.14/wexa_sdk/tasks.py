from __future__ import annotations
from typing import Any, Dict, Optional

from .core.http import HttpClient

class Tasks:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /tasks/?projectID=...&limit=...&skip=...&created_by=...
    def list(self, project_id: str, *, limit: Optional[int] = None, skip: Optional[int] = None, created_by: Optional[str] = None):
        """
        Get tasks by project ID.
        GET /tasks/{projectID}?limit=...&skip=...&created_by=...

        Retrieve All Tasks by Project ID.

        Use this endpoint to retrieve a list of all tasks associated with a specific project 
        in your Wexa.ai environment. This functionality allows you to access metadata such as 
        task names, statuses, due dates, and assigned agents, facilitating the management and 
        monitoring of tasks within your project.

        Args:
            project_id: The unique identifier of the project (required)
            limit: Optional limit on the number of tasks to return
            skip: Optional number of tasks to skip (for pagination)
            created_by: Optional filter by user ID who created the task

        Returns:
            List of tasks associated with the project, containing metadata like task names, 
            statuses, due dates, and assigned agents.

        Example:
            >>> tasks = client.tasks.list(project_id="68dcb579121a635f13002bf7", limit=50)
        """
        api_url = f"/tasks/{project_id}"
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if skip is not None:
            params["skip"] = skip
        if created_by:
            params["created_by"] = created_by
        return self.http.request("GET", api_url, params=params)

    # GET /task/{id}?projectID=...
    def get(self, task_id: str, project_id: Optional[str] = None):
        """
        Get task by ID.
        GET /task/{id}?projectID=...

        Retrieve Task by ID.

        Use this endpoint to retrieve detailed information about a specific task within your 
        Wexa.ai environment by providing its unique task_id. This functionality allows you to 
        access metadata such as the task's name, description, status, due date, assigned agents, 
        and associated connectors, facilitating the management and monitoring of tasks within 
        your project.

        Args:
            task_id: The unique identifier of the task (required)
            project_id: Optional project ID for additional context

        Returns:
            Task object containing detailed information including task name, description, 
            status, due date, assigned agents, and associated connectors.

        Example:
            >>> task = client.tasks.get(task_id="task-id-123", project_id="68dcb579121a635f13002bf7")
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/task/{task_id}", params=params)

    # POST /task/{id}/pause
    def pause(self, task_id: str):
        """
        Pause running task.
        POST /task/{id}/pause

        Pause a Specific Task.

        Use this endpoint to pause a specific task within your Wexa.ai environment by 
        providing its unique task_id. Pausing a task halts its current execution, 
        allowing you to temporarily suspend its operations without losing its state 
        or progress.

        Args:
            task_id: The unique identifier of the task (required)

        Returns:
            Task object containing metadata about the paused task including task_id, 
            status, and other relevant details.

        Example:
            >>> task = client.tasks.pause(task_id="task-id-123")
        """
        return self.http.request("POST", f"/task/{task_id}/pause")

    # POST /task/{id}/resume
    def resume(self, task_id: str):
        """
        Resume task.
        POST /task/{id}/resume

        Resume a Specific Task.

        Use this endpoint to resume a specific task within your Wexa.ai environment by 
        providing its unique task_id. Resuming a task reactivates its execution, 
        allowing it to continue from where it was paused.

        Args:
            task_id: The unique identifier of the task (required)

        Returns:
            Task object containing metadata about the resumed task including task_id, 
            status, and other relevant details.

        Example:
            >>> task = client.tasks.resume(task_id="task-id-123")
        """
        return self.http.request("POST", f"/task/{task_id}/resume")

    # POST /task/{id}/stop
    def stop(self, task_id: str):
        """
        Stop task.
        POST /task/{id}/stop

        Stop a Specific Task.

        Use this endpoint to stop a specific task within your Wexa.ai environment by 
        providing its unique task_id. Stopping a task halts its current execution, 
        allowing you to terminate operations that are no longer needed or are causing issues.

        Args:
            task_id: The unique identifier of the task (required)

        Returns:
            Task object containing metadata about the stopped task including task_id, 
            status, and other relevant details.

        Example:
            >>> task = client.tasks.stop(task_id="task-id-123")
        """
        return self.http.request("POST", f"/task/{task_id}/stop")
