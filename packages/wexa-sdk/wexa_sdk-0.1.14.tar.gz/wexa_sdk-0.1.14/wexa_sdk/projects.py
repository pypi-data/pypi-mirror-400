from __future__ import annotations
from typing import Optional, Dict, Any, TypedDict
from urllib.parse import quote

from .core.http import HttpClient


class ProjectCreateBody(TypedDict, total=False):
    """Body for creating a project.

    Required fields:
      - orgId: str
      - projectName: str

    Optional fields:
      - description: str
      - coworker_role: str
      - status: str (e.g., "published")
    """
    orgId: str
    projectName: str
    description: str
    coworker_role: str
    status: str

class Projects:
    def __init__(self, http: HttpClient):
        self.http = http

    # Per developers.wexa.ai: POST https://api.wexa.ai/v1/project
    def create(self, body: ProjectCreateBody):
        """
        Create project.
        POST /v1/project

        Create a New Project.

        Create a new project within your organization by providing essential details such as the 
        organization ID (orgId), project name (projectName), description (description), and the 
        role of the AI coworker (coworker_role). This endpoint allows you to establish a structured 
        environment for your AI workflows, facilitating better organization, management, and execution 
        of tasks within your automation processes.

        Args:
            body: Project creation body containing:
                - orgId: The unique identifier of the organization (string, required)
                - projectName: The name of the project (string, required)
                - description: The description of the project (string, required)
                - coworker_role: The role of the AI coworker (string, required)
                - status: Optional project status (e.g., "published") (string, optional)

        Returns:
            Created project object containing metadata about the new project including _id, 
            projectName, description, orgId, coworkerRole, status, createdAt, etc.

        Example:
            >>> project_body = {
            ...     "orgId": "68dbdfb92797c909223ea38f",
            ...     "projectName": "My New Project",
            ...     "description": "Project description",
            ...     "coworker_role": "Assistant",
            ...     "status": "published"
            ... }
            >>> project = client.projects.create(body=project_body)
        """
        return self.http.request("POST", "/v1/project", json=body)

    def create_simple(
        self,
        *,
        orgId: str,
        projectName: str,
        description: Optional[str] = None,
        coworker_role: Optional[str] = None,
        status: Optional[str] = None,
    ):
        """Convenience wrapper: builds the body and calls create(body)."""
        body: Dict[str, Any] = {"orgId": orgId, "projectName": projectName}
        if description is not None:
            body["description"] = description
        if coworker_role is not None:
            body["coworker_role"] = coworker_role
        if status is not None:
            body["status"] = status
        return self.create(body)  # type: ignore[arg-type]


    def list_all(self, user_id: str):
        """
        Get all projects for a given user (organization-wide).
        GET /v1/project/all?userId=...

        Headers:
          - x-api-key: string (required)

        Query params:
          - userId: string (required)
        """
        params = {"userId": user_id}
        return self.http.request("GET", "/v1/project/all", params=params)

    def get_all(
        self,
        *,
        status: Optional[str] = None,
        user_id: Optional[str] = None,
        org_id: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
    ):
        """
        Get all projects.
        GET /v1/project?status=...&userId=...&orgId=...&page=...&limit=...

        Get All Projects.

        Retrieve a comprehensive list of all projects within your organization. This endpoint 
        provides an overview of the projects, including their names, descriptions, and associated 
        roles. It's essential for managing and navigating through multiple projects, ensuring 
        efficient organization and access to various automation workflows.

        Args:
            status: Optional project status filter (e.g., "published") (optional)
            user_id: Optional user ID filter (optional)
            org_id: Optional organization ID filter (optional)
            page: Optional page number for pagination (int) (optional)
            limit: Optional limit on the number of results to return (int) (optional)

        Returns:
            List of projects within the organization, containing information about project names, 
            descriptions, and associated roles.

        Example:
            >>> projects = client.projects.get_all(
            ...     status="published",
            ...     user_id="68dbdfb92797c909223ea38e",
            ...     page=1,
            ...     limit=12
            ... )
        """
        params: Dict[str, Any] = {}
        if status is not None:
            params["status"] = status
        if user_id is not None:
            params["userId"] = user_id
        if org_id is not None:
            params["orgId"] = org_id
        if page is not None:
            params["page"] = page
        if limit is not None:
            params["limit"] = limit

        return self.http.request("GET", "/v1/project", params=params)

    def get(self, project_id: str):
        """
        Get project by ID.
        GET /v1/project/{projectId}

        Retrieve detailed information about a specific project within your organization 
        by providing its unique projectID. This endpoint returns comprehensive metadata 
        about the project, including its name, description, associated organization, and 
        the role of the AI coworker within the project. It's essential for managing and 
        accessing specific projects, ensuring efficient organization and execution of tasks 
        within your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Project object containing fields like _id, projectName, description, orgId, 
            coworkerRole, status, createdAt, updatedAt, etc.

        Example:
            >>> project = client.projects.get(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("GET", f"/v1/project/{project_id}")

    class ProjectUpdateBody(TypedDict):
        orgId: str
        projectName: str
        description: str
        coworker_role: str

    def update(self, project_id: str, body: ProjectUpdateBody):
        """
        Update project.
        PUT /v1/project?projectId=...

        Update Project.

        Update the details of an existing project within your organization. This endpoint 
        allows you to modify attributes such as the project name, description, and the role 
        of the AI coworker associated with the project. It's essential for keeping project 
        information current and aligned with evolving organizational needs.

        Args:
            project_id: The unique identifier of the project (required)
            body: Project update body containing:
                - orgId: The unique identifier of the organization (string, required)
                - projectName: The name of the project (string, required)
                - description: The description of the project (string, required)
                - coworker_role: The role of the AI coworker (string, required)

        Returns:
            Updated project object containing the modified project details including 
            projectName, description, orgId, coworkerRole, etc.

        Example:
            >>> update_body = {
            ...     "orgId": "68dbdfb92797c909223ea38f",
            ...     "projectName": "Updated Project Name",
            ...     "description": "Updated description",
            ...     "coworker_role": "Updated Role"
            ... }
            >>> project = client.projects.update(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     body=update_body
            ... )
        """
        params = {"projectId": project_id}
        return self.http.request("PUT", "/v1/project", params=params, json=body)

    def delete(self, project_id: str):
        """
        Delete project.
        DELETE /v1/project/{projectId}

        Delete Project by ID.

        Permanently remove a specific project from your organization by providing its unique 
        projectID. This endpoint allows you to delete a project, including all associated 
        resources such as AgentFlows, agents, and skills. It's essential to exercise caution 
        when using this endpoint, as the deletion is irreversible and all data related to the 
        project will be lost.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Deletion confirmation or status indicating the project has been removed.

        Example:
            >>> client.projects.delete(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("DELETE", f"/v1/project/{project_id}")

    def get_by_project_name(self, project_name: str):
        """
        Get project by projectName.

        GET /project/projectName/{projectName}
        """
        safe = quote(project_name, safe="")
        return self.http.request("GET", f"/project/projectName/{safe}")
