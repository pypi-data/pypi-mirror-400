from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_datastore.cache.cache import BaseCache as BaseCache
from gllm_datastore.cache.hybrid_cache.key_matcher import ExactKeyMatcher as ExactKeyMatcher
from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher
from gllm_datastore.cache.hybrid_cache.utils import generate_key_from_func as generate_key_from_func
from gllm_datastore.utils import convert_ttl_to_seconds as convert_ttl_to_seconds
from typing import Any, Callable, ParamSpec, TypeVar

P = ParamSpec('P')
T = TypeVar('T')

class BaseHybridCache(BaseCache, ABC):
    """A base class for hybrid cache used in Gen AI applications.

    The `BaseHybridCache` class provides a framework for storing and retrieving cache data.

    Attributes:
        key_matcher (BaseKeyMatcher): The key matcher that defines the cache key matching strategy.
    """
    key_matcher: Incomplete
    def __init__(self, key_matcher: BaseKeyMatcher | None = None) -> None:
        """Initialize a new instance of the `BaseHybridCache` class.

        Args:
            key_matcher (BaseKeyMatcher | None, optional): The key matcher that defines the cache key matching
                strategy. Defaults to None, in which case the `ExactKeyMatcher` will be used.
        """
    def cache(self, key_func: Callable[P, str] | None = None, name: str = '', ttl: int | str | None = None) -> Callable[[Callable[P, T]], Callable[P, T]]:
        '''Decorator for caching function results.

        This decorator caches the results of the decorated function using this cache storage.
        The cache key is generated using the provided key function or a default key generation
        based on the function name and arguments.

        Synchronous and asynchronous functions are supported.

        Args:
            key_func (Callable[P, str] | None, optional): Function to generate cache keys.
                Must accept the same parameters as the decorated function.
            name (str, optional): Name to use in the default key generation if key_func is None.
            ttl (int | str | None, optional): The time-to-live for the cached data. Can be an integer
                in seconds or a string (e.g. "1h", "1d", "1w", "1y"). If None, the cache data will not expire.
                Defaults to None. In this case, the cache will not expire.
            matching_strategy (MatchingStrategy, optional): The strategy to use for matching keys.
                This can be one of the values from the MatchingStrategy enum. Defaults to exact matching.
            matching_config (dict[str, Any], optional): Configuration parameters for matching strategies.
                Defaults to None.

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
    async def store(self, key: str, value: Any, ttl: int | str | None = None) -> None:
        '''Stores cache data in the storage.

        This method preprocesses the TTL (time-to-live) value to seconds if provided, and then calls both
        the `key_matcher.store` and `_store` methods to store the cache data in the storage.

        Args:
            key (str): The key to store the cache data.
            value (Any): The cache data to store.
            ttl (int | str | None): The time-to-live (TTL) for the cache data. Must either be an integer in seconds
                or a string (e.g. "1h", "1d", "1w", "1y"). If None, the cache data will not expire.
        '''
    async def retrieve(self, key: str) -> Any:
        """Retrieves cache data from the storage.

        This method first retrieves the key using the strategy defined in the `key_matcher`. If a matching key is
        found, the method will retrieve the cache data from the storage using the `_retrieve` method. Otherwise,
        the method will return None.

        Args:
            key (str): The key to retrieve the cache data.

        Returns:
            Any: The retrieved cache data.
        """
    async def delete(self, key: str | list[str]) -> None:
        """Deletes cache data from the storage.

        This method deletes the key by calling both the `key_matcher.delete` and `_delete` methods.

        Args:
            key (str | list[str]): The key(s) to delete the cache data.
        """
    async def clear(self) -> None:
        """Clears all cache data from the storage.

        This method clears all cache data from the storage by calling both the `key_matcher.clear` and `_clear` methods.
        """
    @abstractmethod
    async def retrieve_all_keys(self) -> set[str]:
        """Retrieves all keys from the storage.

        This method must be implemented by the subclasses to define the logic for retrieving all keys from the storage.

        Returns:
            set[str]: A set of all keys in the storage.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
