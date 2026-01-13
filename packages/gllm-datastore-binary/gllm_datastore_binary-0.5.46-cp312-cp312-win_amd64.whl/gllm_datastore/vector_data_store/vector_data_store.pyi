from abc import ABC, abstractmethod
from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import DEFAULT_TOP_K as DEFAULT_TOP_K
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from langchain_core.embeddings import Embeddings
from typing import Any

class BaseVectorDataStore(ABC):
    """Abstract base class for vector data stores in the retrieval system.

    This class defines the interface for all vector data store implementations.
    Subclasses must implement the `query` and `query_by_id` methods.
    """
    @property
    def embedding(self) -> BaseEMInvoker | Embeddings | None:
        """Returns the embedding model associated with this data store.

        Returns:
            BaseEMInvoker | Embeddings | None: The embedding model.
        """
    async def get_size(self) -> int:
        """Returns the total number of vectors in the index.

        If the index is not initialized returns 0.

        Returns:
            int: The total number of vectors.
        """
    @abstractmethod
    async def query(self, query: str, top_k: int = ..., retrieval_params: dict[str, Any] | None = None) -> list[Chunk]:
        """Executes a query on the data store.

        This method must be implemented by subclasses.

        Args:
            query (str): The query string to execute.
            top_k (int, optional): The maximum number of results to return. Defaults to DEFAULT_TOP_K.
            retrieval_params (dict[str, Any] | None, optional): Additional parameters for the query.
                Defaults to None.

        Returns:
            list[Chunk]: A list of query results.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def query_by_id(self, id_: str | list[str]) -> list[Chunk]:
        """Retrieves chunks by their IDs.

        This method must be implemented by subclasses.

        Args:
            id_ (str | list[str]): A single ID or a list of IDs to retrieve.

        Returns:
            list[Chunk]: A list of retrieved chunks.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def add_chunks(self, chunk: Chunk | list[Chunk], **kwargs) -> list[str]:
        """Adds a chunk or a list of chunks in the data store.

        This method must be implemented by subclasses.

        Args:
            chunk (Chunk | list[Chunk]): A single chunk or a list of chunks to index.
            **kwargs: Additional keyword arguments to pass to the method.

        Returns:
            list[str]: A list of unique identifiers (IDs) assigned to the added chunks.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete_chunks(self, **kwargs: Any) -> None:
        """Deletes chunks from the data store by filter or query.

        This method must be implemented by subclasses.

        Args:
            **kwargs: Additional keyword arguments specifying the filter or query for deletion.
                The exact parameters depend on the backend implementation.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete_chunks_by_ids(self, ids: str | list[str], **kwargs: Any) -> None:
        """Deletes a chunk or a list of chunks from the data store by their IDs.

        This method must be implemented by subclasses.

        Args:
            ids (str | list[str]): A single ID or a list of IDs to delete.
            **kwargs: Additional keyword arguments.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    async def clear(self) -> None:
        """Clear all entries in the storage.

        This method should be implemented by subclasses.
        """
    async def query_by_field(self, retrieval_params: dict[str, Any], limit: int | None = None, **kwargs) -> list[Chunk]:
        """Retrieve documents that match specific metadata constraints.

        This method filters and returns stored chunks based on metadata values
        rather than vector similarity. It is particularly useful for structured lookups,
        such as retrieving all chunks from a certain source, tagged with a specific label,
        or authored by a particular user.

        Unlike semantic search methods, `query_by_field` operates purely on metadata fields
        associated with each document, allowing precise filtering based on key-value pairs.

        Args:
            retrieval_params (dict[str, Any]): A dictionary defining filter criteria.
            limit (int | None, optional): The maximum number of results to return. If None, all matching
                documents will be returned.
            **kwargs: Additional arguments to support datastore-specific behavior or filtering logic.

        Returns:
            list[Chunk]: A list of `Chunk` objects that satisfy the metadata criteria.

        Raises:
            NotImplementedError: If not implemented in the subclass.
        """
    async def query_by_vector(self, vector: list[float], top_k: int = ..., min_similarity: float = 0.8, retrieval_params: dict | None = None) -> list[Chunk]:
        """Search for documents that are similar to a given vector.

        Args:
            vector (list[float]): The query embedding vector to compare against stored vectors.
            top_k (int, optional): The number of top results to return. Defaults to DEFAULT_TOP_K.
            min_similarity (float): Minimum similarity score for vector similarity.
            retrieval_params (dict | None, optional): Filter parameters to narrow the search:
                - filter (Where): Metadata-based filter.
                - where_document (WhereDocument): Content-based filter.
                Defaults to None.

        Returns:
            list[Chunk]: A list of Chunk objects with similarity scores based on the input vector.
        """
