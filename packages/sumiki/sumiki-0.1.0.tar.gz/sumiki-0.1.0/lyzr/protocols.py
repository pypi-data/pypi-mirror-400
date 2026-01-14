"""
Protocols for Lyzr Agent SDK

Defines interfaces that all runnable entities must implement.
"""

from typing import Protocol, Optional, Union, Iterator, runtime_checkable


@runtime_checkable
class Runnable(Protocol):
    """
    Protocol for entities that can be executed/run

    Any class that implements this protocol can be used as a runnable entity
    in the Lyzr Agent SDK. This includes Agent, Workflow, MultiAgentSystem, etc.

    The protocol defines a standard interface for execution that allows
    different types of entities to be used interchangeably.

    Example:
        >>> def execute_runnable(runnable: Runnable, message: str):
        ...     response = runnable.run(message)
        ...     return response
        >>>
        >>> # Works with any Runnable
        >>> execute_runnable(agent, "Hello")
        >>> execute_runnable(workflow, "Hello")
        >>> execute_runnable(multi_agent_system, "Hello")
    """

    def run(
        self,
        message: str,
        session_id: Optional[str] = None,
        stream: bool = False,
        **kwargs
    ) -> Union['AgentResponse', Iterator['AgentStream']]:
        """
        Run the entity with a message

        Args:
            message: Input message to process
            session_id: Optional session ID (auto-generated if None)
            stream: Whether to stream response (default: False)
            **kwargs: Additional entity-specific parameters

        Returns:
            AgentResponse: If stream=False, returns complete response
            Iterator[AgentStream]: If stream=True, yields response chunks

        Example:
            >>> # Non-streaming
            >>> response = runnable.run("What is 2+2?")
            >>> print(response.response)
            >>>
            >>> # Streaming
            >>> for chunk in runnable.run("Tell a story", stream=True):
            ...     print(chunk.content, end="")
        """
        ...


@runtime_checkable
class Updatable(Protocol):
    """
    Protocol for entities that can be updated

    Entities implementing this protocol can modify their configuration
    after creation.
    """

    def update(self, **kwargs) -> 'Updatable':
        """
        Update entity configuration

        Args:
            **kwargs: Configuration parameters to update

        Returns:
            Updated entity instance
        """
        ...


@runtime_checkable
class Deletable(Protocol):
    """
    Protocol for entities that can be deleted

    Entities implementing this protocol can be removed from the system.
    """

    def delete(self) -> bool:
        """
        Delete this entity

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If entity doesn't exist
            APIError: If deletion fails
        """
        ...


@runtime_checkable
class Cloneable(Protocol):
    """
    Protocol for entities that can be cloned

    Entities implementing this protocol can create copies of themselves.
    """

    def clone(self, new_name: Optional[str] = None) -> 'Cloneable':
        """
        Create a copy of this entity

        Args:
            new_name: Optional name for the cloned entity

        Returns:
            Cloned entity instance
        """
        ...
