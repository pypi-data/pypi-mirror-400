"""
Triggers module for managing webhook triggers and automations.

Triggers allow you to:
- Automatically execute AgentFlows when events occur (e.g., WhatsApp message received)
- Set up webhooks for real-time event processing
- Create automated reply systems
"""

import uuid
import time
from typing import Any, Dict, List, Literal, Optional, TypedDict, Union

from wexa_sdk.core.http import HttpClient

# Type definitions
WhatsAppEvent = Literal["message_received", "message_read", "message_reaction"]
TriggerConnectorCategory = Literal["whatsapp", "mail", "linkedin", "twilio", "jira", "bland", "fal_ai"]
TriggerType = Literal["coworker", "connector"]


class TableCondition(TypedDict, total=False):
    """Table condition for conditional triggers."""
    condition_for: Literal["insert", "delete", "update"]
    condition_query: Optional[Dict[str, Any]]


class TriggerFilter(TypedDict):
    """Filter for trigger conditions."""
    field_name: str
    condition: str
    field_type: str
    value: Any


class CreateCoworkerTriggerInput(TypedDict, total=False):
    """Input for creating a coworker (AgentFlow) trigger."""
    name: str
    event: str
    agentflow_id: str
    goal: str
    start_from_agent_id: Optional[str]
    schedule_time: Optional[str]
    filters: Optional[List[TriggerFilter]]
    condition: Optional[TableCondition]


class CreateConnectorTriggerInput(TypedDict):
    """Input for creating a connector (data pull) trigger."""
    name: str
    event: str
    connector_id: str


class Trigger(TypedDict, total=False):
    """Trigger stored in database."""
    _id: str
    name: Optional[str]
    trigger_name: Optional[str]
    event: str
    trigger_type: TriggerType
    # Coworker trigger fields
    agentflow_id: Optional[str]
    goal: Optional[str]
    start_from_agent_id: Optional[str]
    schedule_time: Optional[str]
    filters: Optional[List[TriggerFilter]]
    condition: Optional[TableCondition]
    # Connector trigger fields
    connector_id: Optional[str]


class TriggerInDB(TypedDict):
    """Response from updating triggers."""
    connector_id: str
    connector_type: TriggerConnectorCategory
    triggers: List[Trigger]


class TriggerExecutionResult(TypedDict, total=False):
    """Trigger execution result."""
    status: Literal["success", "error"]
    execution: Optional[Any]
    error: Optional[str]


