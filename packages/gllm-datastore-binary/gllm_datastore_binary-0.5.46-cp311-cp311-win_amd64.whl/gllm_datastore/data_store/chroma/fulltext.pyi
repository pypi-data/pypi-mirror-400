from _typeshed import Incomplete
from chromadb import ClientAPI
from gllm_core.schema import Chunk
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS, METADATA_KEYS as METADATA_KEYS
from gllm_datastore.core.filters import FilterClause as FilterClause, QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.chroma._chroma_import import safe_import_chromadb as safe_import_chromadb
from gllm_datastore.data_store.chroma.query import ChromaCollectionKeys as ChromaCollectionKeys, DEFAULT_NUM_CANDIDATES as DEFAULT_NUM_CANDIDATES, build_chroma_delete_kwargs as build_chroma_delete_kwargs, build_chroma_get_kwargs as build_chroma_get_kwargs, sanitize_metadata as sanitize_metadata
from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator as ChromaQueryTranslator
from typing import Any

chromadb: Incomplete

class ChromaFulltextCapability:
    """ChromaDB implementation of FulltextCapability protocol.

    This class provides document CRUD operations and text search using ChromaDB.

    Attributes:
        collection_name (str): The name of the ChromaDB collection.
        client (ClientAPI): ChromaDB client instance.
        collection: ChromaDB collection instance.
        num_candidates (int): Maximum number of candidates to consider during search.
    """
    collection_name: Incomplete
    client: Incomplete
    collection: Incomplete
    num_candidates: Incomplete
    def __init__(self, collection_name: str, client: ClientAPI, num_candidates: int = ...) -> None:
        """Initialize the ChromaDB fulltext capability.

        Args:
            collection_name (str): The name of the ChromaDB collection.
            client (ClientAPI): ChromaDB client instance.
            num_candidates (int, optional): Maximum number of candidates to consider during search.
                Defaults to DEFAULT_NUM_CANDIDATES.
        """
    def get_size(self) -> int:
        """Returns the total number of documents in the collection.

        Returns:
            int: The total number of documents.
        """
    async def create(self, data: Chunk | list[Chunk], **kwargs: Any) -> None:
        """Create new records in the datastore.

        Args:
            data (Chunk | list[Chunk]): Data to create (single item or collection).
            **kwargs: Backend-specific parameters.

        Raises:
            ValueError: If data structure is invalid.
        """
    async def retrieve(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs: Any) -> list[Chunk]:
        '''Read records from the datastore with optional filtering.

        Usage Example:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Direct FilterClause usage
            results = await fulltext_capability.retrieve(filters=F.eq("metadata.category", "tech"))

            # Multiple filters
            results = await fulltext_capability.retrieve(
                filters=F.and_(F.eq("metadata.category", "tech"), F.eq("metadata.status", "active"))
            )
            ```

        Args:
            filters (FilterClause | QueryFilter | None, optional): Query filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options (sorting, pagination, etc.).
                Defaults to None.
            **kwargs: Backend-specific parameters.

        Returns:
            list[Chunk]: Query results.

        Raises:
            NotImplementedError: If unsupported operators are used for id or content filters.
        '''
    async def retrieve_fuzzy(self, query: str, max_distance: int = 2, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None, **kwargs: Any) -> list[Chunk]:
        """Find records that fuzzy match the query within distance threshold.

        Args:
            query (str): Text to fuzzy match against.
            max_distance (int): Maximum edit distance for matches. Defaults to 2.
            filters (FilterClause | QueryFilter | None, optional): Optional metadata filters to apply.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.
            options (QueryOptions | None, optional): Query options (sorting, limit, etc.). Defaults to None.
            **kwargs: Backend-specific parameters.

        Returns:
            list[Chunk]: Matched chunks ordered by distance (ascending) or by options.order_by if specified.
        """
    async def update(self, update_values: dict[str, Any], filters: FilterClause | QueryFilter | None = None) -> None:
        '''Update existing records in the datastore.

        Examples:
            Update the content and metadata of the chunk with the id "unique_id" to "updated_content"
            and "published" respectively.
            ```python
            from gllm_datastore.core.filters import filter as F

            await fulltext_capability.update(
                update_values={"content": "updated_content", "metadata": {"status": "published"}},
                filters=F.eq("id", "unique_id"),
            )
            ```

        Args:
            update_values (dict[str, Any]): Values to update. Supports "content" for updating document content
                and "metadata" for updating metadata. Other keys are treated as direct metadata updates.
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to update.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None.

        Note:
            ChromaDB doesn\'t support direct update operations. This method will
            retrieve matching records, update them, and re-add them to the collection.
        '''
    async def delete(self, filters: FilterClause | QueryFilter | None = None, options: QueryOptions | None = None) -> None:
        """Delete records from the datastore.

        Args:
            filters (FilterClause | QueryFilter | None, optional): Filters to select records to delete.
                FilterClause objects are automatically converted to QueryFilter internally.
                Defaults to None, in which case no operation is performed (no-op).
            options (QueryOptions | None, optional): Query options for sorting and limiting deletions. Defaults to None.
        """
    async def clear(self) -> None:
        """Clear all records from the datastore."""
