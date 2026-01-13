from _typeshed import Incomplete
from collections.abc import Callable
from gllm_datastore.constants import BOOL_FALSE_STR as BOOL_FALSE_STR, BOOL_TRUE_STR as BOOL_TRUE_STR, CHUNK_KEYS as CHUNK_KEYS, FIELD_CONFIG_NAME as FIELD_CONFIG_NAME, FIELD_CONFIG_TYPE as FIELD_CONFIG_TYPE, FieldType as FieldType, METADATA_SEPARATOR as METADATA_SEPARATOR
from gllm_datastore.core.filters import FilterClause as FilterClause, FilterCondition as FilterCondition, FilterOperator as FilterOperator, QueryFilter as QueryFilter
from typing import Any

REDIS_SPECIAL_CHARS: str
REDIS_SPECIAL_CHARS_PATTERN: Incomplete

class RedisQueryTranslator:
    """Translates QueryFilter and FilterClause objects to Redis Search query syntax.

    This class encapsulates all query translation logic.
    """
    def __init__(self, get_filterable_fields: Callable[[], list[dict[str, Any]]]) -> None:
        """Initialize the Redis query translator.

        Args:
            get_filterable_fields (Callable[[], list[dict[str, Any]]]): Callable that returns
                the current filterable_fields configuration. This allows lazy loading of
                filterable_fields when they become available.
        """
    def translate(self, filters: QueryFilter | None) -> str | None:
        """Translate a structured QueryFilter into a Redis Search query string.

        This is the main entry point for query translation. It handles None filters
        and delegates to internal translation methods.

        Args:
            filters (QueryFilter | None): Structured QueryFilter to translate. Defaults to None.

        Returns:
            str | None: A Redis Search query string or None if no filters are provided.

        Raises:
            ValueError: When the filter structure is invalid or operator is incompatible with field type.
        """
