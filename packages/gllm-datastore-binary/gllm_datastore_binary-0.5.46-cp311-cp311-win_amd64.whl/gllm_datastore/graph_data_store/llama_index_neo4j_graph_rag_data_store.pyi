from _typeshed import Incomplete
from gllm_datastore.graph_data_store.llama_index_graph_rag_data_store import LlamaIndexGraphRAGDataStore as LlamaIndexGraphRAGDataStore
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker
from llama_index.graph_stores.neo4j import Neo4jPropertyGraphStore
from typing import Any

class LlamaIndexNeo4jGraphRAGDataStore(LlamaIndexGraphRAGDataStore, Neo4jPropertyGraphStore):
    '''Graph RAG data store for Neo4j.

    This class extends the Neo4jPropertyGraphStore class from LlamaIndex.
    This class provides an interface for graph-based Retrieval-Augmented Generation (RAG)
    operations on Neo4j graph databases.

    Attributes:
        neo4j_version_tuple (tuple[int, ...]): The Neo4j version tuple.
        lm_invoker (BaseLMInvoker | None): The GLLM language model invoker (inherited from parent).
        em_invoker (BaseEMInvoker | None): The GLLM embedding model invoker (inherited from parent).
        llm (LLM | None): The LlamaIndex LLM instance (converted from lm_invoker, inherited from parent).
        embed_model (BaseEmbedding | None): The LlamaIndex embedding instance
            (converted from em_invoker, inherited from parent).

    Example:
        ```python
        # Option 1: Use with GLLM invokers (recommended)
        from gllm_inference.builder import build_lm_invoker, build_em_invoker

        lm_invoker = build_lm_invoker(model_id="openai/gpt-4o-mini")
        em_invoker = build_em_invoker(model_id="openai/text-embedding-3-small")

        store = LlamaIndexNeo4jGraphRAGDataStore(
            url="bolt://localhost:7687",
            username="neo4j",
            password="password",
            lm_invoker=lm_invoker,  # Optional: Auto-converted to LlamaIndex LLM
            em_invoker=em_invoker,  # Optional: Auto-converted to LlamaIndex Embedding
        )

        # Option 2: Use with LlamaIndex LLM/Embeddings directly
        from llama_index.llms.openai import OpenAI
        from llama_index.embeddings.openai import OpenAIEmbedding

        store = LlamaIndexNeo4jGraphRAGDataStore(
            url="bolt://localhost:7687",
            username="neo4j",
            password="password",
        )

        # Perform RAG query
        results = await store.query("What is the relationship between X and Y?")

        # Delete document data
        await store.delete_by_document_id("doc123")
        ```
    '''
    neo4j_version_tuple: Incomplete
    def __init__(self, url: str, username: str, password: str, lm_invoker: BaseLMInvoker | None = None, em_invoker: BaseEMInvoker | None = None, **kwargs: Any) -> None:
        '''Initialize the LlamaIndexNeo4jGraphRAGDataStore.

        Args:
            url (str): The Neo4j database URL (e.g., "bolt://localhost:7687").
            username (str): The Neo4j database username.
            password (str): The Neo4j database password.
            lm_invoker (BaseLMInvoker | None, optional): GLLM language model invoker.
                If provided, it will be automatically converted to a LlamaIndex LLM instance
                by the parent class. Defaults to None.
            em_invoker (BaseEMInvoker | None, optional): GLLM embedding model invoker.
                If provided, it will be automatically converted to a LlamaIndex BaseEmbedding instance
                by the parent class. Defaults to None.
            **kwargs (Any): Additional keyword arguments passed to Neo4jPropertyGraphStore.
        '''
    async def delete_by_document_id(self, document_id: str, **kwargs: Any) -> None:
        """Delete nodes and edges by document ID.

        Args:
            document_id (str): The document ID.
            **kwargs (Any): Additional keyword arguments.
        """
