from _typeshed import Incomplete
from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS, FIELD_CONFIG_NAME as FIELD_CONFIG_NAME, FIELD_CONFIG_TYPE as FIELD_CONFIG_TYPE
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.redis.query import build_filter_expression as build_filter_expression, check_index_exists as check_index_exists, execute_update as execute_update, fetch_hash_data_batch as fetch_hash_data_batch, get_filterable_fields_from_index as get_filterable_fields_from_index, infer_filterable_fields_from_chunks as infer_filterable_fields_from_chunks, normalize_field_name_for_schema as normalize_field_name_for_schema, parse_redisvl_result_to_chunks as parse_redisvl_result_to_chunks, prepare_chunk_document as prepare_chunk_document, strip_index_prefix as strip_index_prefix, validate_chunk_content as validate_chunk_content, validate_chunk_list as validate_chunk_list, validate_metadata_fields as validate_metadata_fields
from gllm_datastore.data_store.redis.query_translator import RedisQueryTranslator as RedisQueryTranslator
from gllm_datastore.utils.converter import cosine_distance_to_similarity_score as cosine_distance_to_similarity_score
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.schema import Vector
from redis.asyncio.client import Redis
from typing import Any

class RedisVectorCapability:
    """Redis implementation of VectorCapability protocol.

    This class provides vector similarity search operations using RedisVL
    AsyncSearchIndex for vector storage and retrieval.

    Attributes:
        index_name (str): Name of the Redis index.
        client (Redis): Redis async client instance.
        em_invoker (BaseEMInvoker): Embedding model for vectorization.
        index (Any): RedisVL AsyncSearchIndex instance.
    """
    index_name: Incomplete
    client: Incomplete
    index: Any
    def __init__(self, index_name: str, client: Redis, em_invoker: BaseEMInvoker) -> None:
        """Initialize the Redis vector capability.

        Schema will be automatically inferred from chunks when creating a new index,
        or auto-detected from an existing index when performing operations.

        Args:
            index_name (str): Name of the Redis index.
            client (Redis): Redis async client instance.
            em_invoker (BaseEMInvoker): Embedding model for vectorization.
        """
    @property
    def em_invoker(self) -> BaseEMInvoker:
        """Returns the EM Invoker instance.

        Returns:
            BaseEMInvoker: The EM Invoker instance.
        """
    async def ensure_index(self, filterable_fields: list[dict[str, Any]] | None = None) -> None:
        '''Ensure Redis vector index exists, creating it if necessary.

        This method is idempotent - if the index already exists, it will skip creation
        and return early.

        Args:
            filterable_fields (list[dict[str, Any]] | None, optional): List of filterable field
                configurations to use when creating a new index. Each field should be a dictionary
                with "name" and "type" keys. For example:
                [{"name": "metadata.category", "type": "tag"}, {"name": "metadata.score", "type": "numeric"}]
                If not provided and index doesn\'t exist, a default schema will be created with
                only basic fields (id, content, metadata, vector). Defaults to None.

        Raises:
            RuntimeError: If index creation fails.
        '''
    async def create(self, data: Chunk | list[Chunk]) -> None:
        """Add chunks to the vector store with automatic embedding generation.

        If the index does not exist, the schema will be inferred from the chunks being created.

        Args:
            data (Chunk | list[Chunk]): Single chunk or list of chunks to add.

        Raises:
            ValueError: If data structure is invalid or chunk content is invalid.
        """
    async def create_from_vector(self, chunk_vectors: list[tuple[Chunk, Vector]]) -> None:
        """Add pre-computed vectors directly.

        If the index does not exist, the schema will be inferred from the chunks being created.

        Args:
            chunk_vectors (list[tuple[Chunk, Vector]]): List of tuples containing chunks
                and their corresponding vectors.

        Raises:
            ValueError: If chunk content is invalid.
        """
    async def retrieve(self, query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        """Read records from the datastore using text-based similarity search with optional filtering.

        Args:
            query (str): Input text to embed and search with.
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting. Defaults to None.

        Returns:
            list[Chunk]: Query results ordered by similarity score.
        """
    async def retrieve_by_vector(self, vector: Vector, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        """Direct vector similarity search.

        Args:
            vector (Vector): Query embedding vector.
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options like limit and sorting. Defaults to None.

        Returns:
            list[Chunk]: List of chunks ordered by similarity score.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None) -> None:
        """Update existing records in the datastore.

        Args:
            update_values (dict[str, Any]): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
        """
    async def delete(self, filters: FilterClause | QueryFilter | None = None) -> None:
        """Delete records from the datastore.

        Processes deletions in batches to avoid loading all matching documents into memory.
        If filters is None, no operation is performed (no-op).

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                Defaults to None.
        """
    async def clear(self) -> None:
        """Clear all records from the datastore."""
