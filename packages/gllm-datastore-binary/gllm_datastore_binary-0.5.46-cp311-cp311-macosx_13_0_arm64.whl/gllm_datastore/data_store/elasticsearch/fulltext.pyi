from _typeshed import Incomplete
from elasticsearch import AsyncElasticsearch
from elasticsearch.dsl import AttrDict as AttrDict
from enum import StrEnum
from gllm_core.schema import Chunk
from gllm_datastore.constants import METADATA_KEYS as METADATA_KEYS
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store._elastic_core.base import ElasticLikeCore as ElasticLikeCore
from gllm_datastore.data_store.elasticsearch.query import apply_filter_query_to_search as apply_filter_query_to_search, apply_filters_and_options as apply_filters_and_options, create_search_with_filters as create_search_with_filters, delete_by_id as delete_by_id, delete_by_query as delete_by_query, safe_execute as safe_execute, translate_filter as translate_filter, update_by_query as update_by_query, validate_query_length as validate_query_length
from typing import Any, Literal, overload

class SupportedQueryMethods(StrEnum):
    """Supported query methods for Elasticsearch fulltext capability."""
    AUTOCOMPLETE: str
    AUTOSUGGEST: str
    BM25: str
    BY_FIELD: str
    SHINGLES: str

QUERY_REQUIRED_STRATEGIES: Incomplete

