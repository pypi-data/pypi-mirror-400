import logging
from _typeshed import Incomplete
from gllm_datastore.core.filters.schema import QueryFilter as QueryFilter
from gllm_datastore.data_store.opensearch.query_translator import OpenSearchQueryTranslator as OpenSearchQueryTranslator
from gllm_datastore.utils import flatten_dict as flatten_dict
from opensearchpy import AsyncOpenSearch
from opensearchpy._async.helpers.search import AsyncSearch
from opensearchpy.helpers.query import Query
from typing import Any

VALID_FIELD_PATH: Incomplete

async def update_by_query(client: AsyncOpenSearch, index_name: str, update_values: dict[str, Any], filters: QueryFilter | None = None, logger: logging.Logger | None = None) -> None:
    '''Update records in OpenSearch using UpdateByQuery with retry logic for version conflicts.

    This function builds a painless script that safely assigns each updated field.
    When a field path contains dots (e.g. "metadata.cache_value"), we must
    access the corresponding param using bracket syntax: params[\'metadata.cache_value\']
    to avoid Painless treating it as nested object access (which would be None).

    Args:
        client (AsyncOpenSearch): OpenSearch client instance.
        index_name (str): The name of the OpenSearch index.
        update_values (dict[str, Any]): Values to update.
        filters (QueryFilter | None, optional): QueryFilter to select records to update.
            Defaults to None.
        logger (logging.Logger | None, optional): Logger instance. Defaults to None.
    '''
async def delete_by_query(client: AsyncOpenSearch, index_name: str, filters: QueryFilter | None = None) -> None:
    """Delete records from OpenSearch using delete_by_query.

    Args:
        client (AsyncOpenSearch): OpenSearch client instance.
        index_name (str): The name of the OpenSearch index.
        filters (QueryFilter | None, optional): QueryFilter to select records for deletion.
            Defaults to None, in which case no operation will be performed.
    """
async def delete_by_id(client: AsyncOpenSearch, index_name: str, ids: str | list[str]) -> None:
    """Delete records from OpenSearch by IDs using Search.delete().

    Args:
        client (AsyncOpenSearch): OpenSearch client instance.
        index_name (str): The name of the OpenSearch index.
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
def create_search_with_filters(client: AsyncOpenSearch, index_name: str, filters: QueryFilter | None = None, exclude_fields: list[str] | None = None) -> AsyncSearch:
    """Create an AsyncSearch object with optional filters and field exclusions.

    Args:
        client (AsyncOpenSearch): OpenSearch client instance.
        index_name (str): The name of the OpenSearch index.
        filters (QueryFilter | None, optional): QueryFilter to apply. Defaults to None.
        exclude_fields (list[str] | None, optional): Fields to exclude from source. Defaults to None.

    Returns:
        AsyncSearch: Configured AsyncSearch object.
    """
def apply_filter_query_to_search(search: AsyncSearch, main_query: Query, filters: QueryFilter | None = None) -> AsyncSearch:
    """Apply filter query to a search with a main query.

    Args:
        search (AsyncSearch): OpenSearch search object.
        main_query (Query): The main query to apply.
        filters (QueryFilter | None, optional): Query filters to apply. Defaults to None.

    Returns:
        AsyncSearch: Search object with applied queries.
    """
async def safe_execute(search: AsyncSearch, logger: logging.Logger | None = None) -> Any | None:
    """Execute an OpenSearch DSL search with unified error handling.

    Args:
        search (AsyncSearch): OpenSearch DSL AsyncSearch object.
        logger (logging.Logger | None, optional): Logger instance for error messages. Defaults to None.

    Returns:
        Response | None: The OpenSearch response on success, otherwise None.
    """
