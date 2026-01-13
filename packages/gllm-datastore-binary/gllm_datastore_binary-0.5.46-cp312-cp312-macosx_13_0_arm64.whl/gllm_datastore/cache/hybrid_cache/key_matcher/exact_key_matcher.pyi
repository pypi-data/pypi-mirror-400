from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher

class ExactKeyMatcher(BaseKeyMatcher):
    """A key matcher that performs exact matching strategy.

    This implementation simply checks if the input key exists in the set of cached keys
    and returns it if found, otherwise returns None. The store_key method is a no-op.
    """
    async def store(self, key: str) -> None:
        """Store the key as additional information during the matching process.

        This method does nothing as exact matching doesn't require storing additional information.

        Args:
            key (str): The key to be stored.
        """
    async def retrieve(self, key: str, cached_keys: set[str]) -> str | None:
        """Retrieve the key with exact matching strategy.

        This method performs exact matching as follows:
        1. Check if the input key exists in the set of cached keys.
        2. If it does, return the input key.
        3. Otherwise, return None.

        Args:
            key (str): The input key to be matched.
            cached_keys (set[str]): The set of cached keys to be matched.

        Returns:
            str | None: The key if it exists in cached_keys, otherwise None.
        """
    async def delete(self, key: str | list[str]) -> None:
        """Delete the key stored as additional information during the matching process.

        This method does nothing as exact matching doesn't require deleting additional information.

        Args:
            key (str | list[str]): The key(s) to be deleted.
        """
    async def clear(self) -> None:
        """Clear all the keys that are stored as additional information during the matching process.

        This method does nothing as exact matching doesn't require clearing additional information.
        """
