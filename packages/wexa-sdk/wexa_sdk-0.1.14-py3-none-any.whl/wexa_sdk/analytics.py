from __future__ import annotations
from typing import Any

from .core.http import HttpClient

class Analytics:
    def __init__(self, http: HttpClient):
        self.http = http

    def get(self, project_id: str) -> Any:
        """
        Get analytics.
        GET /analytics?projectID=...

        Retrieve Analytics Overview.

        Use this endpoint to access a comprehensive summary of your organization's usage 
        statistics within the Wexa.ai platform. It provides key metrics that help you monitor 
        and optimize your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Analytics overview object containing comprehensive summary of usage statistics 
            including key metrics, workflow performance data, and other relevant analytics 
            information.

        Example:
            >>> analytics = client.analytics.get(project_id="67fdea40aac77be632954f13")
        """
        return self.http.request("GET", "/analytics", params={"projectID": project_id})
