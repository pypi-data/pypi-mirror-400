import logging
from _typeshed import Incomplete
from elasticsearch import AsyncElasticsearch
from elasticsearch.dsl import AsyncSearch
from elasticsearch.dsl.query import Query
from elasticsearch.dsl.response import Response
from gllm_datastore.core.filters.schema import QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.elasticsearch.query_translator import ElasticsearchQueryTranslator as ElasticsearchQueryTranslator
from gllm_datastore.utils import flatten_dict as flatten_dict
from typing import Any

VALID_FIELD_PATH: Incomplete

def apply_filters_and_options(search: AsyncSearch, filters: QueryFilter | None = None, options: QueryOptions | None = None) -> AsyncSearch:
    """Apply filters and options to an Elasticsearch search object.

    Args:
        search (AsyncSearch): Elasticsearch search object.
        filters (QueryFilter | None, optional): New QueryFilter with filters and condition.
        options (QueryOptions | None, optional): Query options (limit, sort, fields).

    Returns:
        AsyncSearch: Elasticsearch search object.
    """
def translate_filter(filters: QueryFilter | None) -> Query | None:
    """Translate a structured QueryFilter into an Elasticsearch DSL Query.

    The translation supports comparison operators (EQ, NE, GT, LT, GTE, LTE),
    array operators (IN, NIN, ARRAY_CONTAINS, ANY, ALL), text operators (TEXT_CONTAINS),
    and logical conditions (AND, OR, NOT), including nested filters.

    Args:
        filters (QueryFilter | None): Structured QueryFilter. If None, returns None.

    Returns:
        Query | None: An Elasticsearch Query object or None if no filters are provided.

    Raises:
        ValueError: When the filter structure is invalid.
        TypeError: When an operator-value type combination is invalid.
    """
async def update_by_query(client: AsyncElasticsearch, index_name: str, update_values: dict[str, Any], filters: QueryFilter | None = None, logger: logging.Logger | None = None) -> None:
    '''Update records in Elasticsearch using UpdateByQuery with retry logic for version conflicts.

    This function builds a painless script that safely assigns each updated field.
    When a field path contains dots (e.g. "metadata.cache_value"), we must
    access the corresponding param using bracket syntax: params[\'metadata.cache_value\']
    to avoid Painless treating it as nested object access (which would be None).

    Args:
        client (AsyncElasticsearch): Elasticsearch client instance.
        index_name (str): The name of the Elasticsearch index.
        update_values (dict[str, Any]): Values to update.
        filters (QueryFilter | None, optional): New QueryFilter to select records to update.
            Defaults to None.
        logger (Any | None, optional): Logger instance. Defaults to None.
    '''
async def delete_by_query(client: AsyncElasticsearch, index_name: str, filters: QueryFilter | None = None) -> None:
    """Delete records from Elasticsearch using delete_by_query.

    Args:
        client (AsyncElasticsearch): Elasticsearch client instance.
        index_name (str): The name of the Elasticsearch index.
        filters (QueryFilter | None, optional): New QueryFilter to select records for deletion.
            Defaults to None, in which case no operation will be performed.
    """
async def delete_by_id(client: AsyncElasticsearch, index_name: str, ids: str | list[str]) -> None:
    """Delete records from Elasticsearch by IDs using Search.delete().

    Args:
        client (AsyncElasticsearch): Elasticsearch client instance.
        index_name (str): The name of the Elasticsearch index.
        ids (str | list[str]): ID or list of IDs to delete.
    """
def validate_query_length(query: str, min_length: int = 0, max_length: int | None = None) -> bool:
    """Validate query length against minimum and maximum constraints.

    Args:
        query (str): The query string to validate.
        min_length (int, optional): Minimum required length. Defaults to 0.
        max_length (int | None, optional): Maximum allowed length. Defaults to None.

    Returns:
        bool: True if query is valid, False otherwise.
    """
def create_search_with_filters(client: AsyncElasticsearch, index_name: str, filters: QueryFilter | None = None, exclude_fields: list[str] | None = None) -> AsyncSearch:
    """Create an AsyncSearch object with optional filters and field exclusions.

    Args:
        client (AsyncElasticsearch): Elasticsearch client instance.
        index_name (str): The name of the Elasticsearch index.
        filters (QueryFilter | None, optional): New QueryFilter to apply. Defaults to None.
        exclude_fields (list[str] | None, optional): Fields to exclude from source. Defaults to None.

    Returns:
        AsyncSearch: Configured AsyncSearch object.
    """
def apply_filter_query_to_search(search: AsyncSearch, main_query: Query, filters: QueryFilter | None = None) -> AsyncSearch:
    """Apply filter query to a search with a main query.

    Args:
        search (AsyncSearch): Elasticsearch search object.
        main_query (Query): The main query to apply.
        filters (QueryFilter | None, optional): Query filters to apply. Defaults to None.

    Returns:
        AsyncSearch: Search object with applied queries.
    """
async def safe_execute(search: AsyncSearch, logger: logging.Logger | None = None) -> Response | None:
    """Execute an Elasticsearch DSL search with unified error handling.

    Args:
        search (AsyncSearch): Elasticsearch DSL AsyncSearch object.
        logger (logging.Logger | None, optional): Logger instance for error messages. Defaults to None.

    Returns:
        Response | None: The Elasticsearch response on success, otherwise None.
    """
