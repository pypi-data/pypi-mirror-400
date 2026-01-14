"""
Agent module for managing agents
"""

from typing import Optional, List, Dict, Any, Type
from pydantic import BaseModel
from lyzr.base import BaseModule
from lyzr.models import Agent, AgentConfig, AgentList
from lyzr.exceptions import ValidationError
from lyzr.inference import InferenceModule


class AgentModule(BaseModule):
    """
    Module for managing Lyzr agents

    Can be used standalone or through Studio client.

    Example (Standalone):
        >>> from lyzr.http import HTTPClient
        >>> from lyzr.agents import AgentModule
        >>> http = HTTPClient(api_key="sk-xxx")
        >>> agents = AgentModule(http)
        >>> agent = agents.create(name="Bot", provider="openai/gpt-4o")

    Example (Through Studio):
        >>> from lyzr import Studio
        >>> studio = Studio(api_key="sk-xxx")
        >>> agent = studio.create_agent(name="Bot", provider="openai/gpt-4o")
        >>> # OR
        >>> agent = studio.agents.create(name="Bot", provider="openai/gpt-4o")
    """

    def __init__(self, http_client):
        """Initialize AgentModule with HTTP client and inference module"""
        super().__init__(http_client)
        self._inference = InferenceModule(http_client)

    def _make_smart_agent(
        self,
        agent_data: Dict[str, Any],
        response_model: Optional[Type[BaseModel]] = None
    ) -> Agent:
        """
        Create a smart Agent with injected clients

        Args:
            agent_data: Raw agent data from API
            response_model: Optional Pydantic model for structured responses

        Returns:
            Agent: Smart agent with .run(), .update(), .delete(), .clone() methods
        """
        agent = Agent(**agent_data)
        # Inject clients
        agent._http = self._http
        agent._inference = self._inference
        agent._agent_module = self
        agent._response_model = response_model
        return agent

    def create(
        self,
        name: str,
        provider: str,
        temperature: float = 0.7,
        top_p: float = 0.9,
        description: Optional[str] = None,
        agent_role: Optional[str] = None,
        agent_goal: Optional[str] = None,
        agent_instructions: Optional[str] = None,
        tools: Optional[List[str]] = None,
        response_model: Optional[Type[BaseModel]] = None,
        **kwargs
    ) -> Agent:
        """
        Create a new agent

        Args:
            name: Agent name
            provider: Provider and model (e.g., 'openai/gpt-4o' or 'gpt-4o')
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter (0.0 to 1.0)
            description: Agent description
            agent_role: Agent's role or persona
            agent_goal: Agent's primary goal
            agent_instructions: Detailed instructions
            tools: List of tool IDs to enable
            response_model: Pydantic model for structured responses
            **kwargs: Additional configuration options

        Returns:
            Agent: Created smart agent object

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API request fails

        Example:
            >>> # Text response
            >>> agent = agents.create(
            ...     name="Support Bot",
            ...     provider="openai/gpt-4o",
            ...     agent_role="Customer support assistant",
            ...     temperature=0.7
            ... )
            >>>
            >>> # Structured response
            >>> class Result(BaseModel):
            ...     answer: str
            >>>
            >>> agent = agents.create(
            ...     name="Structured Bot",
            ...     provider="openai/gpt-4o",
            ...     response_model=Result
            ... )
        """
        # Build configuration using Pydantic model
        config = AgentConfig(
            name=name,
            provider=provider,
            temperature=temperature,
            top_p=top_p,
            description=description,
            agent_role=agent_role,
            agent_goal=agent_goal,
            agent_instructions=agent_instructions,
            tools=tools or [],
            response_model=response_model,
            **kwargs
        )

        # Make API request
        response = self._http.post("/v3/agents/", json=config.to_api_dict())

        # API returns {"agent_id": "..."}
        agent_id = response.get("agent_id")
        if not agent_id:
            raise ValidationError("API did not return agent_id")

        # Fetch full agent details and inject response_model
        return self.get(agent_id, response_model=response_model)

    def get(
        self,
        agent_id: str,
        response_model: Optional[Type[BaseModel]] = None
    ) -> Agent:
        """
        Get an existing agent by ID

        Args:
            agent_id: Agent ID
            response_model: Optional Pydantic model for structured responses

        Returns:
            Agent: Smart agent object with .run(), .update(), .delete(), .clone()

        Raises:
            NotFoundError: If agent doesn't exist
            APIError: If API request fails

        Example:
            >>> # Get agent with text responses
            >>> agent = agents.get("agent_abc123")
            >>> print(agent.name)
            >>> response = agent.run("Hello!")
            >>>
            >>> # Get agent with structured responses
            >>> class Result(BaseModel):
            ...     answer: str
            >>>
            >>> agent = agents.get("agent_abc123", response_model=Result)
            >>> result: Result = agent.run("Question?")
        """
        response = self._http.get(f"/v3/agents/{agent_id}")
        return self._make_smart_agent(response, response_model=response_model)

    def list(self) -> AgentList:
        """
        List all agents

        Returns:
            AgentList: List of smart agents (iterable)

        Raises:
            APIError: If API request fails

        Example:
            >>> all_agents = agents.list()
            >>> for agent in all_agents:
            ...     print(agent.name)
            ...     # Each agent is smart and can run
            ...     response = agent.run("Hello")
        """
        response = self._http.get("/v3/agents/")

        # Handle different response formats
        if isinstance(response, list):
            agents = []
            for agent_data in response:
                try:
                    agent = self._make_smart_agent(agent_data)
                    agents.append(agent)
                except Exception as e:
                    # Skip agents that fail validation (might be corrupted/old)
                    print(f"Warning: Skipping agent {agent_data.get('_id', 'unknown')}: {str(e)}")
                    continue
            return AgentList(agents=agents, total=len(agents))
        elif isinstance(response, dict):
            agents_data = response.get("agents", response.get("data", []))
            agents = [self._make_smart_agent(agent_data) for agent_data in agents_data]
            return AgentList(
                agents=agents,
                total=response.get("total", len(agents))
            )
        else:
            return AgentList(agents=[])

    def update(
        self,
        agent_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        **kwargs
    ) -> Agent:
        """
        Update an existing agent

        Args:
            agent_id: Agent ID
            name: New agent name
            description: New description
            temperature: New temperature
            top_p: New top_p value
            **kwargs: Other fields to update

        Returns:
            Agent: Updated agent object

        Raises:
            NotFoundError: If agent doesn't exist
            ValidationError: If parameters are invalid
            APIError: If API request fails

        Example:
            >>> agent = agents.update(
            ...     "agent_abc123",
            ...     temperature=0.5,
            ...     description="Updated description"
            ... )
        """
        # Get current agent to merge with updates
        current_agent = self.get(agent_id)

        # Build update data with current values as base
        update_data = {
            "name": name if name is not None else current_agent.name,
            "provider_id": current_agent.provider_id,
            "model": current_agent.model,
            "top_p": top_p if top_p is not None else current_agent.top_p,
            "temperature": temperature if temperature is not None else current_agent.temperature,
        }

        # Add optional fields if they exist in current agent
        if description is not None:
            update_data["description"] = description
        elif current_agent.description:
            update_data["description"] = current_agent.description

        # Validate ranges
        if not 0.0 <= update_data["temperature"] <= 2.0:
            raise ValidationError("Temperature must be between 0.0 and 2.0")
        if not 0.0 <= update_data["top_p"] <= 1.0:
            raise ValidationError("top_p must be between 0.0 and 1.0")

        # Add any additional kwargs
        update_data.update(kwargs)

        response = self._http.put(f"/v3/agents/{agent_id}", json=update_data)

        # API returns success message, not agent data
        # Fetch updated agent
        return self.get(agent_id)

    def delete(self, agent_id: str) -> bool:
        """
        Delete an agent

        Args:
            agent_id: Agent ID

        Returns:
            bool: True if deleted successfully

        Raises:
            NotFoundError: If agent doesn't exist
            APIError: If API request fails

        Example:
            >>> success = agents.delete("agent_abc123")
            >>> print(success)
            True
        """
        return self._http.delete(f"/v3/agents/{agent_id}")

    def clone(self, agent_id: str, new_name: Optional[str] = None) -> Agent:
        """
        Clone an existing agent

        Args:
            agent_id: Agent ID to clone
            new_name: Name for the cloned agent

        Returns:
            Agent: Cloned agent object

        Raises:
            NotFoundError: If agent doesn't exist
            APIError: If API request fails

        Example:
            >>> cloned = agents.clone("agent_abc123", "Cloned Agent")
        """
        payload = {"agent_id": agent_id}
        if new_name:
            payload["name"] = new_name

        response = self._http.post("/v3/agents/clone", json=payload)

        # API returns {"agent_id": "..."}
        agent_id = response.get("agent_id")
        if not agent_id:
            raise ValidationError("API did not return agent_id")

        return self.get(agent_id)

    def bulk_delete(self, agent_ids: List[str]) -> bool:
        """
        Delete multiple agents at once

        Args:
            agent_ids: List of agent IDs to delete

        Returns:
            bool: True if successful

        Raises:
            ValidationError: If agent_ids is empty
            APIError: If API request fails

        Example:
            >>> success = agents.bulk_delete(["id1", "id2", "id3"])
        """
        if not agent_ids:
            raise ValidationError("agent_ids cannot be empty")

        response = self._http.post(
            "/v3/agents/bulk-delete",
            json={"agent_ids": agent_ids}
        )
        return True
