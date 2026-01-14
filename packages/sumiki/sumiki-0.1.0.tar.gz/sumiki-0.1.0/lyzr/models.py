"""
Pydantic models for Lyzr Agent SDK
"""

from typing import Optional, List, Dict, Any, Literal, Union, Iterator, TYPE_CHECKING, Type
from pydantic import BaseModel, Field, validator, model_validator, ConfigDict, PrivateAttr
from lyzr.providers import ProviderName, ModelResolver

if TYPE_CHECKING:
    from lyzr.http import HTTPClient
    from lyzr.inference import InferenceModule
    from lyzr.responses import AgentResponse, AgentStream
    from lyzr.knowledge_base import KnowledgeBase, KnowledgeBaseRuntimeConfig


class AgentConfig(BaseModel):
    """Configuration for creating an agent"""

    name: str = Field(..., min_length=1, max_length=200, description="Agent name")
    description: Optional[str] = Field(None, max_length=1000, description="Agent description")
    agent_role: Optional[str] = Field(None, description="Agent's role/persona")
    agent_goal: Optional[str] = Field(None, description="Agent's primary goal")
    agent_instructions: Optional[str] = Field(None, description="Detailed instructions for the agent")

    # Model configuration
    provider: str = Field(..., description="Provider and model (e.g., 'openai/gpt-4o' or 'gpt-4o')")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Sampling temperature")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")

    # Optional configurations
    examples: Optional[str] = Field(None, description="Example interactions")
    tools: List[str] = Field(default_factory=list, description="List of tool IDs")
    tool_usage_description: str = Field("{}", description="Tool usage description JSON")
    tool_configs: List[Any] = Field(default_factory=list, description="Tool configurations")

    # Advanced settings
    llm_credential_id: str = Field("lyzr_openai", description="LLM credential ID")
    features: List[Any] = Field(default_factory=list, description="Enabled features")
    managed_agents: List[Any] = Field(default_factory=list, description="Managed sub-agents")
    a2a_tools: List[Any] = Field(default_factory=list, description="Agent-to-agent tools")
    additional_model_params: Optional[Dict[str, Any]] = Field(None, description="Additional model parameters")
    response_format: Dict[str, Any] = Field({"type": "text"}, description="Response format configuration")
    store_messages: bool = Field(True, description="Whether to store conversation messages")
    file_output: bool = Field(False, description="Whether agent can output files")
    image_output_config: Optional[Dict[str, Any]] = Field(None, description="Image output configuration")

    # Structured response support
    response_model: Optional[Type[BaseModel]] = Field(
        None,
        exclude=True,
        description="Pydantic model for structured responses (not sent to API)"
    )

    # Internal fields (populated after parsing)
    provider_id: Optional[str] = Field(None, description="Resolved provider ID")
    model: Optional[str] = Field(None, description="Resolved model name")

    class Config:
        validate_assignment = True

    @validator("name")
    def validate_name(cls, v):
        """Validate agent name"""
        if not v or not v.strip():
            raise ValueError("Agent name cannot be empty")
        return v.strip()

    @model_validator(mode='before')
    @classmethod
    def parse_provider_and_build_features(cls, data: Any) -> Any:
        """Parse provider string and build response_format"""
        if isinstance(data, dict):
            # Parse provider if present
            if 'provider' in data:
                try:
                    provider_str = data['provider']
                    provider, model, model_info = ModelResolver.parse(provider_str)

                    # Set resolved values
                    data['provider_id'] = provider.value
                    data['model'] = model
                    data['llm_credential_id'] = ModelResolver.get_credential_id(provider)
                except ValueError as e:
                    raise ValueError(f"Invalid provider/model: {str(e)}")

            # Build response_format from response_model if present
            if 'response_model' in data and data['response_model']:
                from lyzr.structured import ResponseSchemaBuilder
                data['response_format'] = ResponseSchemaBuilder.to_json_schema(data['response_model'])
            elif 'response_format' not in data or not data['response_format']:
                data['response_format'] = {"type": "text"}

        return data

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API request format"""
        return {
            "name": self.name,
            "description": self.description,
            "agent_role": self.agent_role,
            "agent_goal": self.agent_goal,
            "agent_instructions": self.agent_instructions,
            "examples": self.examples,
            "tools": self.tools,
            "tool_usage_description": self.tool_usage_description,
            "tool_configs": self.tool_configs,
            "provider_id": self.provider_id,
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "llm_credential_id": self.llm_credential_id,
            "features": self.features,
            "managed_agents": self.managed_agents,
            "a2a_tools": self.a2a_tools,
            "additional_model_params": self.additional_model_params,
            "response_format": self.response_format,
            "store_messages": self.store_messages,
            "file_output": self.file_output,
            "image_output_config": self.image_output_config,
        }


class Agent(BaseModel):
    """Agent model representing a created agent"""

    id: str = Field(..., alias="_id", description="Agent ID")
    api_key: str = Field(..., description="API key associated with agent")
    name: str = Field(..., description="Agent name")
    description: Optional[str] = Field(None, description="Agent description")
    agent_role: Optional[str] = Field(None, description="Agent role")
    agent_goal: Optional[str] = Field(None, description="Agent goal")
    agent_instructions: Optional[str] = Field(None, description="Agent instructions")
    agent_context: Optional[str] = Field(None, description="Agent context")
    agent_output: Optional[str] = Field(None, description="Agent output format")

    # Model configuration
    provider_id: str = Field(..., description="Provider ID")
    model: str = Field(..., description="Model name")
    temperature: float = Field(..., description="Temperature setting")
    top_p: float = Field(..., description="Top-p setting")
    llm_credential_id: str = Field(default="lyzr_openai", description="LLM credential ID")

    # Features and tools
    tools: List[str] = Field(default_factory=list, description="Tool IDs")
    features: List[Any] = Field(default_factory=list, description="Features")
    managed_agents: List[Any] = Field(default_factory=list, description="Managed agents")
    tool_configs: List[Any] = Field(default_factory=list, description="Tool configurations")
    tool_usage_description: Optional[str] = Field(default="{}", description="Tool usage description")
    a2a_tools: List[Any] = Field(default_factory=list, description="Agent-to-agent tools")

    # Output configuration
    response_format: Optional[Dict[str, Any]] = Field(default={"type": "text"}, description="Response format")
    store_messages: bool = Field(default=True, description="Whether to store messages")
    file_output: bool = Field(default=False, description="Whether to output files")
    image_output_config: Optional[Dict[str, Any]] = Field(None, description="Image output config")
    voice_config: Optional[Dict[str, Any]] = Field(None, description="Voice configuration")

    # Additional params
    examples: Optional[str] = Field(None, description="Example interactions")
    additional_model_params: Optional[Dict[str, Any]] = Field(None, description="Additional model parameters")

    # Metadata
    version: str = Field(default="3", description="API version")
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    # Private fields (injected by AgentModule, not serialized)
    _http: Optional['HTTPClient'] = PrivateAttr(default=None)
    _inference: Optional['InferenceModule'] = PrivateAttr(default=None)
    _agent_module: Optional[Any] = PrivateAttr(default=None)
    _response_model: Optional[Type[BaseModel]] = PrivateAttr(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    @model_validator(mode='before')
    @classmethod
    def handle_null_lists(cls, data: Any) -> Any:
        """Convert None to empty list for list fields"""
        if isinstance(data, dict):
            # Handle None values for list fields
            list_fields = ['tools', 'features', 'managed_agents', 'tool_configs', 'a2a_tools']
            for field in list_fields:
                if field in data and data[field] is None:
                    data[field] = []

            # Handle None for dict fields
            if 'response_format' in data and data['response_format'] is None:
                data['response_format'] = {"type": "text"}

            if 'tool_usage_description' in data and data['tool_usage_description'] is None:
                data['tool_usage_description'] = "{}"

        return data

    def _ensure_clients(self):
        """Ensure HTTP and inference clients are available"""
        if not self._http or not self._inference:
            raise RuntimeError(
                "Agent not properly initialized with clients. "
                "Agents should be created using Studio.create_agent() or Studio.get_agent()"
            )

    def run(
        self,
        message: str,
        session_id: Optional[str] = None,
        stream: bool = False,
        user_id: str = "default_user",
        knowledge_bases: Optional[List[Union['KnowledgeBase', 'KnowledgeBaseRuntimeConfig']]] = None,
        **kwargs
    ) -> Union['AgentResponse', BaseModel, Iterator['AgentStream']]:
        """
        Run the agent with a message

        Args:
            message: User message to process
            session_id: Optional session ID (auto-generated if None)
            stream: Whether to stream response (default: False)
            user_id: User ID (default: "default_user")
            knowledge_bases: Knowledge bases to use for this run (passed at runtime!)
            **kwargs: Additional parameters (system_prompt_variables, features, etc.)

        Returns:
            AgentResponse: If no response_model (text response)
            BaseModel: If response_model is set (structured response - typed Pydantic instance)
            Iterator[AgentStream]: If stream=True, yields chunks (final chunk has structured_data)

        Raises:
            RuntimeError: If agent not properly initialized
            InvalidResponseError: If structured response validation fails
            APIError: If API request fails

        Example:
            >>> # Text response
            >>> agent = studio.create_agent(name="Bot", provider="gpt-4o")
            >>> response = agent.run("What is 2+2?")
            >>> print(response.response)
            >>>
            >>> # With knowledge base
            >>> kb = studio.create_knowledge_base(name="docs")
            >>> response = agent.run(
            ...     "What are business hours?",
            ...     knowledge_bases=[kb]
            ... )
            >>>
            >>> # Structured response
            >>> class Result(BaseModel):
            ...     answer: int
            >>> agent = studio.create_agent(
            ...     name="Math Bot",
            ...     provider="gpt-4o",
            ...     response_model=Result
            ... )
            >>> result: Result = agent.run("What is 2+2?")
            >>> print(result.answer)  # 4
            >>>
            >>> # Streaming
            >>> for chunk in agent.run("Tell a story", stream=True):
            ...     print(chunk.content, end="")
        """
        self._ensure_clients()

        # Auto-generate session_id if not provided
        if session_id is None:
            import uuid
            session_id = f"session_{uuid.uuid4().hex[:16]}"

        # Build features array from knowledge_bases (runtime integration)
        if knowledge_bases:
            from lyzr.knowledge_base import KnowledgeBaseRuntimeConfig

            kb_configs = []
            for kb in knowledge_bases:
                if isinstance(kb, KnowledgeBaseRuntimeConfig):
                    kb_configs.append(kb.to_agentic_config())
                else:
                    # Plain KnowledgeBase - use defaults
                    kb_configs.append(kb.to_agentic_config())

            kb_feature = {
                "type": "KNOWLEDGE_BASE",
                "config": {
                    "lyzr_rag": {},
                    "agentic_rag": kb_configs
                },
                "priority": 0
            }

            # Add to kwargs features
            existing_features = kwargs.get("features", [])
            kwargs["features"] = [kb_feature] + (existing_features if isinstance(existing_features, list) else [])

        # Streaming
        if stream:
            return self._stream_with_validation(
                message=message,
                session_id=session_id,
                user_id=user_id,
                **kwargs
            )

        # Non-streaming
        raw_response = self._inference.chat(
            agent_id=self.id,
            message=message,
            session_id=session_id,
            user_id=user_id,
            **kwargs
        )

        # If structured response, parse and validate
        if self._response_model:
            from lyzr.structured import ResponseParser
            return ResponseParser.parse(
                raw_response.response,
                self._response_model
            )

        return raw_response

    def _stream_with_validation(
        self,
        message: str,
        session_id: str,
        user_id: str,
        **kwargs
    ) -> Iterator['AgentStream']:
        """
        Stream response with optional structured validation at the end

        Yields chunks as they arrive. If response_model is set, the final
        chunk will include the validated structured_data.
        """
        accumulated_content = []

        # Stream chunks
        for chunk in self._inference.stream(
            agent_id=self.id,
            message=message,
            session_id=session_id,
            user_id=user_id,
            **kwargs
        ):
            # Accumulate ALL content (including final chunk)
            if chunk.content:
                accumulated_content.append(chunk.content)

            # If this is the final chunk and we have a response_model
            if chunk.done and self._response_model:
                # Parse accumulated content
                from lyzr.structured import ResponseParser
                full_response = "".join(accumulated_content)

                try:
                    structured_data = ResponseParser.parse(
                        full_response,
                        self._response_model
                    )
                    # Add structured data to final chunk
                    chunk.structured_data = structured_data
                except Exception as e:
                    # Add error info to final chunk
                    chunk.metadata = chunk.metadata or {}
                    chunk.metadata["validation_error"] = str(e)
                    # Don't suppress the error - let it be visible in metadata

            yield chunk

    def update(self, **kwargs) -> 'Agent':
        """
        Update agent configuration

        Args:
            **kwargs: Configuration parameters to update (name, description,
                     temperature, top_p, etc.)

        Returns:
            Agent: Updated agent instance

        Raises:
            RuntimeError: If agent not properly initialized
            ValidationError: If parameters are invalid
            APIError: If API request fails

        Example:
            >>> agent = studio.get_agent("agent_id")
            >>> agent = agent.update(temperature=0.5, description="Updated")
            >>> print(agent.temperature)  # 0.5
        """
        self._ensure_clients()

        if not self._agent_module:
            raise RuntimeError("Agent module not available")

        return self._agent_module.update(self.id, **kwargs)

    def delete(self) -> bool:
        """
        Delete this agent

        Returns:
            bool: True if deletion was successful

        Raises:
            RuntimeError: If agent not properly initialized
            NotFoundError: If agent doesn't exist
            APIError: If deletion fails

        Example:
            >>> agent = studio.get_agent("agent_id")
            >>> success = agent.delete()
            >>> print(success)  # True
        """
        self._ensure_clients()

        if not self._agent_module:
            raise RuntimeError("Agent module not available")

        return self._agent_module.delete(self.id)

    def clone(self, new_name: Optional[str] = None) -> 'Agent':
        """
        Create a copy of this agent

        Args:
            new_name: Optional name for the cloned agent (defaults to "{name} (Clone)")

        Returns:
            Agent: Cloned agent instance

        Raises:
            RuntimeError: If agent not properly initialized
            APIError: If cloning fails

        Example:
            >>> agent = studio.get_agent("agent_id")
            >>> cloned = agent.clone("My Cloned Agent")
            >>> print(cloned.id)  # Different from original
            >>> print(cloned.name)  # "My Cloned Agent"
        """
        self._ensure_clients()

        if not self._agent_module:
            raise RuntimeError("Agent module not available")

        return self._agent_module.clone(self.id, new_name)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes private fields)"""
        return self.model_dump(by_alias=False, exclude_none=True)

    def __str__(self) -> str:
        return f"Agent(id='{self.id}', name='{self.name}', model='{self.provider_id}/{self.model}')"

    def __repr__(self) -> str:
        return self.__str__()


class AgentList(BaseModel):
    """List of agents with metadata"""
    agents: List[Agent] = Field(default_factory=list, description="List of agents")
    total: Optional[int] = Field(None, description="Total count")

    def __iter__(self):
        return iter(self.agents)

    def __len__(self):
        return len(self.agents)

    def __getitem__(self, index):
        return self.agents[index]
