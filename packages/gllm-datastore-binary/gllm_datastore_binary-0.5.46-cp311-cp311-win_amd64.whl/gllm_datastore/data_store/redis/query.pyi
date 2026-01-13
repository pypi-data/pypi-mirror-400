from _typeshed import Incomplete
from collections.abc import AsyncIterator
from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import BOOL_FALSE_STR as BOOL_FALSE_STR, BOOL_TRUE_STR as BOOL_TRUE_STR, CHUNK_KEYS as CHUNK_KEYS, DEFAULT_REDIS_QUERY_BATCH_SIZE as DEFAULT_REDIS_QUERY_BATCH_SIZE, FIELD_CONFIG_NAME as FIELD_CONFIG_NAME, FIELD_CONFIG_TYPE as FIELD_CONFIG_TYPE, FieldType as FieldType, LIST_SEPARATOR as LIST_SEPARATOR, METADATA_PREFIX as METADATA_PREFIX, METADATA_SEPARATOR as METADATA_SEPARATOR, REDIS_DEFAULT_DB as REDIS_DEFAULT_DB, REDIS_DEFAULT_HOST as REDIS_DEFAULT_HOST, REDIS_DEFAULT_PORT as REDIS_DEFAULT_PORT
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.redis.query_translator import RedisQueryTranslator as RedisQueryTranslator
from gllm_inference.schema import Vector
from redis.asyncio.client import Redis
from redis.commands.search.document import Document as Document
from redis.commands.search.query import Query
from typing import Any

REDIS_SPECIAL_CHARS: str
REDIS_SPECIAL_CHARS_PATTERN: Incomplete
logger: Incomplete

def sanitize_key(key: str) -> str:
    """Sanitize a key for use in Redis queries.

    Args:
        key (str): The key to sanitize.

    Returns:
        str: The sanitized key.
    """
def sanitize_value(value: Any) -> str:
    """Sanitize a value for use in Redis queries.

    Args:
        value (Any): The value to sanitize.

    Returns:
        str: The sanitized value.
    """
def build_redis_query(query_translator: RedisQueryTranslator, filters: QueryFilter | None = None) -> str:
    '''Build a Redis query string from filters.

    Translates QueryFilter to Redis Search query syntax.

    Examples:
        - F.eq("name", "John") → "@name:{John}"
        - F.gt("age", 18) → "@age:[18 +inf]"
        - F.and_(F.eq("status", "active"), F.gt("score", 50)) → "@status:{active} @score:[50 +inf]"
        - F.in_("category", ["tech", "science"]) → "@category:(tech|science)"

    Args:
        query_translator (RedisQueryTranslator): Query translator instance.
        filters (QueryFilter | None, optional): Query filters to apply. Defaults to None.

    Returns:
        str: Redis query string.

    Raises:
        ValueError: If filter structure is invalid or operator is incompatible with field type.
        TypeError: If filter contains type mismatches.
    '''
def apply_options_to_query(query: Query, options: QueryOptions | None = None) -> Query:
    """Apply query options to Redis Search Query object.

    Uses Redis Search's native SORTBY and LIMIT capabilities for better performance.

    Args:
        query (Query): Redis Search Query object.
        options (QueryOptions | None, optional): Query options to apply. Defaults to None.

    Returns:
        Query: Modified Query object with options applied.
    """
