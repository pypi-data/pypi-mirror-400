"""
Response types for agent execution
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AgentResponse(BaseModel):
    """
    Response from agent.run() method

    Contains the agent's response text and associated metadata.
    Future: Will support Pydantic validation for structured outputs.
    """

    response: str = Field(..., description="The actual response text from the agent")
    session_id: str = Field(..., description="Session ID for this interaction")
    message_id: Optional[str] = Field(None, description="Unique message identifier")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        None, description="Tool/function calls made during execution"
    )
    raw_response: Optional[Dict[str, Any]] = Field(
        None, description="Raw API response for debugging"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)

    def __str__(self) -> str:
        return f"AgentResponse(session_id='{self.session_id}', response='{self.response[:50]}...')"

    def __repr__(self) -> str:
        return self.__str__()


class AgentStream(BaseModel):
    """
    Single chunk from streaming response

    Represents one piece of a streamed response from an agent.
    Used when agent.run(stream=True) is called.

    For structured responses, the final chunk (done=True) will contain
    the validated Pydantic model in structured_data.
    """

    content: str = Field(..., description="Content of this chunk")
    delta: Optional[str] = Field(None, description="Delta/difference from previous chunk")
    done: bool = Field(False, description="Whether this is the final chunk")
    session_id: Optional[str] = Field(None, description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Chunk-specific metadata")
    chunk_index: Optional[int] = Field(None, description="Index of this chunk in the stream")
    structured_data: Optional[BaseModel] = Field(
        None,
        description="Parsed structured response (only in final chunk if response_model is set)"
    )

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)

    def __str__(self) -> str:
        status = "DONE" if self.done else "STREAMING"
        return f"AgentStream({status}, content='{self.content[:30]}...')"

    def __repr__(self) -> str:
        return self.__str__()


class TaskResponse(BaseModel):
    """
    Response from creating a long-running task

    Contains the task ID that can be used to poll for status.
    """

    task_id: str = Field(..., description="Unique identifier for the task")
    status: str = Field("pending", description="Current status of the task")
    session_id: Optional[str] = Field(None, description="Session ID associated with task")
    created_at: Optional[str] = Field(None, description="Task creation timestamp")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)

    def __str__(self) -> str:
        return f"TaskResponse(task_id='{self.task_id}', status='{self.status}')"

    def __repr__(self) -> str:
        return self.__str__()


class TaskStatus(BaseModel):
    """
    Status of a long-running task

    Contains information about task execution progress.
    """

    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Current status (pending, running, completed, failed)")
    result: Optional[AgentResponse] = Field(None, description="Result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    progress: Optional[float] = Field(None, description="Progress percentage (0-100)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Task metadata")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def is_complete(self) -> bool:
        """Check if task is complete"""
        return self.status in ["completed", "failed"]

    def is_successful(self) -> bool:
        """Check if task completed successfully"""
        return self.status == "completed"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)

    def __str__(self) -> str:
        return f"TaskStatus(task_id='{self.task_id}', status='{self.status}')"

    def __repr__(self) -> str:
        return self.__str__()
