from _typeshed import Incomplete
from elasticsearch import AsyncElasticsearch
from gllm_datastore.constants import DEFAULT_REQUEST_TIMEOUT as DEFAULT_REQUEST_TIMEOUT
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store._elastic_core.base import ElasticLikeCore as ElasticLikeCore
from gllm_datastore.data_store._elastic_core.client_factory import EngineType as EngineType, create_client as create_client
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.elasticsearch.fulltext import ElasticsearchFulltextCapability as ElasticsearchFulltextCapability
from gllm_datastore.data_store.elasticsearch.query_translator import ElasticsearchQueryTranslator as ElasticsearchQueryTranslator
from gllm_datastore.data_store.elasticsearch.vector import ElasticsearchVectorCapability as ElasticsearchVectorCapability
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from langchain_elasticsearch.vectorstores import AsyncRetrievalStrategy
from typing import Any

class ElasticsearchDataStore(BaseDataStore):
    '''Elasticsearch data store with multiple capability support.

    This is the explicit public API for Elasticsearch. Users know they\'re
    using Elasticsearch, not a generic "elastic-like" datastore.

    Attributes:
        engine (str): Always "elasticsearch" for explicit identification.
            This attribute ensures users know they\'re using Elasticsearch, not a generic
            "elastic-like" datastore.
        index_name (str): The name of the Elasticsearch index.
        client (AsyncElasticsearch): AsyncElasticsearch client.
    '''
    engine: str
    client: Incomplete
    index_name: Incomplete
    def __init__(self, index_name: str, client: AsyncElasticsearch | None = None, url: str | None = None, cloud_id: str | None = None, api_key: str | None = None, username: str | None = None, password: str | None = None, request_timeout: int = ...) -> None:
        '''Initialize the Elasticsearch data store.

        Args:
            index_name (str): The name of the Elasticsearch index to use for operations.
                This index name will be used for all queries and operations.
            client (AsyncElasticsearch | None, optional): Pre-configured Elasticsearch client instance.
                If provided, it will be used instead of creating a new client from url/cloud_id.
                Must be an instance of AsyncElasticsearch. Defaults to None.
            url (str | None, optional): The URL of the Elasticsearch server.
                For example, "http://localhost:9200". Either url or cloud_id must be provided
                if client is None. Defaults to None.
            cloud_id (str | None, optional): The cloud ID of the Elasticsearch cluster.
                Used for Elastic Cloud connections. Either url or cloud_id must be provided
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
            TypeError: If client is provided but is not an instance of AsyncElasticsearch.
        '''
    @property
    def supported_capabilities(self) -> list[str]:
        """Return list of currently supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.
        """
    @property
    def fulltext(self) -> ElasticsearchFulltextCapability:
        """Access fulltext capability if supported.

        This method uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the ElasticsearchFulltextCapability handler for better
        type hinting.

        Returns:
            ElasticsearchFulltextCapability: Fulltext capability handler.

        Raises:
            NotSupportedException: If fulltext capability is not supported.
        """
    @property
    def vector(self) -> ElasticsearchVectorCapability:
        """Access vector capability if supported.

        This method uses the logic of its parent class to return the vector capability handler.
        This method overrides the parent class to return the ElasticsearchVectorCapability handler for better
        type hinting.

        Returns:
            ElasticsearchVectorCapability: Vector capability handler.

        Raises:
            NotSupportedException: If vector capability is not supported.
        """
    def with_fulltext(self, index_name: str | None = None, query_field: str = 'text') -> ElasticsearchDataStore:
        '''Configure fulltext capability and return datastore instance.

        This method uses the logic of its parent class to configure the fulltext capability.
        This method overrides the parent class for better type hinting.

        Args:
            index_name (str | None, optional): The name of the Elasticsearch index to use for fulltext operations.
                If None, uses the default index_name from the datastore instance.
                Defaults to None.
            query_field (str, optional): The field name to use for text content in queries.
                This field will be used for BM25 and other text search operations.
                Defaults to "text".

        Returns:
            ElasticsearchDataStore: Self for method chaining.
        '''
    def with_vector(self, em_invoker: BaseEMInvoker, index_name: str | None = None, query_field: str = 'text', vector_query_field: str = 'vector', retrieval_strategy: AsyncRetrievalStrategy | None = None, distance_strategy: str | None = None) -> ElasticsearchDataStore:
        '''Configure vector capability and return datastore instance.

        This method uses the logic of its parent class to configure the vector capability.
        This method overrides the parent class for better type hinting.

        Args:
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            index_name (str | None, optional): The name of the Elasticsearch index. Defaults to None,
                in which case the default class attribute will be utilized.
            query_field (str, optional): The field name for text queries. Defaults to "text".
            vector_query_field (str, optional): The field name for vector queries. Defaults to "vector".
            retrieval_strategy (AsyncRetrievalStrategy | None, optional): The retrieval strategy for retrieval.
                Defaults to None, in which case DenseVectorStrategy() is used.
            distance_strategy (str | None, optional): The distance strategy for retrieval. Defaults to None.

        Returns:
            Self: Self for method chaining.
        '''
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None) -> dict[str, Any] | None:
        """Translate QueryFilter or FilterClause to Elasticsearch native filter syntax.

        This method delegates to the ElasticsearchQueryTranslator and returns the result as a dictionary.

        Args:
            query_filter (FilterClause | QueryFilter | None): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses and logical conditions,
                or None for empty filters. FilterClause objects are automatically converted to QueryFilter.

        Returns:
            dict[str, Any] | None: The translated filter as an Elasticsearch DSL dictionary.
                Returns None for empty filters or when query_filter is None.
                The dictionary format matches Elasticsearch Query DSL syntax.
        """
