from _typeshed import Incomplete
from gllm_datastore.constants import DEFAULT_REQUEST_TIMEOUT as DEFAULT_REQUEST_TIMEOUT
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store._elastic_core.base import ElasticLikeCore as ElasticLikeCore
from gllm_datastore.data_store._elastic_core.client_factory import EngineType as EngineType, create_client as create_client
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.opensearch.fulltext import OpenSearchFulltextCapability as OpenSearchFulltextCapability
from gllm_datastore.data_store.opensearch.query_translator import OpenSearchQueryTranslator as OpenSearchQueryTranslator
from opensearchpy import AsyncOpenSearch
from typing import Any

class OpenSearchDataStore(BaseDataStore):
    '''OpenSearch data store with multiple capability support.

    This is the explicit public API for OpenSearch. Users know they\'re
    using OpenSearch, not a generic "elastic-like" datastore.

    Attributes:
        engine (str): Always "opensearch" for explicit identification.
            This attribute ensures users know they\'re using OpenSearch, not a generic
            "elastic-like" datastore.
        index_name (str): The name of the OpenSearch index.
        client (AsyncOpenSearch): AsyncOpenSearch client.
    '''
    engine: str
    client: Incomplete
    index_name: Incomplete
    def __init__(self, index_name: str, client: AsyncOpenSearch | None = None, url: str | None = None, cloud_id: str | None = None, api_key: str | None = None, username: str | None = None, password: str | None = None, request_timeout: int = ...) -> None:
        '''Initialize the OpenSearch data store.

        Args:
            index_name (str): The name of the OpenSearch index to use for operations.
                This index name will be used for all queries and operations.
            client (AsyncOpenSearch | None, optional): Pre-configured OpenSearch client instance.
                If provided, it will be used instead of creating a new client from url/cloud_id.
                Must be an instance of AsyncOpenSearch. Defaults to None.
            url (str | None, optional): The URL of the OpenSearch server.
                For example, "http://localhost:9200". Either url or cloud_id must be provided
                if client is None. Defaults to None.
            cloud_id (str | None, optional): The cloud ID of the OpenSearch cluster.
                Used for OpenSearch Service connections. Either url or cloud_id must be provided
                if client is None. Defaults to None.
            api_key (str | None, optional): The API key for authentication.
                If provided, will be used for authentication. Mutually exclusive with username/password.
                Defaults to None.
            username (str | None, optional): The username for basic authentication.
                Must be provided together with password. Mutually exclusive with api_key.
                Defaults to None.
            password (str | None, optional): The password for basic authentication.
                Must be provided together with username. Mutually exclusive with api_key.
                Defaults to None.
            request_timeout (int, optional): The request timeout in seconds.
                Defaults to DEFAULT_REQUEST_TIMEOUT.

        Raises:
            ValueError: If neither url nor cloud_id is provided when client is None.
            TypeError: If client is provided but is not an instance of AsyncOpenSearch.
        '''
    @property
    def supported_capabilities(self) -> list[str]:
        """Return list of currently supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.
                Currently returns [CapabilityType.FULLTEXT, CapabilityType.VECTOR].
                Note: Vector capability is not yet implemented.
        """
    @property
    def fulltext(self) -> OpenSearchFulltextCapability:
        """Access fulltext capability if supported.

        This method uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the OpenSearchFulltextCapability handler for better
        type hinting.

        Returns:
            OpenSearchFulltextCapability: Fulltext capability handler.

        Raises:
            NotSupportedException: If fulltext capability is not supported.
        """
    @property
    def vector(self) -> None:
        """Access vector capability if supported.

        Raises:
            NotImplementedError: Vector capability not yet implemented.
        """
    def with_fulltext(self, index_name: str | None = None, query_field: str = 'text') -> OpenSearchDataStore:
        '''Configure fulltext capability and return datastore instance.

        This method uses the logic of its parent class to configure the fulltext capability.
        This method overrides the parent class for better type hinting.

        Args:
            index_name (str | None, optional): The name of the OpenSearch index to use for fulltext operations.
                If None, uses the default index_name from the datastore instance.
                Defaults to None.
            query_field (str, optional): The field name to use for text content in queries.
                This field will be used for BM25 and other text search operations.
                Defaults to "text".

        Returns:
            OpenSearchDataStore: Self for method chaining.
        '''
    def with_vector(self, *args: Any, **kwargs: Any) -> OpenSearchDataStore:
        """Configure vector capability and return datastore instance.

        Args:
            *args: Placeholder arguments.
            **kwargs: Placeholder keyword arguments.

        Returns:
            Self: Self for method chaining.

        Raises:
            NotImplementedError: Vector capability not yet implemented.
        """
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None) -> dict[str, Any] | None:
        """Translate QueryFilter or FilterClause to OpenSearch native filter syntax.

        This method delegates to the OpenSearchQueryTranslator and returns the result as a dictionary.

        Args:
            query_filter (FilterClause | QueryFilter | None): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses and logical conditions,
                or None for empty filters. FilterClause objects are automatically converted to QueryFilter.

        Returns:
            dict[str, Any] | None: The translated filter as an OpenSearch DSL dictionary.
                Returns None for empty filters or when query_filter is None.
                The dictionary format matches OpenSearch Query DSL syntax.
        """
