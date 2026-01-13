from abc import ABC, abstractmethod
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore
from gllm_datastore.vector_data_store.mixin.cache_compatible_mixin import CacheCompatibleMixin as CacheCompatibleMixin
from typing import Any

class BaseEvictionStrategy(ABC):
    """Base class for eviction strategies."""
    @abstractmethod
    async def prepare_metadata(self, **kwargs) -> dict[str, Any]:
        """Prepare metadata for a new cache entry.

        This method should be implemented by subclasses to define how metadata should be prepared
        for a new cache entry.

        Returns:
            dict[str, Any]: A dictionary containing metadata for the new entry.
            **kwargs: Additional keyword arguments to pass to the eviction strategy.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
    @abstractmethod
    async def evict(self, vector_store: CacheCompatibleMixin | BaseDataStore) -> None:
        """Evict entries based on the eviction policy.

        This method should be implemented by subclasses to define how entries should be selected
        for eviction.

        Args:
            vector_store (CacheCompatibleMixin | BaseDataStore): The cache store to use for eviction.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
