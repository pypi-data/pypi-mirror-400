from _typeshed import Incomplete
from chromadb.types import Where, WhereDocument
from datetime import datetime
from enum import Enum
from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import DEFAULT_TOP_K as DEFAULT_TOP_K, METADATA_KEYS as METADATA_KEYS
from gllm_datastore.utils.converter import from_langchain as from_langchain, l2_distance_to_similarity_score as l2_distance_to_similarity_score, to_langchain as to_langchain
from gllm_datastore.vector_data_store.mixin.cache_compatible_mixin import CacheCompatibleMixin as CacheCompatibleMixin
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from langchain_core.embeddings import Embeddings
from typing import Any

DEFAULT_NUM_CANDIDATES: int

class ChromaClientType(str, Enum):
    """Enum for different types of ChromaDB clients.

    Attributes:
        MEMORY (str): Client type for an in-memory data store.
        PERSISTENT (str): Client type for a persistent data store.
        HTTP (str): Client type for a client-server architecture.
    """
    MEMORY: str
    PERSISTENT: str
    HTTP: str

class ChromaVectorDataStore(BaseVectorDataStore, CacheCompatibleMixin):
    """Datastore for interacting with ChromaDB.

    This class provides methods to interact with ChromaDB for vector storage and retrieval
    using the langchain-chroma integration.

    Attributes:
        vector_store (Chroma): The langchain Chroma vector store instance.
        collection_name (str): The name of the ChromaDB collection to use.
        num_candidates (int): The maximum number of candidates to consider during search.
        embedding (BaseEMInvoker | Embeddings | None): The embedding model to perform vectorization.
    """
    vector_store: Incomplete
    collection_name: Incomplete
    num_candidates: Incomplete
    def __init__(self, collection_name: str, embedding: BaseEMInvoker | Embeddings | None = None, client_type: ChromaClientType = ..., persist_directory: str | None = None, host: str | None = None, port: int | None = None, headers: dict | None = None, num_candidates: int = ..., **kwargs: Any) -> None:
        """Initialize the ChromaDB vector data store with langchain-chroma.

        Args:
            collection_name (str): Name of the collection to use in ChromaDB.
            embedding (BaseEMInvoker | Embeddings | None, optional): The embedding model to perform vectorization.
                Defaults to None.
            client_type (ChromaClientType, optional): Type of ChromaDB client to use.
                Defaults to ChromaClientType.MEMORY.
            persist_directory (str | None, optional): Directory to persist vector store data.
                Required for PERSISTENT client type. Defaults to None.
            host (str | None, optional): Host address for ChromaDB server.
                Required for HTTP client type. Defaults to None.
            port (int | None, optional): Port for ChromaDB server.
                Required for HTTP client type. Defaults to None.
            headers (dict | None, optional): Headers for ChromaDB server.
                Used for HTTP client type. Defaults to None.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to DEFAULT_NUM_CANDIDATES.
            **kwargs: Additional parameters for Chroma initialization.

        Note:
            num_candidates (int, optional): This constant affects the maximum number of results to consider
            during the search. Index with more documents would need a higher value for the whole documents
            to be considered during search. This happens due to a bug with Chroma's search algorithm as discussed
            in this issue: [3] https://github.com/langchain-ai/langchain/issues/1946
        """
    async def get_size(self) -> int:
        """Returns the total number of vectors in the index.

        If the index is not initialized returns 0.

        Returns:
            int: The total number of vectors.
        """
    async def query(self, query: str, top_k: int = ..., retrieval_params: dict[str, dict[str, str]] | None = None) -> list[Chunk]:
        '''Query the vector data store for similar chunks with similarity scores.

        Args:
            query (str): The query string to find similar chunks for.
            top_k (int, optional): Maximum number of results to return. Defaults to DEFAULT_TOP_K.
            retrieval_params (dict[str, Any] | None, optional): Additional parameters for retrieval.
                - filter (Where, optional): A Where type dict used to filter the retrieval by the metadata keys.
                    E.g. `{"$and": [{"color" : "red"}, {"price": {"$gte": 4.20}]}}`.
                - where_document (WhereDocument, optional): A WhereDocument type dict used to filter the retrieval by
                    the document content. E.g. `{$contains: {"text": "hello"}}`.
                Defaults to None.

        Returns:
            list[Chunk]: A list of Chunk objects matching the query, with similarity scores.
        '''
    async def query_by_id(self, id: str | list[str]) -> list[Chunk]:
        """Retrieve chunks by their IDs.

        Args:
            id (str | list[str]): A single ID or a list of IDs to retrieve.

        Returns:
            list[Chunk]: A list of retrieved Chunk objects.
        """
    async def add_chunks(self, chunks: Chunk | list[Chunk], **kwargs) -> list[str]:
        """Add chunks to the vector data store.

        Args:
            chunks (Chunk | list[Chunk]): A single chunk or list of chunks to add.
            **kwargs: Additional keyword arguments for the add operation.

        Returns:
            list[str]: List of IDs of the added chunks.
        """
    async def delete_chunks(self, where: Where | None = None, where_document: WhereDocument | None = None, **kwargs: Any) -> None:
        '''Delete chunks from the vector data store.

        Args:
            where (Where | None, optional): A Where type dict used to filter the deletion by metadata.
                E.g. `{"source": "mydoc"}`. Defaults to None.
            where_document (WhereDocument | None, optional): A WhereDocument type dict used to filter the deletion by
                the document content. E.g. `{$contains: {"text": "hello"}}`. Defaults to None.
            **kwargs: Additional keyword arguments for the delete operation.

        Note:
            If no filter criteria is provided, all chunks in the collection will be deleted. Please use with caution.
        '''
    async def delete_chunks_by_ids(self, ids: str | list[str], **kwargs: Any) -> None:
        """Delete chunks from the vector data store by IDs.

        Args:
            ids (str | list[str]): A single ID or a list of IDs to delete.
            **kwargs: Additional keyword arguments.

        Note:
            If no IDs are provided, no chunks will be deleted.
        """
    async def exact_match(self, key: str, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that exactly match the given key.

        This method searches for documents with the exact original_key in metadata.

        Args:
            key (str): The key to match.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The value stored with the exact key match, or None if no match is found.
        '''
    async def fuzzy_match(self, key: str, max_distance: int = 2, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that approximately match the given key using fuzzy matching.

        Args:
            key (str): The key to match.
            max_distance (int): Maximum allowed Levenshtein distance for fuzzy matching.
                Higher values are more lenient. Defaults to 2.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The value with the closest fuzzy match to the key, or None if no match meets the threshold.
        '''
    async def semantic_match(self, key: str, min_similarity: float = 0.2, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that semantically match the given key using vector similarity.

        Args:
            key (str): The key to match.
            min_similarity (float): Minimum similarity score for semantic matching
                (higher values are more strict). Ranges from 0 to 1. Defaults to 0.8.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The semantically closest value, or None if no match meets the min_similarity.
        '''
    async def delete_expired_entries(self, now: datetime, max_size: int = 10000) -> None:
        """Delete expired entries (for TTL eviction).

        Args:
            now (datetime): The current datetime for comparison.
            max_size (int): The maximum number of entries to return. Defaults to 10000.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for ChromaVectorDataStore.
        """
    async def delete_least_frequently_used_entries(self, num_entries: int) -> None:
        """Delete least frequently used entries (for LFU eviction).

        Args:
            num_entries (int): Number of entries to return.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for ChromaVectorDataStore.
        """
    async def delete_least_recently_used_entries(self, num_entries: int) -> None:
        """Delete least recently used entries (for LRU eviction).

        Args:
            num_entries (int): Number of entries to return.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for ChromaVectorDataStore.
        """
    async def delete_entries_by_key(self, key: str, metadata: dict[str, Any] | None = None) -> None:
        '''Delete entries by key.

        Args:
            key (str): The key to delete entries for.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for ChromaVectorDataStore.
        '''
    async def clear(self) -> None:
        """Clear all entries in the storage.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for ChromaVectorDataStore.
        """
    async def query_by_field(self, retrieval_params: dict[str, Any], limit: int | None = None, **kwargs) -> list[Chunk]:
        """Retrieve documents that match specific metadata constraints.

        This method filters and returns stored chunks based on metadata values
        rather than vector similarity. It is particularly useful for structured lookups,
        such as retrieving all chunks from a certain source, tagged with a specific label,
        or authored by a particular user.

        Unlike semantic search methods, `query_by_field` operates purely on metadata fields
        associated with each document, allowing precise filtering based on key-value pairs.

        Args:
            retrieval_params (dict[str, Any]): A dictionary defining filter criteria. Common keys include:
                - `filter` (dict): A dictionary of metadata field conditions.
                - `where_document` (dict, optional): Conditions based on document content.
            limit (int | None, optional): The maximum number of results to return. If None, all matching
                documents will be returned.
            **kwargs: Additional arguments to support datastore-specific behavior or filtering logic.

        Returns:
            list[Chunk]: A list of `Chunk` objects that satisfy the metadata criteria.

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
    async def query_by_vector(self, vector: list[float], top_k: int = ..., min_similarity: float = 0.8, retrieval_params: dict | None = None) -> list[Chunk]:
        """Search for documents that are similar to a given vector.

        Args:
            vector (list[float]): The query embedding vector to compare against stored vectors.
            top_k (int, optional): The number of top results to return. Defaults to DEFAULT_TOP_K.
            min_similarity (float): Minimum similarity score for vector similarity.
            retrieval_params (dict | None, optional): Filter parameters to narrow the search:
                - filter (Where): Metadata-based filter.
                - where_document (WhereDocument): Content-based filter.
                Defaults to None.

        Returns:
            list[Chunk]: A list of Chunk objects with similarity scores based on the input vector.
        """
