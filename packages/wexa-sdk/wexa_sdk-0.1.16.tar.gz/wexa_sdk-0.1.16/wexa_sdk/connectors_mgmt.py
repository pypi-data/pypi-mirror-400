from __future__ import annotations
from typing import Any, Optional, Dict

from .core.http import HttpClient

class ConnectorsMgmt:
    def __init__(self, http: HttpClient):
        self.http = http

    # GET /connectors/?projectID=...
    def list(self, project_id: Optional[str] = None) -> Any:
        params = {"projectID": project_id} if project_id else None
        return self.http.request("GET", "/connectors/", params=params)

    # GET /connectors/{projectID}
    def list_by_project_id(self, project_id: str) -> Any:
        """
        Get connectors by project ID.
        GET /connectors/{projectID}

        Get All Connectors by Project ID.

        Retrieve a comprehensive list of all connectors associated with a specific project by 
        providing the unique projectID. This endpoint allows you to access information about the 
        connectors available within the project, facilitating the integration of external systems 
        and services into your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            List of connectors associated with the project, containing information about the 
            connectors available within the project.

        Example:
            >>> connectors = client.connectors_mgmt.list_by_project_id(
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        return self.http.request("GET", f"/connectors/{project_id}")

    # GET /v1/connector/{id}
    def get_by_id(self, connector_id: str) -> Any:
        return self.http.request("GET", f"/v1/connector/{connector_id}")

    # GET /connector/{connector_id}
    def get_by_id_path(self, connector_id: str) -> Any:
        """
        Get connector by ID.
        GET /connector/{connector_id}

        Get Connector by ID.

        Retrieve detailed information about a specific connector by providing its unique 
        connector_id. This endpoint allows you to access metadata such as the connector's 
        name, description, status, and configuration details. It's essential for managing 
        and monitoring the connectors integrated into your automation workflows.

        Args:
            connector_id: The unique identifier of the connector (required)

        Returns:
            Connector object containing detailed information including connector name, 
            description, status, and configuration details.

        Example:
            >>> connector = client.connectors_mgmt.get_by_id_path(
            ...     connector_id="connector-id-123"
            ... )
        """
        return self.http.request("GET", f"/connector/{connector_id}")

    # DELETE /v1/connector/{id}?projectID=...
    def delete(self, connector_id: str, *, project_id: Optional[str] = None) -> Any:
        params = {"projectID": project_id} if project_id else None
        return self.http.request("DELETE", f"/v1/connector/{connector_id}", params=params)

    # DELETE /connector/{connector_id}?projectID=...
    def delete_by_id_path(self, connector_id: str, *, project_id: str) -> Any:
        """
        Delete a connector.
        DELETE /connector/{connector_id}?projectID=...

        Delete Connector by ID.

        Permanently remove a specific connector from your organization by providing its unique 
        connector_id. This endpoint allows you to delete a connector, including all associated 
        resources and configurations. It's essential to exercise caution when using this endpoint, 
        as the deletion is irreversible and all data related to the connector will be lost.

        Args:
            connector_id: The unique identifier of the connector (required)
            project_id: The unique identifier of the project (required)

        Returns:
            Deletion confirmation or status indicating the connector has been removed.

        Example:
            >>> client.connectors_mgmt.delete_by_id_path(
            ...     connector_id="connector-id-123",
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        return self.http.request("DELETE", f"/connector/{connector_id}", params={"projectID": project_id})

    # POST /connectors/change_status
    def update_status(self, *, new_status: str, connectorID: str, data_loader_config: dict) -> Any:
        """
        Connector update status.
        POST /connectors/change_status

        Update Connector Status.

        Update the operational status and configuration settings of a specific connector by 
        providing its unique connector_id. This endpoint allows you to modify the connector's 
        status (e.g., pending, active, inactive) and adjust its configuration parameters, such 
        as data source details and authentication credentials.

        Args:
            new_status: The new status for the connector (e.g., "pending", "active", "inactive") (required)
            connectorID: The unique identifier of the connector (required)
            data_loader_config: Configuration object containing:
                - source: The data source (string, required)
                - batch_size: The batch size for data loading (integer, required)
                - auth: Authentication object (object, required)

        Returns:
            Updated connector object containing the new status and configuration details.

        Example:
            >>> data_loader_config = {
            ...     "source": "api",
            ...     "batch_size": 100,
            ...     "auth": {
            ...         "api_key": "your-api-key"
            ...     }
            ... }
            >>> connector = client.connectors_mgmt.update_status(
            ...     new_status="active",
            ...     connectorID="connector-id-123",
            ...     data_loader_config=data_loader_config
            ... )
        """
        body = {"new_status": new_status, "connectorID": connectorID, "data_loader_config": data_loader_config}
        return self.http.request("POST", "/connectors/change_status", json=body)

    # GET /connectors/trigger_actions?projectID=...
    def list_trigger_actions(self, project_id: str) -> Any:
        return self.http.request("GET", "/connectors/trigger_actions", params={"projectID": project_id})

    # GET /connectors/{projectID}/trigger_actions
    def list_trigger_actions_by_project(self, project_id: str) -> Any:
        """
        Get all available trigger actions.
        GET /connectors/{projectID}/trigger_actions?projectID=...

        Get All Trigger Actions by Project ID.

        Retrieve a comprehensive list of all trigger actions associated with a specific project 
        by providing its unique projectID. This endpoint allows you to access information about 
        the trigger actions configured within the project, facilitating the automation of workflows 
        based on specific events or conditions.

        Args:
            project_id: The unique identifier of the project (required, used in both path and query)

        Returns:
            List of trigger actions associated with the project, containing information about 
            the trigger actions configured within the project.

        Example:
            >>> trigger_actions = client.connectors_mgmt.list_trigger_actions_by_project(
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        return self.http.request("GET", f"/connectors/{project_id}/trigger_actions", params={"projectID": project_id})

    def get_config(self, category: str, project_id: str, *, project_id_query: Optional[str] = None) -> Any:
        """
        Get config.
        GET /actions/{CATEGORY}/config/{projectID}?projectID=...

        Get config.

        Get the configuration details for a specific connector category within a project.

        Args:
            category: The category of the connector/action (e.g., "content_creator", "whatsapp", 
                     "linkedin", "mail", "restful") (required)
            project_id: The unique identifier of the project (required, used in path)
            project_id_query: Optional project ID to use as query parameter (optional)

        Returns:
            Configuration details for the specified connector category.

        Example:
            >>> config = client.connectors_mgmt.get_config(
            ...     category="content_creator",
            ...     project_id="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"projectID": project_id_query} if project_id_query else None
        return self.http.request("GET", f"/actions/{category}/config/{project_id}", params=params)

    def configure_connector(self, category: str, *, project_id: str, body: Optional[Dict[str, Any]] = None) -> Any:
        """
        Configure connector.
        POST /actions/{CATEGORY}/config?projectID=...

        Configure connector.

        Creates a new connector configuration for the given category. This is used to configure 
        action/connectors (e.g., content_creator, whatsapp, linkedin, mail, restful, etc.) 
        under a project.

        Args:
            category: The category of the connector/action (e.g., "content_creator", "whatsapp", 
                     "linkedin", "mail", "restful") (required)
            project_id: The unique identifier of the project (required)
            body: Optional configuration body containing connector-specific settings (optional)

        Returns:
            Created connector configuration object containing metadata about the configured connector.

        Example:
            >>> config_body = {
            ...     "setting1": "value1",
            ...     "setting2": "value2"
            ... }
            >>> connector = client.connectors_mgmt.configure_connector(
            ...     category="content_creator",
            ...     project_id="68dcb579121a635f13002bf7",
            ...     body=config_body
            ... )
        """
        params = {"projectID": project_id}
        return self.http.request("POST", f"/actions/{category}/config", params=params, json=body)

    def retrieve_linkedin_params(
        self,
        project_id: str,
        *,
        search_type: Optional[str] = None,
        keyword: Optional[str] = None,
        limit: Optional[int] = None,
        connector_id: Optional[str] = None
    ) -> Any:
        """
        Retrieve LinkedIn params.
        GET /connectors/{projectID}/retrieve/linkedin_params

        Retrieve linkedin params.

        Retrieves LinkedIn search parameter suggestions for a project from Unipile based on a 
        required uppercase search type (e.g., PEOPLE, COMPANY), with optional keyword filtering 
        and result limit; optionally accepts a specific LinkedIn connector_id to use that 
        connector's account_id, otherwise uses the first configured LinkedIn connector in the project.

        Args:
            project_id: The unique identifier of the project (required)
            search_type: The uppercase search type (e.g., "PEOPLE", "COMPANY") (optional)
            keyword: Optional keyword for filtering results (optional)
            limit: Optional limit on the number of results to return (optional)
            connector_id: Optional specific LinkedIn connector ID to use (optional)

        Returns:
            LinkedIn search parameter suggestions based on the provided criteria.

        Example:
            >>> params = client.connectors_mgmt.retrieve_linkedin_params(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     search_type="PEOPLE",
            ...     keyword="software engineer",
            ...     limit=10
            ... )
        """
        params: Dict[str, Any] = {}
        if search_type is not None:
            params["search_type"] = search_type
        if keyword is not None:
            params["keyword"] = keyword
        if limit is not None:
            params["limit"] = limit
        if connector_id is not None:
            params["connector_id"] = connector_id
        
        return self.http.request("GET", f"/connectors/{project_id}/retrieve/linkedin_params", params=params if params else None)
