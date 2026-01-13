from gllm_datastore.encryptor.encryptor import BaseEncryptor as BaseEncryptor
from gllm_datastore.encryptor.key_ring.key_ring import BaseKeyRing as BaseKeyRing

class InMemoryKeyRing(BaseKeyRing):
    """In-memory implementation of BaseKeyRing.

    This class provides a simple in-memory storage for encryption keys and
    their associated encryptors. All keys are stored in memory and will be
    lost when the application terminates.

    Attributes:
        encryptors (dict[str, BaseEncryptor]): A dictionary to store the keys and their associated encryptors.
    """
    encryptors: dict[str, BaseEncryptor]
    def __init__(self, encryptors: dict[str, BaseEncryptor] | None = None) -> None:
        """Initialize the InMemoryKeyRing.

        Args:
            encryptors (dict[str, BaseEncryptor] | None, optional): A dictionary to store the keys and
                their associated encryptors. Defaults to None.
        """
    def get(self, key_id: str) -> BaseEncryptor:
        """Get an encryptor by key ID.

        Args:
            key_id (str): ID of the key to retrieve.

        Returns:
            BaseEncryptor: The encryptor for the specified key.

        Raises:
            KeyError: If key_id does not exist.
        """
    def add(self, key_id: str, encryptor: BaseEncryptor) -> None:
        """Add a new key to the key ring.

        Args:
            key_id (str): Unique identifier for the key.
            encryptor (BaseEncryptor): The encryptor instance for this key.

        Raises:
            KeyError: If key_id already exists.
        """
    def remove(self, key_id: str) -> None:
        """Remove a key from the key ring.

        Args:
            key_id (str): ID of the key to remove.

        Raises:
            KeyError: If key_id does not exist.
        """
