from gllm_core.schema.chunk import Chunk
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from typing import Any, Protocol

class FulltextCapability(Protocol):
    """Protocol for full-text search and document operations.

    This protocol defines the interface for datastores that support CRUD operations
    and flexible querying mechanisms for document data.
    """
    async def create(self, data: Chunk | list[Chunk], **kwargs) -> None:
        """Create new records in the datastore.

        Args:
            data (Chunk | list[Chunk]): Data to create (single item or collection).
            **kwargs: Datastore-specific parameters.
        """
    async def retrieve(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs) -> list[Chunk]:
        """Read records from the datastore with optional filtering.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting.
                Defaults to None.
            **kwargs: Datastore-specific parameters.

        Returns:
            list[Chunk]: Query results.
        """
    async def retrieve_fuzzy(self, query: str, max_distance: int = 2, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs) -> list[Chunk]:
        """Find records that fuzzy match the query within distance threshold.

        Args:
            query (str): Text to fuzzy match against.
            max_distance (int): Maximum edit distance for matches (Levenshtein distance). Defaults to 2.
            filters (FilterClause | QueryFilter | None, optional): Optional metadata filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options (limit, sorting, etc.). Defaults to None.
            **kwargs: Datastore-specific parameters.

        Returns:
            list[Chunk]: Matched chunks ordered by relevance/distance.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None, **kwargs) -> None:
        """Update existing records in the datastore.

        Args:
            update_values (dict[str, Any]): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            **kwargs: Datastore-specific parameters.
        """
    async def delete(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs) -> None:
        """Delete records from the datastore.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None, in which case no operation is performed (no-op).
            options (QueryOptions | None, optional): Query options for sorting and limiting deletions.
                Defaults to None.
            **kwargs: Datastore-specific parameters.
        """
    async def clear(self, **kwargs) -> None:
        """Clear all records from the datastore.

        Args:
            **kwargs: Datastore-specific parameters.
        """
