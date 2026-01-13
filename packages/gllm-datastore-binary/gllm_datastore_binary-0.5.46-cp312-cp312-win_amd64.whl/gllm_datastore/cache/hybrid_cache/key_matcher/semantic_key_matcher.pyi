from _typeshed import Incomplete
from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher
from gllm_datastore.vector_data_store import ElasticsearchVectorDataStore as ElasticsearchVectorDataStore
from gllm_datastore.vector_data_store.vector_data_store import BaseVectorDataStore as BaseVectorDataStore

class SemanticKeyMatcher(BaseKeyMatcher):
    """A key matcher that performs semantic matching strategy.

    This implementation uses semantic matching to find the closest match between the input key
    and the cached keys. The similarity is calculated using a vector data store instance.

    Attributes:
        vector_data_store (BaseVectorDataStore): The vector data store to be used for semantic matching.
        max_distance_ratio (float): The ratio of key length to use as maximum Levenshtein distance
            for a key to match with the cached keys (e.g., 0.05 means 5% of key length).

    Note:
        Since the semantic matching heavily depends on the semantic similarity between the key and the cached
        key, it should only be used when the key is a plain string. Semantic matching SHOULD NOT be used when the key
        is a hash / encryption of the input data.

        Additionally, the semantic matching is currently has the following tech debts:
        1. The distance to be evaluated againts the threshold is calculated using the Levenshtein distance.
           This will be updated to use semantic score once the vector data store supports retrieval with scores.
        2. The vector data store currently only supports `ElasticsearchVectorDataStore`.
           This should be updated once the vector data store supports a general interface to delete and clear all
           chunks from the vector data store.
    """
    vector_data_store: Incomplete
    max_distance_ratio: Incomplete
    def __init__(self, vector_data_store: BaseVectorDataStore, max_distance_ratio: float = 0.05) -> None:
        """Initialize a new instance of the `SemanticKeyMatcher` class.

        Args:
            vector_data_store (BaseVectorDataStore): The vector data store to be used for semantic matching.
            max_distance_ratio (float, optional): The ratio of key length to use as maximum Levenshtein distance
                for a key to match with the cached keys (e.g., 0.05 means 5% of key length). Must be between 0 and 1.
                Defaults to 0.05.

        Raises:
            ValueError: If the fuzzy distance ratio is not between 0 and 1.
            ValueError: If the vector data store is not an instance of `ElasticsearchVectorDataStore`.
        """
    async def store(self, key: str) -> None:
        """Store the key as additional information during the matching process.

        This method adds the key to the vector data store.

        Args:
            key (str): The key to be stored.
        """
    async def retrieve(self, key: str, cached_keys: set[str]) -> str | None:
        """Retrieve the key with the semantic matching strategy.

        This method performs semantic matching as follows:
        1. Retrieve the most similar key from the vector data store.
        2. Calculate the distance between the input key and the retrieved key.
        3. Calculate the maximum distance as a ratio of the input key length.
        4. If the distance is less than or equal to the maximum distance and the retrieved key exists in cached_keys,
           return the retrieved key. Otherwise, return None.

        Note:
            As of now, the distance to be evaluated againts the threshold is calculated using the Levenshtein distance.
            This will be updated to use semantic score once the vector data store supports retrieval with scores.

        Args:
            key (str): The input key to be matched.
            cached_keys (set[str]): The set of cached keys to be matched.

        Returns:
            str | None: The key if it exists in cached_keys, otherwise None.
        """
    async def delete(self, key: str | list[str]) -> None:
        """Delete the key stored as additional information during the matching process.

        This method deletes the key from the vector data store.

        Note:
            As of now, this is only compatible with the `ElasticsearchVectorDataStore` implementation.
            This should be updated once the vector data store supports deletion of chunks by query.

        Args:
            key (str | list[str]): The key(s) to be deleted.
        """
    async def clear(self) -> None:
        """Clear all the keys that are stored as additional information during the matching process.

        Note:
            As of now, this is only compatible with the `ElasticsearchVectorDataStore` implementation.
            This should be updated once the vector data store supports deletion of chunks by query.

        This method deletes all keys from the vector data store.
        """
