import logging
from chromadb.types import Where, WhereDocument
from dataclasses import dataclass
from enum import StrEnum
from gllm_datastore.core.filters.schema import FilterOperator as FilterOperator, QueryFilter as QueryFilter
from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator as ChromaQueryTranslator
from typing import Any

DEFAULT_NUM_CANDIDATES: int

class ChromaCollectionKeys:
    """Constants for ChromaDB collection method keyword arguments.

    This class provides constants for all string literals used in ChromaDB
    collection method calls (get, delete, query, etc.) to avoid magic strings
    and improve maintainability.

    Attributes:
        WHERE (str): Keyword for metadata filtering condition.
        WHERE_DOCUMENT (str): Keyword for document content filtering condition.
        IDS (str): Keyword for filtering by document IDs.
        INCLUDE (str): Keyword for specifying fields to include in results.
        LIMIT (str): Keyword for limiting the number of results.
        METADATA_PREFIX (str): Prefix for metadata field keys.
    """
    WHERE: str
    WHERE_DOCUMENT: str
    IDS: str
    INCLUDE: str
    LIMIT: str
    METADATA_PREFIX: str

class ChromaOperators(StrEnum):
    """Constants for ChromaDB query operators.

    This class provides constants for all operator string literals used in
    ChromaDB query expressions to avoid magic strings and improve maintainability.

    Attributes:
        AND (str): Logical AND operator for combining filters.
        OR (str): Logical OR operator for combining filters.
        NE (str): Not equal comparison operator.
        GT (str): Greater than comparison operator.
        LT (str): Less than comparison operator.
        GTE (str): Greater than or equal comparison operator.
        LTE (str): Less than or equal comparison operator.
        IN (str): Array membership operator (value in list).
        NIN (str): Array non-membership operator (value not in list).
        TEXT_CONTAINS (str): Document content substring match operator.
        NOT_CONTAINS (str): Document content substring exclusion operator.
    """
    AND: str
    OR: str
    NE: str
    GT: str
    LT: str
    GTE: str
    LTE: str
    IN: str
    NIN: str
    TEXT_CONTAINS: str
    NOT_CONTAINS: str

class ChromaOperatorMapper:
    """Maps FilterOperator to ChromaDB operators and provides inverse operator mappings.

    This class encapsulates operator translation logic.

    Attributes:
        OPERATOR_TO_CHROMA (dict[FilterOperator, str]): Mapping from FilterOperator to ChromaDB operators.
        OPERATOR_INVERSE (dict[FilterOperator, FilterOperator]): Mapping from FilterOperator to its inverse operator.
    """
    OPERATOR_TO_CHROMA: dict[FilterOperator, str]
    OPERATOR_INVERSE: dict[FilterOperator, FilterOperator]
    @classmethod
    def get_inverse_operator(cls, operator: FilterOperator) -> FilterOperator | None:
        """Get the inverse operator for a given FilterOperator.

        Args:
            operator (FilterOperator): The operator to get the inverse for.

        Returns:
            FilterOperator | None: The inverse operator, or None if no inverse exists.
        """
    @classmethod
    def has_inverse(cls, operator: FilterOperator) -> bool:
        """Check if an operator has an inverse mapping.

        Args:
            operator (FilterOperator): The operator to check.

        Returns:
            bool: True if the operator has an inverse, False otherwise.
        """

@dataclass
class ChromaQueryComponents:
    """ChromaDB query components extracted from a QueryFilter.

    Attributes:
        where_condition (Where | None): Where clause for metadata filters, or None.
        where_document (WhereDocument | None): WhereDocument clause for content filters, or None.
        id_values (list[str] | None): List of IDs for id filters, or None.
    """
    where_condition: Where | None
    where_document: WhereDocument | None
    id_values: list[str] | None
    def to_dict(self) -> dict[str, Any] | None:
        """Convert to ChromaDB kwargs dict, omitting None values.

        Returns:
            dict[str, Any] | None: Dictionary with non-None components,
                or None if all components are None/empty.
        """

def sanitize_metadata(metadata: dict[str, Any] | None, logger: logging.Logger) -> dict[str, Any]:
    '''Sanitize metadata by removing list values that ChromaDB doesn\'t support.

    ChromaDB only supports str, int, float, or bool as metadata values.
    This function filters out list values and logs warnings for each removed key.

    Examples:
        1. Remove list values:
            ```python
            logger = logging.getLogger(__name__)
            input_meta = {"status": "active", "tags": ["a", "b"], "age": 30}
            out = sanitize_metadata(input_meta, logger)
            # out -> {"status": "active", "age": 30}
            ```

        2. Handle None input:
            ```python
            out = sanitize_metadata(None, logging.getLogger(__name__))
            # out -> {}
            ```

    Args:
        metadata (dict[str, Any] | None): Metadata dictionary to sanitize.
        logger (logging.Logger): Logger instance for warning messages.

    Returns:
        dict[str, Any]: Sanitized metadata with list values removed.
    '''
