from _typeshed import Incomplete
from elasticsearch import AsyncElasticsearch
from opensearchpy import AsyncOpenSearch

class ElasticLikeCore:
    """Shared core implementation for Elasticsearch-like datastores.

    This class contains the common logic shared between Elasticsearch and OpenSearch.
    Product-specific datastores delegate to this core and override methods where needed.

    Attributes:
        index_name (str): The name of the index used for all operations.
        client (AsyncElasticsearch | AsyncOpenSearch): The Elasticsearch or OpenSearch client.
            Used for all index and document operations.
        _logger (Logger): Logger instance for this core. Used for logging operations and errors.
    """
    index_name: Incomplete
    client: Incomplete
    def __init__(self, index_name: str, client: AsyncElasticsearch | AsyncOpenSearch) -> None:
        """Initialize the shared core.

        Args:
            index_name (str): The name of the index to use for operations.
                This index name will be used for all queries and operations.
            client (AsyncElasticsearch | AsyncOpenSearch): The Elasticsearch or OpenSearch client.
                Must be a properly configured async client instance.
        """
    async def check_index_exists(self) -> bool:
        """Check if index exists.

        Returns:
            bool: True if the index exists, False otherwise.
        """
    async def get_index_count(self) -> int:
        """Get document count for the index.

        Returns:
            int: The total number of documents in the index.
        """
