from _typeshed import Incomplete
from abc import ABC
from gllm_datastore.graph_data_store.graph_rag_data_store import BaseGraphRAGDataStore as BaseGraphRAGDataStore
from gllm_datastore.graph_data_store.utils import LlamaIndexEMInvokerAdapter as LlamaIndexEMInvokerAdapter, LlamaIndexLMInvokerAdapter as LlamaIndexLMInvokerAdapter
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker
from llama_index.core.base.embeddings.base import BaseEmbedding
from llama_index.core.graph_stores.types import PropertyGraphStore
from llama_index.core.llms import LLM
from typing import Any

class LlamaIndexGraphRAGDataStore(PropertyGraphStore, BaseGraphRAGDataStore, ABC):
    """Abstract base class for a LlamaIndex graph RAG data store.

    This class provides a common interface for LlamaIndex-based graph RAG data stores.
    It handles conversion from GLLM invokers to LlamaIndex LLM and embedding models.

    Attributes:
        lm_invoker (BaseLMInvoker | None): The GLLM language model invoker.
        em_invoker (BaseEMInvoker | None): The GLLM embedding model invoker.
        llm (LLM | None): The LlamaIndex LLM instance (converted from lm_invoker if provided).
        embed_model (BaseEmbedding | None): The LlamaIndex embedding instance (converted from em_invoker if provided).
    """
    lm_invoker: Incomplete
    em_invoker: Incomplete
    llm: LLM | None
    embed_model: BaseEmbedding | None
    def __init__(self, lm_invoker: BaseLMInvoker | None = None, em_invoker: BaseEMInvoker | None = None, **kwargs: Any) -> None:
        """Initialize the LlamaIndexGraphRAGDataStore.

        Args:
            lm_invoker (BaseLMInvoker | None, optional): GLLM language model invoker.
                If provided, it will be automatically converted to a LlamaIndex LLM instance
                using LlamaIndexLMInvokerAdapter. Defaults to None.
            em_invoker (BaseEMInvoker | None, optional): GLLM embedding model invoker.
                If provided, it will be automatically converted to a LlamaIndex BaseEmbedding instance
                using LlamaIndexEMInvokerAdapter. Defaults to None.
            **kwargs (Any): Additional keyword arguments passed to PropertyGraphStore.
        """
    async def query(self, query: str, **kwargs: Any) -> Any:
        """Query the graph RAG data store.

        Args:
            query (str): The query to be executed.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            Any: The result of the query.
        """