async def execute_search_query(client: Redis, index_name: str, query_translator: RedisQueryTranslator, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> Any:
    """Execute a Redis search query with filters and options.

    When options is None or options.limit is None, automatically paginates to fetch all matching results
    using DEFAULT_REDIS_QUERY_BATCH_SIZE.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index to search.
        query_translator (RedisQueryTranslator): Query translator instance.
        filters (FilterClause | QueryFilter | None, optional): Query filters to apply. Defaults to None.
        options (QueryOptions | None, optional): Query options for sorting and pagination. Defaults to None,
            in which case query is executed in batches of DEFAULT_REDIS_QUERY_BATCH_SIZE.

    Returns:
        Any: Redis search result containing documents and metadata.
    """
async def retrieve_document_ids_batched(client: Redis, index_name: str, query_translator: RedisQueryTranslator, filters: FilterClause | QueryFilter | None = None, batch_size: int = 100) -> AsyncIterator[list[str]]:
    """Retrieve matching document IDs in batches without loading full document content.

    This function is optimized for delete operations where only document IDs are needed.
    It extracts IDs directly from search results without parsing full document content,
    significantly reducing memory usage.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index to search.
        query_translator (RedisQueryTranslator): Query translator instance.
        filters (FilterClause | QueryFilter | None, optional): Query filters to apply. Defaults to None.
        batch_size (int, optional): Number of document IDs per batch. Defaults to 100.

    Yields:
        list[str]: Batches of document IDs for processing.
    """
def parse_redis_documents(docs: list[Document], logger: Any | None = None) -> list[Chunk]:
    """Parse Redis search result documents into Chunk objects.

    Args:
        docs (list[Document]): List of Redis search result documents.
        logger (Any | None, optional): Logger instance for error logging. Defaults to None.

    Returns:
        list[Chunk]: List of parsed Chunk objects.
    """
def get_str_value(data: dict, key: str, default: str = '') -> str:
    """Extract string value from Redis hash data, handling bytes keys and values.

    Args:
        data (dict): Redis hash data (may have bytes keys/values).
        key (str): Key to look up.
        default (str): Default value if key not found.

    Returns:
        str: Decoded string value.
    """
def normalize_field_name_for_schema(field_name: str) -> str:
    '''Normalize field name for Redis schema (dot to underscore).

    This matches the query builder\'s normalization so schema fields match query fields.

    Args:
        field_name (str): Field name in dot notation (e.g., "metadata.score").

    Returns:
        str: Normalized field name with underscores (e.g., "metadata_score").
    '''
def get_filterable_field_type(field_name: str, filterable_fields: list[dict[str, Any]]) -> str | None:
    '''Get the field type for a metadata key from filterable_fields.

    Args:
        field_name (str): Metadata key (e.g., "score") or full field name (e.g., "metadata.score").
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.

    Returns:
        str | None: Field type (FieldType enum value) or None if not found.
    '''
def metadata_field_mapping(metadata: dict[str, Any], filterable_fields: list[dict[str, Any]]) -> dict[str, Any]:
    '''Convert metadata dictionary into Redis hash field mappings with type-aware storage.

    Values are stored in appropriate formats based on their types and filterable_fields configuration:
    1. Numeric values: stored as numbers (for NUMERIC fields)
    2. String values: stored as strings (for TAG fields)
    3. Boolean values: stored as "1"/"0" (for TAG fields)
    4. List values: stored as comma-separated strings (for TAG fields)

    Args:
        metadata (dict[str, Any]): Metadata dictionary to convert.
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.

    Returns:
        dict[str, Any]: Mapping of normalized field names to values in appropriate formats.
    '''
def infer_filterable_fields_from_chunks(items: list[Any]) -> list[dict[str, Any]]:
    '''Infer filterable fields schema from chunks.

    Analyzes metadata in chunks to determine field types:
    1. Boolean types (bool) -> FieldType.TAG (stored as "1"/"0" strings)
    2. Numeric types (int, float) -> FieldType.NUMERIC
    3. All other types -> FieldType.TEXT (default)

    Note: bool must be checked before int/float since bool is a subclass of int in Python.

    Args:
        items (list[Any]): Chunks to analyze.

    Returns:
        list[dict[str, Any]]: List of inferred filterable field configurations.
    '''
def validate_metadata_fields(items: list[Any], filterable_fields: list[dict[str, Any]]) -> None:
    '''Validate that metadata fields in chunks are compatible with the index schema.

    For example, if filterable_fields is [{"name": "metadata.score", "type": "numeric"}],
    and the chunk has metadata {"score": "not-a-number"}, this method will raise a ValueError.

    Args:
        items (list[Any]): Chunks to validate.
        filterable_fields (list[dict[str, Any]]): Filterable fields configuration.

    Raises:
        ValueError: If values are incompatible with the field type (e.g., non-numeric
            value for numeric field).
    '''
async def get_doc_ids_for_deletion(client: Redis, index_name: str, query_translator: RedisQueryTranslator, filters: QueryFilter | None = None, options: QueryOptions | None = None) -> list[str]:
    """Get document IDs for deletion based on filters or options.

    When using filters (not options), uses batching with incrementing offset to collect
    all matching document IDs before deletion.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.
        query_translator (RedisQueryTranslator): Query translator instance.
        filters (QueryFilter | None, optional): Query filters. Defaults to None.
        options (QueryOptions | None, optional): Query options. Defaults to None.

    Returns:
        list[str]: List of document IDs to delete.
    """
async def collect_document_ids(client: Redis, index_name: str, query_translator: RedisQueryTranslator, filters: QueryFilter | None = None, batch_size: int = 100) -> list[str]:
    """Collect all matching document IDs from the datastore.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index to search.
        query_translator (RedisQueryTranslator): Query translator instance.
        filters (QueryFilter | None, optional): Query filters to apply. Defaults to None.
        batch_size (int, optional): Number of document IDs per batch. Defaults to 100.

    Returns:
        list[str]: List of all matching document IDs.
    """
async def delete_keys_batched(client: Redis, index_name: str, doc_ids: list[str]) -> int:
    """Delete Redis keys for the specified document IDs in a batch.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.
        doc_ids (list[str]): List of document IDs to delete.

    Returns:
        int: Number of keys deleted.
    """
async def process_doc_ids_in_batches(client: Redis, index_name: str, doc_ids: list[str], batch_func: Any, *args, batch_size: int = 100) -> int:
    """Process document IDs in batches using the provided batch function.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.
        doc_ids (list[str]): List of document IDs to process.
        batch_func (Any): Async function to call for each batch.
        *args: Additional arguments to pass to batch_func.
        batch_size (int, optional): Number of documents per batch. Defaults to 100.

    Returns:
        int: Total number of documents processed.
    """
async def fetch_hash_data_batch(client: Redis, index_name: str, doc_ids: list[str]) -> list[dict[str, Any]]:
    """Fetch hash data for a batch of document IDs.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.
        doc_ids (list[str]): List of document IDs to fetch.

    Returns:
        list[dict[str, Any]]: List of hash data for each document.
    """
def prepare_update_values(doc: dict[str, Any], update_values: dict[str, Any], filterable_fields: list[dict[str, Any]]) -> tuple[str, dict[str, Any], set[str]]:
    """Prepare update values for a document.

    Args:
        doc (dict[str, Any]): Current document data from Redis.
        update_values (dict[str, Any]): Values to update.
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.

    Returns:
        tuple[str, dict[str, Any], set[str]]: Tuple of (content, merged_metadata, old_metadata_fields).
    """
def build_update_commands(keys: list[str], doc_data: list[dict[str, Any]], update_values: dict[str, Any], filterable_fields: list[dict[str, Any]]) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]]]:
    """Build update commands for a batch of documents.

    Args:
        keys (list[str]): List of Redis keys for the documents.
        doc_data (list[dict[str, Any]]): List of current document data.
        update_values (dict[str, Any]): Values to update.
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.

    Returns:
        tuple[dict[str, dict[str, Any]], dict[str, set[str]]]: Tuple of (update_mappings, removal_fields).
    """
