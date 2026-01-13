from _typeshed import Incomplete
from gllm_datastore.encryptor.encryptor import BaseEncryptor as BaseEncryptor

KEY_LENGTH_BYTES: int
NONCE_LENGTH_BYTES: int

class AESGCMEncryptor(BaseEncryptor):
    """AES-GCM 256 Encryptor that accepts keys directly.

    This class provides AES-GCM symmetric encryption and decryption methods
    with a 256-bit key provided directly by the client.

    Attributes:
        key (bytes): 256-bit encryption key.
        aesgcm (AESGCM): AES-GCM instance.
    """
    key: Incomplete
    aesgcm: Incomplete
    def __init__(self, key: bytes) -> None:
        """Initialize AESGCMEncryptor with a direct key.

        Args:
            key (bytes): 256-bit encryption key.

        Raises:
            ValueError: If key length is not 256 bits.
        """
    def encrypt(self, plaintext: str) -> str:
        """Encrypts the plaintext using AES-GCM with a random nonce.

        Args:
            plaintext (str): The plaintext data to be encrypted.

        Returns:
            str: The encrypted data, encoded in base64 format.
        """
    def decrypt(self, ciphertext: str) -> str:
        """Decrypts the AES-GCM ciphertext.

        Args:
            ciphertext (str): The ciphertext in base64 format to be decrypted.

        Returns:
            str: The decrypted plaintext data.
        """
