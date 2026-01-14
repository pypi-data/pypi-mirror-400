from __future__ import annotations
import time
from typing import Any, Callable, Optional

from .core.http import HttpClient

DEFAULT_TERMINAL = {"completed", "failed", "canceled"}

class Executions:
    def __init__(self, http: HttpClient, polling: Optional[dict] = None):
        self.http = http
        self.polling = polling or {}

    def start(self, payload: dict, *, projectID: Optional[str] = None):
        """
        Create executeflow.
        POST /execute_flow?projectID=...

        Execute AgentFlow.

        Initiate the execution of a specified AgentFlow by providing its unique agentflow_id 
        along with relevant execution parameters. This endpoint triggers the defined sequence 
        of AI agents (Coworkers) within the AgentFlow to perform their tasks based on the 
        provided goal and input variables. It's essential for automating workflows and ensuring 
        that the AI agents operate in alignment with your organization's objectives.

        Args:
            payload: Execution payload containing:
                - agentflow_id (str): The unique identifier of the AgentFlow to execute (required)
                - executed_by (str): The unique identifier of the user executing the flow (required)
                - goal (str): The goal or objective for the execution (required)
                - input_variables (dict): Input variables for the execution (required)
                - projectID (str): The unique identifier of the project (required)
            projectID: The unique identifier of the project (optional, can be provided in payload)

        Returns:
            Execution object containing metadata about the initiated execution including 
            execution_id, status, and other execution details.

        Example:
            >>> execution_payload = {
            ...     "agentflow_id": "6901c5852a1fb6a6073b49e5",
            ...     "executed_by": "68dbdfb92797c909223ea38e",
            ...     "goal": "Create content for social media",
            ...     "input_variables": {"topic": "AI", "platform": "LinkedIn"},
            ...     "projectID": "68dcb579121a635f13002bf7"
            ... }
            >>> execution = client.executions.start(
            ...     payload=execution_payload,
            ...     projectID="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"projectID": projectID} if projectID else None
        return self.http.request("POST", "/execute_flow", json=payload, params=params)

    def list(self, project_id: str):
        """
        Get executions.
        GET /{projectID}/execution_flows?projectID=...

        Get All Execution Flows by Project ID.

        Retrieve a comprehensive list of all execution flows associated with a specific project 
        by providing the unique projectID. This endpoint enables you to monitor and manage the 
        execution history of AgentFlows within the specified project, offering insights into past 
        executions, their statuses, and other relevant details. It's essential for auditing, 
        tracking progress, and optimizing your AI-driven workflows.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            List of execution flows associated with the project, containing detailed information 
            on each execution including status, execution history, and other relevant details.

        Example:
            >>> executions = client.executions.list(project_id="68dcb579121a635f13002bf7")
        """
        params = {"projectID": project_id}
        return self.http.request("GET", f"/{project_id}/execution_flows", params=params)

    def get(self, execution_id: str):
        """
        Execution details.
        GET /execute_flow/{execution_id}

        Execution details.

        This API returns the status of an agentflow execution, including whether it completed 
        successfully or failed. It provides any error messages, debug information (e.g., HTTP 
        status codes), and conclusion details. The response may also include execution metadata 
        such as tokens used, execution time, and summaries.

        Args:
            execution_id: The unique identifier of the execution (required)

        Returns:
            Execution details object containing:
            - Status of the agentflow execution (completed, failed, etc.)
            - Error messages (if any)
            - Debug information (e.g., HTTP status codes)
            - Conclusion details
            - Execution metadata (tokens used, execution time, summaries)
            - Other relevant execution information

        Example:
            >>> execution = client.executions.get(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc"
            ... )
        """
        return self.http.request("GET", f"/execute_flow/{execution_id}")

    def monitor(self, agentflow_id: str):
        """
        Get execution details for monitoring.
        GET /execute_flow/{agentflow_id}/monitor

        Monitor Execution Flow by AgentFlow ID.

        Retrieve real-time monitoring data for a specific execution flow by providing the 
        unique agentflow_id. This endpoint allows you to track the current status, progress, 
        and performance metrics of the execution flow, enabling proactive management and 
        timely interventions in your automated workflows.

        Args:
            agentflow_id: The unique identifier of the AgentFlow (required)

        Returns:
            Monitoring data object containing real-time information about the execution flow 
            including current status, progress, and performance metrics.

        Example:
            >>> monitoring_data = client.executions.monitor(
            ...     agentflow_id="67fdea9b68df1c3e9580a549"
            ... )
        """
        return self.http.request("GET", f"/execute_flow/{agentflow_id}/monitor")

    def pause(self, execution_id: str):
        """
        Pause executeflow.
        POST /execute_flow/{execution_id}/pause

        Pause Execution Flow.

        Temporarily pause an ongoing execution flow by providing its unique execution_id. 
        This endpoint allows you to halt the execution of an AgentFlow, enabling intervention 
        for review, adjustments, or other necessary actions before resuming. Pausing an 
        execution ensures that workflows can be managed with greater control and flexibility, 
        aligning with dynamic operational requirements.

        Args:
            execution_id: The unique identifier of the execution (required)

        Returns:
            Execution object containing metadata about the paused execution including 
            execution_id, status, and other execution details.

        Example:
            >>> execution = client.executions.pause(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc"
            ... )
        """
        return self.http.request("POST", f"/execute_flow/{execution_id}/pause")

    def resume(self, execution_id: str):
        """
        Resume execution.
        POST /execute_flow/{execution_id}/resume

        Resume Execution Flow.

        Resume a previously paused execution flow by providing its unique execution_id. 
        This endpoint allows you to continue the execution of an AgentFlow from the point 
        it was paused, ensuring seamless workflow management and minimizing disruptions 
        in automated processes.

        Args:
            execution_id: The unique identifier of the execution (required)

        Returns:
            Execution object containing metadata about the resumed execution including 
            execution_id, status, and other execution details.

        Example:
            >>> execution = client.executions.resume(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc"
            ... )
        """
        return self.http.request("POST", f"/execute_flow/{execution_id}/resume")

    def cancel(self, execution_id: str):
        """
        Cancel executeflow.
        POST /execute_flow/{execution_id}/cancel

        Cancel Execution Flow.

        Terminate an ongoing execution flow by providing its unique execution_id. 
        This endpoint allows you to halt the execution of an AgentFlow that is 
        currently in progress, ensuring that workflows can be stopped promptly in 
        response to changing requirements or unforeseen issues. Once canceled, 
        the execution cannot be resumed and must be restarted if needed.

        Args:
            execution_id: The unique identifier of the execution (required)

        Returns:
            Execution object containing metadata about the canceled execution including 
            execution_id, status, and other execution details.

        Example:
            >>> execution = client.executions.cancel(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc"
            ... )
        """
        return self.http.request("POST", f"/execute_flow/{execution_id}/cancel")

    def execute(self, execution_id: str, *, projectID: str, body: Optional[dict] = None):
        """
        Execute agentflow.
        POST /execute_flow/{execution_id}/execute?projectID=...

        Execute AgentFlow by Execution ID.

        Initiate the execution of a specific AgentFlow by providing its unique execution_id. 
        This endpoint triggers the defined sequence of AI agents (Coworkers) within the 
        AgentFlow to perform their tasks based on the provided goal and input variables. 
        It's essential for automating workflows and ensuring that the AI agents operate in 
        alignment with your organization's objectives.

        Args:
            execution_id: The unique identifier of the execution (required)
            projectID: The unique identifier of the project (required)
            body: Optional execution body containing:
                - projectID (str): The unique identifier of the project (required)
                - execution_id (str): The unique identifier of the execution (required)
                If not provided, will be constructed from parameters.

        Returns:
            Execution object containing metadata about the executed AgentFlow including 
            execution_id, status, and other execution details.

        Example:
            >>> execution_body = {
            ...     "projectID": "68dcb579121a635f13002bf7",
            ...     "execution_id": "8ffc2a03-5d38-4321-aae8-c9f32d7707fc"
            ... }
            >>> execution = client.executions.execute(
            ...     execution_id="8ffc2a03-5d38-4321-aae8-c9f32d7707fc",
            ...     projectID="68dcb579121a635f13002bf7",
            ...     body=execution_body
            ... )
        """
        params = {"projectID": projectID}
        json_body = {"execution_id": execution_id, "projectID": projectID}
        if body:
            json_body.update(body)
        return self.http.request("POST", f"/execute_flow/{execution_id}/execute", params=params, json=json_body)

    # Removed wait/approve/update-runtime endpoints per request
