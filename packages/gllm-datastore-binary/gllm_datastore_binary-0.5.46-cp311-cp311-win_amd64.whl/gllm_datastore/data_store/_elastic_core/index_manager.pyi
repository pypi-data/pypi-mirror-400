from elasticsearch import AsyncElasticsearch
from opensearchpy import AsyncOpenSearch
from typing import Any

async def create_index_if_not_exists(client: AsyncElasticsearch | AsyncOpenSearch, index_name: str, mapping: dict[str, Any] | None = None, settings: dict[str, Any] | None = None) -> None:
    """Create index if it doesn't exist (shared implementation).

    This function checks if the index exists, and if not, creates it with the provided
    mapping and settings. If the index already exists, the function returns without error.

    Args:
        client (AsyncElasticsearch | AsyncOpenSearch): The Elasticsearch or OpenSearch client.
            Used to check index existence and create the index.
        index_name (str): The name of the index to create.
            Must be a valid index name according to Elasticsearch/OpenSearch naming rules.
        mapping (dict[str, Any] | None, optional): Optional index mapping dictionary.
            Defines the schema for fields in the index. If None, no custom mapping is applied.
            Defaults to None.
        settings (dict[str, Any] | None, optional): Optional index settings dictionary.
            Defines index-level settings like number of shards, replicas, etc.
            If None, no custom settings are applied. Defaults to None.

    Raises:
        RuntimeError: If index creation fails after checking existence.
    """
async def delete_index_if_exists(client: AsyncElasticsearch | AsyncOpenSearch, index_name: str) -> None:
    """Delete index if it exists (shared implementation).

    This function checks if the index exists, and if it does, deletes it.
    If the index does not exist, the function returns without error.

    Args:
        client (AsyncElasticsearch | AsyncOpenSearch): The Elasticsearch or OpenSearch client.
            Used to check index existence and delete the index.
        index_name (str): The name of the index to delete.
            Must be a valid index name according to Elasticsearch/OpenSearch naming rules.
    """
