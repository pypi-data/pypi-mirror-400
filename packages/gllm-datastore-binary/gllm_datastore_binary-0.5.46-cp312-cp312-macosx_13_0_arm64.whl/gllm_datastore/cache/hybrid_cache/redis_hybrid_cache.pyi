from _typeshed import Incomplete
from gllm_datastore.cache.hybrid_cache.hybrid_cache import BaseHybridCache as BaseHybridCache
from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher

class RedisHybridCache(BaseHybridCache):
    """A hybrid cache that stores data in Redis.

    The `RedisHybridCache` class utilizes Redis to store the cache data.

    Attributes:
        client (StrictRedis): The Redis client.
        key_matcher (BaseKeyMatcher): The key matcher that defines the cache key matching strategy.
    """
    client: Incomplete
    def __init__(self, host: str, port: int, password: str, db: int = 0, ssl: bool = False, key_matcher: BaseKeyMatcher | None = None) -> None:
        """Initializes a new instance of the RedisHybridCache class.

        Args:
            host (str): The host of the Redis server.
            port (int): The port of the Redis server.
            password (str): The password for the Redis server.
            db (int, optional): The database number. Defaults to 0.
            ssl (bool, optional): Whether to use SSL. Defaults to False.
            key_matcher (BaseKeyMatcher, optional): The key matcher to use. Defaults to None, in which case the
                `ExactKeyMatcher` will be used.
        """
    async def retrieve_all_keys(self) -> set[str]:
        """Retrieves all keys from the storage.

        This method filters out and deletes any expired keys before returning the set.

        Returns:
            set[str]: A set of all keys in the storage.
        """