class Triggers:
    """
    Triggers module for managing webhook triggers and automations.
    
    Triggers allow you to:
    - Automatically execute AgentFlows when events occur (e.g., WhatsApp message received)
    - Set up webhooks for real-time event processing
    - Create automated reply systems
    """

    def __init__(self, http: HttpClient):
        self._http = http

    def list_by_connector(self, connector_id: str) -> Optional[TriggerInDB]:
        """
        List all triggers for a connector.

        Args:
            connector_id: The connector ID

        Returns:
            List of triggers attached to the connector, or None if not found
        """
        return self._http.request("GET", f"/triggers/connector/{connector_id}")

    def update(
        self,
        connector_id: str,
        category: TriggerConnectorCategory,
        triggers: List[Dict[str, Any]]
    ) -> TriggerInDB:
        """
        Create or update triggers for a connector.

        This is the main method to set up automation. When you attach a trigger:
        1. A webhook is registered with the external service (e.g., Unipile for WhatsApp)
        2. When the event occurs, the webhook is called
        3. The specified AgentFlow is executed with the event data

        Args:
            connector_id: The connector ID (e.g., your WhatsApp connector)
            category: Connector category ("whatsapp", "mail", etc.)
            triggers: Array of triggers to attach

        Returns:
            Updated trigger configuration

        Example:
            >>> # Set up auto-reply for WhatsApp messages
            >>> triggers = client.triggers.update(
            ...     "whatsapp-connector-id",
            ...     "whatsapp",
            ...     [{
            ...         "name": "Auto Reply",
            ...         "event": "message_received",
            ...         "trigger_type": "coworker",
            ...         "agentflow_id": "your-agentflow-id",
            ...         "goal": "Read the incoming WhatsApp message and generate a helpful reply"
            ...     }]
            ... )
        """
        # Ensure each trigger has an _id and trigger_type
        processed_triggers = []
        for t in triggers:
            trigger = {**t}
            if "_id" not in trigger:
                trigger["_id"] = self._generate_object_id()
            if "trigger_type" not in trigger:
                trigger["trigger_type"] = "coworker"
            if "name" in trigger:
                trigger["trigger_name"] = trigger["name"]
            processed_triggers.append(trigger)

        return self._http.request(
            "PUT",
            f"/triggers/connector/{connector_id}/{category}",
            body={"triggers": processed_triggers}
        )

    def add_coworker_trigger(
        self,
        connector_id: str,
        category: TriggerConnectorCategory,
        trigger: CreateCoworkerTriggerInput
    ) -> TriggerInDB:
        """
        Add a single coworker trigger to a connector.

        Args:
            connector_id: The connector ID
            category: Connector category
            trigger: Trigger configuration

        Returns:
            Updated trigger configuration

        Example:
            >>> # Add WhatsApp auto-reply trigger
            >>> client.triggers.add_coworker_trigger(
            ...     "whatsapp-connector-id",
            ...     "whatsapp",
            ...     {
            ...         "name": "Customer Support Auto-Reply",
            ...         "event": "message_received",
            ...         "agentflow_id": "support-agentflow-id",
            ...         "goal": "Analyze the customer's message and provide helpful information"
            ...     }
            ... )
        """
        # First get existing triggers
        existing = self.list_by_connector(connector_id)
        existing_triggers = existing.get("triggers", []) if existing else []

        # Add new trigger
        new_trigger: Trigger = {
            "_id": self._generate_object_id(),
            "name": trigger["name"],
            "trigger_name": trigger["name"],
            "event": trigger["event"],
            "trigger_type": "coworker",
            "agentflow_id": trigger["agentflow_id"],
            "goal": trigger["goal"],
        }
        
        if "start_from_agent_id" in trigger:
            new_trigger["start_from_agent_id"] = trigger["start_from_agent_id"]
        if "schedule_time" in trigger:
            new_trigger["schedule_time"] = trigger["schedule_time"]
        if "filters" in trigger:
            new_trigger["filters"] = trigger["filters"]
        if "condition" in trigger:
            new_trigger["condition"] = trigger["condition"]

        return self.update(connector_id, category, [*existing_triggers, new_trigger])

    def remove(
        self,
        connector_id: str,
        category: TriggerConnectorCategory,
        trigger_id: str
    ) -> TriggerInDB:
        """
        Remove a trigger from a connector.

        Args:
            connector_id: The connector ID
            category: Connector category
            trigger_id: ID of the trigger to remove

        Returns:
            Updated trigger configuration
        """
        existing = self.list_by_connector(connector_id)
        remaining_triggers = [
            t for t in (existing.get("triggers", []) if existing else [])
            if t.get("_id") != trigger_id
        ]
        return self.update(connector_id, category, remaining_triggers)

    def remove_all(
        self,
        connector_id: str,
        category: TriggerConnectorCategory
    ) -> TriggerInDB:
        """
        Remove all triggers from a connector.

        Args:
            connector_id: The connector ID
            category: Connector category

        Returns:
            Empty trigger configuration
        """
        return self.update(connector_id, category, [])

    def execute(
        self,
        project_id: str,
        connector_id: str,
        trigger_id: str,
        data: Dict[str, Any]
    ) -> TriggerExecutionResult:
        """
        Manually trigger an AgentFlow execution.

        This bypasses the webhook and directly executes the AgentFlow
        with the provided data.

        Args:
            project_id: Project ID
            connector_id: Connector ID
            trigger_id: Trigger ID
            data: Data to pass to the AgentFlow

        Returns:
            Execution result
        """
        return self._http.request(
            "POST",
            f"/trigger/{project_id}/{connector_id}/{trigger_id}",
            body=data
        )

    def execute_multiple(
        self,
        project_id: str,
        triggers: List[Trigger],
        response_data: Any,
        triggered_by: str,
        execution_id: Optional[str] = None
    ) -> Dict[str, List[TriggerExecutionResult]]:
        """
        Execute multiple triggers at once.

        Args:
            project_id: Project ID
            triggers: Array of triggers to execute
            response_data: Data to pass to all triggers
            triggered_by: User/entity triggering the execution
            execution_id: Optional existing execution ID

        Returns:
            Execution results
        """
        body: Dict[str, Any] = {
            "triggers": triggers,
            "response_data": response_data,
            "triggered_by": triggered_by,
        }
        if execution_id:
            body["execution_id"] = execution_id

        return self._http.request(
            "POST",
            f"/trigger/{project_id}/coworker",
            body=body
        )

    def _generate_object_id(self) -> str:
        """
        Generate a MongoDB-style ObjectId.
        This is needed when creating new triggers.
        """
        timestamp = format(int(time.time()), "08x")
        machine_id = format(uuid.getnode() % 16777216, "06x")
        process_id = format(uuid.uuid4().int % 65536, "04x")
        counter = format(uuid.uuid4().int % 16777216, "06x")
        return timestamp + machine_id + process_id + counter

