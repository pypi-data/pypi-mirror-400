from abc import ABC, abstractmethod
from typing import Any

class BaseGraphDataStore(ABC):
    """Abstract base class for an async graph data store interface.

    This class defines the asynchronous interface for all graph data store implementations.
    It provides methods for creating, updating, and querying graph data.
    """
    @abstractmethod
    async def upsert_node(self, label: str, identifier_key: str, identifier_value: str, properties: dict[str, Any] | None) -> Any:
        """Upsert a node in the graph.

        Args:
            label (str): The label of the node.
            identifier_key (str): The key of the identifier.
            identifier_value (str): The value of the identifier.
            properties (dict[str, Any] | None, optional): The properties of the node. Defaults to None.

        Returns:
            Any: The result of the operation.
        """
    @abstractmethod
    async def upsert_relationship(self, node_source_key: str, node_source_value: str, relation: str, node_target_key: str, node_target_value: str, properties: dict[str, Any] | None) -> Any:
        """Upsert a relationship between two nodes in the graph.

        Args:
            node_source_key (str): The key of the source node.
            node_source_value (str): The value of the source node.
            relation (str): The type of the relationship.
            node_target_key (str): The key of the target node.
            node_target_value (str): The value of the target node.
            properties (dict[str, Any] | None, optional): The properties of the relationship. Defaults to None.

        Returns:
            Any: The result of the operation.
        """
    @abstractmethod
    async def delete_node(self, label: str, identifier_key: str, identifier_value: str) -> Any:
        """Delete a node from the graph.

        Args:
            label (str): The label of the node.
            identifier_key (str): The key of the identifier.
            identifier_value (str): The identifier of the node.

        Returns:
            Any: The result of the operation.
        """
    @abstractmethod
    async def delete_relationship(self, node_source_key: str, node_source_value: str, relation: str, node_target_key: str, node_target_value: str) -> Any:
        """Delete a relationship between two nodes in the graph.

        Args:
            node_source_key (str): The key of the source node.
            node_source_value (str): The identifier of the source node.
            relation (str): The type of the relationship.
            node_target_key (str): The key of the target node.
            node_target_value (str): The identifier of the target node.

        Returns:
            Any: The result of the operation.
        """
    @abstractmethod
    async def query(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Query the graph data store.

        Args:
            query (str): The query to be executed.
            parameters (dict[str, Any] | None, optional): The parameters of the query. Defaults to None.

        Returns:
            list[dict[str, Any]]: The result of the query as a list of dictionaries.
        """
    @abstractmethod
    async def traverse_graph(self, node_properties: dict[str, Any], extracted_node_properties: list[str] | None = None, extracted_relationship_properties: list[str] | None = None, depth: int = 3) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        '''Traverse graph from a node with specified properties, ignoring relationship\'s direction, up to a given depth.

        Example:
            ```python
            nodes, relationships = await graph_data_store.traverse_graph(
                node_properties={"name": "John Doe"},
                extracted_node_properties=["name", "age"],
                extracted_relationship_properties=["since"],
                depth=1
            )
            ```
            Means starting from the node with property `name` equal to "John Doe", traverse
            the graph up to depth 1, extracting the `name` and `age` properties from nodes
            and the `since` property from relationships.

            ```python
            nodes, relationships = await graph_data_store.traverse_graph(
                node_properties={"name": "John Doe"},
                depth=2
            )
            ```
            Means starting from the node with property `name` equal to "John Doe", traverse
            the graph up to depth 2, extracting all properties from nodes and relationships.

        Args:
            node_properties (dict[str, Any]): The properties of the starting node.
            extracted_node_properties (list[str] | None, optional): The properties to extract from nodes during
                traversal. If None or empty list, all node properties will be returned. Defaults to None.
            extracted_relationship_properties (list[str] | None, optional): The properties to extract from relationships
                during traversal. If None or empty list, all relationship properties will be returned. Defaults to None.
            depth (int, optional): The depth of traversal. Defaults to 3.

        Returns:
            tuple[list[dict[str, Any]], list[dict[str, Any]]]: A tuple containing two lists:
                - List of nodes with their extracted properties.
                - List of relationships with their extracted properties.

            Example return value:
            nodes = [
                {
                    "id": 1001,
                    "labels": ["Person"],
                    "properties": {
                        "name": "John Doe",
                        "age": 30,
                        "occupation": "Engineer"
                    }
                },
                {
                    "id": 2001,
                    "labels": ["Company"],
                    "properties": {
                        "name": "TechCorp",
                        "industry": "Technology",
                        "employees": 500
                    }
                }
            ]

            relationships = [
                {
                    "id": 5002,
                    "type": "FRIEND_OF",
                    "start_node": 1001,
                    "end_node": 1002,
                    "properties": {
                        "since": "2018-05-20",
                        "closeness": 8
                    }
                }
            ]
        '''
    @abstractmethod
    async def close(self) -> None:
        """Close the graph data store."""
