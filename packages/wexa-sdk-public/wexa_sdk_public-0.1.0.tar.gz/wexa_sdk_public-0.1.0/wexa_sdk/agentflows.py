from __future__ import annotations
from typing import Optional, TypedDict, Dict, Any
from .core.http import HttpClient


class AgentflowCreateBody(TypedDict, total=False):
    """Body for creating an AgentFlow (Coworker).

    Required:
      - name: str
      - description: str
      - role: str
      - projectID: str

    Optional: backend-supported fields like agents/processflow, anomaly_detection, cron_details, etc.
    """
    name: str
    description: str
    role: str
    projectID: str

class AgentFlows:
    def __init__(self, http: HttpClient):
        self.http = http

    def list(
        self,
        project_id: str | None = None,
        projectID: str | None = None,
        skip: int | None = None,
        limit: int | None = None,
    ):
        """
        Get agentflows.
        GET /agentflows?projectID=...&skip=...&limit=...

        Get All AgentFlows.

        Retrieve a comprehensive list of all AgentFlows within your organization. Each 
        AgentFlow represents a structured workflow comprising AI agents (Coworkers) equipped 
        with specific skills to automate tasks and processes. This endpoint provides detailed 
        information on each AgentFlow, including its configuration, associated agents, and 
        current status, enabling effective management and monitoring of your AI-driven workflows.

        Args:
            project_id: The unique identifier of the project (optional, accepts both project_id and projectID)
            projectID: The unique identifier of the project (optional, accepts both project_id and projectID)
            skip: Optional number of AgentFlows to skip (for pagination) (optional)
            limit: Optional limit on the number of AgentFlows to return (optional)

        Returns:
            List of AgentFlows within the organization, containing detailed information on each 
            AgentFlow including configuration, associated agents, and current status.

        Example:
            >>> agentflows = client.agentflows.list(
            ...     projectID="68dcb579121a635f13002bf7",
            ...     limit=50,
            ...     skip=0
            ... )
        """
        # API expects 'projectID' (capital D); accept both and normalize
        pid = projectID or project_id
        params: dict | None = None
        if pid is not None or skip is not None or limit is not None:
            params = {}
            if pid is not None:
                params["projectID"] = pid
            if skip is not None:
                params["skip"] = skip
            if limit is not None:
                params["limit"] = limit
        return self.http.request("GET", "/agentflows", params=params)

    def get(self, id: str):
        """
        Get agentflow by ID.
        GET /agentflow/{agentflow_id}

        Get AgentFlow by ID.

        This endpoint fetches comprehensive details of an AgentFlow specified by its unique id. 
        The response includes information such as the AgentFlow's name, description, status, 
        associated agents, their configurations, and assigned skills. This is essential for 
        understanding and managing the automation workflows orchestrated by AI Coworkers in 
        your organization. Retrieve detailed information about a specific AgentFlow using its 
        unique identifier. This endpoint is essential for accessing the configuration and 
        status of individual AgentFlows within your system.

        Args:
            id: The unique identifier of the AgentFlow (required)

        Returns:
            AgentFlow object containing comprehensive details including name, description, 
            status, associated agents, their configurations, and assigned skills.

        Example:
            >>> agentflow = client.agentflows.get(id="6901c5852a1fb6a6073b49e5")
        """
        return self.http.request("GET", f"/agentflow/{id}")

    def get_by_user_and_project(
        self,
        agentflow_id: str,
        executed_by: str,
        projectID: str,
    ) -> Dict[str, Any]:
        """
        Get AgentFlow by projectId and UserId.

        Retrieve an AgentFlow associated with a specific user and project by providing
        the agentflow_id, executed_by (user_id), and projectID. This endpoint enables
        you to access and manage the AI Coworker workflows that a particular user has
        created and is actively utilizing within a specific project.

        Args:
            agentflow_id: The unique identifier of the AgentFlow.
            executed_by: The unique identifier of the user who executed the AgentFlow.
            projectID: The unique identifier of the project.

        Returns:
            The AgentFlow JSON object containing fields like _id, name, role, projectID,
            organization_id, agents, etc.

        Example:
            >>> agentflow = client.agentflows.get_by_user_and_project(
            ...     agentflow_id="67fdea9b68df1c3e9580a549",
            ...     executed_by="user-id-123",
            ...     projectID="67fdea40aac77be632954f13"
            ... )
        """
        return self.http.request(
            "GET",
            f"/agentflow/{agentflow_id}/user/{executed_by}/project/{projectID}"
        )

    def add_skilled_agent(
        self,
        agentflow_id: str,
        projectID: str,
        body: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add skilled agent to agentflow.
        POST /agentflow/{agentflow_id}/skilled?projectID=...

        Add Skilled Agent to AgentFlow.

        Integrate a skilled AI agent into an existing AgentFlow by specifying the agentflow_id.
        This endpoint allows you to enhance the capabilities of your AgentFlow by adding agents
        equipped with specific skills, enabling more complex and dynamic automation workflows
        tailored to your organization's needs.

        Args:
            agentflow_id: The unique identifier of the AgentFlow (required)
            projectID: The unique identifier of the project (required)
            body: The skilled agent configuration data. Required fields include:
                - _id (str): Agent ID (required)
                - role (str): Agent role (required)
                - title (str): Agent title (required)
                - skills (List[str]): Array of skill IDs (required)
                - context (List): Context array (required)
                - llm (Dict): LLM configuration with model, max_tokens, temperature (required)
                    - model (str): LLM model name (required)
                    - max_tokens (int): Maximum tokens (required)
                    - temperature (int): Temperature setting (required)
                - memory (Dict): Memory configuration with memory_type (required)
                    - memory_type (str): Type of memory (required)
                - agent_type (str): Type of agent (e.g., "skilled_agent") (required)
                - role_description (str): Description of the role (required)
                - prompt (Dict): Prompt configuration (required)
                    - template (str): Prompt template (required)
                    - variables (List): Variables array (required)
                    - display_template (str): Display template (required)
                - triggers (List): Triggers array (required)
                - has_knowledge_base (bool): Whether knowledge base is enabled (required)
                - is_user_specific_task (bool): Whether task is user-specific (required)
                - is_preview_mode_enabled (bool): Whether preview mode is enabled (required)
                - conditions (List[Dict]): Conditions array (required)
                    - decision (str): Decision value (optional)
                    - condition (str): Condition value (optional)

        Returns:
            Updated AgentFlow object containing metadata including _id, name, description, 
            and the newly added skilled agent.

        Example:
            >>> skilled_agent_body = {
            ...     "_id": "agent-id",
            ...     "role": "Content Creator",
            ...     "title": "Content Creator Agent",
            ...     "skills": ["skill-id-1"],
            ...     "context": [],
            ...     "llm": {"model": "azure/gpt-4o", "max_tokens": 10000, "temperature": 0},
            ...     "memory": {"memory_type": "lt"},
            ...     "agent_type": "skilled_agent",
            ...     "role_description": "Creates content",
            ...     "prompt": {"template": "...", "variables": [], "display_template": "..."},
            ...     "triggers": [],
            ...     "has_knowledge_base": False,
            ...     "is_user_specific_task": False,
            ...     "is_preview_mode_enabled": False,
            ...     "conditions": []
            ... }
            >>> agentflow = client.agentflows.add_skilled_agent(
            ...     agentflow_id="6901c5852a1fb6a6073b49e5",
            ...     projectID="68dcb579121a635f13002bf7",
            ...     body=skilled_agent_body
            ... )
        """
        params = {"projectID": projectID}
        return self.http.request(
            "POST",
            f"/agentflow/{agentflow_id}/skilled",
            params=params,
            json=body
        )

    def create(self, body: AgentflowCreateBody, projectID: Optional[str] = None):
        """
        Create agentflow.
        POST /agentflow/?projectID=...

        Create AgentFlow.

        Create a new AgentFlow within your organization. An AgentFlow in Wexa.ai represents 
        a structured workflow comprising AI agents (Coworkers) equipped with specific skills 
        to automate tasks and processes. This endpoint allows you to define the AgentFlow's 
        configuration, including its name, description, associated agents, and operational 
        parameters, enabling the orchestration of complex automation workflows tailored to 
        your organization's needs.

        Args:
            body: AgentFlow creation body containing:
                - name: The name of the AgentFlow (string, required)
                - description: The description of the AgentFlow (string, required)
                - role: The role of the AgentFlow (string, required)
                - projectID: The unique identifier of the project (string, required)
          - ...additional optional fields supported by backend (e.g., agents, anomaly_detection, cron_details)
            projectID: The unique identifier of the project (optional, can be inferred from body)

        Returns:
            Created AgentFlow object containing metadata about the new AgentFlow including 
            _id, name, description, role, projectID, agents, etc.

        Example:
            >>> agentflow_body = {
            ...     "name": "Content Creation Flow",
            ...     "description": "Automated content creation workflow",
            ...     "role": "Content Creator",
            ...     "projectID": "68dcb579121a635f13002bf7"
            ... }
            >>> agentflow = client.agentflows.create(
            ...     body=agentflow_body,
            ...     projectID="68dcb579121a635f13002bf7"
            ... )
        """
        # include projectID in query if provided, or infer from body
        pid = projectID or body.get("projectID") or body.get("projectId")
        params = {"projectID": pid} if pid else None
        return self.http.request("POST", "/agentflow/", params=params, json=body)

    def update(self, id: str, body: dict):
        return self.http.request("PUT", f"/agentflow/{id}", json=body)

    # Typed body for updating a skilled agent to enable IDE suggestions
    class UpdateSkilledAgentBody(TypedDict, total=False):
        """Body for updating a skilled agent within an AgentFlow.

        Required (per API docs):
          - role: str
          - title: str
          - skills: list[str]
          - prompt: { template: str, variables: list, display_template: str }
          - context: list
          - triggers: list
          - llm: { model: str, max_tokens: int, temperature: int }
          - role_description: str
          - memory: { memory_type: str }
          - has_knowledge_base: bool
          - is_user_specific_task: bool
          - is_preview_mode_enabled: bool
        """
        role: str
        title: str
        skills: list[str]
        prompt: dict
        context: list
        triggers: list
        llm: dict
        role_description: str
        memory: dict
        has_knowledge_base: bool
        is_user_specific_task: bool
        is_preview_mode_enabled: bool

    def update_skilled_agent(self, agentflow_id: str, agent_id: str, *, projectID: str, body: UpdateSkilledAgentBody | dict):
        """
        Update skilled agent.
        POST /agentflow/{agentflow_id}/update/skilled/{agent_id}?projectID=...

        Update Skilled Agent in AgentFlow.

        Update the configuration of an existing skilled AI agent within a specified AgentFlow 
        by providing the unique agentflow_id and agent_id. This endpoint allows you to modify 
        the agent's parameters, such as its role, skills, enabling the refinement and optimization 
        of your automation workflows to better align with evolving business requirements.

        Args:
            agentflow_id: The unique identifier of the AgentFlow (required)
            agent_id: The unique identifier of the skilled agent within the AgentFlow (required)
            projectID: The unique identifier of the project (required)
            body: The skilled agent update configuration data. Required fields include:
                - role (str): Agent role (required)
                - title (str): Agent title (required)
                - skills (List[str]): Array of skill IDs (required)
                - prompt (Dict): Prompt configuration (required)
                    - template (str): Prompt template (required)
                    - variables (List): Variables array (required)
                    - display_template (str): Display template (required)
                - context (List): Context array (required)
                - triggers (List): Triggers array (required)
                - llm (Dict): LLM configuration (required)
                    - model (str): LLM model name (required)
                    - max_tokens (int): Maximum tokens (required)
                    - temperature (int): Temperature setting (required)
                - role_description (str): Description of the role (required)
                - memory (Dict): Memory configuration (required)
                    - memory_type (str): Type of memory (required)
                - has_knowledge_base (bool): Whether knowledge base is enabled (required)
                - is_user_specific_task (bool): Whether task is user-specific (required)
                - is_preview_mode_enabled (bool): Whether preview mode is enabled (required)

        Returns:
            Updated AgentFlow object containing the modified skilled agent configuration.

        Example:
            >>> update_body = {
            ...     "role": "Content Creator",
            ...     "title": "Updated Content Creator Agent",
            ...     "skills": ["skill-id-1", "skill-id-2"],
            ...     "prompt": {
            ...         "template": "Create content for...",
            ...         "variables": [],
            ...         "display_template": "Display template"
            ...     },
            ...     "context": [],
            ...     "triggers": [],
            ...     "llm": {"model": "azure/gpt-4o", "max_tokens": 10000, "temperature": 0},
            ...     "role_description": "Creates and updates content",
            ...     "memory": {"memory_type": "lt"},
            ...     "has_knowledge_base": True,
            ...     "is_user_specific_task": False,
            ...     "is_preview_mode_enabled": False
            ... }
            >>> agentflow = client.agentflows.update_skilled_agent(
            ...     agentflow_id="6901c5852a1fb6a6073b49e5",
            ...     agent_id="6901c586eedc9fe81f0105ee",
            ...     projectID="68dcb579121a635f13002bf7",
            ...     body=update_body
            ... )
        """
        params = {"projectID": projectID} if projectID else None
        path = f"/agentflow/{agentflow_id}/update/skilled/{agent_id}"
        return self.http.request("POST", path, params=params, json=body)
