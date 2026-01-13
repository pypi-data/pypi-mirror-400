from _typeshed import Incomplete
from datetime import datetime
from gllm_core.schema import Chunk
from gllm_datastore.constants import DEFAULT_REQUEST_TIMEOUT as DEFAULT_REQUEST_TIMEOUT, DEFAULT_TOP_K as DEFAULT_TOP_K, METADATA_KEYS as METADATA_KEYS
from gllm_datastore.utils.converter import from_langchain as from_langchain, to_langchain as to_langchain
from gllm_datastore.vector_data_store.mixin.cache_compatible_mixin import CacheCompatibleMixin as CacheCompatibleMixin
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from langchain_core.embeddings import Embeddings
from typing import Any

DEFAULT_FETCH_K: int

class ElasticsearchVectorDataStore(BaseVectorDataStore, CacheCompatibleMixin):
    """DataStore for interacting with Elasticsearch.

    This class provides methods for executing queries and retrieving documents
    from Elasticsearch. It relies on the LangChain's ElasticsearchStore  for
    vector operations and the underlying Elasticsearch client management.

    Attributes:
        vector_store (ElasticsearchStore): The ElasticsearchStore instance for vector operations.
        sync_vector_store (ElasticsearchStore): The ElasticsearchStore instance for sync operations.
        index_name (str): The name of the Elasticsearch index.
        embedding (BaseEMInvoker | Embeddings | None): The embedding model to perform vectorization.
        logger (Logger): The logger object.
    """
    index_name: Incomplete
    vector_store: Incomplete
    logger: Incomplete
    def __init__(self, index_name: str, embedding: BaseEMInvoker | Embeddings | None = None, connection: Any | None = None, url: str | None = None, cloud_id: str | None = None, user: str | None = None, api_key: str | None = None, password: str | None = None, vector_query_field: str = 'vector', query_field: str = 'text', distance_strategy: str | None = None, strategy: Any | None = None, request_timeout: int = ...) -> None:
        '''Initializes an instance of the ElasticsearchVectorDataStore class.

        Args:
            index_name (str): The name of the Elasticsearch index.
            embedding (BaseEMInvoker | Embeddings | None, optional): The embedding model to perform vectorization.
                Defaults to None.
            connection (Any | None, optional): The Elasticsearch connection object. Defaults to None.
            url (str | None, optional): The URL of the Elasticsearch server. Defaults to None.
            cloud_id (str | None, optional): The cloud ID of the Elasticsearch cluster. Defaults to None.
            user (str | None, optional): The username for authentication. Defaults to None.
            api_key (str | None, optional): The API key for authentication. Defaults to None.
            password (str | None, optional): The password for authentication. Defaults to None.
            vector_query_field (str, optional): The field name for vector queries. Defaults to "vector".
            query_field (str, optional): The field name for text queries. Defaults to "text".
            distance_strategy (str | None, optional): The distance strategy for retrieval. Defaults to None.
            strategy (Any | None, optional): The retrieval strategy for retrieval. Defaults to None, in which case
                DenseVectorStrategy() is used.
            request_timeout (int, optional): The request timeout. Defaults to DEFAULT_REQUEST_TIMEOUT.

        Raises:
            TypeError: If `embedding` is not an instance of `BaseEMInvoker` or `Embeddings`.
        '''
    async def get_size(self) -> int:
        """Returns the total number of vectors in the index.

        If the index is not initialized returns 0.

        Returns:
            int: The total number of vectors.
        """
    async def query(self, query: str, top_k: int = ..., retrieval_params: dict[str, Any] | None = None) -> list[Chunk]:
        """Queries the Elasticsearch data store and includes similarity scores.

        Args:
            query (str): The query string.
            top_k (int, optional): The number of top results to retrieve. Defaults to DEFAULT_TOP_K.
            retrieval_params (dict[str, Any] | None, optional): Additional retrieval parameters. Defaults to None.

        Returns:
            list[Chunk]: A list of Chunk objects representing the retrieved documents with
                similarity scores.
        """
    async def query_by_id(self, id_: str | list[str]) -> list[Chunk]:
        """Queries the data store by ID and returns a list of Chunk objects.

        Args:
            id_: The ID of the document to query.

        Returns:
            A list of Chunk objects representing the queried documents.

        Note:
            This method not implement yet. Because the ElasticsearchStore
            still not implement the get_by_ids method yet.
        """
    async def bm25_query(self, query: str, top_k: int = ..., search_fields: list[str] | None = None, filter: dict[str, Any] | None = None, metadata: dict[str, Any] | None = None, k1: float | None = None, b: float | None = None) -> list[Chunk]:
        '''Queries the Elasticsearch data store using BM25 algorithm for keyword-based search.

        Args:
            query (str): The query string.
            top_k (int, optional): The number of top results to retrieve. Defaults to DEFAULT_TOP_K.
            search_fields (list[str] | None, optional): The fields to search in. If None, defaults to ["text"].
                For multiple fields, uses multi_match query. Defaults to None.
            filter (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"category": "AI", "source": ["doc1", "doc2"]}`. Defaults to None.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                DEPRECATED: Use `filter` parameter instead. Will be removed in a future version.
                For example, `{"category": "AI", "source": ["doc1", "doc2"]}`. Defaults to None.
            k1 (float | None, optional): BM25 parameter controlling term frequency saturation.
                Higher values mean term frequency has more impact before diminishing returns.
                Typical values: 1.2-2.0. If None, uses Elasticsearch default (~1.2). Defaults to None.
            b (float | None, optional): BM25 parameter controlling document length normalization.
                0.0 = no length normalization, 1.0 = full normalization.
                Typical values: 0.75. If None, uses Elasticsearch default (~0.75). Defaults to None.

        Example:
            ```python
            # Basic BM25 query on the \'text\' field
            results = await data_store.bm25_query("machine learning")

            # BM25 query on specific fields with a custom top_k
            results = await data_store.bm25_query(
                "natural language",
                top_k=5,
                search_fields=["title", "abstract"]
            )

            # BM25 query with filter
            results = await data_store.bm25_query(
                "deep learning",
                filter={"category": "AI", "status": "published"}
            )

            # BM25 query with metadata filtering (deprecated)
            results = await data_store.bm25_query(
                "deep learning",
                metadata={"category": "AI", "status": "published"}
            )

            # BM25 query with custom BM25 parameters for more aggressive term frequency weighting
            results = await data_store.bm25_query(
                "artificial intelligence",
                k1=2.0,
                b=0.5
            )

            # BM25 query with both search fields and BM25 tuning
            results = await data_store.bm25_query(
                "data science applications",
                search_fields=["content", "tags"],
                filter={"author_id": "user123", "publication_year": [2022, 2023]},
                k1=1.5,
                b=0.9
            )
            ```

        Returns:
            list[Chunk]: A list of Chunk objects representing the retrieved documents.
        '''
    async def autocomplete(self, query: str, field: str, size: int = 20, fuzzy_tolerance: int = 1, min_prefix_length: int = 3, filter_query: dict[str, Any] | None = None) -> list[str]:
        """Provides suggestions based on a prefix query for a specific field.

        Args:
            query (str): The query string.
            field (str): The field name for autocomplete.
            size (int, optional): The number of suggestions to retrieve. Defaults to 20.
            fuzzy_tolerance (int, optional): The level of fuzziness for suggestions. Defaults to 1.
            min_prefix_length (int, optional): The minimum prefix length to trigger fuzzy matching. Defaults to 3.
            filter_query (dict[str, Any] | None, optional): The filter query. Defaults to None.

        Returns:
            list[str]: A list of suggestions.
        """
    async def autosuggest(self, query: str, search_fields: list[str], autocomplete_field: str, size: int = 20, min_length: int = 3, filter_query: dict[str, Any] | None = None) -> list[str]:
        """Generates suggestions across multiple fields using a multi_match query to broaden the search criteria.

        Args:
            query (str): The query string.
            search_fields (list[str]): The fields to search for.
            autocomplete_field (str): The field name for autocomplete.
            size (int, optional): The number of suggestions to retrieve. Defaults to 20.
            min_length (int, optional): The minimum length of the query. Defaults to 3.
            filter_query (dict[str, Any] | None, optional): The filter query. Defaults to None.

        Returns:
            list[str]: A list of suggestions.
        """
    async def shingles(self, query: str, field: str, size: int = 20, min_length: int = 3, max_length: int = 30, filter_query: dict[str, Any] | None = None) -> list[str]:
        """Searches using shingles for prefix and fuzzy matching.

        Args:
            query (str): The query string.
            field (str): The field name for autocomplete.
            size (int, optional): The number of suggestions to retrieve. Defaults to 20.
            min_length (int, optional): The minimum length of the query.
                Queries shorter than this limit will return an empty list. Defaults to 3.
            max_length (int, optional): The maximum length of the query.
                Queries exceeding this limit will return an empty list. Defaults to 30.
            filter_query (dict[str, Any] | None, optional): The filter query. Defaults to None.

        Returns:
            list[str]: A list of suggestions.
        """
    async def add_chunks(self, chunk: Chunk | list[Chunk], **kwargs: Any) -> list[str]:
        """Adds a chunk or a list of chunks to the data store.

        Args:
            chunk (Chunk | list[Chunk]): The chunk or list of chunks to add.
            kwargs (Any): Additional keyword arguments.

        Returns:
            list[str]: A list of unique identifiers (IDs) assigned to the added chunks.
        """
    async def add_embeddings(self, text_embeddings: list[tuple[str, list[float]]], metadatas: list[dict] | None = None, ids: list[str] | None = None, **kwargs) -> list[str]:
        """Adds text embeddings to the data store.

        Args:
            text_embeddings (list[tuple[str, list[float]]]): Pairs of string and embedding to add to the store.
            metadatas (list[dict], optional): Optional list of metadatas associated with the texts. Defaults to None.
            ids (list[str], optional): Optional list of unique IDs. Defaults to None.
            kwargs (Any): Additional keyword arguments.

        Returns:
            list[str]: A list of unique identifiers (IDs) assigned to the added embeddings.
        """
    async def delete_chunks(self, query: dict[str, Any], **kwargs: Any) -> None:
        """Deletes chunks from the data store based on a query.

        Args:
            query (dict[str, Any]): Query to match documents for deletion.
            kwargs (Any): Additional keyword arguments.

        Returns:
            None
        """
    async def delete_chunks_by_ids(self, ids: str | list[str], **kwargs: Any) -> None:
        """Deletes chunks from the data store based on IDs.

        Args:
            ids (str | list[str]): A single ID or a list of IDs to delete.
            kwargs (Any): Additional keyword arguments.
        """
    async def exact_match(self, key: str, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that exactly match the given key.

        Args:
            key (str): The key to match.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The value stored with the exact key, or None if no match is found.
        '''
    async def fuzzy_match(self, key: str, max_distance: int = 2, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that approximately match the given key using fuzzy matching.

        Args:
            key (str): The key to match.
            max_distance (int): The maximum distance for fuzzy matching. Defaults to 2. Ranges from 0 to 2.
                Higher values are more lenient.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The value with the closest fuzzy match, or None if no match meets the threshold.
        '''
    async def semantic_match(self, key: str, min_similarity: float = 0.8, metadata: dict[str, Any] | None = None) -> Any | None:
        '''Find chunks that semantically match the given key using vector similarity.

        Args:
            key (str): The key to match.
            min_similarity (float): Minimum similarity score for semantic matching
                (higher values are more strict). Ranges from 0 to 1. Defaults to 0.8.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                For example, `{"key": "value"}`. Defaults to None.

        Returns:
            Any: The semantically closest value, or None if no match meets the min_similarity threshold.
        '''
    async def delete_expired_entries(self, now: datetime, max_size: int = 10000) -> None:
        """Delete expired entries (for TTL eviction).

        Args:
            now (datetime): The current datetime for comparison.
            max_size (int): The maximum number of entries to return. Defaults to 10000.

        Returns:
            None
        """
    async def delete_least_frequently_used_entries(self, num_entries: int) -> None:
        """Delete least frequently used entries (for LFU eviction).

        Args:
            num_entries (int): Number of entries to return.

        Returns:
            None
        """
    async def delete_least_recently_used_entries(self, num_entries: int) -> None:
        """Delete least recently used entries (for LRU eviction).

        Args:
            num_entries (int): Number of entries to return.

        Returns:
            None
        """
    async def delete_entries_by_key(self, key: str | list[str], metadata: dict[str, Any] | None = None) -> None:
        '''Delete entries by key.

        Example:
            ```python
            key = "key-1"
            metadata = {"id": "id-1"}
            await delete_entries_by_key(key, metadata)
            ```
            This will delete the entry with the key "key-1" by filtering by the metadata "id": "id-1".

        Args:
            key (str | list[str]): The key or list of keys to delete entries for.
            metadata (dict[str, Any] | None, optional): Optional metadata filter to apply to the search.
                Defaults to None.
        '''
    async def clear(self) -> None:
        """Clear all entries in the storage.

        Raises:
            NotImplementedError: Currently, app-level eviction is not supported for ElasticsearchVectorDataStore.
        """
    async def query_by_field(self, retrieval_params: dict, limit: int | None = None, **kwargs) -> list[Chunk]:
        """Retrieve documents that match specific metadata constraints.

        This method filters and returns stored chunks based on metadata values
        rather than vector similarity. It is particularly useful for structured lookups,
        such as retrieving all chunks from a certain source, tagged with a specific label,
        or authored by a particular user.

        Unlike semantic search methods, `query_by_field` operates purely on metadata fields
        associated with each document, allowing precise filtering based on key-value pairs.

        Expected:
            Returns a list of `Chunk` objects matching the metadata query.

        Args:
            retrieval_params (dict): Must contain a `filter` key with an Elasticsearch DSL query.
            limit (int, optional): Maximum number of results to return.
            **kwargs: Additional arguments for the Elasticsearch search call.

        Returns:
            list[Chunk]: The filtered results as `Chunk` objects.
        """
    async def query_by_vector(self, vector: list[float], top_k: int = ..., min_similarity: float = 0.8, retrieval_params: dict | None = None) -> list[Chunk]:
        """Search for documents that are similar to a given vector.

        Args:
            vector (list[float]): The query embedding vector to compare against stored vectors.
            top_k (int, optional): The number of top results to return. Defaults to DEFAULT_TOP_K.
            min_similarity (float): Minimum similarity score for vector similarity.
            retrieval_params (dict | None, optional): Filter parameters to narrow the search:
                - filter (Where): Metadata-based filter.
                - where_document (WhereDocument): Content-based filter.
                Defaults to None.

        Returns:
            list[Chunk]: A list of Chunk objects with similarity scores based on the input vector.
        """
