from __future__ import annotations
from .core.http import HttpClient


class Tags:
    def __init__(self, http: HttpClient):
        self.http = http

    def get_by_project_id(self, project_id: str):
        """
        Get tags by project ID.
        GET /tagsbyprojectId/{projectID}

        Retrieve Tags by Project ID.

        Use this endpoint to retrieve all tags associated with a specific project in your Wexa.ai 
        environment. Tags serve as unique identifiers for various entities within the project, such 
        as files, connectors, or actions, enabling efficient categorization, search, and management.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            List of tags associated with the project, containing metadata about tags used for 
            categorization, search, and management of project entities.

        Example:
            >>> tags = client.tags.get_by_project_id(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("GET", f"/tagsbyprojectId/{project_id}")


