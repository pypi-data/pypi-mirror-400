from _typeshed import Incomplete
from gllm_datastore.cache.hybrid_cache.hybrid_cache import BaseHybridCache as BaseHybridCache
from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher

class InMemoryHybridCache(BaseHybridCache):
    """A hybrid cache that stores data in an in-memory dictionary.

    The `InMemoryHybridCache` class utilizes an in-memory dictionary to store the cache data.

    Attributes:
        in_memory_cache (dict[str, Any]): An in-memory dictionary to store the cache data.
        key_matcher (BaseKeyMatcher): The key matcher to use that defines the cache key matching strategy.
    """
    in_memory_cache: Incomplete
    def __init__(self, key_matcher: BaseKeyMatcher | None = None) -> None:
        """Initializes a new instance of the InMemoryHybridCache class.

        Args:
            key_matcher (BaseKeyMatcher | None, optional): The key matcher to use that defines the cache key
                matching strategy. Defaults to None, in which case the `ExactKeyMatcher` will be used.
        """
    async def retrieve_all_keys(self) -> set[str]:
        """Retrieves all keys from the storage.

        This method filters out and deletes any expired keys before returning the set.

        Returns:
            set[str]: A set of all keys in the storage.
        """
