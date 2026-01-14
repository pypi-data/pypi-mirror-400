"""
Knowledge Base module for managing RAG configurations
"""

from typing import Optional, List, Dict, Any, Union, TYPE_CHECKING
from pydantic import BaseModel, Field, validator, ConfigDict, PrivateAttr, model_validator
import re
import random
import string
from lyzr.base import BaseModule
from lyzr.vector_stores import VectorStoreResolver
from lyzr.exceptions import ValidationError

if TYPE_CHECKING:
    from lyzr.http import HTTPClient


class QueryResult(BaseModel):
    """Result from knowledge base query"""
    text: str = Field(..., description="Retrieved text chunk")
    score: float = Field(default=0.0, ge=0.0, le=1.0, description="Relevance score (0-1)")
    source: Optional[str] = Field(None, description="Source document name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    # Optional fields
    id: Optional[str] = Field(None, description="Document/chunk ID")
    page: Optional[int] = Field(None, description="Page number (for PDFs)")
    chunk_index: Optional[int] = Field(None, description="Chunk index in document")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)


class Document(BaseModel):
    """Document in knowledge base"""
    id: str = Field(..., description="Document ID")
    source: str = Field(..., description="Source identifier")
    text: Optional[str] = Field(None, description="Document text content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Document metadata")
    created_at: Optional[str] = Field(None, description="Creation timestamp")

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump(exclude_none=True)


class KnowledgeBaseConfig(BaseModel):
    """Configuration for creating a knowledge base"""

    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Knowledge base name (lowercase, numbers, underscores only)"
    )
    collection_name: Optional[str] = Field(
        None,
        description="Vector DB collection name (auto-generated if not provided)"
    )
    description: Optional[str] = Field(None, max_length=1000, description="KB description")

    # Vector store configuration
    vector_store: str = Field("qdrant", description="Vector store type (qdrant, weaviate, etc.)")
    vector_db_credential_id: Optional[str] = Field(None, description="Custom vector DB credential ID")
    vector_store_provider: Optional[str] = Field(None, description="Provider display name")

    # Model configuration
    embedding_model: str = Field("text-embedding-3-large", description="Embedding model name")
    embedding_credential_id: str = Field("lyzr_openai", description="Embedding credential ID")
    llm_model: str = Field("gpt-4o", description="LLM model for query processing")
    llm_credential_id: str = Field("lyzr_openai", description="LLM credential ID")

    # Advanced settings
    semantic_data_model: bool = Field(False, description="Enable semantic data modeling")
    user_id: Optional[str] = Field(None, description="User ID")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    model_config = ConfigDict(validate_assignment=True)

    @model_validator(mode='before')
    @classmethod
    def process_config(cls, data: Any) -> Any:
        """Process and validate configuration"""
        if isinstance(data, dict):
            # Validate name format
            if 'name' in data:
                name = data['name']
                if not re.match(r'^[a-z0-9_]+$', name):
                    raise ValueError(
                        "Knowledge base name must contain only lowercase letters, numbers, and underscores. "
                        f"Invalid: '{name}'. Examples: 'customer_support', 'product_docs_2024', 'faq_kb'"
                    )

            # Auto-generate collection_name if not provided
            if 'collection_name' not in data or not data['collection_name']:
                if 'name' in data:
                    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
                    data['collection_name'] = f"{data['name']}{suffix}"

            # Resolve vector store credentials
            if 'vector_store' in data:
                try:
                    provider = VectorStoreResolver.resolve(data['vector_store'])

                    # Set credential and display name if not explicitly provided
                    if 'vector_db_credential_id' not in data or not data['vector_db_credential_id']:
                        data['vector_db_credential_id'] = provider.credential_id
                    if 'vector_store_provider' not in data or not data['vector_store_provider']:
                        data['vector_store_provider'] = provider.display_name
                except ValueError as e:
                    raise ValueError(f"Invalid vector store: {str(e)}")

        return data

    def to_api_dict(self) -> Dict[str, Any]:
        """Convert to API request format"""
        return {
            "name": self.name,
            "collection_name": self.collection_name,
            "description": self.description,
            "vector_db_credential_id": self.vector_db_credential_id,
            "vector_store_provider": self.vector_store_provider,
            "embedding_model": self.embedding_model,
            "embedding_credential_id": self.embedding_credential_id,
            "llm_model": self.llm_model,
            "llm_credential_id": self.llm_credential_id,
            "semantic_data_model": self.semantic_data_model,
            "user_id": self.user_id,
            "meta_data": self.meta_data,
        }