async def process_update_batch(client: Redis, index_name: str, doc_ids: list[str], update_values: dict[str, Any], filterable_fields: list[dict[str, Any]]) -> int:
    """Process a batch of document updates.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.
        doc_ids (list[str]): List of document IDs to update.
        update_values (dict[str, Any]): Values to update.
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.

    Returns:
        int: Number of documents updated.
    """
def build_filter_expression(query_translator: RedisQueryTranslator, filters: QueryFilter | None = None) -> str | None:
    '''Build RedisVL filter expression from QueryFilter.

    This function converts QueryFilter objects into RedisVL filter expression format.
    Both RedisVL and Redis Search use the same query syntax, so this delegates to
    RedisQueryTranslator which produces Redis Search/RedisVL compatible queries.

    Examples:
        1. F.eq("name", "John") → "@name:{John}"
        2. F.gt("age", 18) → "@age:[18 +inf]"
        3. F.and_(F.eq("status", "active"), F.gt("score", 50)) → "@status:{active} @score:[50 +inf]"

    Args:
        query_translator (RedisQueryTranslator): Query translator instance.
        filters (QueryFilter | None, optional): Query filters to apply. Defaults to None.

    Returns:
        str | None: RedisVL filter expression string or None if no filters.

    Raises:
        ValueError: If filter structure is invalid or operator is incompatible with field type.
        TypeError: If filter contains type mismatches.
    '''
