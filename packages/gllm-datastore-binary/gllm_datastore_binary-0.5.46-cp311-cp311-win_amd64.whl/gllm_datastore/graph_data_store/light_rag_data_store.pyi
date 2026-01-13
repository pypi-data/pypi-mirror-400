from _typeshed import Incomplete
from gllm_core.schema import Chunk as Chunk
from gllm_datastore.graph_data_store.graph_rag_data_store import BaseGraphRAGDataStore as BaseGraphRAGDataStore
from gllm_datastore.graph_data_store.utils.constants import LightRAGConstants as LightRAGConstants, LightRAGKeys as LightRAGKeys
from gllm_datastore.graph_data_store.utils.light_rag_em_invoker_adapter import LightRAGEMInvokerAdapter as LightRAGEMInvokerAdapter
from lightrag import LightRAG
from typing import Any

class BaseLightRAGDataStore(BaseGraphRAGDataStore):
    """LightRAG data store base class.

    This class provides an abstract base class for the BaseGraphRAGDataStore interface
    using LightRAG as the underlying technology. It handles indexing files
    into a graph database, creating relationships between files and chunks,
    and provides methods for deleting files and chunks from the graph.

    Please use LightRAGPostgresDataStore or other concrete implementations instead.

    To implement a concrete data store, inherit from this class and implement the
    abstract methods.

    Attributes:
        instance (LightRAG): The LightRAG instance to use.
        is_initialized (bool): Whether the data store is initialized.
    """
    instance: Incomplete
    is_initialized: bool
    def __init__(self, instance: LightRAG) -> None:
        """Initialize the LightRAG data store.

        This is an abstract base class and cannot be instantiated directly.
        Use LightRAGPostgresDataStore or other concrete implementations instead.

        Args:
            instance (LightRAG): The LightRAG instance to use for indexing.

        Raises:
            TypeError: If attempting to instantiate BaseLightRAGDataStore directly.
        """
    async def ensure_initialized(self) -> None:
        """Ensure that the LightRAG data store is initialized.

        This asynchronous method ensures that the LightRAG data store is initialized.
        If the data store is not initialized, it will initialize it.
        """
    async def map_file_id_to_chunk_ids_using_graph(self, file_id: str, chunk_ids: list[str]) -> None:
        """Create file and chunk nodes in the graph and establish relationships.

        This asynchronous method creates a file node and multiple chunk nodes
        in the graph database, then establishes relationships between the file
        and its chunks. The relationships are necessary for retaining the relationships
        between the file and its chunks when deleting the file.

        Args:
            file_id (str): The ID of the file to create in the graph.
            chunk_ids (list[str]): List of chunk IDs that belong to the file.
        """
    async def insert(self, chunks: list[Chunk]) -> None:
        """Insert a chunk into the LightRAG data store.

        This asynchronous method inserts a chunk into the LightRAG data store.
        If the data store is not initialized, it will initialize it.

        Args:
            chunks (list[Chunk]): The chunks to insert.
        """
    async def query(self, query: str, **kwargs: Any) -> Any:
        """Query the LightRAG data store.

        Args:
            query (str): The query to be executed.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Any: The result of the query.
        """
    async def delete(self, chunk_id: str) -> None:
        """Delete a chunk from the LightRAG data store.

        Args:
            chunk_id (str): The ID of the chunk to delete.
        """
    async def delete_by_document_id(self, document_id: str, **kwargs: Any) -> None:
        """Delete a document/file and all its associated chunks from the LightRAG data store.

        This asynchronous method retrieves all chunks associated with a document/file,
        deletes each chunk from both the LightRAG system and the graph database,
        and finally deletes the document/file node itself.

        Args:
            document_id (str): The ID of the document to delete.
            **kwargs (Any): Additional keyword arguments.
        """
