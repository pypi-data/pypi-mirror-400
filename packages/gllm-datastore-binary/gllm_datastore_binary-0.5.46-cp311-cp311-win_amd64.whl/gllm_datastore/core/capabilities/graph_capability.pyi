from typing import Any, Protocol

class GraphCapability(Protocol):
    """Protocol for graph database operations.

    This protocol defines the interface for datastores that support graph-based
    data operations. This includes node and relationship management as well as graph queries.
    """
    async def upsert_node(self, label: str, identifier_key: str, identifier_value: str, properties: dict[str, Any] | None = None) -> Any:
        """Create or update a node in the graph.

        Args:
            label (str): Node label/type.
            identifier_key (str): Key field for node identification.
            identifier_value (str): Value for node identification.
            properties (dict[str, Any] | None, optional): Additional node properties.
                Defaults to None.

        Returns:
            Any: Created/updated node information.
        """
    async def upsert_relationship(self, node_source_key: str, node_source_value: str, relation: str, node_target_key: str, node_target_value: str, properties: dict[str, Any] | None = None) -> Any:
        """Create or update a relationship between nodes.

        Args:
            node_source_key (str): Source node identifier key.
            node_source_value (str): Source node identifier value.
            relation (str): Relationship type.
            node_target_key (str): Target node identifier key.
            node_target_value (str): Target node identifier value.
            properties (dict[str, Any] | None, optional): Relationship properties.
                Defaults to None.

        Returns:
            Any: Created/updated relationship information.
        """
    async def retrieve(self, query: str, parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        """Retrieve data from the graph with specific query.

        Args:
            query (str): Query to retrieve data from the graph.
            parameters (dict[str, Any] | None, optional): Query parameters. Defaults to None.

        Returns:
            list[dict[str, Any]]: Query results as list of dictionaries.
        """
    async def delete_node(self, label: str, identifier_key: str, identifier_value: str) -> Any:
        """Delete a node and its relationships.

        Args:
            label (str): Node label/type.
            identifier_key (str): Node identifier key.
            identifier_value (str): Node identifier value.

        Returns:
            Any: Deletion result information.
        """
    async def delete_relationship(self, node_source_key: str, node_source_value: str, relation: str, node_target_key: str, node_target_value: str) -> Any:
        """Delete a relationship between nodes.

        Args:
            node_source_key (str): Source node identifier key.
            node_source_value (str): Source node identifier value.
            relation (str): Relationship type.
            node_target_key (str): Target node identifier key.
            node_target_value (str): Target node identifier value.

        Returns:
            Any: Deletion result information.
        """
