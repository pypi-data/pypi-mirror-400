from __future__ import annotations
from typing import Any, Optional, TypedDict, List, Dict, Union

from .core.http import HttpClient

class ObjectField(TypedDict, total=False):
    """Field descriptor for object-type columns."""
    key: str
    keyType: str


class AgentflowTrigger(TypedDict, total=False):
    """Trigger configuration attached to a table or column.

    Note: exact schemas for `condition` and `filters` may evolve; we leave them open.
    """
    _id: str
    id: str
    condition: Dict[str, Any]
    name: Optional[str]
    goal: str
    agentflow_id: Optional[str]
    filters: List[Dict[str, Any]]
    schedule_time: Optional[str]
    event: str
    start_from_agent_id: Optional[str]
    trigger_type: str  # e.g. "coworker"


class Column(TypedDict, total=False):
    """Column definition for a table."""
    column_name: str
    column_type: str
    column_id: str
    array_type: Optional[str]
    default_value: Union[Any, List[Any], Dict[str, Any]]
    object_fields: List[ObjectField]
    triggers: List[AgentflowTrigger]
    enum_options: List[str]


class CreateTableInput(TypedDict, total=False):
    """Typed input for creating a table.

    Required keys: projectID, table_name
    Optional keys: columns, triggers
    """
    projectID: str
    table_name: str
    columns: List[Column]
    triggers: List[AgentflowTrigger]


