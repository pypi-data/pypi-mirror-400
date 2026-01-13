from _typeshed import Incomplete
from gllm_core.schema.chunk import Chunk
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS, DEFAULT_TOP_K as DEFAULT_TOP_K
from gllm_datastore.core.filters import QueryFilter as QueryFilter, QueryOptions as QueryOptions
from gllm_datastore.data_store.in_memory.data_store import InMemoryDataStore as InMemoryDataStore
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.schema import Vector
from typing import Any

class InMemoryVectorDataStore(BaseVectorDataStore):
    """In-memory vector data store implementation.

    This class provides a simple in-memory implementation of the BaseVectorDataStore
    that stores vectors and metadata in memory. It's primarily intended for testing
    purposes and does not require any external services.

    Attributes:
        store (dict[str, dict[str, Any]]): Dictionary storing documents with their vectors and metadata.
            Each entry has keys: 'id', 'vector', 'text', 'metadata'.
        embedding (BaseEMInvoker | None): Optional embedding model for vectorization.
    """
    store: Incomplete
    def __init__(self, embedding: BaseEMInvoker | None = None) -> None:
        """Initialize the in-memory vector data store.

        Args:
            embedding (BaseEMInvoker | None, optional): The embedding model to perform vectorization.
                Defaults to None, in which case vectors must be provided manually when adding chunks.
        """
    async def get_size(self) -> int:
        """Return the number of items in the data store.

        Returns:
            int: The number of items in the data store.
        """
    async def add_chunks(self, chunk: Chunk | list[Chunk], vector: Vector | list[Vector] | None = None) -> list[str]:
        '''Adds a chunk or a list of chunks in the data store.

        Example:
            ```python
            await store.add_chunks(
                [Chunk(id="1", content="AI contains machine learning", metadata={"topic": "AI"}),
                Chunk(id="2", content="AI in 2025", metadata={"topic": "AI"}),
            ])
            ```
        Args:
            chunk (Chunk | list[Chunk]): A single chunk or a list of chunks to index.
            vector (Vector | list[Vector] | None, optional): A manual vector specification.
                Defaults to None, in which case the embedding model will be used.
                The vector length must match the embedding size used by the store.
            **kwargs: Additional keyword arguments.

        Returns:
            list[str]: A list of unique identifiers (IDs) assigned to the added chunks.

        Raises:
            ValueError: If the number of chunks and vectors are not the same.
            ValueError: If no embedding model is provided and no vector is specified.
        '''
    async def query(self, query: str, top_k: int = ..., retrieval_params: dict[str, Any] | None = None) -> list[Chunk]:
        '''Executes a query on the data store using semantic similarity.

        Example:
            ```python
            chunks = await store.add_chunks(
                [
                    Chunk(id="1", content="AI contains machine learning", metadata={"topic": "AI"}),
                    Chunk(id="2", content="AI in 2025", metadata={"topic": "AI"}),
                ]
            )
            await store.query(query="AI and machine learning", retrieval_params={"topic": "AI"})
            ```

        Args:
            query (str): The query string to execute.
            top_k (int, optional): The maximum number of results to return. Defaults to DEFAULT_TOP_K.
            retrieval_params (dict[str, Any] | None, optional): Additional parameters for the query.

        Returns:
            list[Chunk]: A list of query results with similarity scores.

        Raises:
            ValueError: If no embedding model is provided.
        '''
    async def query_by_vector(self, vector: Vector, top_k: int = ..., min_similarity: float = 0.8, retrieval_params: dict[str, Any] | None = None) -> list[Chunk]:
        '''Search for documents that are similar to a given vector.

        Example:
            ```python
            chunks = await store.add_chunks(
                [
                    Chunk(id="1", content="AI contains machine learning", metadata={"topic": "AI"}),
                    Chunk(id="2", content="AI in 2025", metadata={"topic": "AI"}),
                ]
            )
            query_vector = await embedding.invoke("AI and machine learning")
            await store.query_by_vector(query_vector, retrieval_params={"topic": "AI"})
            ```
        Args:
            vector (Vector): The query embedding vector to compare against stored vectors.
            top_k (int, optional): The number of top results to return. Defaults to DEFAULT_TOP_K.
            min_similarity (float, optional): Minimum similarity score for vector similarity. Defaults to 0.8.
            retrieval_params (dict[str, Any] | None, optional): Filter parameters to narrow the search.

        Returns:
            list[Chunk]: A list of Chunk objects with similarity scores based on the input vector.
        '''
    async def query_by_field(self, retrieval_params: dict[str, Any], limit: int | None = None, **kwargs) -> list[Chunk]:
        '''Retrieve documents that match specific metadata constraints.

        Example:
            ```python
            sample_chunks = [
                Chunk(id="1", content="AI is a topic", metadata={"topic": "AI"}),
                Chunk(id="2", content="Deep learning is a topic", metadata={"topic": "Deep Learning"}),
            ]
            await store.add_chunks(sample_chunks)
            await store.query_by_field({"topic": "AI"})
            ```

        Args:
            retrieval_params (dict[str, Any]): A dictionary with metadata field names as keys and their expected values.
            limit (int | None, optional): The maximum number of results to return. Defaults to None, in which
                case all matching documents will be returned.
            **kwargs: Additional arguments (currently unused).

        Returns:
            list[Chunk]: A list of Chunk objects that satisfy the metadata criteria.
        '''
    async def query_by_id(self, id_: str | list[str]) -> list[Chunk]:
        '''Retrieves chunks by their IDs.

        Example:
            ```python
            chunks = await store.add_chunks(
                [Chunk(id="1", content="AI contains machine learning", metadata={"topic": "AI"}),
                Chunk(id="2", content="AI in 2025", metadata={"topic": "AI"}),
            ])
            await store.query_by_id(["1", "2"])
            ```

        Args:
            id_ (str | list[str]): A single ID or a list of IDs to retrieve.

        Returns:
            list[Chunk]: A list of retrieved chunks.
        '''
    async def delete_chunks(self, retrieval_params: dict[str, Any] | None = None) -> None:
        '''Deletes chunks from the data store by filter criteria.

        Example:
            ```python
            sample_chunks = [
                Chunk(id="1", content="AI is a topic", metadata={"topic": "AI"}),
                Chunk(id="2", content="Deep learning is a topic", metadata={"topic": "Deep Learning"}),
            ]
            await store.add_chunks(sample_chunks)
            await store.delete_chunks(retrieval_params={"topic": "AI"})
            ```

        Args:
            retrieval_params (dict[str, Any] | None, optional): A dictionary with metadata field names as keys
                and their expected values. Defaults to None, in which case no operation is performed (no-op).
        '''
    async def delete_chunks_by_ids(self, ids: str | list[str], **kwargs: Any) -> None:
        '''Deletes a chunk or a list of chunks from the data store by their IDs.

        Example:
            ```python
            await store.delete_chunks_by_ids(["1", "2"])
            ```

        Args:
            ids (str | list[str]): A single ID or a list of IDs to delete.
            **kwargs: Additional keyword arguments (currently unused).
        '''
    async def clear(self) -> None:
        """Clear all entries in the storage."""
