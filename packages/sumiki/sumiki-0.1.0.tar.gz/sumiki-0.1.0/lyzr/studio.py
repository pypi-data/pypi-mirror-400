"""
Studio - Main entry point for Lyzr Agent SDK
"""

from typing import Optional
from lyzr.http import HTTPClient
from lyzr.agents import AgentModule
from lyzr.knowledge_base import KnowledgeBaseModule


class Studio:
    """
    Main client for interacting with Lyzr Agent API

    Studio provides a clean interface to all Lyzr Agent API functionality.
    Each resource (agents, memory, artifacts, etc.) is accessible both as
    a module and through convenience methods.

    Example:
        >>> studio = Studio(api_key="sk-xxx")
        >>>
        >>> # Method 1: Direct convenience methods
        >>> agent = studio.create_agent(name="Bot", provider="openai/gpt-4o")
        >>>
        >>> # Method 2: Through module
        >>> agent = studio.agents.create(name="Bot", provider="openai/gpt-4o")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://agent-prod.studio.lyzr.ai",
        timeout: int = 30,
    ):
        """
        Initialize Studio client

        Args:
            api_key: Lyzr API key (reads from LYZR_API_KEY env var if not provided)
            base_url: Base URL for API (default: production URL)
            timeout: Request timeout in seconds

        Raises:
            AuthenticationError: If API key is not provided or invalid

        Example:
            >>> # Using API key directly
            >>> studio = Studio(api_key="sk-xxx")
            >>>
            >>> # Using environment variable
            >>> import os
            >>> os.environ["LYZR_API_KEY"] = "sk-xxx"
            >>> studio = Studio()
        """
        # Initialize HTTP client
        self._http = HTTPClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout
        )

        # Register modules
        self._register_modules()

    def _register_modules(self):
        """Register all SDK modules and inject convenience methods"""

        # Register Agents module
        self.agents = AgentModule(self._http)

        # Inject convenience methods for agents
        # This allows both studio.create_agent() and studio.agents.create()
        self.create_agent = self.agents.create
        self.get_agent = self.agents.get
        self.list_agents = self.agents.list
        self.update_agent = self.agents.update
        self.delete_agent = self.agents.delete
        self.clone_agent = self.agents.clone
        self.bulk_delete_agents = self.agents.bulk_delete

        # Register KnowledgeBase module
        # Note: KnowledgeBaseModule creates its own HTTP client for RAG API
        self.knowledge_bases = KnowledgeBaseModule(self._http)

        # Inject convenience methods for knowledge bases
        self.create_knowledge_base = self.knowledge_bases.create
        self.get_knowledge_base = self.knowledge_bases.get
        self.list_knowledge_bases = self.knowledge_bases.list
        self.delete_knowledge_base = self.knowledge_bases.delete
        self.bulk_delete_knowledge_bases = self.knowledge_bases.bulk_delete

        # Future modules will be registered here:
        # self.memory = MemoryModule(self._http)
        # self.artifacts = ArtifactModule(self._http)
        # ...

    def close(self):
        """Close the HTTP client connection"""
        self._http.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def __repr__(self) -> str:
        """String representation"""
        return f"Studio(base_url='{self._http.base_url}')"
