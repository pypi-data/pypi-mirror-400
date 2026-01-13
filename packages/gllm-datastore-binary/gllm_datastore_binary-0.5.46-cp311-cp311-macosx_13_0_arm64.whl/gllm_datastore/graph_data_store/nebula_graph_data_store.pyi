from _typeshed import Incomplete
from gllm_datastore.graph_data_store.graph_data_store import BaseGraphDataStore as BaseGraphDataStore
from typing import Any

class NebulaGraphDataStore(BaseGraphDataStore):
    '''Implementation of BaseGraphDataStore for Nebula Graph.

    This class provides an interface for graph-based Retrieval-Augmented Generation (RAG)
    operations on Nebula graph databases.

    Attributes:
        connection_pool (ConnectionPool): The connection pool for Nebula Graph.
        space (str): The space name.
        user (str): The username.
        password (str): The password.
        operation_wait_time (int): The timeout in seconds.

    Example:
        ```python
        store = NebulaGraphDataStore(
            url="127.0.0.1",
            port=9669,
            user="root",
            password="nebula",
            space="testing"
        )
        # Perform query
        results = await store.query("MATCH (n) RETURN n")

        # Create a node
        node = await store.upsert_node("Person", "name", "John", {"age": 30})
        ```
    '''
    connection_pool: Incomplete
    space: Incomplete
    user: Incomplete
    password: Incomplete
    operation_wait_time: Incomplete
    def __init__(self, url: str, port: int, user: str, password: str, space: str, operation_wait_time: int = 5) -> None:
        """Initialize NebulaGraphDataStore.

        Args:
            url (str): The URL of the graph store.
            port (int): The port of the graph store.
            user (str): The user of the graph store.
            password (str): The password of the graph store.
            space (str): The space name.
            operation_wait_time (int, optional): The operation wait time in seconds. Defaults to 5.
        """
    async def upsert_node(self, label: str, identifier_key: str, identifier_value: str, properties: dict[str, Any] | None = None) -> Any:
        """Upsert a node in the graph.

        Args:
            label (str): The label of the node.
            identifier_key (str): The key of the identifier.
            identifier_value (str): The value of the identifier.
            properties (dict[str, Any] | None, optional): The properties of the node. Defaults to None.

        Returns:
            Any: The result of the operation.
        """
    async def upsert_relationship(self, node_source_key: str, node_source_value: str, relation: str, node_target_key: str, node_target_value: str, properties: dict[str, Any] | None = None) -> Any:
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
    async def delete_node(self, label: str, identifier_key: str, identifier_value: str) -> Any:
        """Delete a node from the graph.

        Args:
            label (str): The label of the node.
            identifier_key (str): The key of the identifier.
            identifier_value (str): The identifier of the node.

        Returns:
            Any: The result of the operation.
        """
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
    async def query(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Query the graph store.

        Args:
            query (str): The query to be executed.
            parameters (dict[str, Any] | None, optional): The parameters of the query. Defaults to None.

        Returns:
            list[dict[str, Any]]: The result of the query.
        """
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
                - List of nodes with their extracted properties (including the source node).
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

        Raises:
            ValueError: If node_properties is empty or depth is less than 1.
        '''
    async def close(self) -> None:
        """Close the graph data store."""
    async def get_nodes(self, label: str | None = None) -> list[dict[str, Any]]:
        """Get all nodes with optional label filter.

        Args:
            label (str | None, optional): The label of the nodes. Defaults to None.

        Returns:
            list[dict[str, Any]]: The result of the query.
        """
    async def get_relationships(self, source_value: str | None = None, relation: str | None = None) -> list[dict[str, Any]]:
        """Get relationships with optional filters.

        Args:
            source_value (str | None, optional): The source vertex identifier. Defaults to None.
            relation (str | None, optional): The relationship type. Defaults to None.

        Returns:
            list[dict[str, Any]]: The result of the query.
        """
