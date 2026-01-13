from gllm_datastore.data_store._elastic_core.query_translator import ElasticLikeQueryTranslator as ElasticLikeQueryTranslator

class OpenSearchQueryTranslator(ElasticLikeQueryTranslator):
    """Translates QueryFilter and FilterClause objects to OpenSearch Query DSL.

    This class extends ElasticLikeQueryTranslator and implements abstract methods
    using OpenSearch DSL API (Q function). It also provides QueryOptions handling
    methods specific to OpenSearch.

    Attributes:
        _logger (Logger): Logger instance for error messages and debugging.
    """
    def __init__(self) -> None:
        """Initialize the OpenSearch query translator.

        Raises:
            ImportError: If opensearchpy package is not installed.
        """
