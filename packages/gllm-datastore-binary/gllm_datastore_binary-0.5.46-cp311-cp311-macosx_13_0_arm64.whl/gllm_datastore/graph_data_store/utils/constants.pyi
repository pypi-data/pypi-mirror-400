class LightRAGKeys:
    """Keys used in LightRAG indexer."""
    ENTITY_TYPE: str
    ENTITY_ID: str
    SOURCE_ID: str
    ROLE: str
    CONTENT: str

class LightRAGConstants:
    """Constants used in LightRAG indexer."""
    CHUNK_TYPE: str
    DEVELOPER_ROLE: str
    EMBEDDING_PAYLOAD_TEST: str
    FILE_TYPE: str

class LightRAGPostgresStorageConstants:
    """Constants used in LightRAG indexer with PostgreSQL storage."""
    DOC_STATUS_STORAGE: str
    GRAPH_STORAGE: str
    KV_STORAGE: str
    VECTOR_STORAGE: str
