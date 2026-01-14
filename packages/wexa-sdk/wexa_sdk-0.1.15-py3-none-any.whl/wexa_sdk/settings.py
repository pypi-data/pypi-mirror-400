from __future__ import annotations

from .core.http import HttpClient

class Settings:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /settings/{projectID}
    def get(self, project_id: str):
        """
        Get settings.
        GET /settings/{projectID}

        Retrieve Project Settings.

        Use this endpoint to retrieve the configuration settings for a specific project within 
        your Wexa.ai environment. Accessing project settings allows you to view and manage various 
        parameters that govern the behavior and integration of your AI Coworkers, connectors, and 
        workflows.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Project settings object containing configuration parameters including AI Coworker 
            settings, connector configurations, workflow parameters, and other relevant project 
            settings.

        Example:
            >>> settings = client.settings.get(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("GET", f"/settings/{project_id}")
