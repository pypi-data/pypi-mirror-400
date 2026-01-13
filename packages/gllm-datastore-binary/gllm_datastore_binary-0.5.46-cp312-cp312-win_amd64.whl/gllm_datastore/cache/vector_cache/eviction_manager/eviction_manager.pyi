from _typeshed import Incomplete
from abc import ABC, abstractmethod
from gllm_datastore.cache.vector_cache.eviction_strategy.eviction_strategy import BaseEvictionStrategy as BaseEvictionStrategy
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore

class BaseEvictionManager(ABC):
    """Base class for eviction managers that handle the eviction process."""
    vector_store: Incomplete
    eviction_strategy: Incomplete
    check_interval: Incomplete
    def __init__(self, vector_store: BaseVectorDataStore | BaseDataStore, eviction_strategy: BaseEvictionStrategy, check_interval: int = 60) -> None:
        """Initialize the eviction manager.

        Args:
            vector_store (BaseVectorDataStore | BaseDataStore): The datastore that will be managed by the
                eviction manager.
            eviction_strategy (BaseEvictionStrategy): The eviction strategy to use.
            check_interval (int, optional): How often to check for entries to evict (seconds). Defaults to 60.
        """
    @abstractmethod
    def start(self) -> None:
        """Start the eviction checking process.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass
        """
    @abstractmethod
    def stop(self) -> None:
        """Stop the eviction checking process.

        This method should be implemented by subclasses.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass
        """
