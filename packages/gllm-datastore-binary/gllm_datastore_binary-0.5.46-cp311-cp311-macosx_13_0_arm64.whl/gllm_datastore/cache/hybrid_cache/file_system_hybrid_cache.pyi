from _typeshed import Incomplete
from gllm_datastore.cache.hybrid_cache.hybrid_cache import BaseHybridCache as BaseHybridCache
from gllm_datastore.cache.hybrid_cache.key_matcher.key_matcher import BaseKeyMatcher as BaseKeyMatcher

class FileSystemHybridCache(BaseHybridCache):
    '''A cache that stores data in the file system.

    The `FileSystemHybridCache` class utilizes the file system to store cache data.

    Attributes:
        cache_dir (str): The directory to store the cache data.
        cache_version (str): The version of the cache data.
        current_version_dir (str): The directory to store the cache data for the current version.
        metadata_dir (str): The directory to store the metadata for the cache data.
        serialization_format (str): The serialization format to use for storing the cache data.
            The supported serialization formats are "json" and "pickle".
        compression_extension (str): The extension to use for the compression of the cache data. The supported
            compression extensions are "json.gz" and "pkl.gz".
        logger (Logger): The logger to use for logging.
        key_matcher (BaseKeyMatcher): The key matcher to use that defines the cache key matching strategy.
    '''
    logger: Incomplete
    cache_dir: Incomplete
    cache_version: Incomplete
    current_version_dir: Incomplete
    metadata_dir: Incomplete
    serialization_format: Incomplete
    compression_extension: Incomplete
    def __init__(self, cache_dir: str, cache_version: str = '1.0.0', serialization_format: str = 'json', key_matcher: BaseKeyMatcher | None = None) -> None:
        '''Initializes a new instance of the FileSystemHybridCache class.

        Args:
            cache_dir (str): The directory to store the cache data.
            cache_version (str, optional): The version of the cache data. Defaults to "1.0.0".
            serialization_format (str, optional): The serialization format to use for storing the cache data.
                The supported serialization formats are "json" and "pickle". Defaults to "json".
            key_matcher (BaseKeyMatcher | None, optional): The key matcher to use that defines the cache key
                matching strategy. Defaults to None, in which case the `ExactKeyMatcher` will be used.

        Raises:
            ValueError: If the serialization format is not supported.
        '''
    async def retrieve_all_keys(self) -> set[str]:
        """Retrieves all keys from the file system cache.

        This method filters out and deletes any expired keys before returning the set.

        Returns:
            set[str]: A set of all keys in the file system cache.
        """
