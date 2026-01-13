from _typeshed import Incomplete
from gllm_datastore.encryptor.encryptor import BaseEncryptor as BaseEncryptor
from gllm_datastore.encryptor.key_ring.key_ring import BaseKeyRing as BaseKeyRing

class KeyRotatingEncryptor(BaseEncryptor):
    """Encryptor that supports key rotation through a key ring.

    This encryptor uses a BaseKeyRing to manage multiple encryption keys.
    Users must specify which key to use for encryption and decryption operations.

    Attributes:
        key_ring (BaseKeyRing): The key ring managing encryption keys.
        active_key_id (str): The ID of the current key to use for encryption.
    """
    key_ring: Incomplete
    def __init__(self, key_ring: BaseKeyRing, active_key_id: str) -> None:
        """Initialize KeyRotatingEncryptor with a key ring.

        Args:
            key_ring (BaseKeyRing): The key ring to use for key management.
            active_key_id (str): The ID of the current key to use for encryption.
        """
    @property
    def active_key_id(self) -> str:
        """Get the ID of the current key to use for encryption."""
    @active_key_id.setter
    def active_key_id(self, value: str) -> None:
        """Set the ID of the current key to use for encryption.

        Args:
            value (str): The ID of the current key to use for encryption.

        Raises:
            KeyError: If the specified key does not exist.
        """
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plaintext using the specified key.

        Args:
            plaintext (str): The plaintext to encrypt.

        Returns:
            str: The encrypted data with key metadata, encoded in base64.

        Raises:
            KeyError: If the specified key does not exist.
        """
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt ciphertext the key detected from metadata.

        Args:
            ciphertext (str): The encrypted data with key metadata.

        Returns:
            str: The decrypted plaintext.

        Raises:
            ValueError: If the data format is invalid or decryption fails.
            KeyError: If the required key is not available.
        """
