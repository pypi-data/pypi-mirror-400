from _typeshed import Incomplete
from enum import StrEnum
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.chroma._chroma_import import safe_import_chromadb as safe_import_chromadb
from gllm_datastore.data_store.chroma.fulltext import ChromaFulltextCapability as ChromaFulltextCapability
from gllm_datastore.data_store.chroma.query import DEFAULT_NUM_CANDIDATES as DEFAULT_NUM_CANDIDATES
from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator as ChromaQueryTranslator
from gllm_datastore.data_store.chroma.vector import ChromaVectorCapability as ChromaVectorCapability
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from typing import Any

chromadb: Incomplete

class ChromaClientType(StrEnum):
    """Enum for different types of ChromaDB clients."""
    MEMORY: str
    PERSISTENT: str
    HTTP: str

class ChromaDataStore(BaseDataStore):
    """ChromaDB data store with multiple capability support.

    Attributes:
        collection_name (str): The name of the ChromaDB collection.
        client (chromadb.ClientAPI): The ChromaDB client instance.
    """
    collection_name: Incomplete
    client: Incomplete
    def __init__(self, collection_name: str, client_type: ChromaClientType = ..., persist_directory: str | None = None, host: str | None = None, port: int | None = None, headers: dict | None = None, client_settings: dict | None = None) -> None:
        """Initialize the ChromaDB data store.

        Args:
            collection_name (str): The name of the ChromaDB collection.
            client_type (ChromaClientType, optional): Type of ChromaDB client to use.
                Defaults to ChromaClientType.MEMORY.
            persist_directory (str | None, optional): Directory to persist vector store data.
                Required for PERSISTENT client type. Defaults to None.
            host (str | None, optional): Host address for ChromaDB server.
                Required for HTTP client type. Defaults to None.
            port (int | None, optional): Port for ChromaDB server.
                Required for HTTP client type. Defaults to None.
            headers (dict | None, optional): A dictionary of headers to send to the Chroma server.
                Used for authentication with the Chroma server for HTTP client type. Defaults to None.
            client_settings (dict | None, optional): A dictionary of additional settings for the Chroma client.
                Defaults to None.
        """
    @property
    def supported_capabilities(self) -> list[str]:
        """Return list of currently supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.
        """
    @property
    def fulltext(self) -> ChromaFulltextCapability:
        """Access fulltext capability if supported.

        This method uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the ChromaFulltextCapability handler for better
        type hinting.

        Returns:
            ChromaFulltextCapability: Fulltext capability handler.

        Raises:
            NotSupportedException: If fulltext capability is not supported.
        """
    @property
    def vector(self) -> ChromaVectorCapability:
        """Access vector capability if supported.

        This method uses the logic of its parent class to return the vector capability handler.
        This method overrides the parent class to return the ChromaVectorCapability handler for better
        type hinting.

        Returns:
            ChromaVectorCapability: Vector capability handler.

        Raises:
            NotSupportedException: If vector capability is not supported.
        """
    def with_fulltext(self, collection_name: str | None = None, num_candidates: int = ...) -> ChromaDataStore:
        """Configure fulltext capability and return datastore instance.

        This method uses the logic of its parent class to configure the fulltext capability.
        This method overrides the parent class for better type hinting.

        Args:
            collection_name (str | None, optional): Name of the collection to use in ChromaDB. Defaults to None,
                in which case the default class attribute will be utilized.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to DEFAULT_NUM_CANDIDATES.

        Returns:
            Self: Self for method chaining.
        """
    def with_vector(self, em_invoker: BaseEMInvoker, collection_name: str | None = None, num_candidates: int = ...) -> ChromaDataStore:
        """Configure vector capability and return datastore instance.

        This method uses the logic of its parent class to configure the vector capability.
        This method overrides the parent class for better type hinting.

        Args:
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            collection_name (str | None, optional): Name of the collection to use in ChromaDB. Defaults to None,
                in which case the default class attribute will be utilized.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to DEFAULT_NUM_CANDIDATES.

        Returns:
            Self: Self for method chaining.
        """
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None = None) -> dict[str, Any] | None:
        '''Translate QueryFilter or FilterClause to ChromaDB native filter syntax.

        This method uses ChromaQueryTranslator to translate filters and returns
        the result as a dictionary.

        Examples:
            1. Translate a simple FilterClause:
                ```python
                from gllm_datastore.core.filters import filter as F

                filter_clause = F.eq("metadata.status", "active")
                result = ChromaDataStore.translate_query_filter(filter_clause)
                # result -> {"where": {"status": "active"}}
                ```

            2. Translate QueryFilter with metadata filters:
                ```python
                from gllm_datastore.core.filters import filter as F

                filters = F.and_(
                    F.eq("metadata.category", "tech"),
                    F.gte("metadata.price", 10),
                )
                result = ChromaDataStore.translate_query_filter(filters)
                # result ->
                # {
                #   "where": {
                #     "$and": [
                #       {"category": "tech"},
                #       {"price": {"$gte": 10}}
                #     ]
                #   }
                # }
                ```

            3. Translate QueryFilter with content filters:
                ```python
                from gllm_datastore.core.filters import filter as F

                filters = F.text_contains("content", "python")
                result = ChromaDataStore.translate_query_filter(filters)
                # result -> {"where_document": {"$contains": "python"}}
                ```

            4. Translate QueryFilter with id filters:
                ```python
                from gllm_datastore.core.filters import filter as F

                filters = F.in_("id", ["chunk_1", "chunk_2"])
                result = ChromaDataStore.translate_query_filter(filters)
                # result -> {"ids": ["chunk_1", "chunk_2"]}
                ```

            5. Translate complex nested QueryFilter:
                ```python
                from gllm_datastore.core.filters import filter as F

                filters = F.and_(
                    F.or_(
                        F.eq("metadata.status", "active"),
                        F.eq("metadata.status", "pending"),
                    ),
                    F.text_contains("content", "machine learning"),
                    F.in_("id", ["chunk_1", "chunk_2"]),
                )
                result = ChromaDataStore.translate_query_filter(filters)
                # result ->
                # {
                #   "where": {
                #     "$or": [
                #       {"status": "active"},
                #       {"status": "pending"}
                #     ]
                #   },
                #   "where_document": {"$contains": "machine learning"},
                #   "ids": ["chunk_1", "chunk_2"]
                # }
                ```

        Args:
            query_filter (FilterClause | QueryFilter | None, optional): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses. Defaults to None.

        Returns:
            dict[str, Any] | None: The translated filter as a ChromaDB query dict.
                Returns None for empty filters.
        '''
