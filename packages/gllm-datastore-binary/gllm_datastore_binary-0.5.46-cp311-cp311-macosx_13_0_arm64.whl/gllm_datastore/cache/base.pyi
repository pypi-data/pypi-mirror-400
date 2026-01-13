from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, Callable

class MatchingStrategy(StrEnum):
    """Defines how keys should be matched during retrieval."""
    EXACT: str
    FUZZY: str
    SEMANTIC: str

class BaseCache(ABC):
    """Base class for cache using data store."""
    @abstractmethod
    def cache(self, key_func: Callable | None = None, name: str = '', matching_strategy: MatchingStrategy = ..., matching_config: dict[str, Any] | None = None, **kwargs) -> Callable:
        """Decorator to cache the result of a function.

        This method should be implemented by subclasses to provide the caching functionality.

        Args:
            key_func (Callable | None, optional): Function to generate the cache key. Defaults to None.
            name (str, optional): Name of the cache. Defaults to an empty string.
            matching_strategy (MatchingStrategy, optional): The strategy to use for matching keys.
                This can be one of the values from the MatchingStrategy enum. Defaults to exact matching.
            matching_config (dict[str, Any] | None, optional): Configuration parameters for matching strategies.
                Defaults to None.
            **kwargs: Additional parameters specific to the caching method.

        Returns:
            Callable: A decorator that can be applied to a function to cache its result.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    def retrieve(self, key: str, **kwargs) -> Any | None:
        """Retrieve the cached result.

        This method should be implemented by subclasses to provide the retrieval functionality.

        Args:
            key (str): The cache key to retrieve.
            **kwargs: Additional parameters specific to the retrieval method.

        Returns:
            Any | None: The cached result if found, otherwise None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    def store(self, key: str, value: Any, **kwargs) -> None:
        """Store the cached result.

        This method should be implemented by subclasses to provide the storage functionality.

        Args:
            key (str): The cache key to store.
            value (Any): The value to store in the cache.
            **kwargs: Additional parameters specific to the storage method.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    def delete(self, key: str | list[str]) -> None:
        """Delete the cached result.

        This method should be implemented by subclasses to provide the deletion functionality.

        Args:
            key (str | list[str]): The cache key to delete.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    def clear(self) -> None:
        """Clear all cached results.

        This method should be implemented by subclasses to provide the clearing functionality.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
