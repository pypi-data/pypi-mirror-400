from gllm_core.schema.chunk import Chunk
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_inference.schema import Vector
from typing import Any, Protocol

class VectorCapability(Protocol):
    """Protocol for vector similarity search operations.

    This protocol defines the interface for datastores that support vector-based
    retrieval operations. This includes similarity search, ID-based lookup as well as
    vector storage.
    """
    async def create(self, data: Chunk | list[Chunk]) -> None:
        """Add chunks to the vector store with automatic embedding generation.

        Args:
            data (Chunk | list[Chunk]): Single chunk or list of chunks to add.
        """
    async def create_from_vector(self, chunk_vectors: list[tuple[Chunk, Vector]], **kwargs: Any) -> None:
        """Add pre-computed vectors directly.

        Args:
            chunk_vectors (list[tuple[Chunk, Vector]]): List of tuples containing chunks and their
                corresponding vectors.
            **kwargs: Datastore-specific parameters.
        """
    async def retrieve(self, query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs: Any) -> list[Chunk]:
        """Read records from the datastore using text-based similarity search with optional filtering.

        Args:
            query (str): Input text to embed and search with.
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting.
                Defaults to None.
            **kwargs: Datastore-specific parameters.

        Returns:
            list[Chunk]: Query results.
        """
    async def retrieve_by_vector(self, vector: Vector, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs: Any) -> list[Chunk]:
        """Direct vector similarity search.

        Args:
            vector (Vector): Query embedding vector.
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting.
                Defaults to None.
            **kwargs: Datastore-specific parameters.

        Returns:
            list[Chunk]: List of chunks ordered by similarity score.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None, **kwargs: Any) -> None:
        """Update existing records in the datastore.

        Args:
            update_values (dict[str, Any]): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            **kwargs: Datastore-specific parameters.
        """
    async def delete(self, filters: FilterClause | QueryFilter | None = None, **kwargs: Any) -> None:
        """Delete records from the datastore.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            **kwargs: Datastore-specific parameters

        Note:
            If filters is None, no operation is performed (no-op).
        """
    async def clear(self) -> None:
        """Clear all records from the datastore."""
    async def ensure_index(self, **kwargs: Any) -> None:
        """Ensure vector index exists, creating it if necessary.

        This method ensures that the vector index required for similarity search
        operations is created. If the index already exists, this method performs
        no operation (idempotent).

        Args:
            **kwargs (Any): Datastore-specific parameters for index configuration.
        """
