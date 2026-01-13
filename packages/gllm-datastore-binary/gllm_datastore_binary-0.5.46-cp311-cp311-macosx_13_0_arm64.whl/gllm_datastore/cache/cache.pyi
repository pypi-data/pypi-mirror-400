from _typeshed import Incomplete
from gllm_datastore.cache.base import BaseCache as BaseCache, MatchingStrategy as MatchingStrategy
from gllm_datastore.cache.utils import generate_cache_id as generate_cache_id, generate_key_from_func as generate_key_from_func, serialize_pydantic as serialize_pydantic
from gllm_datastore.cache.vector_cache.eviction_manager.eviction_manager import BaseEvictionManager as BaseEvictionManager
from gllm_datastore.constants import METADATA_KEYS as METADATA_KEYS
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from typing import Any, Callable, Literal, overload

class Cache(BaseCache):
    """Cache interface that uses a data store for storage and retrieval.

    Attributes:
        data_store (BaseDataStore): The data store to use for storage.
        eviction_manager (BaseEvictionManager | None): The eviction manager to use for cache eviction.
        matching_strategy (MatchingStrategy): The strategy to use for matching keys.
        eviction_config (dict[str, Any] | None): Configuration parameters for eviction strategies.
        max_locks (int): Maximum number of locks to keep in memory for race condition mitigation.
    """
    data_store: Incomplete
    eviction_manager: Incomplete
    eviction_strategy: Incomplete
    matching_strategy: Incomplete
    eviction_config: Incomplete
    def __init__(self, data_store: BaseDataStore, eviction_manager: BaseEvictionManager | None = None, matching_strategy: MatchingStrategy = ..., eviction_config: dict[str, Any] | None = None, max_locks: int = 100) -> None:
        """Initialize the data store cache.

        Args:
            data_store (BaseDataStore): The data store to use for storage.
                Must have fulltext capability registered.
                Vector capability required only for semantic matching.
            eviction_manager (BaseEvictionManager | None, optional): The eviction manager to use for cache eviction.
                Defaults to None. If None, no eviction will be performed.
            matching_strategy (MatchingStrategy, optional): The strategy to use for matching keys.
                Defaults to MatchingStrategy.EXACT.
            eviction_config (dict[str, Any] | None, optional): Configuration parameters for eviction strategies.
                Defaults to None, which means no specific configuration is provided.
            max_locks (int, optional): Maximum number of locks to keep in memory. When exceeded,
                least recently used locks are automatically evicted. Defaults to 100.

        Raises:
            ValueError: If data_store doesn't have fulltext capability.
            ValueError: If semantic matching requested without vector capability.
        """
    def cache(self, key_func: Callable | None = None, name: str = '', matching_strategy: MatchingStrategy | None = None, eviction_config: dict[str, Any] | None = None) -> Callable:
        '''Decorator for caching function results.

        This decorator caches the results of the decorated function using this cache storage.
        The cache key is generated using the provided key function or a default key generation
        based on the function name and arguments.

        Synchronous and asynchronous functions are supported.

        Example:
            1. Basic usage:
            ```python
            def get_user_cache_key(user_id: int) -> str:
                return f"user:{user_id}"

            @cache_store.cache(key_func=get_user_cache_key)
            async def get_user(user_id: int) -> User:
                return await db.get_user(user_id)

            # will use/store cache with key "user:1"
            user1 = await get_user(1)
            ```

            2. Using eviction config:
            ```python
            @cache_store.cache(eviction_config={"ttl": "1h"})
            async def get_user(user_id: int) -> User:
                return await db.get_user(user_id)
            ```

        Args:
            key_func (Callable | None, optional): A function to generate the cache key.
                Defaults to None, in which case the function name and arguments will be used to generate the cache key.
            name (str, optional): The name of the cache. This can be used to identify the cache in logs or metrics.
                Defaults to an empty string.
            matching_strategy (MatchingStrategy | None, optional): The strategy to use for matching keys.
                Defaults to None, in which case the class-level matching strategy will be used.
            eviction_config (dict[str, Any] | None, optional): Configuration parameters for eviction strategies.
                Defaults to None, in which case the class-level eviction config will be used.

        Returns:
            Callable: A decorator function.
        '''
    async def store(self, key: str, value: str, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        '''Store the cached result based on the key and matching strategy.

        Example:
            ```python
            await cache.store("my_key", "my_value", metadata={"category": "ML", "subcategory": "AI"}, ttl="1h")
            ```

        Args:
            key (str): The cache key to store.
            value (str): The value to store in the cache.
            metadata (dict[str, Any] | None, optional): Metadata to store with the cache.
                Defaults to None.
            **kwargs: Additional keyword arguments to pass to the eviction strategy (e.g. ttl).
        '''
    @overload
    async def retrieve(self, key: str, matching_strategy: Literal[MatchingStrategy.EXACT], filters: FilterClause | QueryFilter | None = None) -> Any | None: ...
    @overload
    async def retrieve(self, key: str, matching_strategy: Literal[MatchingStrategy.FUZZY], max_distance: int = 2, filters: FilterClause | QueryFilter | None = None) -> Any | None: ...
    @overload
    async def retrieve(self, key: str, matching_strategy: Literal[MatchingStrategy.SEMANTIC], min_similarity: float = 0.8, filters: FilterClause | QueryFilter | None = None) -> Any | None: ...
    async def delete(self, key: str | list[str], filters: FilterClause | QueryFilter | None = None) -> None:
        '''Delete the cached result based on the key and matching strategy.

        Example:
            ```python
            # Using QueryFilter for multiple conditions
            await cache.delete(
                "my_key",
                filters=F.and_(F.eq("metadata.category", "ML"), F.eq("metadata.subcategory", "AI"))
            )

            # Using FilterClause directly
            await cache.delete("my_key", filters=F.eq("metadata.category", "ML"))
            ```

        Args:
            key (str | list[str]): The cache key to delete.
            filters (FilterClause | QueryFilter | None, optional): Optional filters to apply to the search.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
        '''
    async def clear(self) -> None:
        """Clear all cached results based on the matching strategy.

        Example:
            ```python
            await cache.clear()
            ```
        """
