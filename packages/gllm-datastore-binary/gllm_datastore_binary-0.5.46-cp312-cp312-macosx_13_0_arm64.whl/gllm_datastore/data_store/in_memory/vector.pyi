from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.in_memory.query import create_updated_chunk as create_updated_chunk, delete_chunks_by_filters as delete_chunks_by_filters, get_chunks_from_store as get_chunks_from_store, similarity_search as similarity_search
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.schema import Vector
from typing import Any

class InMemoryVectorCapability:
    """In-memory implementation of VectorCapability protocol.

    This class provides vector similarity search operations using pure Python
    data structures optimized for development and testing.

    Attributes:
        store (dict[str, Chunk]): Dictionary storing Chunk objects with their IDs as keys.
        em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
    """
    store: dict[str, Chunk]
    def __init__(self, em_invoker: BaseEMInvoker, store: dict[str, Any] | None = None) -> None:
        """Initialize the in-memory vector capability.

        Args:
            em_invoker (BaseEMInvoker): em_invoker model for text-to-vector conversion.
            store (dict[str, Any] | None, optional): Dictionary storing Chunk objects with their IDs as keys.
                Defaults to None.
        """
    @property
    def em_invoker(self) -> BaseEMInvoker:
        """Returns the EM Invoker instance.

        Returns:
            BaseEMInvoker: The EM Invoker instance.
        """
    async def ensure_index(self) -> None:
        """Ensure in-memory vector store exists, initializing it if necessary.

        This method is idempotent - if the store already exists, it will skip
        initialization and return early.
        """
    async def create(self, data: Chunk | list[Chunk]) -> None:
        """Add chunks to the vector store with automatic embedding generation.

        Args:
            data (Chunk | list[Chunk]): Single chunk or list of chunks to add.
        """
    async def create_from_vector(self, chunk_vectors: list[tuple[Chunk, Vector]]) -> None:
        """Add pre-computed vectors directly.

        Args:
            chunk_vectors (list[tuple[Chunk, Vector]]): List of tuples containing chunks and their
                corresponding vectors.
        """
    async def retrieve(self, query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        '''Read records from the datastore using text-based similarity search with optional filtering.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await vector_capability.retrieve(
                query="What is the capital of France?",
                filters=F.eq("metadata.category", "tech"),
                options=QueryOptions(limit=2),
            )

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await vector_capability.retrieve(
                query="What is the capital of France?",
                filters=filters,
                options=QueryOptions(limit=2),
            )
            ```
            This will retrieve the top 2 chunks by similarity score from the vector store
            that match the query and the filters. The chunks will be sorted by score in descending order.

        Args:
            query (str): Input text to embed and search with.
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting.
                Defaults to None, in which case, no sorting is applied and top 10 chunks are returned.

        Returns:
            list[Chunk]: Top ranked chunks by similarity score.
        '''
    async def retrieve_by_vector(self, vector: Vector, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        """Direct vector similarity search.

        Args:
            vector (Vector): Query embedding vector.
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting.
                Defaults to None, in which case, no sorting is applied and top 10 chunks are returned.

        Returns:
            list[Chunk]: List of chunks ordered by similarity score.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None, **kwargs: Any) -> None:
        '''Update existing records in the datastore.

        Examples:
            1. Update certain metadata of a chunk with specific filters.
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await vector_capability.update(
                update_values={"metadata": {"status": "published"}},
                filters=F.eq("metadata.category", "tech"),
            )

            # Multiple filters
            await vector_capability.update(
                update_values={"metadata": {"status": "published"}},
                filters=F.and_(F.eq("metadata.status", "draft"), F.eq("metadata.category", "tech")),
            )
            ```

            2. Update certain content of a chunk with specific id.
            This will also regenerate the vector of the chunk.
            ```python
            # Direct FilterClause usage
            await vector_capability.update(
                update_values={"content": "new_content"},
                filters=F.eq("id", "unique_id"),
            )

            # Multiple filters
            await vector_capability.update(
                update_values={"content": "new_content"},
                filters=F.and_(F.eq("id", "unique_id"), F.eq("metadata.category", "tech")),
            )
            ```

        Args:
            update_values (dict[str, Any]): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None, in which case no operation is performed (no-op).
            **kwargs: Datastore-specific parameters.

        Raises:
            ValueError: If content is empty.
        '''
    async def delete(self, filters: FilterClause | QueryFilter | None = None) -> None:
        '''Delete records from the datastore.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await vector_capability.delete(filters=F.eq("metadata.category", "AI"))

            # Multiple filters
            await vector_capability.delete(
                filters=F.and_(F.eq("metadata.category", "AI"), F.eq("metadata.status", "published")),
            )
            ```
            This will delete all chunks from the vector store that match the filters.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None, in which case no operation is performed (no-op).
        '''
    async def clear(self) -> None:
        """Clear all vectors from the store."""
