from _typeshed import Incomplete
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, QueryFilter as QueryFilter
from gllm_datastore.data_store.base import BaseDataStore as BaseDataStore, CapabilityType as CapabilityType
from gllm_datastore.data_store.redis.fulltext import RedisFulltextCapability as RedisFulltextCapability
from gllm_datastore.data_store.redis.query import get_filterable_fields_from_index as get_filterable_fields_from_index
from gllm_datastore.data_store.redis.query_translator import RedisQueryTranslator as RedisQueryTranslator
from gllm_datastore.data_store.redis.vector import RedisVectorCapability as RedisVectorCapability
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from redis.asyncio.client import Redis

class RedisDataStore(BaseDataStore):
    """Redis data store with fulltext capability support.

    Attributes:
        index_name (str): Name for the Redis index.
        client (Redis): Redis client instance.
    """
    client: Incomplete
    index_name: Incomplete
    def __init__(self, index_name: str, url: str | None = None, client: Redis | None = None) -> None:
        """Initialize the Redis data store.

        Args:
            index_name (str): Name of the Redis index to use.
            url (str | None, optional): URL for Redis connection. Defaults to None.
                Format: redis://[[username]:[password]]@host:port/database
            client (Redis | None, optional): Redis client instance to use. Defaults to None.
                in which case the url parameter will be used to create a new Redis client.

        Raises:
            ValueError: If neither `url` nor `client` is provided, or if URL is invalid.
            TypeError: If `client` is not a Redis instance.
            ConnectionError: If Redis connection fails.
        """
    @property
    def supported_capabilities(self) -> list[CapabilityType]:
        """Return list of currently supported capabilities.

        Returns:
            list[CapabilityType]: List of capability names that are supported.
        """
    @property
    def fulltext(self) -> RedisFulltextCapability:
        """Access fulltext capability if registered.

        This method uses the logic of its parent class to return the fulltext capability handler.
        This method overrides the parent class to return the RedisFulltextCapability handler for better
        type hinting.

        Returns:
            RedisFulltextCapability: Fulltext capability handler.

        Raises:
            NotRegisteredException: If fulltext capability is not registered.
        """
    @property
    def vector(self) -> RedisVectorCapability:
        """Access vector capability if registered.

        This method uses the logic of its parent class to return the vector capability handler.
        This method overrides the parent class to return the RedisVectorCapability handler for better
        type hinting.

        Returns:
            RedisVectorCapability: Vector capability handler.

        Raises:
            NotRegisteredException: If vector capability is not registered.
        """
    def with_fulltext(self, index_name: str | None = None) -> RedisDataStore:
        """Configure fulltext capability and return datastore instance.

        Schema will be automatically inferred from chunks when creating a new index,
        or auto-detected from an existing index when performing operations.

        Args:
            index_name (str | None, optional): The name of the Redis index. Defaults to None,
                in which case the default class attribute will be utilized.

        Returns:
            RedisDataStore: RedisDataStore instance for method chaining.
        """
    def with_vector(self, em_invoker: BaseEMInvoker, index_name: str | None = None) -> RedisDataStore:
        """Configure vector capability and return datastore instance.

        Schema will be automatically inferred from chunks when creating a new index,
        or auto-detected from an existing index when performing operations.

        Args:
            em_invoker (BaseEMInvoker): The embedding model to perform vectorization.
            index_name (str | None, optional): The name of the Redis index. Defaults to None,
                in which case the default class attribute will be utilized.

        Returns:
            RedisDataStore: RedisDataStore instance for method chaining.

        Raises:
            ValueError: If em_invoker is not provided.
        """
    def translate_query_filter(self, query_filter: FilterClause | QueryFilter | None = None) -> str | None:
        '''Translate QueryFilter or FilterClause to Redis native filter syntax.

        This method delegates to the existing RedisQueryTranslator in the
        redis.query_translator module and returns the result as a string.
        It uses the instance\'s index_name and client to detect field types
        for accurate Redis Search query syntax.

        Examples:
            ```python
            from gllm_datastore.core.filters import filter as F

            # Create datastore instance
            datastore = RedisDataStore(index_name="my_index", url="redis://localhost:6379")

            # Single FilterClause (field types detected from index schema)
            clause = F.eq("metadata.status", "active")
            result = datastore.translate_query_filter(clause)
            # Returns: "@metadata_status:{active}" if status is a TAG field
            # Returns: "@metadata_status:active" if status is a TEXT field

            # QueryFilter with multiple clauses (AND condition)
            filter_obj = F.and_(
                F.eq("metadata.status", "active"),
                F.gt("metadata.age", 25),
            )
            result = datastore.translate_query_filter(filter_obj)
            # Returns: "@metadata_status:{active} @metadata_age:[(25 +inf]"

            # QueryFilter with OR condition
            filter_obj = F.or_(
                F.eq("metadata.status", "active"),
                F.eq("metadata.status", "pending"),
            )
            result = datastore.translate_query_filter(filter_obj)
            # Returns: "@metadata_status:{active} | @metadata_status:{pending}"

            # IN operator (produces parentheses syntax)
            filter_obj = F.in_("metadata.category", ["tech", "science"])
            result = datastore.translate_query_filter(filter_obj)
            # Returns: "@metadata_category:(tech|science)"

            # Empty filter returns None
            result = datastore.translate_query_filter(None)
            # Returns: None
            ```

        Args:
            query_filter (FilterClause | QueryFilter | None, optional): The filter to translate.
                Can be a single FilterClause, a QueryFilter with multiple clauses. Defaults to None.

        Returns:
            str | None: The translated filter as a Redis Search query string.
                Returns None if no filter is provided.
        '''
