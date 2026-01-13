from _typeshed import Incomplete
from gllm_datastore.cache.cache import BaseCache as BaseCache, MatchingStrategy as MatchingStrategy
from gllm_datastore.cache.utils import generate_key_from_func as generate_key_from_func, serialize_pydantic as serialize_pydantic
from gllm_datastore.cache.vector_cache.eviction_manager.eviction_manager import BaseEvictionManager as BaseEvictionManager
from gllm_datastore.vector_data_store.mixin.cache_compatible_mixin import CacheCompatibleMixin as CacheCompatibleMixin
from typing import Any, Callable

class VectorCache(BaseCache):
    """Cache interface that uses a vector datastore for storage and retrieval."""
    vector_store: Incomplete
    eviction_manager: Incomplete
    eviction_strategy: Incomplete
    matching_strategy: Incomplete
    matching_config: Incomplete
    saving_config: Incomplete
    def __init__(self, vector_store: CacheCompatibleMixin, eviction_manager: BaseEvictionManager | None = None, matching_strategy: MatchingStrategy = ..., matching_config: dict[str, Any] | None = None, saving_config: dict[str, Any] | None = None) -> None:
        """Initialize the vector cache.

        Args:
            vector_store (CacheCompatibleMixin): The vector datastore to use for storage.
                Must inherit both CacheCompatibleMixin and BaseVectorDataStore.
            eviction_manager (BaseEvictionManager | None, optional): The eviction manager to use for cache eviction.
                Defaults to None. If None, no eviction will be performed.
            matching_strategy (MatchingStrategy, optional): The strategy to use for matching keys.
                Defaults to MatchingStrategy.EXACT.
            matching_config (dict[str, Any] | None, optional): Configuration parameters for matching strategies.
                Defaults to None, which means no specific configuration is provided.
            saving_config (dict[str, Any] | None, optional): Configuration parameters for saving strategies.
                Defaults to None, which means no specific configuration is provided.
        """
    def cache(self, key_func: Callable | None = None, name: str = '', matching_strategy: MatchingStrategy | None = None, matching_config: dict[str, Any] | None = None, saving_config: dict[str, Any] | None = None) -> Callable:
        '''Decorator for caching function results.

        This decorator caches the results of the decorated function using this cache storage.
        The cache key is generated using the provided key function or a default key generation
        based on the function name and arguments.

        Synchronous and asynchronous functions are supported.

        Args:
            key_func (Callable | None, optional): A function to generate the cache key.
                If None, a default key generation will be used.
            name (str, optional): The name of the cache. This can be used to identify the cache in logs or metrics.
                Defaults to an empty string.
            matching_strategy (MatchingStrategy | None, optional): The strategy to use for matching keys.
                This can be one of the values from the MatchingStrategy enum. Defaults to None. If None,
                the class-level matching strategy will be used.
            matching_config (dict[str, Any] | None, optional): Configuration parameters for matching strategies.
                Defaults to None. If None, the class-level matching config will be used.
            saving_config (dict[str, Any] | None, optional): Configuration parameters for saving strategies.
                Defaults to None. If None, the class-level saving config will be used.

        Example:
            ```python
            def get_user_cache_key(user_id: int) -> str:
                return f"user:{user_id}"

            @cache_store.cache(key_func=get_user_cache_key, ttl="1h")
            async def get_user(user_id: int) -> User:
                return await db.get_user(user_id)

            # will use/store cache with key "user:1", expiring after 1 hour
            user1 = await get_user(1)
            ```

        Returns:
            Callable: A decorator function.
        '''
    async def retrieve(self, key: str, matching_strategy: MatchingStrategy, matching_config: dict[str, Any] | None = None) -> Any | None:
        """Retrieve the cached result based on the key and matching strategy.

        Args:
            key (str): The cache key to retrieve.
            matching_strategy (MatchingStrategy): The strategy to use for matching keys.
            matching_config (dict[str, Any]): Configuration parameters for the matching strategy.

        Returns:
            The cached result if found, otherwise None.
        """
    async def store(self, key: str, value: Any, metadata: dict[str, Any] | None = None, **kwargs) -> None:
        """Store the cached result based on the key and matching strategy.

        Args:
            key (str): The cache key to store.
            value (Any): The value to store in the cache.
            metadata (dict[str, Any] | None, optional): Metadata to store with the cache.
                Defaults to None.
            **kwargs: Additional keyword arguments to pass to the eviction strategy.
        """
    async def delete(self, key: str | list[str], metadata: dict[str, Any] | None = None) -> None:
        '''Delete the cached result based on the key and matching strategy.

        Args:
            key (str | list[str]): The cache key to delete.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.
        '''
    async def clear(self) -> None:
        """Clear all cached results based on the matching strategy."""