async def check_index_exists(client: Redis, index_name: str) -> bool:
    """Check if a Redis index exists.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.

    Returns:
        bool: True if index exists, False otherwise.
    """
def validate_chunk_list(data: Any) -> list[Any]:
    """Validate and normalize chunk input to a list.

    Args:
        data (Any): Input data to validate (single Chunk or list of Chunks).

    Returns:
        list[Any]: List of chunks.

    Raises:
        ValueError: If data structure is invalid.
    """
def validate_chunk_content(chunks: list[Any]) -> None:
    """Validate chunk content is non-empty string.

    Args:
        chunks (list[Any]): List of chunks to validate.

    Raises:
        ValueError: If chunk content is invalid.
    """
def prepare_chunk_document(chunk: Any, filterable_fields: list[dict[str, Any]], include_vector: bool = False, vector: Vector | None = None, index_name: str | None = None) -> dict[str, Any]:
    """Prepare a chunk document for Redis storage.

    Args:
        chunk (Any): Chunk object to prepare.
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.
        include_vector (bool, optional): Whether to include vector field. Defaults to False.
        vector (Vector | None, optional): Vector data to include if include_vector is True. Defaults to None.
        index_name (str | None, optional): Index name to strip from chunk ID if present. Defaults to None.

    Returns:
        dict[str, Any]: Document dictionary ready for Redis storage.
    """
def strip_index_prefix(doc_id: str, index_name: str) -> str:
    '''Remove index prefix from document ID.

    RedisVL returns document IDs with the index prefix (e.g., "index_name:doc_id" or "index_name::doc_id").
    This function strips the prefix to return just the document ID.
    Also handles cases where the ID starts with just ":" or "::" separators.

    Args:
        doc_id (str): Full document ID with index prefix.
        index_name (str): Index name to remove from the prefix.

    Returns:
        str: Document ID without the index prefix.
    '''
def get_redis_url_from_client(client: Any) -> str:
    """Extract Redis URL from a Redis client connection.

    Works with both sync and async Redis clients.

    Warning:
        This function returns the Redis URL with additional information like password, host, port, and database.
        Do not log the returned URL.

    Args:
        client (Any): Redis client instance (sync or async).

    Returns:
        str: Redis URL in the format redis://[password@]host:port[/db].
    """
def get_filterable_fields_from_index(index_name: str, client: Any, cached_fields: list[dict[str, Any]] | None = None, excluded_fields: set[str] | None = None) -> list[dict[str, Any]]:
    """Get filterable fields from an existing Redis index schema.

    This function extracts filterable field definitions from a Redis index
    and converts them into the filterable_fields format used by this library.

    Args:
        index_name (str): Name of the Redis index.
        client (Any): Redis client instance (sync or async).
        cached_fields (list[dict[str, Any]] | None, optional): Cached filterable fields
            to return if available. Defaults to None.
        excluded_fields (set[str] | None, optional): Set of field names to exclude
            from the result. Defaults to None.

    Returns:
        list[dict[str, Any]]: List of filterable field configurations.
    """
async def execute_update(client: Redis, index_name: str, chunks: list[Chunk], chunk_ids: list[str], vectors: list[Vector], filterable_fields: list[dict[str, Any]]) -> None:
    """Execute update transaction using Redis pipeline.

    Args:
        client (Redis): Redis client instance.
        index_name (str): Name of the Redis index.
        chunks (list[Chunk]): List of updated chunks.
        chunk_ids (list[str]): List of chunk IDs to update.
        vectors (list[Vector]): List of vectors corresponding to chunks.
        filterable_fields (list[dict[str, Any]]): List of filterable field configurations.
    """
def parse_redisvl_result_to_chunks(results: list[dict[str, Any]], index_name: str) -> list[Chunk]:
    """Parse RedisVL search results into Chunk objects.

    RedisVL returns search results as a list of dictionaries. This function
    converts them into Chunk objects with proper metadata parsing and ID stripping.

    Args:
        results (list[dict[str, Any]]): List of RedisVL search result dictionaries.
        index_name (str): Index name for stripping prefixes from document IDs.

    Returns:
        list[Chunk]: List of parsed Chunk objects.
    """
