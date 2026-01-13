from abc import ABC, abstractmethod

class BaseEncryptor(ABC):
    """Abstract base class defining the interface for encryption implementations.

    This abstract base class ensures that all encryptors implement the required
    encrypt and decrypt methods with consistent signatures.

    Thread-safety requirement:
        Implementations MUST be thread-safe. The client may
        invoke `encrypt` and `decrypt` concurrently from multiple threads, so
        any internal state (e.g., buffers, nonces, cipher instances) must be
        protected or designed to avoid race conditions.
    """
    @abstractmethod
    def encrypt(self, plaintext: str) -> str:
        """Encrypt plain text into cipher text.

        This method should be implemented by subclasses to provide the encryption functionality.

        Note:
            The implementation must be thread-safe and must not mutate shared state
            without proper synchronization.

        Args:
            plaintext (str): The raw plain text to encrypt.

        Returns:
            str: The encrypted cipher text.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
    @abstractmethod
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt cipher text back into plain text.

        This method should be implemented by subclasses to provide the decryption functionality.

        Note:
            The implementation must be thread-safe and must not mutate shared state
            without proper synchronization.

        Args:
            ciphertext (str): The ciphertext to decrypt.

        Returns:
            str: The decrypted plain text.

        Raises:
            NotImplementedError: If the method is not implemented by the subclass.
        """
