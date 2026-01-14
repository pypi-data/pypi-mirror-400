"""
Vector store provider definitions for Lyzr Knowledge Base

Similar to providers.py but for vector databases used in RAG configurations.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class VectorStoreType(str, Enum):
    """Supported vector store types"""
    QDRANT = "qdrant"
    WEAVIATE = "weaviate"
    PG_VECTOR = "pg_vector"
    MILVUS = "milvus"
    NEPTUNE = "neptune"


class VectorStoreProvider(BaseModel):
    """Vector store provider configuration"""
    provider_id: str = Field(..., description="Provider identifier (e.g., 'qdrant')")
    credential_id: str = Field(..., description="Default Lyzr credential ID")
    display_name: str = Field(..., description="Display name (e.g., 'Qdrant [Lyzr 2]')")
    documentation_link: Optional[str] = Field(None, description="Documentation URL")

    model_config = ConfigDict(frozen=True)


# Define vector store providers with default Lyzr credentials
_VECTOR_STORES_DATA: Dict[VectorStoreType, VectorStoreProvider] = {
    VectorStoreType.QDRANT: VectorStoreProvider(
        provider_id="qdrant",
        credential_id="lyzr_qdrant_2",
        display_name="Qdrant [Lyzr 2]",
        documentation_link="https://qdrant.tech/documentation"
    ),
    VectorStoreType.WEAVIATE: VectorStoreProvider(
        provider_id="weaviate",
        credential_id="lyzr_weaviate",
        display_name="Weaviate [Lyzr]",
        documentation_link="https://weaviate.io/developers/weaviate"
    ),
    VectorStoreType.PG_VECTOR: VectorStoreProvider(
        provider_id="pg_vector",
        credential_id="lyzr_pg_vector",
        display_name="PG-Vector [Lyzr]",
        documentation_link="https://supabase.github.io/vecs/"
    ),
    VectorStoreType.MILVUS: VectorStoreProvider(
        provider_id="milvus",
        credential_id="lyzr_milvus",
        display_name="Milvus [Lyzr]",
        documentation_link="https://milvus.io/docs"
    ),
    VectorStoreType.NEPTUNE: VectorStoreProvider(
        provider_id="neptune",
        credential_id="lyzr_neptune",
        display_name="Amazon Neptune [Lyzr]",
        documentation_link="https://docs.aws.amazon.com/neptune"
    ),
}


class VectorStoreResolver:
    """Resolve vector store strings to provider information"""

    # Store name aliases for easier parsing
    STORE_ALIASES = {
        'qdrant': VectorStoreType.QDRANT,
        'weaviate': VectorStoreType.WEAVIATE,
        'pg_vector': VectorStoreType.PG_VECTOR,
        'pg-vector': VectorStoreType.PG_VECTOR,
        'pgvector': VectorStoreType.PG_VECTOR,
        'milvus': VectorStoreType.MILVUS,
        'neptune': VectorStoreType.NEPTUNE,
        'amazon-neptune': VectorStoreType.NEPTUNE,
    }

    @classmethod
    def resolve(cls, store: str) -> VectorStoreProvider:
        """
        Resolve vector store string to provider information

        Args:
            store: Vector store name (e.g., 'qdrant', 'weaviate')

        Returns:
            VectorStoreProvider: Provider configuration

        Raises:
            ValueError: If store is not recognized

        Examples:
            >>> provider = VectorStoreResolver.resolve('qdrant')
            >>> print(provider.credential_id)
            lyzr_qdrant_2
            >>> print(provider.display_name)
            Qdrant [Lyzr 2]
        """
        store_lower = store.strip().lower()

        if store_lower not in cls.STORE_ALIASES:
            available = ', '.join(sorted(set(cls.STORE_ALIASES.keys())))
            raise ValueError(
                f"Unknown vector store: '{store}'. "
                f"Available stores: {available}"
            )

        store_type = cls.STORE_ALIASES[store_lower]
        return _VECTOR_STORES_DATA[store_type]

    @classmethod
    def get_provider(cls, store_type: VectorStoreType) -> VectorStoreProvider:
        """Get provider configuration by type"""
        return _VECTOR_STORES_DATA[store_type]

    @classmethod
    def get_all_providers(cls) -> Dict[VectorStoreType, VectorStoreProvider]:
        """Get all vector store provider configurations"""
        return _VECTOR_STORES_DATA.copy()

    @classmethod
    def get_all_stores(cls) -> Dict[str, str]:
        """Get all available vector stores"""
        return {
            provider.provider_id: provider.display_name
            for provider in _VECTOR_STORES_DATA.values()
        }


# Convenience function
def resolve_vector_store(store: str) -> VectorStoreProvider:
    """
    Resolve a vector store string to provider information

    Args:
        store: Vector store name (e.g., 'qdrant')

    Returns:
        VectorStoreProvider: Provider configuration

    Examples:
        >>> provider = resolve_vector_store('qdrant')
        >>> print(f"{provider.provider_id} → {provider.credential_id}")
        qdrant → lyzr_qdrant_2
    """
    return VectorStoreResolver.resolve(store)
