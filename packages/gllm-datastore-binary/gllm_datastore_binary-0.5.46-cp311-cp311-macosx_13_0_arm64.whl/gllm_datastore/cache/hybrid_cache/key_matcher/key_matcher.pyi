from abc import ABC, abstractmethod

class BaseKeyMatcher(ABC):
    """A base class for key matcher classes used in hybrid caches.

    The key matcher is a framework that can be used by hybrid caches to retrieve the key that matches
    the input key using different strategies as defined in the subclasses.
    """
    @abstractmethod
    async def store(self, key: str) -> None:
        """Store the key as additional information during the matching process.

        This method must be implemented by the subclasses to define the logic for storing the key as additional
        information during the matching process.

        Args:
            key (str): The key to be stored as additional information during the matching process.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def retrieve(self, key: str, cached_keys: set[str]) -> str | None:
        """Retrieve the key that matches the input key.

        This method must be implemented by the subclasses to define the logic for retrieving the matched key.

        Args:
            key (str): The input key to be matched.
            cached_keys (set[str]): The set of cached keys to be matched.

        Returns:
            str | None: The matched key, if found. Otherwise, None.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def delete(self, key: str | list[str]) -> None:
        """Delete the key stored as additional information during the matching process.

        This method must be implemented by the subclasses to define the logic for deleting the key stored as additional
        information during the matching process.

        Args:
            key (str | list[str]): The key(s) to be deleted.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
    @abstractmethod
    async def clear(self) -> None:
        """Clear all the keys that are stored as additional information during the matching process.

        This method must be implemented by the subclasses to define the logic for clearing all the keys that are
        stored as additional information during the matching process.

        Raises:
            NotImplementedError: If the method is not implemented.
        """