class Tables:
    def __init__(self, http: HttpClient):
        self.http = http

    def create_database(self, project_id: str):
        """
        Create a new storage instance (database).
        POST /storage?projectID=...

        Create a New Storage Instance.

        Use this endpoint to create a new storage instance within your Wexa.ai environment. 
        This functionality allows you to define a dedicated storage space for your data, 
        enabling efficient management and retrieval of information by AI coworkers.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Storage instance object containing metadata about the created storage.

        Example:
            >>> storage = client.tables.create_database(project_id="68dcb579121a635f13002bf7")
        """
        params = {"projectID": project_id}
        return self.http.request("POST", "/storage", params=params)

    # Tables
    def create_table(self, project_id: str, spec: CreateTableInput):
        """
        Create table.
        POST /create/table?projectID=...

        Create a New Table.

        Use this endpoint to create a new table within your Wexa.ai environment. Tables serve 
        as structured data repositories, allowing AI coworkers to store, retrieve, and process 
        data efficiently in real time. This functionality is essential for managing datasets 
        that require organization into rows and columns, facilitating seamless integration with 
        ongoing processes and workflows.

        Args:
            project_id: The unique identifier of the project (required, placed into query as 
                     `projectID` and also included in the request body)
            spec: Table specification containing:
                - projectID (str): The unique identifier of the project (required)
                - table_name (str): The name of the table to create (required)
                - columns (List[Column], optional): List of column definitions for the table
                - triggers (List[AgentflowTrigger], optional): List of trigger configurations

        Returns:
            Created table object containing metadata about the new table including _id, 
            table_name, and other relevant details.

        Example:
            >>> table_spec = {
            ...     "projectID": "68dcb579121a635f13002bf7",
            ...     "table_name": "Users",
            ...     "columns": [
            ...         {
            ...             "column_name": "name",
            ...             "column_type": "string",
            ...             "column_id": "col-1"
            ...         }
            ...     ]
            ... }
            >>> table = client.tables.create_table(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     spec=table_spec
            ... )
        """
        # API expects projectID as query param and in body with 'projectID' casing
        params = {"projectID": project_id}
        body = {"projectID": project_id, **spec}
        return self.http.request("POST", "/create/table", params=params, json=body)

    # New: POST /storage/{projectID}/{collection_name}
    def create_records_by_collection(self, project_id: str, collection_name: str, records: List[dict]):
        return self.http.request("POST", f"/storage/{project_id}/{collection_name}", json=records)

    def list_tables(self, project_id: str):
        """
        Get tables.
        GET /storage/{projectID}

        Retrieve Tables by Project ID.

        Use this endpoint to retrieve a list of all tables associated with a specific project 
        in your Wexa.ai environment. Tables serve as structured data repositories, allowing AI 
        coworkers to store, retrieve, and process data efficiently in real time. This 
        functionality is essential for managing datasets that require organization into rows 
        and columns, facilitating seamless integration with ongoing processes and workflows.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            List of tables associated with the project, containing metadata about each table 
            including _id, table_name, and other relevant details.

        Example:
            >>> tables = client.tables.list_tables(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("GET", f"/storage/{project_id}")

    def get_table_names(self, project_id: str):
        """
        Get table names.
        GET /storage/{projectID}/names

        Retrieve Table Names by Project ID.

        Use this endpoint to retrieve a list of all table names associated with a specific 
        project in your Wexa.ai environment. This functionality allows you to access the names 
        of tables within the project, enabling efficient organization and management of your 
        data storage resources.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            List of table names associated with the project, containing the names of all 
            tables within the project.

        Example:
            >>> table_names = client.tables.get_table_names(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("GET", f"/storage/{project_id}/names")

    def get_table(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/storage/{project_id}/{table_id}")

    def get_table_view(self, table_id: str):
        return self.http.request("GET", f"/table/view/{table_id}")

    def rename_table(self, project_id: str, table_id: str, new_name: str):
        return self.http.request("POST", f"/table/rename/{project_id}", json={"tableId": table_id, "newName": new_name})

    # Columns
    def get_columns(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/column/storage/{project_id}/{table_id}")

    def edit_columns(self, table_id: str, spec: dict):
        return self.http.request("POST", f"/edit/columns/{table_id}", json=spec)

    def delete_column(self, project_id: str, column_id: str):
        """
        Delete a column.
        DELETE /delete/column/{projectID}

        Delete a Column from a Table.

        Use this endpoint to delete a specific column from a table within a given project in your 
        Wexa.ai environment. Deleting a column removes all data associated with that column across 
        all records in the table. This operation is irreversible and should be performed with caution.

        Args:
            project_id: The unique identifier of the project (required, used in path as projectID)
            column_id: The unique identifier of the column to delete (required, included in request body as columnId)

        Returns:
            Deletion confirmation response indicating that the column has been successfully 
            removed from the table.

        Example:
            >>> result = client.tables.delete_column(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     column_id="column-id-456"
            ... )
        """
        return self.http.request("DELETE", f"/delete/column/{project_id}", json={"columnId": column_id})

    # New: POST /column/storage/{projectID}/{table_id}?ignore_existing_columns=...
    def add_columns(self, project_id: str, table_id: str, columns: List[Column], ignore_existing_columns: Optional[bool] = None):
        params: Dict[str, Any] = {}
        if ignore_existing_columns is not None:
            params["ignore_existing_columns"] = ignore_existing_columns
        return self.http.request("POST", f"/column/storage/{project_id}/{table_id}", params=params or None, json=columns)

    # New: PUT /edit/columns/{projectId} with rename body
    def update_column_name(self, project_id: str, *, column_id: str, column_name: str, table_id: str):
        body = {"column_id": column_id, "column_name": column_name, "table_id": table_id}
        return self.http.request("PUT", f"/edit/columns/{project_id}", json=body)

    # New: PATCH /edit/columns/{table_id} with full Column
    def patch_column(self, table_id: str, column: Column):
        return self.http.request("PATCH", f"/edit/columns/{table_id}", json=column)

    # New: DELETE /delete/column/{projectId} body { table_id, column_id }
    def delete_column_extended(self, project_id: str, *, table_id: str, column_id: str):
        return self.http.request("DELETE", f"/delete/column/{project_id}", json={"table_id": table_id, "column_id": column_id})

    # Records
    def create_record(self, project_id: str, table_id: str, record: dict):
        """
        Insert row in a table.
        POST /storage/{projectID}/{table_id}

        Insert row in a table.

        Insert multiple records into a table (collection_name is the table_id). 
        This endpoint allows you to add new rows to a table within your Wexa.ai 
        environment, enabling data storage and management for your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            table_id: The unique identifier of the table (collection_name) (required)
            record: Record data to insert. Can be a single record (dict) or multiple 
                   records (list of dicts) (required)

        Returns:
            Created record(s) object(s) containing metadata about the inserted row(s) 
            including _id and other relevant details.

        Example:
            >>> # Insert a single record
            >>> record = {
            ...     "name": "John Doe",
            ...     "email": "john@example.com",
            ...     "age": 30
            ... }
            >>> result = client.tables.create_record(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     table_id="table-id-123",
            ...     record=record
            ... )
        """
        return self.http.request("POST", f"/storage/{project_id}/{table_id}", json=record)

    def get_record(self, project_id: str, table_id: str, record_id: str):
        """
        Get record by id.
        GET /storage/{projectID}/{table_id}/{record_id}

        Get record by id.

        Retrieve a single record using its ID. Here, table_id represents the collection name. 
        This endpoint allows you to access detailed information about a specific record 
        within a table in your Wexa.ai environment, enabling efficient data retrieval and 
        management for your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            table_id: The unique identifier of the table (collection_name) (required)
            record_id: The unique identifier of the record (required)

        Returns:
            Record object containing detailed information about the requested record 
            including _id and all other relevant fields.

        Example:
            >>> record = client.tables.get_record(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     table_id="table-id-123",
            ...     record_id="record-id-456"
            ... )
        """
        return self.http.request("GET", f"/storage/{project_id}/{table_id}/{record_id}")

    def update_record(self, project_id: str, table_id: str, record_id: str, record: dict):
        """
        Update record by id.
        PUT /storage/{projectID}/{tableId}/{record_id}

        Update record.

        Update a specific record using its ID. Here, the tableId represents the collection name, 
        and the id refers to the unique identifier of the particular row to be updated. 
        This endpoint allows you to modify existing records within a table in your Wexa.ai 
        environment, enabling efficient data management and updates for your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            table_id: The unique identifier of the table (collection_name, referred to as 
                     tableId in the path) (required)
            record_id: The unique identifier of the record (id) to be updated (required)
            record: Record data to update. Contains the fields to be modified (required)

        Returns:
            Updated record object containing metadata about the modified record including 
            _id and all updated fields.

        Example:
            >>> # Update a record
            >>> updated_data = {
            ...     "name": "Jane Doe",
            ...     "email": "jane@example.com",
            ...     "age": 31
            ... }
            >>> result = client.tables.update_record(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     table_id="table-id-123",
            ...     record_id="record-id-456",
            ...     record=updated_data
            ... )
        """
        return self.http.request("PUT", f"/storage/{project_id}/{table_id}/{record_id}", json=record)

    def delete_record(self, project_id: str, table_id: str, record_id: str):
        return self.http.request("DELETE", f"/storage/{project_id}/{table_id}/{record_id}")

    def list_records(self, project_id: str, table_id: str, query: Optional[dict] = None):
        """
        Get records.
        GET /storage/{projectID}/{table_id}?page=...&page_size=...&sort=...&sort_key=...&query=...&filters=...&search_filters=...

        Get the records in table.

        Retrieve a paginated list of records from a table. Here, table_id refers to the 
        collection name. This endpoint allows you to access and filter records within a 
        table in your Wexa.ai environment, enabling efficient data retrieval and management 
        for your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            table_id: The unique identifier of the table (collection_name) (required)
            query: Optional query parameters dictionary containing:
                - page: Page number for pagination (optional, default: 1)
                - page_size: Number of records per page (optional, default: 50)
                - sort: Sort order (required, integer: 1 for ascending)
                - sort_key: Field name to sort by (required, string)
                - query: Search query string for Atlas Search if enabled (required, string)
                - filters: JSON-encoded dictionary for filtering records (required, string)
                - search_filters: JSON-encoded array of Filter objects for advanced filtering (required, string)

        Returns:
            Paginated list of records from the table, containing metadata about each record 
            including _id and other relevant details.

        Example:
            >>> records = client.tables.list_records(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     table_id="table-id-123",
            ...     query={
            ...         "page": 1,
            ...         "page_size": 50,
            ...         "sort": 1,
            ...         "sort_key": "created_at",
            ...         "query": "search term",
            ...         "filters": '{"status": "active"}',
            ...         "search_filters": '[{"field": "name", "operator": "equals", "value": "John"}]'
            ...     }
            ... )
        """
        return self.http.request("GET", f"/storage/{project_id}/{table_id}", params=query)

    def delete_records(self, project_id: str, table_id: str, storage_ids: List[str], *, projectID: Optional[str] = None):
        """
        Delete record.
        DELETE /storage/{projectID}/{tableId}?projectID=...

        Delete one or more records (rows) from a storage table.

        Use this endpoint to delete one or more records (rows) from a storage table. Here storage 
        ids are the row_ids that can be found while you click on inspect. This endpoint allows 
        you to remove multiple records at once from a table in your Wexa.ai environment, enabling 
        efficient data management and cleanup for your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            table_id: The unique identifier of the table (collection_name, referred to as 
                     tableId in the path) (required)
            storage_ids: Array of storage IDs (row_ids) to delete. These are the row_ids that 
                        can be found while clicking on inspect (required)
            projectID: The unique identifier of the project (required as query parameter)

        Returns:
            Deletion confirmation response indicating that the specified records have been 
            successfully removed from the table.

        Example:
            >>> result = client.tables.delete_records(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     table_id="table-id-123",
            ...     storage_ids=["row-id-1", "row-id-2", "row-id-3"],
            ...     projectID="68dcb579121a635f13002bf7"
            ... )
        """
        params = {"projectID": projectID if projectID else project_id}
        body = {"storage_ids": storage_ids}
        return self.http.request("DELETE", f"/storage/{project_id}/{table_id}", params=params, json=body)

    # New: DELETE /storage/{projectID}/{tableId} body { storage_ids: [] }
    def delete_records_bulk(self, project_id: str, table_id: str, storage_ids: List[str]):
        """
        Delete record.
        DELETE /storage/{projectID}/{tableId}

        Delete one or more records (rows) from a storage table.

        Use this endpoint to delete one or more records (rows) from a storage table. Here storage 
        ids are the row_ids that can be found while you click on inspect. This endpoint allows 
        you to remove multiple records at once from a table in your Wexa.ai environment, enabling 
        efficient data management and cleanup for your automation workflows.

        Args:
            project_id: The unique identifier of the project (required)
            table_id: The unique identifier of the table (collection_name, referred to as 
                     tableId in the path) (required)
            storage_ids: Array of storage IDs (row_ids) to delete. These are the row_ids that 
                        can be found while clicking on inspect (required)

        Returns:
            Deletion confirmation response indicating that the specified records have been 
            successfully removed from the table.

        Example:
            >>> result = client.tables.delete_records_bulk(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     table_id="table-id-123",
            ...     storage_ids=["row-id-1", "row-id-2", "row-id-3"]
            ... )
        """
        return self.http.request("DELETE", f"/storage/{project_id}/{table_id}", json={"storage_ids": storage_ids})

    # New: PUT /bulk/storage/{projectID}/{table_id} body { records, record_ids: { storage_ids: [] } }
    def bulk_update_records(self, project_id: str, table_id: str, *, records: Dict[str, Any], record_ids: Dict[str, Any]):
        return self.http.request("PUT", f"/bulk/storage/{project_id}/{table_id}", json={"records": records, "record_ids": record_ids})

    def export(self, project_id: str, table_id: str):
        return self.http.request("GET", f"/table_data/storage/{table_id}/export")

    def get_dashboard(self, project_id: str):
        """
        Get dashboard.
        GET /dashboard/{projectID}

        Retrieve Dashboard Overview by Project ID.

        Use this endpoint to retrieve a comprehensive overview of your project's dashboard 
        in the Wexa.ai environment. The dashboard serves as your central hub for monitoring 
        and managing your automation workflows, providing insights into key metrics, 
        workflow executions, and easy access to all platform functionalities.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Dashboard object containing comprehensive overview including key metrics, 
            workflow executions, and other relevant dashboard information.

        Example:
            >>> dashboard = client.tables.get_dashboard(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("GET", f"/dashboard/{project_id}")

    def refresh_dashboard(self, project_id: str):
        """
        Refresh dashboard.
        POST /dashboard/refresh/{projectID}

        Refresh Project Dashboard.

        Use this endpoint to refresh the dashboard for a specific project within your 
        Wexa.ai environment. Refreshing the dashboard ensures that all metrics, 
        visualizations, and data representations are up-to-date, reflecting the latest 
        status of your automation workflows and resource utilization.

        Args:
            project_id: The unique identifier of the project (required)

        Returns:
            Dashboard refresh response containing confirmation of the refresh operation 
            and updated dashboard status.

        Example:
            >>> result = client.tables.refresh_dashboard(project_id="68dcb579121a635f13002bf7")
        """
        return self.http.request("POST", f"/dashboard/refresh/{project_id}")

    def delete_dashboard_component(self, project_id: str, component_id: str):
        """
        Delete component in dashboard.
        DELETE /dashboard/component/{projectID}/{component_id}

        Delete a Dashboard Component.

        Use this endpoint to delete a specific component from a project's dashboard in 
        your Wexa.ai environment. Deleting a component removes it from the dashboard view, 
        allowing you to customize and streamline the information displayed.

        Args:
            project_id: The unique identifier of the project (required)
            component_id: The unique identifier of the dashboard component (required)

        Returns:
            Deletion confirmation response indicating that the component has been 
            successfully removed from the dashboard.

        Example:
            >>> result = client.tables.delete_dashboard_component(
            ...     project_id="68dcb579121a635f13002bf7",
            ...     component_id="component-id-123"
            ... )
        """
        return self.http.request("DELETE", f"/dashboard/component/{project_id}/{component_id}")

    # New: PUT /table/rename/{projectID} body { table_id, table_name, triggers? }
    def rename_table_extended(self, project_id: str, *, table_id: str, table_name: str, triggers: Optional[List[AgentflowTrigger]] = None):
        body: Dict[str, Any] = {"table_id": table_id, "table_name": table_name}
        if triggers is not None:
            body["triggers"] = triggers
        return self.http.request("PUT", f"/table/rename/{project_id}", json=body)

    # New: POST /table/column_mapper
    def column_mapper(self, *, column_names: List[Dict[str, str]], csv_headers: List[str]):
        body = {"column_names": column_names, "csv_headers": csv_headers}
        return self.http.request("POST", "/table/column_mapper", json=body)

    # New: POST /table/fieldcount/{project_id}/{table_id}
    def field_count(self, project_id: str, table_id: str, filters: List[Dict[str, Any]]):
        return self.http.request("POST", f"/table/fieldcount/{project_id}/{table_id}", json=filters)
