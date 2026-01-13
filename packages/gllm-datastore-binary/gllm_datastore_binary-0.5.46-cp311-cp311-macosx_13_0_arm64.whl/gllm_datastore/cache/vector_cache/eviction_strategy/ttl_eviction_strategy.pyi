from _typeshed import Incomplete
from gllm_datastore.cache.vector_cache.eviction_strategy.eviction_strategy import BaseEvictionStrategy as BaseEvictionStrategy
from gllm_datastore.constants import METADATA_KEYS as METADATA_KEYS
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore
from gllm_datastore.utils import convert_ttl_to_seconds as convert_ttl_to_seconds
from gllm_datastore.vector_data_store.mixin.cache_compatible_mixin import CacheCompatibleMixin as CacheCompatibleMixin
from typing import Any

class TTLEvictionStrategy(BaseEvictionStrategy):
    """Eviction strategy based on time-to-live."""
    ttl: Incomplete
    def __init__(self, ttl: int | str) -> None:
        '''Initialize the TTL eviction strategy.

        Args:
            ttl (int | str): The time-to-live for the cache. This can be an integer (in seconds)
                or a string (e.g., "1h", "30m").
        '''
    async def prepare_metadata(self, ttl: int | str | None = None) -> dict[str, Any]:
        """Prepare metadata with expiration time if TTL is provided.

        Args:
            ttl (int | None): The time-to-live for the cache, in seconds. If passed -1, the cache will not expire.
                Defaults to None, in which case the class-defined TTL will be used.

        Returns:
            dict[str, Any]: Metadata dictionary containing creation time and expiration time.
        """
    async def evict(self, vector_store: CacheCompatibleMixin | BaseDataStore) -> None:
        """Evict entries based on the eviction policy.

        Args:
            vector_store (CacheCompatibleMixin): The cache store to use for eviction.
        """