class KnowledgeBaseRuntimeConfig:
    """
    Runtime configuration for KB when passed to agent.run()

    Allows customizing retrieval parameters per-call.
    """

    def __init__(
        self,
        kb: 'KnowledgeBase',
        top_k: int = 10,
        retrieval_type: str = "basic",
        score_threshold: float = 0.0,
        time_decay_factor: float = 0.4,
        **kwargs
    ):
        self.kb = kb
        self.top_k = top_k
        self.retrieval_type = retrieval_type
        self.score_threshold = score_threshold
        self.time_decay_factor = time_decay_factor
        self.extra_config = kwargs

    def to_agentic_config(self) -> Dict[str, Any]:
        """Convert to agentic_rag config format"""
        return self.kb.to_agentic_config(
            top_k=self.top_k,
            retrieval_type=self.retrieval_type,
            score_threshold=self.score_threshold,
            time_decay_factor=self.time_decay_factor,
            **self.extra_config
        )


class KnowledgeBase(BaseModel):
    """
    Smart KnowledgeBase - both data and behavior

    Represents a RAG configuration that can store and query documents.
    """

    id: str = Field(..., alias="_id", description="Knowledge base ID")
    name: Optional[str] = Field(None, description="Knowledge base name (not returned by API)")
    collection_name: str = Field(..., description="Vector DB collection name")
    description: Optional[str] = Field(None, description="KB description")

    # Provider configuration
    vector_db_credential_id: str = Field(..., description="Vector DB credential ID")
    vector_store_provider: str = Field(..., description="Vector store provider display name")
    embedding_model: str = Field(..., description="Embedding model name")
    embedding_credential_id: str = Field(..., description="Embedding credential ID")
    llm_model: str = Field(..., description="LLM model name")
    llm_credential_id: str = Field(..., description="LLM credential ID")

    # Settings
    semantic_data_model: bool = Field(default=False, description="Semantic data modeling enabled")
    user_id: Optional[str] = Field(None, description="User ID")
    api_key: Optional[str] = Field(None, description="API key")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    # Metadata
    created_at: Optional[str] = Field(None, description="Creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last update timestamp")

    # Private fields (injected by KnowledgeBaseModule)
    _http: Optional['HTTPClient'] = PrivateAttr(default=None)
    _kb_module: Optional[Any] = PrivateAttr(default=None)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    def _ensure_clients(self):
        """Ensure HTTP client is available"""
        if not self._http or not self._kb_module:
            raise RuntimeError(
                "KnowledgeBase not properly initialized. "
                "Use Studio.create_knowledge_base() or Studio.get_knowledge_base()"
            )

    def add_pdf(
        self,
        file_path: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        **kwargs
    ) -> bool:
        """
        Add PDF document to knowledge base

        Args:
            file_path: Path to PDF file
            chunk_size: Size of text chunks (default: 1024)
            chunk_overlap: Overlap between chunks (default: 128)
            **kwargs: Additional parameters

        Returns:
            bool: True if successful

        Example:
            >>> kb = studio.create_knowledge_base(name="docs")
            >>> kb.add_pdf("manual.pdf", chunk_size=2048)
        """
        self._ensure_clients()
        return self._kb_module._train_pdf(
            self.id, file_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs
        )

    def add_docx(
        self,
        file_path: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        **kwargs
    ) -> bool:
        """
        Add DOCX document to knowledge base

        Args:
            file_path: Path to DOCX file
            chunk_size: Size of text chunks (default: 1024)
            chunk_overlap: Overlap between chunks (default: 128)
            **kwargs: Additional parameters

        Returns:
            bool: True if successful

        Example:
            >>> kb.add_docx("report.docx")
        """
        self._ensure_clients()
        return self._kb_module._train_docx(
            self.id, file_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs
        )

    def add_txt(
        self,
        file_path: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        **kwargs
    ) -> bool:
        """
        Add TXT file to knowledge base

        Args:
            file_path: Path to TXT file
            chunk_size: Size of text chunks (default: 1024)
            chunk_overlap: Overlap between chunks (default: 128)
            **kwargs: Additional parameters

        Returns:
            bool: True if successful

        Example:
            >>> kb.add_txt("faq.txt")
        """
        self._ensure_clients()
        return self._kb_module._train_txt(
            self.id, file_path, chunk_size=chunk_size, chunk_overlap=chunk_overlap, **kwargs
        )

    def add_website(
        self,
        url: Union[str, List[str]],
        max_pages: int = 10,
        max_depth: int = 2,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        **kwargs
    ) -> bool:
        """
        Add website content to knowledge base

        Args:
            url: Website URL or list of URLs
            max_pages: Maximum pages to crawl (default: 10)
            max_depth: Maximum crawl depth (default: 2)
            chunk_size: Size of text chunks (default: 1024)
            chunk_overlap: Overlap between chunks (default: 128)
            **kwargs: Additional parameters (dynamic_content_wait_secs, etc.)

        Returns:
            bool: True if successful

        Example:
            >>> kb.add_website("https://docs.company.com", max_pages=50, max_depth=3)
            >>> kb.add_website(["https://help.com", "https://faq.com"])
        """
        self._ensure_clients()
        urls = [url] if isinstance(url, str) else url
        return self._kb_module._train_website(
            self.id,
            urls,
            max_pages=max_pages,
            max_depth=max_depth,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def add_text(
        self,
        text: str,
        source: str,
        chunk_size: int = 1024,
        chunk_overlap: int = 128,
        **kwargs
    ) -> bool:
        """
        Add raw text to knowledge base

        Args:
            text: Text content
            source: Source identifier
            chunk_size: Size of text chunks (default: 1024)
            chunk_overlap: Overlap between chunks (default: 128)
            **kwargs: Additional parameters

        Returns:
            bool: True if successful

        Example:
            >>> kb.add_text("FAQ: Business hours are 9am-5pm", source="faq.txt")
        """
        self._ensure_clients()
        return self._kb_module._train_text(
            self.id,
            [{"text": text, "source": source}],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            **kwargs
        )

    def query(
        self,
        query: str,
        top_k: int = 5,
        retrieval_type: str = "basic",
        score_threshold: float = 0.0,
        **kwargs
    ) -> List[QueryResult]:
        """
        Query the knowledge base

        Args:
            query: Search query string
            top_k: Number of results to return (default: 5)
            retrieval_type: Type of retrieval - one of:
                - 'basic': Standard vector similarity search
                - 'mmr': Maximal Marginal Relevance (diverse results)
                - 'hyde': Hypothetical Document Embeddings
                - 'time_aware': Time-decay weighted retrieval
            score_threshold: Minimum relevance score (0.0 to 1.0)
            **kwargs: Additional parameters (lambda_param, time_decay_factor)

        Returns:
            List[QueryResult]: List of relevant results

        Example:
            >>> results = kb.query("What are business hours?", top_k=3)
            >>> for result in results:
            ...     print(f"{result.score:.2f}: {result.text}")
        """
        self._ensure_clients()
        return self._kb_module._query(
            self.id,
            query,
            top_k=top_k,
            retrieval_type=retrieval_type,
            score_threshold=score_threshold,
            **kwargs
        )

    def list_documents(self) -> List[Document]:
        """
        List all documents in knowledge base

        Returns:
            List[Document]: List of documents

        Example:
            >>> docs = kb.list_documents()
            >>> for doc in docs:
            ...     print(doc.source)
        """
        self._ensure_clients()
        return self._kb_module._list_documents(self.id)

    def delete_documents(self, doc_ids: List[str]) -> bool:
        """
        Delete specific documents from knowledge base

        Args:
            doc_ids: List of document IDs to delete

        Returns:
            bool: True if successful

        Example:
            >>> kb.delete_documents(["doc_123", "doc_456"])
        """
        self._ensure_clients()
        return self._kb_module._delete_documents(self.id, doc_ids)

    def reset(self) -> bool:
        """
        Clear all documents from knowledge base

        Removes all documents but keeps the KB configuration.

        Returns:
            bool: True if successful

        Example:
            >>> kb.reset()  # Removes all documents
        """
        self._ensure_clients()
        return self._kb_module._reset(self.id)

    def update(self, **kwargs) -> 'KnowledgeBase':
        """
        Update knowledge base configuration

        Args:
            **kwargs: Fields to update (description, etc.)

        Returns:
            KnowledgeBase: Updated KB instance

        Example:
            >>> kb = kb.update(description="Updated description")
        """
        self._ensure_clients()
        return self._kb_module.update(self.id, **kwargs)

    def delete(self) -> bool:
        """
        Delete this knowledge base

        Returns:
            bool: True if successful

        Example:
            >>> kb.delete()
        """
        self._ensure_clients()
        return self._kb_module.delete(self.id)

    def with_config(
        self,
        top_k: int = 10,
        retrieval_type: str = "basic",
        score_threshold: float = 0.0,
        time_decay_factor: float = 0.4,
        **kwargs
    ) -> 'KnowledgeBaseRuntimeConfig':
        """
        Create runtime config for this KB

        Used when passing KB to agent.run() with custom settings.

        Args:
            top_k: Number of results to retrieve (default: 10)
            retrieval_type: Retrieval method (basic, semantic, keyword, hybrid)
            score_threshold: Minimum relevance score (0.0 to 1.0)
            time_decay_factor: Time-based relevance decay factor
            **kwargs: Additional config parameters

        Returns:
            KnowledgeBaseRuntimeConfig: Runtime configuration wrapper

        Example:
            >>> # Pass KB with custom config to agent.run()
            >>> response = agent.run(
            ...     "Question?",
            ...     knowledge_bases=[kb.with_config(top_k=5, score_threshold=0.7)]
            ... )
        """
        return KnowledgeBaseRuntimeConfig(
            kb=self,
            top_k=top_k,
            retrieval_type=retrieval_type,
            score_threshold=score_threshold,
            time_decay_factor=time_decay_factor,
            **kwargs
        )

    def to_agentic_config(
        self,
        top_k: int = 10,
        retrieval_type: str = "basic",
        score_threshold: float = 0.0,
        time_decay_factor: float = 0.4
    ) -> Dict[str, Any]:
        """
        Convert to agentic_rag config format

        This is the format expected by the inference API features array.

        Args:
            top_k: Number of results to retrieve
            retrieval_type: Retrieval method
            score_threshold: Minimum relevance score
            time_decay_factor: Time-based decay factor

        Returns:
            Dict: Configuration in agentic_rag format

        Example:
            >>> config = kb.to_agentic_config(top_k=5)
            >>> # Used internally when KB is passed to agent.run()
        """
        return {
            "rag_id": self.id,
            "name": self.name,
            "description": self.description or f"Knowledge base: {self.name}",
            "top_k": top_k,
            "retrieval_type": retrieval_type,
            "score_threshold": score_threshold,
            "time_decay_factor": time_decay_factor
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excludes private fields)"""
        return self.model_dump(by_alias=False, exclude_none=True)

    def __str__(self) -> str:
        return f"KnowledgeBase(id='{self.id}', name='{self.name}', provider='{self.vector_store_provider}')"

    def __repr__(self) -> str:
        return self.__str__()


class KnowledgeBaseList(BaseModel):
    """List of knowledge bases"""
    knowledge_bases: List[KnowledgeBase] = Field(default_factory=list, description="List of KBs")
    total: Optional[int] = Field(None, description="Total count")

    def __iter__(self):
        return iter(self.knowledge_bases)

    def __len__(self):
        return len(self.knowledge_bases)

    def __getitem__(self, index):
        return self.knowledge_bases[index]


class KnowledgeBaseModule(BaseModule):
    """
    Module for managing knowledge bases (RAG configurations)

    Can be used standalone or through Studio client.

    Example (Standalone):
        >>> from lyzr.http import HTTPClient
        >>> from lyzr.knowledge_base import KnowledgeBaseModule
        >>> http = HTTPClient(api_key="sk-xxx", base_url="https://rag-prod.studio.lyzr.ai")
        >>> kbs = KnowledgeBaseModule(http)
        >>> kb = kbs.create(name="support_kb")

    Example (Through Studio):
        >>> from lyzr import Studio
        >>> studio = Studio(api_key="sk-xxx")
        >>> kb = studio.create_knowledge_base(name="support_kb")
    """

    def __init__(self, http_client: 'HTTPClient'):
        """
        Initialize KnowledgeBaseModule

        Note: Creates a separate HTTP client for RAG API (different base URL)
        Uses longer timeout (300s) for document processing and website crawling.
        """
        from lyzr.http import HTTPClient

        # Create new HTTP client for RAG API with longer timeout
        # Document processing and website crawling can take several minutes
        self._http = HTTPClient(
            api_key=http_client.api_key,
            base_url="https://rag-prod.studio.lyzr.ai",
            timeout=300  # 5 minutes for RAG operations
        )

    def _make_smart_kb(self, kb_data: Dict[str, Any], name: Optional[str] = None) -> KnowledgeBase:
        """
        Create smart KnowledgeBase with injected clients

        Args:
            kb_data: Raw KB data from API
            name: Optional name to inject (API doesn't return it)

        Returns:
            KnowledgeBase: Smart KB with methods
        """
        # Normalize id field (create returns "id", list/get returns "_id")
        if "id" in kb_data and "_id" not in kb_data:
            kb_data["_id"] = kb_data["id"]

        # Inject name if provided (API doesn't return it)
        if name and "name" not in kb_data:
            kb_data["name"] = name

        kb = KnowledgeBase(**kb_data)
        kb._http = self._http
        kb._kb_module = self
        return kb

    def create(
        self,
        name: str,
        vector_store: str = "qdrant",
        embedding_model: str = "text-embedding-3-large",
        llm_model: str = "gpt-4o",
        description: Optional[str] = None,
        **kwargs
    ) -> KnowledgeBase:
        """
        Create a new knowledge base

        Args:
            name: KB name (lowercase, numbers, underscores only)
            vector_store: Vector store type (qdrant, weaviate, pg_vector, milvus, neptune)
            embedding_model: Embedding model name (default: text-embedding-3-large)
            llm_model: LLM model name (default: gpt-4o)
            description: KB description
            **kwargs: Additional configuration

        Returns:
            KnowledgeBase: Created smart KB object

        Raises:
            ValidationError: If name format is invalid
            APIError: If API request fails

        Example:
            >>> kb = kbs.create(
            ...     name="customer_support",
            ...     description="Customer support docs",
            ...     vector_store="qdrant"
            ... )
        """
        # Build configuration
        config = KnowledgeBaseConfig(
            name=name,
            vector_store=vector_store,
            embedding_model=embedding_model,
            llm_model=llm_model,
            description=description,
            **kwargs
        )

        # Make API request
        response = self._http.post("/v3/rag/", json=config.to_api_dict())

        # API returns KB data but without the name field
        # Inject the name we used for creation
        return self._make_smart_kb(response, name=name)

    def get(self, kb_id: str) -> KnowledgeBase:
        """
        Get knowledge base by ID

        Args:
            kb_id: Knowledge base ID

        Returns:
            KnowledgeBase: Smart KB object

        Raises:
            NotFoundError: If KB doesn't exist
            APIError: If API request fails

        Example:
            >>> kb = kbs.get("kb_abc123")
            >>> print(kb.name)
        """
        response = self._http.get(f"/v3/rag/{kb_id}/")
        return self._make_smart_kb(response)

    def list(self, user_id: Optional[str] = None) -> KnowledgeBaseList:
        """
        List knowledge bases

        Args:
            user_id: Optional user ID to filter by (defaults to API key)

        Returns:
            KnowledgeBaseList: List of KBs (iterable)

        Example:
            >>> all_kbs = kbs.list()
            >>> for kb in all_kbs:
            ...     print(kb.name)
        """
        # Use api_key as user_id if not provided
        if not user_id:
            # Extract from HTTP client - use the api_key value
            user_id = self._http.api_key

        response = self._http.get(f"/v3/rag/user/{user_id}/")

        # Handle response format - API returns {"configs": [...]}
        if isinstance(response, dict) and "configs" in response:
            kb_data_list = response["configs"]
            kb_list = [self._make_smart_kb(kb_data) for kb_data in kb_data_list]
            return KnowledgeBaseList(
                knowledge_bases=kb_list,
                total=len(kb_list)
            )
        elif isinstance(response, list):
            kb_list = [self._make_smart_kb(kb_data) for kb_data in response]
            return KnowledgeBaseList(knowledge_bases=kb_list, total=len(kb_list))
        elif isinstance(response, dict):
            kb_data = response.get("knowledge_bases", response.get("data", []))
            kb_list = [self._make_smart_kb(kb) for kb in kb_data]
            return KnowledgeBaseList(
                knowledge_bases=kb_list,
                total=response.get("total", len(kb_list))
            )
        else:
            return KnowledgeBaseList(knowledge_bases=[])

    def update(self, kb_id: str, **kwargs) -> KnowledgeBase:
        """
        Update knowledge base configuration

        Args:
            kb_id: Knowledge base ID
            **kwargs: Fields to update

        Returns:
            KnowledgeBase: Updated KB object

        Example:
            >>> kb = kbs.update("kb_123", description="Updated desc")
        """
        if not kwargs:
            raise ValidationError("No fields provided for update")

        response = self._http.put(f"/v3/rag/{kb_id}/", json=kwargs)

        # API returns {"success": True}, not KB data
        # Fetch updated KB
        return self.get(kb_id)

    def delete(self, kb_id: str) -> bool:
        """
        Delete a knowledge base

        Args:
            kb_id: Knowledge base ID

        Returns:
            bool: True if successful

        Example:
            >>> success = kbs.delete("kb_123")
        """
        return self._http.delete(f"/v3/rag/{kb_id}/")

    def bulk_delete(self, kb_ids: List[str]) -> bool:
        """
        Delete multiple knowledge bases

        Args:
            kb_ids: List of KB IDs to delete

        Returns:
            bool: True if successful

        Example:
            >>> kbs.bulk_delete(["kb_1", "kb_2", "kb_3"])
        """
        if not kb_ids:
            raise ValidationError("kb_ids cannot be empty")

        response = self._http.post(
            "/v3/rag/bulk-delete/",
            json={"config_ids": kb_ids}
        )
        return True

    # Internal methods (used by KnowledgeBase methods)

    def _train_pdf(self, rag_id: str, file_path: str, **kwargs) -> bool:
        """Internal: Add PDF to knowledge base"""
        return self._http.post_file(
            path="/v3/train/pdf/",
            file_path=file_path,
            file_field="file",
            params={"rag_id": rag_id},
            data={k: str(v) for k, v in kwargs.items() if k in ["chunk_size", "chunk_overlap", "data_parser"]}
        )
        return True

    def _train_docx(self, rag_id: str, file_path: str, **kwargs) -> bool:
        """Internal: Add DOCX to knowledge base"""
        self._http.post_file(
            path="/v3/train/docx/",
            file_path=file_path,
            file_field="file",
            params={"rag_id": rag_id},
            data={k: str(v) for k, v in kwargs.items() if k in ["chunk_size", "chunk_overlap", "data_parser"]}
        )
        return True

    def _train_txt(self, rag_id: str, file_path: str, **kwargs) -> bool:
        """Internal: Add TXT to knowledge base"""
        self._http.post_file(
            path="/v3/train/txt/",
            file_path=file_path,
            file_field="file",
            params={"rag_id": rag_id},
            data={k: str(v) for k, v in kwargs.items() if k in ["chunk_size", "chunk_overlap", "data_parser"]}
        )
        return True

    def _train_website(self, rag_id: str, urls: List[str], **kwargs) -> bool:
        """Internal: Add website to knowledge base"""
        payload = {
            "urls": urls,
            "source": kwargs.get("source", "website"),
            "max_crawl_pages": kwargs.get("max_pages", 10),
            "max_crawl_depth": kwargs.get("max_depth", 2),
            "chunk_size": kwargs.get("chunk_size", 1024),
            "chunk_overlap": kwargs.get("chunk_overlap", 128),
        }

        # Add optional parameters
        if "dynamic_content_wait_secs" in kwargs:
            payload["dynamic_content_wait_secs"] = kwargs["dynamic_content_wait_secs"]

        self._http.post(
            path="/v3/train/website/",
            params={"rag_id": rag_id},
            json=payload
        )
        return True

    def _train_text(self, rag_id: str, data: List[Dict[str, str]], **kwargs) -> bool:
        """Internal: Add text to knowledge base"""
        payload = {
            "data": data,
            "chunk_size": kwargs.get("chunk_size", 1024),
            "chunk_overlap": kwargs.get("chunk_overlap", 128),
        }

        self._http.post(
            path="/v3/train/text/",
            params={"rag_id": rag_id},
            json=payload
        )
        return True

    def _query(self, rag_id: str, query: str, **kwargs) -> List[QueryResult]:
        """Internal: Query knowledge base"""
        params = {
            "query": query,
            "top_k": kwargs.get("top_k", 5),
        }

        # Add optional parameters
        if "retrieval_type" in kwargs:
            params["retrieval_type"] = kwargs["retrieval_type"]
        if "score_threshold" in kwargs:
            params["score_threshold"] = kwargs["score_threshold"]
        if "lambda_param" in kwargs:
            params["lambda_param"] = kwargs["lambda_param"]
        if "time_decay_factor" in kwargs:
            params["time_decay_factor"] = kwargs["time_decay_factor"]

        response = self._http.get(f"/v3/rag/{rag_id}/retrieve/", params=params)

        # Parse results
        results = response.get("results", [])
        return [QueryResult(**result) for result in results]

    def _list_documents(self, rag_id: str) -> List[Document]:
        """Internal: List documents in KB"""
        response = self._http.get(f"/v3/rag/documents/{rag_id}/")

        # API returns a simple list of document names (strings)
        if isinstance(response, list):
            # Convert strings to Document objects
            return [
                Document(id=f"doc_{i}", source=doc_name, text=None)
                for i, doc_name in enumerate(response)
            ]
        else:
            # Fallback if format changes
            documents = response.get("documents", [])
            return [Document(**doc) if isinstance(doc, dict) else Document(id=f"doc_{i}", source=str(doc)) for i, doc in enumerate(documents)]

    def _delete_documents(self, rag_id: str, doc_ids: List[str]) -> bool:
        """Internal: Delete documents from KB"""
        self._http.delete(
            f"/v3/rag/{rag_id}/docs/",
            json_body={"document_ids": doc_ids}
        )
        return True

    def _reset(self, rag_id: str) -> bool:
        """Internal: Clear all documents from KB"""
        self._http.delete(f"/v3/rag/{rag_id}/reset/")
        return True
