from __future__ import annotations
from typing import Any, Dict, Optional, TypedDict, Literal

from .core.http import HttpClient

class Inbox:
    def __init__(self, http: HttpClient):
        self.http = http

    class InboxCreateBody(TypedDict, total=False):
        _id: str
        type: str
        status: str
        created_at: float
        updated_at: float
        agent_id: str
        coworker_id: str
        coworker_name: str
        agent_title: str
        summary: str
        execution_id: str
        projectID: str
        # Allow extra fields if backend accepts more
        Name: str
        Description: str

    def create(self, body: InboxCreateBody):
        """
        Create inbox.
        POST /inbox/create

        Create inbox.

        Creates a new inbox request entry (preview, runtime_input, or anomaly_detection). 
        This endpoint allows you to create inbox entries for various types of requests 
        within your Wexa.ai environment, enabling interaction and management of execution 
        flows through the inbox system.

        Args:
            body: Inbox creation body containing the request data. The body should contain 
                  information relevant to the type of inbox entry being created (preview, 
                  runtime_input, or anomaly_detection), including fields like _id, type, 
                  status, agent_id, coworker_id, execution_id, projectID, etc.

        Returns:
            Created inbox object containing metadata about the new inbox entry including 
            _id, type, status, and other relevant details.

        Example:
            >>> inbox_body = {
            ...     "_id": "inbox_123",
            ...     "type": "preview",
            ...     "status": "pending",
            ...     "execution_id": "8ffc2a03-5d38-4321-aae8-c9f32d7707fc",
            ...     "projectID": "68dcb579121a635f13002bf7"
            ... }
            >>> inbox = client.inbox.create(body=inbox_body)
        """
        return self.http.request("POST", "/inbox/create", json=body)

    def list(
        self,
        project_id: str,
        *,
        limit: Optional[int] = 100,
        status: Optional[str] = None,
        type: Optional[str] = None,
        search_key: Optional[str] = None,
        after_id: Optional[str] = None,
        view: Literal["ui", "studio"] = "ui",
    ):
        """
        Get inbox.
        GET /inbox?projectID=...&limit=...&status=...&type=...&search_key=...&after_id=...&view=...

        Retrieve Inbox for Approval Requests.

        Use this endpoint to access the inbox containing all pending, approved, and 
        completed approval requests within your Wexa.ai environment. This centralized 
        platform streamlines coworker approval processes, providing a comprehensive 
        overview of requests to enable efficient collaboration and decision-making.

        Args:
            project_id: The unique identifier of the project (required)
            limit: Optional limit on the number of inbox items to return (optional, default: 100)
            status: Optional status filter (e.g., "pending", "approved", "completed") (optional)
            type: Optional type filter (e.g., "preview", "runtime_input", "anomaly_detection") (optional)
            search_key: Optional search key for filtering inbox items (optional)
            after_id: Optional ID to fetch items after this ID (for pagination) (optional)
            view: View mode, either "ui" or "studio" (optional, default: "ui")

        Returns:
            List of inbox items containing all pending, approved, and completed approval 
            requests within the project, including metadata about each request.

        Example:
            >>> inbox_items = client.inbox.list(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     limit=50,
            ...     status="pending",
            ...     type="preview"
            ... )
        """
        params: Dict[str, Any] = {"projectID": project_id}
        if limit is not None:
            params["limit"] = limit
        if status is not None:
            params["status"] = status
        if type is not None:
            params["type"] = type
        if search_key is not None:
            params["search_key"] = search_key
        if after_id is not None:
            params["after_id"] = after_id
        if view:
            params["view"] = view
        return self.http.request("GET", "/inbox", params=params)

    class UpdateRuntimeBody(TypedDict):
        is_submitted: bool
        values: Dict[str, str]
        agent_id: str

    def update_runtime(self, execution_id: str, project_id: Optional[str], body: UpdateRuntimeBody):
        """
        Update inbox at runtime.
        POST /inbox/update/runtime_input/{execution_id}?projectID=...

        Update at runtime.

        Updates runtime input for the agent in the specified execution.

        If is_submitted is true, marks inbox item as resolved and resumes the execution.
        If is_submitted is false, saves draft values and keeps status in input_required.

        Args:
            execution_id: The unique identifier of the execution (required)
            project_id: The unique identifier of the project (optional)
            body: Update body containing:
                - is_submitted (bool): Whether the input is submitted (required)
                    - If true: marks inbox item as resolved and resumes the execution
                    - If false: saves draft values and keeps status in input_required
                - values (Dict[str, str]): Runtime input values (required)
                - agent_id (str): The unique identifier of the agent (required)

        Returns:
            Updated inbox object containing metadata about the updated runtime input 
            including status, execution details, and other relevant information.

        Example:
            >>> runtime_body = {
            ...     "is_submitted": True,
            ...     "values": {"key": "value"},
            ...     "agent_id": "agent_123"
            ... }
            >>> inbox = client.inbox.update_runtime(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc",
            ...     project_id="68dcb579121a635f13002bf7",
            ...     body=runtime_body
            ... )
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/runtime_input/{execution_id}", params=params, json=body)

    class UpdateAnomalyBody(TypedDict):
        is_approved: bool

    def update_anomaly(self, execution_id: str, project_id: Optional[str], body: UpdateAnomalyBody):
        """
        Update anomaly detection inbox.
        POST /inbox/update/anomaly_detection/{execution_id}?projectID=...

        Update Anomaly Detection Inbox.

        Approves anomaly detection for the execution and updates the execution's anomaly state.

        Args:
            execution_id: The unique identifier of the execution (required)
            project_id: The unique identifier of the project (optional)
            body: Update body containing:
                - is_approved (bool): Whether the anomaly is approved (required)

        Returns:
            Updated inbox object containing metadata about the updated anomaly detection 
            including status, execution details, and other relevant information.

        Example:
            >>> anomaly_body = {
            ...     "is_approved": True
            ... }
            >>> inbox = client.inbox.update_anomaly(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc",
            ...     project_id="68dcb579121a635f13002bf7",
            ...     body=anomaly_body
            ... )
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/anomaly_detection/{execution_id}", params=params, json=body)

    class UpdatePreviewBody(TypedDict):
        agent_id: str
        is_approved: bool
        preview_input: Dict[str, Any]

    def update_preview(self, execution_id: str, project_id: Optional[str], body: UpdatePreviewBody):
        """
        Update Preview Inbox (Approve or Draft).
        POST /inbox/update/preview/{execution_id}?projectID=...

        Update Preview Inbox.

        Updates the preview inbox for the specified execution. This endpoint allows you to 
        approve or save as draft the preview input for an agent execution.

        Args:
            execution_id: The unique identifier of the execution (required)
            project_id: The unique identifier of the project (optional)
            body: Update body containing:
                - agent_id (str): The unique identifier of the agent (required)
                - is_approved (bool): Whether the preview is approved (required)
                - preview_input (Dict[str, Any]): Preview input data (required)

        Returns:
            Updated inbox object containing metadata about the updated preview including 
            status, execution details, and other relevant information.

        Example:
            >>> preview_body = {
            ...     "agent_id": "agent_123",
            ...     "is_approved": True,
            ...     "preview_input": {"key": "value"}
            ... }
            >>> inbox = client.inbox.update_preview(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc",
            ...     project_id="68dcb579121a635f13002bf7",
            ...     body=preview_body
            ... )
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("POST", f"/inbox/update/preview/{execution_id}", params=params, json=body)

    # GET /inbox/{id}?projectID=...
    def get(self, inbox_id: str, project_id: Optional[str] = None):
        """
        Get inbox by ID.
        GET /inbox/{inbox_id}?projectID=...

        Retrieve Inbox Item by ID.

        Use this endpoint to retrieve detailed information about a specific inbox item 
        within your Wexa.ai environment by providing its unique inbox_id.

        Args:
            inbox_id: The unique identifier of the inbox item (required)
            project_id: The unique identifier of the project (optional)

        Returns:
            Inbox item object containing detailed information including type, status, 
            execution details, and other relevant metadata.

        Example:
            >>> inbox_item = client.inbox.get(
            ...     inbox_id="inbox_123",
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", f"/inbox/{inbox_id}", params=params)
