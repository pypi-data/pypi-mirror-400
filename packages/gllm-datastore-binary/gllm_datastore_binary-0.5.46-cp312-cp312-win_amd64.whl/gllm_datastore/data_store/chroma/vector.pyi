from _typeshed import Incomplete
from chromadb import ClientAPI
from gllm_core.schema import Chunk
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS, DEFAULT_TOP_K as DEFAULT_TOP_K, METADATA_KEYS as METADATA_KEYS
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.chroma._chroma_import import safe_import_chromadb as safe_import_chromadb
from gllm_datastore.data_store.chroma.query import ChromaCollectionKeys as ChromaCollectionKeys, DEFAULT_NUM_CANDIDATES as DEFAULT_NUM_CANDIDATES, build_chroma_delete_kwargs as build_chroma_delete_kwargs, build_chroma_get_kwargs as build_chroma_get_kwargs
from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator as ChromaQueryTranslator
from gllm_datastore.utils.converter import from_langchain as from_langchain, l2_distance_to_similarity_score as l2_distance_to_similarity_score, to_langchain as to_langchain
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.schema import Vector
from typing import Any

chromadb: Incomplete

class ChromaVectorCapability:
    """ChromaDB implementation of VectorCapability protocol.

    This class provides document CRUD operations and vector search using ChromaDB.

    Attributes:
        collection_name (str): The name of the ChromaDB collection.
        collection (Collection): The ChromaDB collection instance.
        vector_store (Chroma): The langchain Chroma vector store instance.
        num_candidates (int): The maximum number of candidates to consider during search.
    """
    collection_name: Incomplete
    client: Incomplete
    collection: Incomplete
    num_candidates: Incomplete
    vector_store: Incomplete
    def __init__(self, collection_name: str, em_invoker: BaseEMInvoker, client: ClientAPI, num_candidates: int = ...) -> None:
        """Initialize the ChromaDB vector capability.

        Args:
            collection_name (str): The name of the ChromaDB collection.
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            client (ClientAPI): The ChromaDB client instance.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to 50.
        """
    @property
    def em_invoker(self) -> BaseEMInvoker:
        """Returns the EM Invoker instance.

        Returns:
            BaseEMInvoker: The EM Invoker instance.
        """
    async def ensure_index(self) -> None:
        """Ensure ChromaDB collection exists, creating it if necessary.

        This method is idempotent - if the collection already exists, it will return
        the existing collection. The collection is automatically created during initialization,
        but this method can be called explicitly to ensure it exists.

        Raises:
            RuntimeError: If collection creation fails.
        """
    async def create(self, data: Chunk | list[Chunk], **kwargs: Any) -> None:
        """Add chunks to the vector store with automatic embedding generation.

        Args:
            data (Chunk | list[Chunk]): Single chunk or list of chunks to add.
            **kwargs: Backend-specific parameters.
        """
    async def create_from_vector(self, chunk_vectors: list[tuple[Chunk, Vector]], **kwargs: Any) -> None:
        '''Add pre-computed embeddings directly.

        Examples:
            ```python
            await datastore.vector.create_from_vector(chunk_vectors=[
                (Chunk(content="text1", metadata={"source": "source1"}, id="id1"), [0.1, 0.2, 0.3]),
                (Chunk(content="text2", metadata={"source": "source2"}, id="id2"), [0.4, 0.5, 0.6]),
            ])
            ```

        Args:
            chunk_vectors (list[tuple[Chunk, Vector]]): List of tuples containing chunks and their
                corresponding vectors.
            **kwargs: Datastore-specific parameters.
        '''
    async def retrieve(self, query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        '''Semantic search using text query converted to vector.

        Examples:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await datastore.vector.retrieve(
                query="What is the capital of France?",
                filters=F.eq("metadata.category", "tech")
            )

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await datastore.vector.retrieve(query="What is the capital of France?", filters=filters)
            ```
            This will retrieve the top 10 chunks by similarity score from the vector store
            that match the query and the filters. The chunks will be sorted by score in descending order.

        Args:
            query (str): Text query to embed and search for.
            filters (FilterClause | QueryFilter | None, optional): Filters to apply to the search.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Options to apply to the search. Defaults to None.

        Returns:
            list[Chunk]: List of chunks ordered by relevance score.
        '''
    async def retrieve_by_vector(self, vector: Vector, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        '''Direct vector similarity search.

        Examples:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await datastore.vector.retrieve_by_vector(
                vector=[0.1, 0.2, 0.3],
                filters=F.eq("metadata.category", "tech")
            )

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await datastore.vector.retrieve_by_vector(vector=[0.1, 0.2, 0.3], filters=filters)
            ```
            This will retrieve the top 10 chunks by similarity score from the vector store
            that match the vector and the filters. The chunks will be sorted by score in descending order.

        Args:
            vector (Vector): Query embedding vector.
            filters (FilterClause | QueryFilter | None, optional): Filters to apply to the search.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Options to apply to the search. Defaults to None.

        Returns:
            list[Chunk]: List of chunks ordered by similarity score.
        '''
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None) -> None:
        '''Update existing records in the datastore.

        Examples:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await datastore.vector.update(
                update_values={"metadata": {"status": "published"}},
                filters=F.eq("metadata.category", "tech"),
            )

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await datastore.vector.update(
                update_values={"metadata": {"status": "published"}},
                filters=filters,
            )
            ```
            This will update the metadata of the chunks that match the filters to "published".

        Args:
            update_values (dict[str, Any]): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None, in which case no operation is performed (no-op).

        Note:
            ChromaDB doesn\'t support direct update operations. This method requires
            filters to identify records and will update matching records.
        '''
    async def delete(self, filters: FilterClause | QueryFilter | None = None, **kwargs: Any) -> None:
        '''Delete records from the datastore.

        Examples:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await datastore.vector.delete(filters=F.eq("metadata.category", "tech"))

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await datastore.vector.delete(filters=filters)
            ```
            This will delete all chunks from the vector store that match the filters.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None, in which case no operation is performed (no-op).
            **kwargs: Datastore-specific parameters.
        '''
    async def clear(self) -> None:
        """Clear all records from the datastore."""
