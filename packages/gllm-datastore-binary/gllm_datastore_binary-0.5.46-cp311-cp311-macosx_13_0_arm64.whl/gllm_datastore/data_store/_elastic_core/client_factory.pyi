from elasticsearch import AsyncElasticsearch
from enum import StrEnum
from gllm_datastore.constants import DEFAULT_REQUEST_TIMEOUT as DEFAULT_REQUEST_TIMEOUT
from opensearchpy import AsyncOpenSearch

ElasticLikeClient = AsyncElasticsearch | AsyncOpenSearch

class EngineType(StrEnum):
    """Engine type for Elasticsearch-like clients."""
    ELASTICSEARCH: str
    OPENSEARCH: str

def create_client(engine: EngineType, client: ElasticLikeClient | None = None, url: str | None = None, cloud_id: str | None = None, api_key: str | None = None, username: str | None = None, password: str | None = None, request_timeout: int = ...) -> ElasticLikeClient:
    '''Create Elasticsearch or OpenSearch client (internal use only).

    This function is used internally by ElasticsearchDataStore and OpenSearchDataStore.
    It is not part of the public API.

    Args:
        engine: Engine type ("elasticsearch" or "opensearch").
            Determines which client library to use for connection.
        client: Pre-configured client instance.
            If provided, will be validated and returned as-is without creating a new client.
            Must match the engine type (AsyncElasticsearch for "elasticsearch",
            AsyncOpenSearch for "opensearch"). Defaults to None.
        url (str | None, optional): The URL of the Elasticsearch or OpenSearch server.
            For example, "http://localhost:9200". Defaults to None.
            Either url or cloud_id must be provided if client is None.
        cloud_id (str | None, optional): The cloud ID of the Elasticsearch cluster.
            Used for Elastic Cloud connections. Defaults to None.
            Either url or cloud_id must be provided if client is None.
            NOTE: Not supported for OpenSearch engine. Will raise ValueError if provided with engine="opensearch".
        api_key (str | None, optional): The API key for authentication.
            If provided, will be used for authentication. Mutually exclusive with username/password.
            Defaults to None.
            NOTE: Not supported for OpenSearch engine. Will raise ValueError if provided with engine="opensearch".
            For OpenSearch, use username/password with http_auth instead.
        username (str | None, optional): The username for basic authentication.
            Must be provided together with password. Mutually exclusive with api_key.
            Defaults to None.
        password (str | None, optional): The password for basic authentication.
            Must be provided together with username. Mutually exclusive with api_key.
            Defaults to None.
        request_timeout (int, optional): The request timeout in seconds.
            Defaults to DEFAULT_REQUEST_TIMEOUT.

    Returns:
        The configured client instance.
            Returns AsyncElasticsearch if engine is "elasticsearch",
            AsyncOpenSearch if engine is "opensearch".

    Raises:
        ValueError: If neither url nor cloud_id is provided when client is None.
            If cloud_id is provided for OpenSearch engine (not supported).
            If api_key is provided for OpenSearch engine (not supported).
        TypeError: If client is provided but has wrong type for the specified engine.
    '''
