from abc import ABC, abstractmethod
from typing import Any

class BaseGraphRAGDataStore(ABC):
    """Abstract base class for graph RAG data stores in the retrieval system.

    This class defines the interface for all graph-based Retrieval-Augmented
    Generation (RAG) implementations. It provides methods for querying the graph with
    natural language and managing document-related data.
    """
    @abstractmethod
    async def query(self, query: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Query the graph RAG data store.

        Args:
            query (str): The query to be executed.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            list[dict[str, Any]]: The result of the query as a list of dictionaries.
        """
    @abstractmethod
    async def delete_by_document_id(self, document_id: str, **kwargs: Any) -> None:
        """Delete nodes and edges by document ID.

        Args:
            document_id (str): The document ID.
            **kwargs (Any): Additional keyword arguments.
        """
