from _typeshed import Incomplete
from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher

class FuzzyKeyMatcher(BaseKeyMatcher):
    """A key matcher that performs fuzzy matching strategy.

    This implementation uses fuzzy matching to find the closest match between the input key
    and the cached keys. The distance is calculated using the Levenshtein distance.

    Attributes:
        max_distance_ratio (float): The ratio of key length to use as maximum Levenshtein distance
            for a key to match with the cached keys (e.g., 0.05 means 5% of key length).

    Note:
        Since the fuzzy matching heavily depends on the syntactic similarity between the key and the cached
        key, it should only be used when the key is a plain string. Fuzzy matching SHOULD NOT be used when the key
        is a hash / encryption of the input data.
    """
    max_distance_ratio: Incomplete
    def __init__(self, max_distance_ratio: float = 0.05) -> None:
        """Initialize a new instance of the `FuzzyKeyMatcher` class.

        Args:
            max_distance_ratio (float, optional): The ratio of key length to use as maximum Levenshtein distance
                for a key to match with the cached keys (e.g., 0.05 means 5% of key length). Must be between 0 and 1.
                Defaults to 0.05.

        Raises:
            ValueError: If the fuzzy distance ratio is not between 0 and 1.
        """
    async def store(self, key: str) -> None:
        """Store the key as additional information during the matching process.

        This method does nothing as fuzzy matching doesn't require storing additional information.

        Args:
            key (str): The key to be stored.
        """
    async def retrieve(self, key: str, cached_keys: set[str]) -> str | None:
        """Retrieve the key with fuzzy matching strategy.

        This method performs fuzzy matching as follows:
        1. Iterate through all cached keys and calculate the Levenshtein distance between the key and the cached key
           to get the key with the smallest distance.
        2. If a cached key with the distance of 0 is found, the cached value of that key is returned immediately.
        3. If the smallest distance is less than the fuzzy distance ratio, the cached value of the key with the
           smallest distance is returned.
        4. Otherwise, None is returned.

        Args:
            key (str): The input key to be matched.
            cached_keys (set[str]): The set of cached keys to be matched.

        Returns:
            str | None: The key with the smallest Levenshtein distance, if the distance is less than the fuzzy
                distance ratio, otherwise None.
        """
    async def delete(self, key: str | list[str]) -> None:
        """Delete the keys stored as additional information during the matching process.

        This method does nothing as fuzzy matching doesn't require deleting additional information.

        Args:
            key (str | list[str]): The key(s) to be deleted.
        """
    async def clear(self) -> None:
        """Clear all the keys that are stored as additional information during the matching process.

        This method does nothing as fuzzy matching doesn't require clearing additional information.
        """
