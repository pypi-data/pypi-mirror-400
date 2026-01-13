from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS
from gllm_datastore.core.filters import FilterClause as FilterClause, FilterCondition as FilterCondition, FilterOperator as FilterOperator, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_inference.schema import Vector
from typing import Any

def apply_filters(chunks: list[Chunk], filters: FilterClause | QueryFilter) -> list[Chunk]:
    '''Apply filters to chunks.

    Usage Example:
        ```python
        from gllm_datastore.core.filters import filter as F

        chunks = [
            Chunk(id="1", content="Chunk 1", metadata={"category": "test"}),
            Chunk(id="2", content="Chunk 2", metadata={"category": "test"}),
            Chunk(id="3", content="Chunk 3", metadata={"category": "test"}),
        ]
        # Direct FilterClause usage
        filters = F.eq("metadata.category", "test")
        filtered_chunks = apply_filters(chunks, filters)

        # Multiple filters
        filters = F.and_(F.eq("metadata.category", "test"), F.eq("metadata.status", "active"))
        filtered_chunks = apply_filters(chunks, filters)
        ```

    Args:
        chunks (list[Chunk]): List of chunks to filter.
        filters (FilterClause | QueryFilter): Filter criteria to apply.
            FilterClause objects are automatically converted to QueryFilter internally.

    Returns:
        list[Chunk]: Filtered list of chunks.
    '''
def apply_options(chunks: list[Chunk], options: QueryOptions) -> list[Chunk]:
    """Apply query options (sorting, pagination).

    Note: columns filtering is not applicable to Chunk objects since they have a fixed structure
    and we can only filter on id, content, score, and metadata.

    Args:
        chunks (list[Chunk]): List of chunks to process.
        options (QueryOptions): Query options to apply.

    Returns:
        list[Chunk]: Processed list of chunks.
    """
def get_nested_value(obj: dict[str, Any], key_path: str) -> Any:
    '''Get a nested value from a dictionary using dot notation.

    Args:
        obj (dict[str, Any]): Dictionary to traverse.
        key_path (str): Dot-separated path to the value (e.g., "user.profile.name").

    Returns:
        Any: The value at the specified path, or None if not found.
    '''
def get_sort_value(chunk: Chunk, order_by: str) -> Any:
    """Get the value to sort by.

    Args:
        chunk (Chunk): Chunk to get the value from.
        order_by (str): The field to sort by.

    Returns:
        Any: The value to sort by.
    """
def validate_cache_key(key: str) -> None:
    """Validate cache key format and content.

    Args:
        key (str): Cache key to validate.

    Raises:
        TypeError: If key is not a string.
        ValueError: If key is empty or whitespace-only.
    """
def get_chunks_from_store(store: dict[str, Chunk], filters: QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
    """Get chunks from a store as a list with optional filters and options.

    Args:
        store (dict[str, Chunk]): Store containing chunks.
        filters (QueryFilter | None, optional): Filter criteria to apply. Defaults to None.
        options (QueryOptions | None, optional): Query options to apply. Defaults to None.

    Returns:
        list[Chunk]: List of all chunks in the store.
    """
def apply_filters_and_options(chunks: list[Chunk], filters: QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
    """Apply filters and options to a list of chunks.

    Args:
        chunks (list[Chunk]): List of chunks to process.
        filters (QueryFilter | None, optional): Filter criteria to apply. Defaults to None.
        options (QueryOptions | None, optional): Query options to apply. Defaults to None.

    Returns:
        list[Chunk]: Processed list of chunks.
    """
def create_updated_chunk(existing_chunk: Chunk, update_values: dict[str, Any]) -> Chunk:
    """Create an updated chunk with new values.

    Args:
        existing_chunk (Chunk): The existing chunk to update.
        update_values (dict[str, Any]): Values to update.

    Returns:
        Chunk: Updated chunk with new values.
    """
def delete_chunks_by_filters(store: dict[str, Chunk], filters: QueryFilter | None = None) -> int:
    """Delete chunks from store based on filters.

    Args:
        store (dict[str, Chunk]): Store containing chunks.
        filters (QueryFilter | None, optional): Filters to select chunks to delete. Defaults to None.

    Returns:
        int: Number of chunks deleted.
    """
def find_matching_chunk_ids(store: dict[str, Chunk], filters: QueryFilter) -> list[str]:
    """Find chunk IDs that match the given filters.

    Args:
        store (dict[str, Chunk]): Store containing chunks.
        filters (QueryFilter): The filters to apply.

    Returns:
        list[str]: List of chunk IDs that match the filters.
    """
def similarity_search(query_vector: Vector, store: dict[str, Chunk], filters: QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
    """Retrieve chunks by vector similarity from a store.

    This method will only return chunks that have a vector in their metadata.
    It will also apply the filters and options to the chunks.

    Args:
        query_vector (Vector): Query embedding vector.
        store (dict[str, Chunk]): Store containing chunks.
        filters (QueryFilter | None): Query filters to apply.
        options (QueryOptions | None, optional): Query options to apply.

    Returns:
        list[Chunk]: List of chunks ordered by similarity score.
    """
def evaluate_filter(chunk: Chunk, filters: QueryFilter) -> bool:
    '''Evaluate if a chunk matches the given filters.

    Examples:
        ```python
        from gllm_datastore.core.filters import filter as F

        # Simple filter
        filters = F.and_(F.eq("metadata.category", "tech"))
        result = evaluate_filter(chunk, filters)

        # Complex nested filter
        filters = F.and_(
            F.gte("metadata.price", 10),
            F.lte("metadata.price", 100),
            F.or_(
                F.eq("metadata.status", "active"),
                F.eq("metadata.status", "pending")
            )
        )
        result = evaluate_filter(chunk, filters)
        ```

    Args:
        chunk (Chunk): The chunk to evaluate.
        filters (QueryFilter): The filters to apply.

    Returns:
        bool: True if the chunk matches all filters, False otherwise.
    '''
