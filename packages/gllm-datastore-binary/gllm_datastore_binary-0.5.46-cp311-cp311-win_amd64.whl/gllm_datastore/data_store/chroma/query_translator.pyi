from dataclasses import dataclass
from gllm_datastore.constants import CHUNK_KEYS as CHUNK_KEYS
from gllm_datastore.core.filters.schema import FilterClause as FilterClause, FilterCondition as FilterCondition, FilterOperator as FilterOperator, QueryFilter as QueryFilter
from gllm_datastore.data_store.chroma.query import ChromaCollectionKeys as ChromaCollectionKeys, ChromaOperatorMapper as ChromaOperatorMapper, ChromaOperators as ChromaOperators, ChromaQueryComponents as ChromaQueryComponents

@dataclass
class FilterSeparationResult:
    """Intermediate result from separating special filters (id, content) from metadata filters.

    Attributes:
        id_values (list[str] | None): Extracted ID values, or None if no ID filters found.
        document_filters (list[FilterClause | QueryFilter]): List of content FilterClauses or
            QueryFilters for where_document. QueryFilters are used to represent NOT conditions.
        metadata_filters (list[FilterClause | QueryFilter]): Metadata filters for where clause.
        condition (FilterCondition): The original FilterCondition from the QueryFilter.
    """
    id_values: list[str] | None
    document_filters: list[FilterClause | QueryFilter]
    metadata_filters: list[FilterClause | QueryFilter]
    condition: FilterCondition

class ChromaQueryTranslator:
    """Translates QueryFilter and FilterClause objects to ChromaDB native filter syntax.

    This class encapsulates all query translation logic for ChromaDB, converting
    structured FilterClause and QueryFilter objects into ChromaDB's where, where_document,
    and ids parameters.
    """
    def translate(self, filters: QueryFilter | None = None) -> ChromaQueryComponents:
        """Translate QueryFilter to ChromaDB query components.

        This is the main entry point for query translation. It handles None filters
        and orchestrates filter separation and translation.

        Args:
            filters (QueryFilter | None, optional): Structured QueryFilter to translate. Defaults to None.

        Returns:
            ChromaQueryComponents: ChromaDB query components containing where,
                where_document, and id_values, or None if no filters are provided.
        """
