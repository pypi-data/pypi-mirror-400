from abc import ABC, abstractmethod
from enum import StrEnum
from gllm_datastore.cache import Cache as Cache
from gllm_datastore.core.capabilities import FulltextCapability as FulltextCapability, GraphCapability as GraphCapability, VectorCapability as VectorCapability
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store.exceptions import NotRegisteredException as NotRegisteredException, NotSupportedException as NotSupportedException
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from typing import Any

class CapabilityType(StrEnum):
    """Enumeration of supported capability types."""
    FULLTEXT: str
    GRAPH: str
    VECTOR: str

class BaseDataStore(ABC):
    """Base class for datastores with multiple capabilities.

    This class provides the infrastructure for capability composition and
    delegation. Datastores inherit from this class and register capability
    handlers based on their configuration.
    """
    def __init__(self) -> None:
        """Initialize the datastore with specified capabilities."""
    @property
    @abstractmethod
    def supported_capabilities(self) -> list[CapabilityType]:
        """Return list of currently supported capabilities.

        A data store might have more capabilities than the ones that are currently registered.
        Each data store should implement this method to return the list of supported capabilities.

        Returns:
            list[str]: List of capability names that are supported.

        Raises:
            NotImplementedError: If the method is not implemented by subclass.
        """
    @property
    def registered_capabilities(self) -> list[CapabilityType]:
        """Return list of currently registered capabilities.

        Returns:
            list[str]: List of capability names that are registered and available.
        """
    @property
    def fulltext(self) -> FulltextCapability:
        """Access fulltext capability if supported.

        Returns:
            FulltextCapability: Fulltext capability handler.

        Raises:
            NotSupportedException: If fulltext capability is not supported.
        """
    @property
    def vector(self) -> VectorCapability:
        """Access vector capability if supported.

        Returns:
            VectorCapability: Vector capability handler.

        Raises:
            NotSupportedException: If vector capability is not supported
        """
    @property
    def graph(self) -> GraphCapability:
        """Access graph capability if supported.

        Returns:
            GraphCapability: Graph capability handler.

        Raises:
            NotSupportedException: If graph capability is not supported.
        """
    def with_fulltext(self, **kwargs) -> Self:
        """Configure fulltext capability and return datastore instance.

        Args:
            **kwargs: Fulltext capability configuration parameters.

        Returns:
            Self: Self for method chaining.
        """
    def with_vector(self, em_invoker: BaseEMInvoker, **kwargs) -> Self:
        """Configure vector capability and return datastore instance.

        Args:
            em_invoker (BaseEMInvoker): Embedding model invoker (required).
            **kwargs: Vector capability configuration parameters.

        Returns:
            Self: Self for method chaining.
        """
    def with_graph(self, **kwargs) -> Self:
        """Configure graph capability and return datastore instance.

        Args:
            **kwargs: Graph capability configuration parameters.

        Returns:
            Self: Self for method chaining.
        """
    def as_cache(self, eviction_manager: Any | None = None, matching_strategy: Any = None) -> Cache:
        """Create a Cache instance from this datastore.

        Args:
            eviction_manager (Any | None, optional): Optional eviction manager for cache eviction.
                Defaults to None.
            matching_strategy (Any, optional): Default matching strategy for cache retrieval.
                Defaults to None.

        Returns:
            Cache: Instance wrapping this datastore.

        Raises:
            ValueError: If required capabilities not registered.
        """
    @classmethod
    def translate_query_filter(cls, query_filter: FilterClause | QueryFilter | None) -> Any:
        """Translate QueryFilter or FilterClause to datastore's native filter syntax.

        This method provides a public interface for converting the GLLM DataStore's
        QueryFilter DSL into each datastore's native filter format. Subclasses must
        implement this method to provide their specific translation logic.

        Args:
            query_filter (FilterClause | QueryFilter | None): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses,
                or None for empty filters.

        Returns:
            Any: The translated filter in the datastore's native format.
                Returns None for empty filters.

        Raises:
            NotImplementedError: If not implemented by subclass.
        """
