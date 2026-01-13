from gllm_core.schema import Chunk as Chunk
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.in_memory.fulltext import InMemoryFulltextCapability as InMemoryFulltextCapability
from gllm_datastore.data_store.in_memory.vector import InMemoryVectorCapability as InMemoryVectorCapability

class InMemoryDataStore(BaseDataStore):
    """In-memory data store with multiple capability support.

    This class provides a unified interface for accessing vector, fulltext,
    and cache capabilities using in-memory storage optimized for development
    and testing scenarios.

    Attributes:
        store (dict[str, Chunk]): Dictionary storing data with their IDs as keys.
    """
    store: dict[str, Chunk]
    def __init__(self) -> None:
        """Initialize the in-memory data store."""
    @property
    def supported_capabilities(self) -> list[CapabilityType]:
        """Return list of currently supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.
        """
    @property
    def fulltext(self) -> InMemoryFulltextCapability:
        """Access fulltext capability if registered.

        This method solely uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the InMemoryFulltextCapability handler for better
        type hinting.

        Returns:
            InMemoryFulltextCapability: Fulltext capability handler.

        Raises:
            NotRegisteredException: If fulltext capability is not registered.
        """
    @property
    def vector(self) -> InMemoryVectorCapability:
        """Access vector capability if registered.

        This method solely uses the logic of its parent class to return the vector capability handler.
        This method overrides the parent class to return the InMemoryVectorCapability handler for better
        type hinting.

        Returns:
            InMemoryVectorCapability: Vector capability handler.

        Raises:
            NotRegisteredException: If vector capability is not registered.
        """
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None) -> FilterClause | QueryFilter | None:
        """Translate QueryFilter or FilterClause to in-memory datastore filter syntax.

        For the in-memory datastore, this method acts as an identity function since
        the datastore works directly with the QueryFilter DSL without requiring
        translation to a native format.

        Args:
            query_filter (FilterClause | QueryFilter | None): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses,
                or None for empty filters.

        Returns:
            FilterClause | QueryFilter | None: The same filter object that was passed in.
                Returns None for empty filters.
        """
