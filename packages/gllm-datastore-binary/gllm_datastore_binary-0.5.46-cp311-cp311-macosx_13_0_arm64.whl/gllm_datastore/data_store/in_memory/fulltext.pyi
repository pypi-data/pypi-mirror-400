from gllm_core.schema.chunk import Chunk
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.in_memory.query import create_updated_chunk as create_updated_chunk, delete_chunks_by_filters as delete_chunks_by_filters, get_chunks_from_store as get_chunks_from_store
from typing import Any

class InMemoryFulltextCapability:
    """In-memory implementation of FulltextCapability protocol.

    This class provides document CRUD operations and flexible querying using pure
    Python data structures optimized for development and testing.

    Attributes:
        store (dict[str, Chunk]): Dictionary storing Chunk objects with their IDs as keys.
    """
    store: dict[str, Chunk]
    def __init__(self, store: dict[str, Any] | None = None) -> None:
        """Initialize the in-memory fulltext capability.

        Args:
            store (dict[str, Any] | None, optional): Dictionary storing Chunk objects with their IDs as keys.
                Defaults to None.
        """
    async def create(self, data: Chunk | list[Chunk]) -> None:
        '''Create new records in the datastore.

        Examples:
            Create a new chunk.
            ```python
            await fulltext_capability.create(Chunk(content="Test chunk", metadata={"category": "test"}))
            ```

        Args:
            data (Chunk | list[Chunk]): Data to create (single item or collection).

        Raises:
            ValueError: If data structure is invalid.
        '''
    async def retrieve(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        '''Read records from the datastore with optional filtering.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            results = await fulltext_capability.retrieve(filters=F.eq("metadata.category", "tech"))

            # Multiple filters
            results = await fulltext_capability.retrieve(
                filters=F.and_(F.eq("metadata.category", "tech"), F.eq("metadata.status", "active"))
            )
            ```

        Args:
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options for sorting and pagination. Defaults to None.

        Returns:
            list[Chunk]: List of matched chunks after applying filters and options.
        '''
    async def retrieve_fuzzy(self, query: str, max_distance: int = 2, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        """Find records that fuzzy match the query within distance threshold.

        Args:
            query (str): Text to fuzzy match against.
            max_distance (int, optional): Maximum edit distance for matches. Defaults to 2.
            filters (FilterClause | QueryFilter | None, optional): Optional metadata filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options, only limit is used here. Defaults to None.

        Returns:
            list[Chunk]: Matched chunks ordered by distance (ascending), limited by options.limit.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None) -> None:
        '''Update existing records in the datastore.

        Examples:
            Update certain metadata of a chunk with specific filters.
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await fulltext_capability.update(
                update_values={"metadata": {"status": "published"}},
                filters=F.eq("metadata.category", "tech"),
            )

            # Multiple filters
            await fulltext_capability.update(
                update_values={"metadata": {"status": "published"}},
                filters=F.and_(F.eq("metadata.status", "draft"), F.eq("metadata.category", "tech")),
            )
            ```

        Args:
            update_values (dict[str, Any]): Mapping of fields to new values to apply.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
        '''
    async def delete(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> None:
        '''Delete records from the datastore.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await fulltext_capability.delete(filters=F.eq("metadata.category", "tech"))

            # Multiple filters
            await fulltext_capability.delete(
                filters=F.and_(F.eq("metadata.category", "tech"), F.eq("metadata.status", "draft"))
            )
            ```

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options for sorting and limiting deletions
                (for eviction-like operations). Defaults to None.

        Returns:
            None: This method performs deletions in-place.
        '''
    async def clear(self) -> None:
        """Clear all records from the datastore."""