class ElasticsearchFulltextCapability:
    """Elasticsearch implementation of FulltextCapability protocol.

    This class provides document CRUD operations and flexible querying using Elasticsearch.

    Attributes:
        index_name (str): The name of the Elasticsearch index.
        client (AsyncElasticsearch): AsyncElasticsearch client.
        query_field (str): The field name to use for text content.

    """
    index_name: Incomplete
    client: Incomplete
    query_field: Incomplete
    def __init__(self, index_name: str, client: AsyncElasticsearch, query_field: str = 'text') -> None:
        '''Initialize the Elasticsearch fulltext capability.

        Args:
            index_name (str): The name of the Elasticsearch index.
            client (AsyncElasticsearch): The Elasticsearch client.
            query_field (str, optional): The field name to use for text content. Defaults to "text".
        '''
    async def get_size(self) -> int:
        """Returns the total number of documents in the index.

        Returns:
            int: The total number of documents.
        """
    async def create(self, data: Chunk | list[Chunk], **kwargs: Any) -> None:
        """Create new records in the datastore.

        Args:
            data (Chunk | list[Chunk]): Data to create (single item or collection).
            **kwargs: Backend-specific parameters forwarded to Elasticsearch bulk API.

        Raises:
            ValueError: If data structure is invalid.
        """
    @overload
    async def retrieve(self, strategy: Literal[SupportedQueryMethods.BY_FIELD] | None = ..., query: str | None = None, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs: Any) -> list[Chunk]: ...
    @overload
    async def retrieve(self, strategy: Literal[SupportedQueryMethods.BM25], query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, k1: float | None = None, b: float | None = None, **kwargs: Any) -> list[Chunk]: ...
    @overload
    async def retrieve(self, strategy: Literal[SupportedQueryMethods.AUTOCOMPLETE], query: str, field: str, size: int = 20, fuzzy_tolerance: int = 1, min_prefix_length: int = 3, filter_query: dict[str, Any] | None = None, **kwargs: Any) -> list[str]: ...
    @overload
    async def retrieve(self, strategy: Literal[SupportedQueryMethods.AUTOSUGGEST], query: str, search_fields: list[str], autocomplete_field: str, size: int = 20, min_length: int = 3, filter_query: dict[str, Any] | None = None, **kwargs: Any) -> list[str]: ...
    @overload
    async def retrieve(self, strategy: Literal[SupportedQueryMethods.SHINGLES], query: str, field: str, size: int = 20, min_length: int = 3, max_length: int = 30, filter_query: dict[str, Any] | None = None, **kwargs: Any) -> list[str]: ...
    async def retrieve_by_field(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        """Retrieve records from the datastore based on metadata field filtering.

        This method filters and returns stored chunks based on metadata values
        rather than text content. It is particularly useful for structured lookups,
        such as retrieving all chunks from a certain source, tagged with a specific label,
        or authored by a particular user.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options (sorting, pagination, etc.).
                Defaults to None.

        Returns:
            list[Chunk]: The filtered results as Chunk objects.
        """
    async def retrieve_bm25(self, query: str, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, k1: float | None = None, b: float | None = None) -> list[Chunk]:
        '''Queries the Elasticsearch data store using BM25 algorithm for keyword-based search.

        Args:
            query (str): The query string.
            filters (FilterClause | QueryFilter | None, optional): Optional metadata filter to apply to the search.
                FilterClause objects are automatically converted to QueryFilter internally.
                Use filter builder functions like `F.eq()`, `F.and_()`, etc. Defaults to None.
            options (QueryOptions | None, optional): Query options including fields, limit, order_by, etc.
                For example, `QueryOptions(fields=["title", "content"], limit=10, order_by="score", order_desc=True)`.
                If fields is None, defaults to ["text"]. For multiple fields, uses multi_match query. Defaults to None.
            k1 (float | None, optional): BM25 parameter controlling term frequency saturation.
                Higher values mean term frequency has more impact before diminishing returns.
                Typical values: 1.2-2.0. If None, uses Elasticsearch default (~1.2). Defaults to None.
            b (float | None, optional): BM25 parameter controlling document length normalization.
                0.0 = no length normalization, 1.0 = full normalization.
                Typical values: 0.75. If None, uses Elasticsearch default (~0.75). Defaults to None.

        Examples:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Basic BM25 query on the \'text\' field
            results = await data_store.query_bm25("machine learning")

            # BM25 query on specific fields with query options
            results = await data_store.query_bm25(
                "natural language",
                options=QueryOptions(fields=["title", "abstract"], limit=5)
            )

            # BM25 query with direct FilterClause
            results = await data_store.query_bm25(
                "deep learning",
                filters=F.eq("metadata.category", "AI")
            )

            # BM25 query with multiple filters
            results = await data_store.query_bm25(
                "deep learning",
                filters=F.and_(F.eq("metadata.category", "AI"), F.eq("metadata.status", "published"))
            )

            # BM25 query with custom BM25 parameters for more aggressive term frequency weighting
            results = await data_store.query_bm25(
                "artificial intelligence",
                k1=2.0,
                b=0.5
            )

            # BM25 query with fields, filters, and options
            results = await data_store.query_bm25(
                "data science applications",
                filters=F.and_(
                    F.eq("metadata.author_id", "user123"),
                    F.in_("metadata.publication_year", [2022, 2023])
                ),
                options=QueryOptions(fields=["content", "tags"], limit=10, order_by="score", order_desc=True),
                k1=1.5,
                b=0.9
            )
            ```

        Returns:
            list[Chunk]: A list of Chunk objects representing the retrieved documents.
        '''
    async def retrieve_autocomplete(self, query: str, field: str, size: int = 20, fuzzy_tolerance: int = 1, min_prefix_length: int = 3, filter_query: dict[str, Any] | None = None) -> list[str]:
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
    async def retrieve_autosuggest(self, query: str, search_fields: list[str], autocomplete_field: str, size: int = 20, min_length: int = 3, filters: QueryFilter | None = None) -> list[str]:
        """Generates suggestions across multiple fields using a multi_match query to broaden the search criteria.

        Args:
            query (str): The query string.
            search_fields (list[str]): The fields to search for.
            autocomplete_field (str): The field name for autocomplete.
            size (int, optional): The number of suggestions to retrieve. Defaults to 20.
            min_length (int, optional): The minimum length of the query. Defaults to 3.
            filters (QueryFilter | None, optional): The filter query. Defaults to None.

        Returns:
            list[str]: A list of suggestions.
        """
    async def retrieve_shingles(self, query: str, field: str, size: int = 20, min_length: int = 3, max_length: int = 30, filters: QueryFilter | None = None) -> list[str]:
        """Searches using shingles for prefix and fuzzy matching.

        Args:
            query (str): The query string.
            field (str): The field name for autocomplete.
            size (int, optional): The number of suggestions to retrieve. Defaults to 20.
            min_length (int, optional): The minimum length of the query.
                Queries shorter than this limit will return an empty list. Defaults to 3.
            max_length (int, optional): The maximum length of the query.
                Queries exceeding this limit will return an empty list. Defaults to 30.
            filters (QueryFilter | None, optional): The filter query. Defaults to None.

        Returns:
            list[str]: A list of suggestions.
        """
    async def retrieve_fuzzy(self, query: str, max_distance: int = 2, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> list[Chunk]:
        """Find records that fuzzy match the query within distance threshold.

        Args:
            query (str): Text to fuzzy match against.
            max_distance (int): Maximum edit distance for matches. Defaults to 2.
            filters (FilterClause | QueryFilter | None, optional): Optional metadata filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options (limit, sorting, etc.). Defaults to None.

        Returns:
            list[Chunk]: Matched chunks.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None) -> None:
        """Update existing records in the datastore.

        Args:
            update_values (dict[str, Any]): Values to update.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
        """
    async def delete(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> None:
        """Delete records from the data store using filters and optional options.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records for deletion.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options supporting limit and sorting
                for eviction-like operations. Defaults to None.
        """
    async def delete_by_id(self, id_: str | list[str]) -> None:
        """Deletes records from the data store based on IDs.

        Args:
            id_ (str | list[str]): ID or list of IDs to delete.
        """
    async def clear(self) -> None:
        """Clear all records from the datastore."""