def build_chroma_get_kwargs(filters: QueryFilter | None, query_translator: ChromaQueryTranslator, include: list[str] | None = None, limit: int | None = None, **additional_kwargs: Any) -> dict[str, Any]:
    '''Build kwargs dictionary for ChromaDB collection.get() operations.

    This function processes filters and builds a kwargs dictionary that includes
    where, where_document, ids, include, and limit parameters as needed.

    Examples:
        1. Build kwargs with metadata and content filters:
            ```python
            from gllm_datastore.core.filters import filter as F
            from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator

            translator = ChromaQueryTranslator()
            filters = F.and_(
                F.eq("metadata.status", "active"),
                F.text_contains("content", "python"),
            )

            out = build_chroma_get_kwargs(filters, translator, include=["documents"], limit=10)
            # out ->
            # {
            #   "where": {"status": "active"},
            #   "where_document": {"$contains": "python"},
            #   "include": ["documents"],
            #   "limit": 10
            # }
            ```

        2. Build kwargs using id filters:
            ```python
            from gllm_datastore.core.filters import filter as F
            from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator

            translator = ChromaQueryTranslator()
            filters = F.or_(F.eq("id", "123"), F.in_("id", ["a", "b"]))
            out = build_chroma_get_kwargs(filters, translator)
            # out -> {"ids": ["123", "a", "b"]}
            ```

    Args:
        filters (QueryFilter | None): QueryFilter to process.
        query_translator (ChromaQueryTranslator): Query translator instance to use.
        include (list[str] | None, optional): List of fields to include in results.
            Defaults to None.
        limit (int | None, optional): Maximum number of results to return.
            Defaults to None.
        **additional_kwargs: Additional kwargs to include in the result.

    Returns:
        dict[str, Any]: Dictionary of kwargs ready for ChromaDB collection.get() call.
    '''
def build_chroma_delete_kwargs(filters: QueryFilter | None, query_translator: ChromaQueryTranslator, **additional_kwargs: Any) -> dict[str, Any]:
    '''Build kwargs dictionary for ChromaDB collection.delete() operations.

    This function processes filters and builds a kwargs dictionary that includes
    where, where_document, and ids parameters as needed.

    Examples:
        1. Delete by ids or where:
            ```python
            from gllm_datastore.core.filters import filter as F
            from gllm_datastore.data_store.chroma.query_translator import ChromaQueryTranslator

            translator = ChromaQueryTranslator()
            filters = F.and_(
                F.in_("id", ["x1", "x2"]),
                F.eq("metadata.status", "inactive"),
            )
            out = build_chroma_delete_kwargs(filters, translator)
            # out ->
            # {
            #   "ids": ["x1", "x2"],
            #   "where": {"status": "inactive"}
            # }
            ```

    Args:
        filters (QueryFilter | None): QueryFilter to process.
        query_translator (ChromaQueryTranslator): Query translator instance to use.
        **additional_kwargs: Additional kwargs to include in the result.

    Returns:
        dict[str, Any]: Dictionary of kwargs ready for ChromaDB collection.delete() call.
    '''
def extract_chroma_query_components(filters: QueryFilter | None) -> ChromaQueryComponents:
    '''Prepare all ChromaDB query parameters from a QueryFilter.

    This function processes a QueryFilter and extracts:
    1. Metadata filters -> Where clause
    2. Content filters -> WhereDocument clause
    3. id filters -> ids parameter

    Only operators natively supported by ChromaDB are allowed:
    1. id: EQ, IN (using ids parameter)
    2. content: TEXT_CONTAINS (substring match in document content, maps to $contains)
    3. metadata: EQ, NE, GT, LT, GTE, LTE, IN, NIN (using where clause)
    4. metadata: ARRAY_CONTAINS (array membership, not supported by ChromaDB - raises NotImplementedError)

    Examples:
        1. Extract all components from a mixed filter:
            ```python
            from gllm_datastore.core.filters import filter as F

            filters = F.and_(
                F.eq("metadata.status", "active"),
                F.text_contains("content", "python"),
                F.in_("id", ["a", "b"]),
            )
            components = extract_chroma_query_components(filters)
            # components.where_condition -> dict
            # components.where_document -> dict
            # components.id_values -> ["a", "b"]
            ```

    Args:
        filters (QueryFilter | None): QueryFilter to process.

    Returns:
        ChromaQueryComponents: Dataclass containing where_condition, where_document, and id_values.

    Raises:
        NotImplementedError: If unsupported operators are used for id or content filters.
    '''
