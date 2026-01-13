from _typeshed import Incomplete
from datetime import datetime
from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import DEFAULT_TOP_K as DEFAULT_TOP_K, METADATA_KEYS as METADATA_KEYS
from gllm_datastore.utils.converter import cosine_distance_to_similarity_score as cosine_distance_to_similarity_score, similarity_score_to_cosine_distance as similarity_score_to_cosine_distance
from gllm_datastore.vector_data_store.mixin.cache_compatible_mixin import CacheCompatibleMixin as CacheCompatibleMixin
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from redis import Redis as Redis
from redisvl.query.filter import FilterExpression as FilterExpression
from typing import Any

FUZZY_MATCH_MAX_DISTANCE: int

class RedisVectorDataStore(BaseVectorDataStore, CacheCompatibleMixin):
    """Vector data store implementation that uses Redis with RedisVL for vector search.

    This class provides methods to interact with Redis for vector storage and retrieval
    using Redis Vector Search capabilities via RedisVL and langchain-redis.

    Attributes:
        redis_url (str): URL for Redis connection.
        index_name (str): Name for the vector index.
        search_index (SearchIndex): RedisVL SearchIndex instance.
        cache_store (SemanticCache): RedisVL SemanticCache instance.
        embedding (BaseEMInvoker | None): The embedding model to perform vectorization.
    """
    index_name: Incomplete
    url: Incomplete
    client: Incomplete
    filterable_fields: Incomplete
    cache_store: Incomplete
    def __init__(self, index_name: str, url: str | None = None, client: Redis | None = None, embedding: BaseEMInvoker | None = None, additional_filter_fields: list[dict[str, Any]] | None = None) -> None:
        '''Initialize Redis vector store using RedisVL and langchain-redis.

        Args:
            index_name (str): Name of the index to use.
            url (str): URL for Redis connection.
            client (Redis | None, optional): Redis client to use for vectorization.
            embedding (BaseEMInvoker | None, optional): Embedding function to use for vectorization.
                Defaults to None. If None, the default embedding model (redis/langcache-embed-v1) will be used.
            additional_filter_fields (list[dict[str, Any]] | None, optional): Additional filterable fields to add
                to the index. For example, to add `entry_id` as a filterable field, pass
                `[{"name": "entry_id", "type": "text"}]`. Defaults to None.

        Notes:
            Besides the `additional_filter_fields`, the class will automatically create default filterable fields:
                1. prompt: TEXT (default from redisvl).
                2. response: TEXT (default from redisvl).
                3. prompt_vector: VECTOR (default from redisvl).
                4. chunk_id: TEXT (default additional_filter_fields).

        Raises:
            TypeError: If `embedding` is not an instance of `BaseEMInvoker`.
        '''
    async def get_size(self) -> int:
        """Returns the total number of vectors in the index.

        If the index is not initialized returns 0.

        Returns:
            int: The total number of vectors.
        """
    async def query(self, query: str, top_k: int = ..., retrieval_params: dict[str, Any] | None = None) -> list[Chunk]:
        """Search for semantically similar documents which returns similarity scores.

        Args:
            query (str): The query text to search for.
            top_k (int): Number of top results to return.
            retrieval_params (dict[str, Any] | None, optional): Additional parameters for the query such as:
                - filter: Redis filter expression to narrow results following RedisVL FilterExpression.

        Returns:
            list[Chunk]: List of chunks semantically similar to the query
        """
    async def query_by_id(self, id_: str | list[str]) -> list[Chunk]:
        """Retrieve chunks by their IDs.

        Args:
            id_ (str | list[str]): A single ID or list of chunk IDs to retrieve

        Returns:
            list[Chunk]: List of retrieved chunks
        """
    async def add_chunks(self, chunks: Chunk | list[Chunk], **kwargs) -> list[str]:
        """Add chunks to the vector store.

        Args:
            chunks (Chunk | list[Chunk]): A single chunk or a list of chunks to add
            **kwargs: Additional parameters for adding chunks

        Returns:
            list[str]: List of IDs of the added chunks
        """
    async def delete_chunks(self, query: str, **kwargs: Any) -> None:
        '''Delete chunks from the vector store by filter/query. Not supported for Redis backend.

        Args:
            query (str): The query to delete chunks by. For example, "user_*" would match keys
                like "user_1", "user_2", etc.
            **kwargs: Additional keyword arguments.
        '''
    async def delete_chunks_by_ids(self, ids: str | list[str], **kwargs: Any) -> None:
        """Delete chunks from the vector store by their IDs.

        Args:
            ids (str | list[str]): A single ID or a list of IDs to delete.
            **kwargs: Additional keyword arguments.
        """
    async def exact_match(self, key: str, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that exactly match the given prompt.

        Args:
            key (str): The prompt to match.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The value stored with the matching prompt, or None if no match is found.
        '''
    async def fuzzy_match(self, key: str, max_distance: int = 2, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that approximately match the given key using fuzzy matching.

        Args:
            key (str): The key to match
            max_distance (int): Maximum allowed distance for fuzzy matching
                (higher values allow for more differences). Maximum is 3. Defaults to 2.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Note:
            Maximum fuzzy distance is 3. This is a limitation of the Redis Vector Search and the Redis Search module.
            See [5] for more details.

        Returns:
            Any: The value with the closest fuzzy match, or None if no match is found
        '''
    async def semantic_match(self, key: str, min_similarity: float = 0.8, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that semantically match the given key using vector similarity.

        This method compares the vector embedding of the search key with vector embeddings
        of stored keys to find semantically similar matches.

        Args:
            key (str): The key to match
            min_similarity (float, optional): Minimum similarity score for semantic matching
                (higher values are more strict). Ranges from 0 to 1. Defaults to 0.8.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The semantically closest value, or None if no match meets the threshold
        '''
    async def delete_expired_entries(self, now: datetime, max_size: int = 10000) -> None:
        """Delete expired entries (for TTL eviction).

        Args:
            now (datetime): The current datetime for comparison.
            max_size (int): The maximum number of entries to return. Defaults to 10000.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for RedisVectorDataStore.
        """
    async def delete_least_frequently_used_entries(self, num_entries: int) -> None:
        """Delete least frequently used entries (for LFU eviction).

        Args:
            num_entries (int): Number of entries to return.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for RedisVectorDataStore.
        """
    async def delete_least_recently_used_entries(self, num_entries: int) -> None:
        """Delete least recently used entries (for LRU eviction).

        Args:
            num_entries (int): Number of entries to return.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for RedisVectorDataStore.
        """
    async def delete_entries_by_key(self, key: str | list[str], metadata: dict[str, Any] | None = None) -> None:
        '''Delete entries by key.

        Args:
            key (str | list[str]): The key or list of keys to delete entries for.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.
        '''
    async def clear(self) -> None:
        """Clear all entries in the storage."""
