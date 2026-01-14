from __future__ import annotations
from typing import Optional, TypedDict, Dict, Any

from .core.http import HttpClient


class SkillCreateBody(TypedDict):
    """Body for creating a Skill.

    Required (user_id can be null but key is required):
      - name: str
      - logo: str
      - connector_name: str
      - description: str
      - projectID: str
      - connector_id: str
      - user_id: Optional[str]
    """
    name: str
    logo: str
    connector_name: str
    description: str
    projectID: str
    connector_id: str
    user_id: Optional[str]


class Skills:
    def __init__(self, http: HttpClient):
        self.http = http

    # POST /skills/
    def create(self, body: SkillCreateBody):
        """
        Create skill.
        POST /skills/

        Create Skill.

        Create a new skill within your organization. In Wexa.ai, skills represent specific 
        capabilities or permissions that can be assigned to AI agents (Coworkers) to perform 
        designated tasks. This endpoint allows you to define a skill by specifying attributes 
        such as its name, description, associated connector, and other relevant metadata. 
        By creating custom skills, you can tailor the functionalities of your AI agents to 
        align with your organization's unique workflows and requirements.

        Args:
            body: Skill creation body containing:
                - name: The name of the skill (string, required)
                - logo: The logo URL or identifier for the skill (string, required)
                - connector_name: The name of the associated connector (string, required)
                - description: The description of the skill (string, required)
                - projectID: The unique identifier of the project (string, required)
                - connector_id: The unique identifier of the connector (string, required)
                - user_id: The unique identifier of the user (string or null, required)

        Returns:
            Created skill object containing metadata about the new skill including _id, 
            name, logo, connector_name, description, projectID, connector_id, etc.

        Example:
            >>> skill_body = {
            ...     "name": "Content Creator",
            ...     "logo": "https://example.com/logo.png",
            ...     "connector_name": "content_creator",
            ...     "description": "Creates content for social media",
            ...     "projectID": "68dcb579121a635f13002bf7",
            ...     "connector_id": "connector-id-123",
            ...     "user_id": "68dbdfb92797c909223ea38e"
            ... }
            >>> skill = client.skills.create(body=skill_body)
        """
        return self.http.request("POST", "/skills/", json=body)

    # GET /skills/?projectID=...&limit=...
    def list(self, project_id: str, *, limit: Optional[int] = None):
        """
        Get skills.
        GET /skills/?projectID=...&limit=...

        Get All Skills.

        Retrieve a comprehensive list of all available skills within your organization. 
        Skills in Wexa.ai are essentially API permissions that grant agents access to 
        perform specific actions within the configured connectors. This endpoint provides 
        detailed information on each skill, including its name, description, and associated 
        connectors, enabling effective management and assignment of skills to agents within 
        your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            limit: Optional limit on the number of skills to return (optional, but recommended)

        Returns:
            List of skills within the organization, containing detailed information on each 
            skill including name, description, associated connectors, and other metadata.

        Example:
            >>> skills = client.skills.list(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     limit=50
            ... )
        """
        params = {"projectID": project_id}
        if limit is not None:
            params["limit"] = limit
        return self.http.request("GET", "/skills/", params=params)

    # GET /skills/category?projectId=...&category=...&limit=...
    def list_by_category(self, project_id: str, category: str, *, limit: Optional[int] = None):
        """
        Get skills by category.
        GET /skills/category?projectId=...&category=...&limit=...

        Get Skills by Category.

        Retrieve a list of skills organized by their respective categories within your 
        organization. This endpoint allows you to filter and access skills based on their 
        categories, enabling more efficient management and assignment of skills to agents 
        within your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            category: The category of the skills to retrieve (e.g., "content_creator") (required)
            limit: Optional limit on the number of skills to return (optional, but recommended)

        Returns:
            List of skills within the specified category, containing detailed information 
            on each skill including name, description, associated connectors, and other metadata.

        Example:
            >>> skills = client.skills.list_by_category(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     category="content_creator",
            ...     limit=50
            ... )
        """
        params: Dict[str, Any] = {"projectId": project_id, "category": category}
        if limit is not None:
            params["limit"] = limit
        return self.http.request("GET", "/skills/category", params=params)

    # GET /skills/{id}
    def get_by_id(self, skill_id: str):
        """
        Get skill by ID.
        GET /skills/{skill_id}

        Get Skill by ID.

        Retrieve detailed information about a specific skill by providing its unique skill_id. 
        This endpoint returns comprehensive metadata about the skill, including its name, 
        description, associated connectors, and configuration details. It is essential for 
        understanding the capabilities and permissions granted by the skill, facilitating 
        effective assignment and management within your AI workflows.

        Args:
            skill_id: The unique identifier of the skill (required)

        Returns:
            Skill object containing detailed information including name, description, 
            associated connectors, configuration details, and other metadata.

        Example:
            >>> skill = client.skills.get_by_id(skill_id="68063653fc2e1fb8597c775f")
        """
        return self.http.request("GET", f"/skills/{skill_id}")

    # GET /skills/?name=...&projectID=...
    def get_by_name(self, name: str, project_id: str):
        """
        Get skills by name.
        GET /skills/?name=...&projectID=...

        Get Skills by Name.

        Retrieve a list of skills filtered by their names. This endpoint allows you to search 
        for specific skills within your organization by providing the skill name as a query 
        parameter, facilitating efficient management and assignment of skills to agents within 
        your automation workflows.

        Args:
            name: The name of the skill to search for (e.g., "Content creator - Content creation") (required)
            project_id: The unique identifier of the project (required)

        Returns:
            List of skills matching the provided name, containing detailed information on each 
            skill including name, description, associated connectors, and other metadata.

        Example:
            >>> skills = client.skills.get_by_name(
            ...     name="Content creator - Content creation",
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"name": name, "projectID": project_id}
        return self.http.request("GET", "/skills/", params=params)
