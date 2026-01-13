from abc import ABC
from elasticsearch.dsl import AsyncSearch as ESAsyncSearch
from elasticsearch.dsl.query import Query as ESQuery
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, FilterCondition as FilterCondition, FilterOperator as FilterOperator, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from opensearchpy._async.helpers.search import AsyncSearch as OSAsyncSearch
from opensearchpy.helpers.query import Query as OSQuery

AsyncSearchType = ESAsyncSearch | OSAsyncSearch
QueryType = ESQuery | OSQuery

class ElasticLikeQueryTranslator(ABC):
    """Base class for Elasticsearch-like query translators.

    This class provides shared translation logic for converting FilterClause and
    QueryFilter objects to product-specific Query DSL objects. Subclasses must
    implement abstract methods to create Query objects using their DSL API.

    Attributes:
        _logger: Logger instance for error messages.
    """
    def __init__(self) -> None:
        """Initialize the query translator."""
    def translate(self, filters: QueryFilter | None) -> QueryType | None:
        """Translate a structured QueryFilter into a Query DSL object.

        The translation supports comparison operators (EQ, NE, GT, LT, GTE, LTE),
        array operators (IN, NIN, ARRAY_CONTAINS, ANY, ALL), text operators (TEXT_CONTAINS),
        and logical conditions (AND, OR, NOT), including nested filters.

        Args:
            filters (QueryFilter | None): Structured QueryFilter containing filter clauses
                and logical conditions. If None or empty, returns None.

        Returns:
            QueryType | None: Query DSL object representing the translated filters.
                Returns None if no filters are provided or filters are empty.
                The actual Query type depends on the product-specific implementation
                (elasticsearch.dsl.query.Query or opensearchpy.helpers.query.Query).

        Raises:
            ValueError: When the filter structure is invalid or translation fails.
        """
    def apply_options(self, search: AsyncSearchType, options: QueryOptions | None) -> AsyncSearchType:
        """Apply QueryOptions to an Elasticsearch/OpenSearch search object.

        This method applies query options including limit, field inclusion, and sorting
        to a search object. Both Elasticsearch and OpenSearch AsyncSearch objects
        support the same API for these operations.

        Args:
            search (AsyncSearchType): Elasticsearch or OpenSearch search object to modify.
                The search object will be modified in-place and returned.
            options (QueryOptions | None): Query options including limit, sort, and fields.
                If None, the search object is returned unchanged. Defaults to None.

        Returns:
            AsyncSearchType: Modified search object with options applied.
                Returns the same search object instance with modifications.
        """
    def apply_filters_and_options(self, search: AsyncSearchType, filters: QueryFilter | None = None, options: QueryOptions | None = None) -> AsyncSearchType:
        """Apply both filters and options to an Elasticsearch/OpenSearch search object.

        This method applies filters first (if provided), then applies options.
        Both operations modify the search object in-place.

        Args:
            search (AsyncSearchType): Elasticsearch or OpenSearch search object to modify.
                The search object will be modified in-place and returned.
            filters (QueryFilter | None, optional): QueryFilter with filters and logical condition.
                If provided, filters will be translated and applied to the search query.
                Defaults to None.
            options (QueryOptions | None, optional): Query options including limit, sort, and fields.
                If provided, options will be applied to the search object.
                Defaults to None.

        Returns:
            AsyncSearchType: Modified search object with filters and options applied.
                Returns the same search object instance with modifications.
        """
