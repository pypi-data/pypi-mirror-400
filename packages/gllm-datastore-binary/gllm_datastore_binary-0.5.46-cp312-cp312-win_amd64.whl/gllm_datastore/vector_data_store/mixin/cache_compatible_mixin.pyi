from abc import ABC, abstractmethod
from datetime import datetime
from gllm_datastore.cache.cache import MatchingStrategy as MatchingStrategy
from gllm_datastore.cache.vector_cache.eviction_manager.eviction_manager import BaseEvictionManager as BaseEvictionManager
from gllm_datastore.cache.vector_cache.vector_cache import VectorCache as VectorCache
from gllm_datastore.constants import METADATA_KEYS as METADATA_KEYS
from typing import Any

class CacheCompatibleMixin(ABC):
    """Mixin that provides cache-specific matching operations for vector datastores.

    This mixin adds methods for exact, fuzzy, and semantic matching that are
    required by the VectorCache implementation, without forcing all vector datastores
    to implement these methods.
    """
    async def store_cache(self, key: str, value: Any, metadata: dict[str, Any] | None = None) -> None:
        """Public method to store cache data in the storage.

        Args:
            key (str): The key to store the cache data.
            value (Any): The cache data to store.
            metadata (dict[str, Any] | None, optional): Additional metadata to store with the cache data.
                Defaults to None.
        """
    @abstractmethod
    async def exact_match(self, key: str, **kwargs) -> Any | None:
        """Find chunks that exactly match the given key.

        This method should be implemented by subclasses.

        Args:
            key (str): The key to match.
            **kwargs (Any): Additional parameters for the matching operation.

        Returns:
            Any: Chunks that exactly match the key.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def fuzzy_match(self, key: str, max_distance: int = 2, **kwargs) -> Any | None:
        """Find chunks that approximately match the given key using fuzzy matching.

        This method should be implemented by subclasses.

        Args:
            key (str): The key to match.
            max_distance (int): Maximum distance for fuzzy matching. Lower values are more strict.
                This is the maximum Levenshtein distance allowed for a match. Defaults to 2.
            **kwargs (Any): Additional parameters for the matching operation.

        Returns:
            Any: Chunks that fuzzy match the key within the threshold.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def semantic_match(self, key: str, min_similarity: float = 0.8, metadata: dict[str, Any] | None = None, **kwargs) -> Any | None:
        """Find chunks that semantically match the given key using vector similarity.

        This method should be implemented by subclasses.

        Args:
            key (str): The key to match.
            min_similarity (float): Minimum similarity score for semantic matching
                (higher values are more strict). Ranges from 0 to 1. Defaults to 0.8.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                Defaults to None.
            **kwargs (Any): Additional parameters for the matching operation.

        Returns:
            Any: Chunks that semantically match the key above the threshold.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete_expired_entries(self, now: datetime, max_size: int = 10000) -> None:
        """Delete expired entries (for TTL eviction).

        This method should be implemented by subclasses.

        Args:
            now (datetime): The current datetime for comparison.
            max_size (int): The maximum number of entries to return. Defaults to 10000.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete_least_frequently_used_entries(self, num_entries: int) -> None:
        """Delete least frequently used entries (for LFU eviction).

        This method should be implemented by subclasses.

        Args:
            num_entries (int): Number of entries to return.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete_least_recently_used_entries(self, num_entries: int) -> None:
        """Delete least recently used entries (for LRU eviction).

        This method should be implemented by subclasses.

        Args:
            num_entries (int): Number of entries to return.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete_entries_by_key(self, key: str | list[str], metadata: dict[str, Any] | None = None) -> None:
        '''Delete entries by key.

        This method should be implemented by subclasses.

        Args:
            key (str): The key to delete entries for.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Raises:
            NotImplementedError: If the method is not implemented.
        '''
    def as_cache(self, eviction_manager: BaseEvictionManager | None = None, matching_strategy: MatchingStrategy = 'exact', matching_config: dict[str, Any] | None = None, saving_config: dict[str, Any] | None = None) -> VectorCache:
        """Return a cache instance that can be used to store and retrieve data.

        Args:
            eviction_manager (Optional[BaseEvictionManager], optional): The eviction manager to use for cache eviction.
                Defaults to None. If None, no eviction will be performed.
            matching_strategy (MatchingStrategy, optional): The strategy to use for matching keys.
                Defaults to MatchingStrategy.EXACT.
            matching_config (dict[str, Any] | None, optional): Configuration parameters for matching strategies.
                Defaults to None, which means no specific configuration is provided.
            saving_config (dict[str, Any] | None, optional): Configuration parameters for saving strategies.
                Defaults to None, which means no specific configuration is provided.

        Returns:
            VectorCache: A cache instance that can be used to store and retrieve data.
        """
