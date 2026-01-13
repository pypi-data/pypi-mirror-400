from _typeshed import Incomplete
from elasticsearch import AsyncElasticsearch
from gllm_core.schema import Chunk
from gllm_datastore.constants import DEFAULT_FETCH_K as DEFAULT_FETCH_K, DEFAULT_TOP_K as DEFAULT_TOP_K
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.elasticsearch.query import delete_by_id as delete_by_id, delete_by_query as delete_by_query, translate_filter as translate_filter, update_by_query as update_by_query
from gllm_datastore.utils.converter import from_langchain as from_langchain, to_langchain as to_langchain
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.schema import Vector
from langchain_elasticsearch.vectorstores import AsyncRetrievalStrategy
from typing import Any

class ElasticsearchVectorCapability:
    """Elasticsearch implementation of VectorCapability protocol.

    This class provides document CRUD operations and vector search using Elasticsearch.

    Attributes:
        index_name (str): The name of the Elasticsearch index.
        vector_store (AsyncElasticsearchStore): The vector store instance.
        em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
    """
    index_name: Incomplete
    vector_store: Incomplete
    def __init__(self, index_name: str, client: AsyncElasticsearch, em_invoker: BaseEMInvoker, query_field: str = 'text', vector_query_field: str = 'vector', retrieval_strategy: AsyncRetrievalStrategy | None = None, distance_strategy: str | None = None) -> None:
        '''Initialize the Elasticsearch vector capability.

        Args:
            index_name (str): The name of the Elasticsearch index.
            client (AsyncElasticsearch): The Elasticsearch client.
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            query_field (str, optional): The field name for text queries. Defaults to "text".
            vector_query_field (str, optional): The field name for vector queries. Defaults to "vector".
            retrieval_strategy (AsyncRetrievalStrategy | None, optional): The retrieval strategy for retrieval.
                Defaults to None, in which case DenseVectorStrategy() is used.
            distance_strategy (str | None, optional): The distance strategy for retrieval. Defaults to None.
        '''
    @property
    def em_invoker(self) -> BaseEMInvoker:
        """Returns the EM Invoker instance.

        Returns:
            BaseEMInvoker: The EM Invoker instance.
        """
    async def ensure_index(self, mapping: dict[str, Any] | None = None, index_settings: dict[str, Any] | None = None, dimension: int | None = None, distance_strategy: str | None = None) -> None:
        '''Ensure Elasticsearch index exists, creating it if necessary.

        This method is idempotent - if the index already exists, it will skip creation
        and return early.

        Args:
            mapping (dict[str, Any] | None, optional): Custom mapping dictionary to use
                for index creation. If provided, this mapping will be used directly.
                The mapping should follow Elasticsearch mapping format. Defaults to None,
                in which default mapping will be used.
            index_settings (dict[str, Any] | None, optional): Custom index settings.
                These settings will be merged with any default settings. Defaults to None.
            dimension (int | None, optional): Vector dimension. If not provided and mapping
                is not provided, will be inferred from em_invoker by generating a test embedding.
            distance_strategy (str | None, optional): Distance strategy for vector similarity.
                Supported values: "cosine", "l2_norm", "dot_product", etc.
                Only used when building default mapping. Defaults to "cosine" if not specified.

        Raises:
            ValueError: If mapping is invalid or required parameters are missing.
            RuntimeError: If index creation fails.
        '''
    async def create(self, data: Chunk | list[Chunk], **kwargs: Any) -> None:
        """Create new records in the datastore.

        Args:
            data (Chunk | list[Chunk]): Data to create (single item or collection).
            **kwargs: Datastore-specific parameters.

        Raises:
            ValueError: If data structure is invalid.
        """
    async def create_from_vector(self, chunk_vectors: list[tuple[Chunk, Vector]], **kwargs) -> list[str]:
        """Add pre-computed embeddings directly.

        Args:
            chunk_vectors (list[tuple[Chunk, Vector]]): List of tuples containing chunks and their
                corresponding vectors.
            **kwargs: Datastore-specific parameters.

        Returns:
            list[str]: List of IDs assigned to added embeddings.
        """
    async def retrieve(self, query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs: Any) -> list[Chunk]:
        '''Semantic search using text query converted to vector.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await vector_capability.retrieve(
                query="What is the capital of France?",
                filters=F.eq("metadata.category", "tech"),
                options=QueryOptions(limit=10),
            )

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await vector_capability.retrieve(query="What is the capital of France?", filters=filters)
            ```

        Args:
            query (str): Text query to embed and search for.
            filters (FilterClause | QueryFilter | None, optional): Filters to apply to the search.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Options to apply to the search. Defaults to None.
            **kwargs: Datastore-specific parameters.

        Returns:
            list[Chunk]: List of chunks ordered by relevance score.
        '''
    async def retrieve_by_vector(self, vector: Vector, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        '''Direct vector similarity search.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            await vector_capability.retrieve_by_vector(
                vector=[0.1, 0.2, 0.3],
                filters=F.eq("metadata.category", "tech"),
                options=QueryOptions(limit=10),
            )

            # Multiple filters
            filters = F.and_(F.eq("metadata.source", "wikipedia"), F.eq("metadata.category", "tech"))
            await vector_capability.retrieve_by_vector(vector=[0.1, 0.2, 0.3], filters=filters)
            ```

        Args:
            vector (Vector): Query embedding vector.
            filters (FilterClause | QueryFilter | None, optional): Filters to apply to the search.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Options to apply to the search. Defaults to None.

        Returns:
            list[Chunk]: List of chunks ordered by similarity score.
        '''
    async def update(self, update_values: dict, filters: FilterClause | QueryFilter | None = None, **kwargs: Any) -> None:
        """Update existing records in the datastore.

        Args:
            update_values (dict): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            **kwargs: Datastore-specific parameters.
        """
    async def delete(self, filters: FilterClause | QueryFilter | None = None, **kwargs: Any) -> None:
        """Delete records from the data store based on filters.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records for deletion.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            **kwargs: Datastore-specific parameters.
        """
    async def delete_by_id(self, id: str | list[str], **kwargs: Any) -> None:
        """Delete records from the data store based on IDs.

        Args:
            id (str | list[str]): ID or list of IDs to delete.
            **kwargs: Datastore-specific parameters.
        """
    async def clear(self, **kwargs: Any) -> None:
        """Clear all records from the datastore.

        Args:
            **kwargs: Datastore-specific parameters.
        """
