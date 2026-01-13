from abc import ABC, abstractmethod
from gllm_datastore.encryptor.encryptor import BaseEncryptor as BaseEncryptor

class BaseKeyRing(ABC):
    """Abstract base class defining the interface for managing multiple encryption keys."""
    @abstractmethod
    def get(self, key_id: str) -> BaseEncryptor:
        """Get an encryptor by key ID.

        This method should be implemented by subclasses to provide the getting functionality.

        Args:
            key_id (str): ID of the key to retrieve.

        Returns:
            BaseEncryptor: The encryptor for the specified key.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
    @abstractmethod
    def add(self, key_id: str, encryptor: BaseEncryptor) -> None:
        """Add a new key to the key ring.

        This method should be implemented by subclasses to provide the adding functionality.

        Args:
            key_id (str): Unique identifier for the key.
            encryptor (BaseEncryptor): The encryptor instance for this key.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
    @abstractmethod
    def remove(self, key_id: str) -> None:
        """Remove a key from the key ring.

        This method should be implemented by subclasses to provide the removing functionality.

        Args:
            key_id (str): ID of the key to remove.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
