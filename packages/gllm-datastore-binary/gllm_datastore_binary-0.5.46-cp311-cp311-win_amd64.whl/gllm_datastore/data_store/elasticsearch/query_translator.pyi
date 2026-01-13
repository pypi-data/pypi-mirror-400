from gllm_datastore.data_store._elastic_core.query_translator import ElasticLikeQueryTranslator as ElasticLikeQueryTranslator

class ElasticsearchQueryTranslator(ElasticLikeQueryTranslator):
    """Translates QueryFilter and FilterClause objects to Elasticsearch Query DSL.

    This class extends ElasticLikeQueryTranslator and implements abstract methods
    using Elasticsearch DSL API. It also provides QueryOptions handling
    methods specific to Elasticsearch.

    Attributes:
        _logger (Logger): Logger instance for error messages and debugging.
    """
    def __init__(self) -> None:
        """Initialize the Elasticsearch query translator.

        Raises:
            ImportError: If elasticsearch package is not installed.
        """
