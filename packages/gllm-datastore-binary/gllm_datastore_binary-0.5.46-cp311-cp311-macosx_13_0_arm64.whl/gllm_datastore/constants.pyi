from enum import Enum

DEFAULT_TOP_K: int
DEFAULT_FETCH_K: int
DEFAULT_REQUEST_TIMEOUT: int
SIMILARITY_SCORE: str
DEFAULT_FUZZY_MATCH_MAX_DISTANCE: int
DEFAULT_REDIS_QUERY_BATCH_SIZE: int
REDIS_DEFAULT_HOST: str
REDIS_DEFAULT_PORT: int
REDIS_DEFAULT_DB: int
FIELD_CONFIG_NAME: str
FIELD_CONFIG_TYPE: str
BOOL_TRUE_STR: str
BOOL_FALSE_STR: str
METADATA_PREFIX: str
METADATA_SEPARATOR: str
LIST_SEPARATOR: str

class FieldType(str, Enum):
    """Redis Search field types for filterable fields.

    Attributes:
        NUMERIC: Numeric field type for range queries.
        TAG: Tag field type for exact matching and filtering.
        TEXT: Text field type for full-text search.
    """
    NUMERIC: str
    TAG: str
    TEXT: str

class CHUNK_KEYS:
    """Dictionary-like keys used internally for in-memory chunk representation."""
    ID: str
    TEXT: str
    CONTENT: str
    METADATA: str
    VECTOR: str
    SCORE: str

class METADATA_KEYS:
    """Metadata keys used in the cache compatible vector data store.

    Attributes:
        EMBEDDINGS (str): Key for the embeddings in the cache.
        DOCUMENTS (str): Key for the documents in the cache.
        METADATA (str): Key for the metadata in the cache.
        ORIGINAL_KEY (str): Key to store the original key value.
        CACHE_VALUE (str): Key for the cached value.
        CACHE_CREATED (str): Key for the timestamp when the cache was created.
        TTL (str): Key for the time-to-live of the cache.
        EXPIRE_AT (str): Key for the expiration time of the cache.
        LAST_USED_AT (str): Key for the last used time of the cache.
        ACCESS_COUNT (str): Key for the access count of the cache.
    """
    EMBEDDINGS: str
    DOCUMENTS: str
    METADATAS: str
    METADATA: str
    ORIGINAL_KEY: str
    CACHE_VALUE: str
    CACHE_CREATED: str
    TTL: str
    EXPIRE_AT: str
    LAST_USED_AT: str
    ACCESS_COUNT: str
