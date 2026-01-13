from _typeshed import Incomplete
from gllm_datastore.cache.vector_cache.eviction_manager.eviction_manager import BaseEvictionManager as BaseEvictionManager
from gllm_datastore.cache.vector_cache.eviction_strategy.eviction_strategy import BaseEvictionStrategy as BaseEvictionStrategy
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore

class AsyncIOEvictionManager(BaseEvictionManager):
    """Eviction manager using asyncio for background tasks.

    The `AsyncIOEvictionManager` is responsible for:
    1. Starting and stopping the background task that performs the eviction check and eviction process.
    2. Providing the eviction strategy to use for the eviction process.

    This eviction manager should be used in the application that is using the cache, not in the database itself.
    It is specifically designed to handle vector datastores that do not have its own eviction policies or specific
    eviction strategy.

    The `AsyncIOEvictionManager` could be used in the following scenarios:
    1. When the `VectorCache` is initialized, it starts the background task.
    2. When the `VectorCache` is shut down, it stops the background task.
    """
    vector_store: Incomplete
    eviction_strategy: Incomplete
    check_interval: Incomplete
    task: Incomplete
    running: bool
    def __init__(self, vector_store: BaseVectorDataStore | BaseDataStore, eviction_strategy: BaseEvictionStrategy, check_interval: int = 60) -> None:
        """Initialize the asyncio eviction manager.

        Args:
            vector_store (BaseVectorDataStore | BaseDataStore): The vector datastore to manage evictions for.
            eviction_strategy (BaseEvictionStrategy): The eviction strategy to use.
            check_interval (int): How often to check for entries to evict (in seconds).
        """
    def start(self) -> None:
        """Start the background task for evicting entries.

        This method starts the background task that periodically checks for entries to evict from the vector datastore
        and evicts them if necessary using the specified eviction strategy.

        If the task currently exists and is not done or cancelled, it will not start a new one.
        """
    def stop(self) -> None:
        """Stop the background task for evicting entries.

        This method stops the background task that periodically checks for entries to evict from the vector datastore
        and evicts them if necessary using the specified eviction strategy.
        """
