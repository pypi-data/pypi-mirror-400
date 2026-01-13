from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from llama_index.core.base.embeddings.base import BaseEmbedding
from typing import Any

class LlamaIndexEMInvokerAdapter(BaseEmbedding):
    """Minimal EMInvoker adapter for the LlamaIndex BaseEmbedding interface.

    This adapter wraps a BaseEMInvoker instance to provide compatibility with
    LlamaIndex's BaseEmbedding interface. Embeddings from the underlying invoker
    are returned directly without any conversion, assuming they are already in
    the correct format (list of floats).

    The adapter provides both synchronous and asynchronous methods for:
    - Query embeddings: Single text embedding for search queries
    - Text embeddings: Single or batch text embedding for documents

    Attributes:
        em_invoker (BaseEMInvoker): The underlying EM invoker instance.
        model_name (str): The name of the embedding model (inherited from invoker).
        embed_batch_size (int): The batch size for batch embedding operations.

    Note:
        Sync methods (_get_*) use asyncio.run internally to call async methods.
        The implementation uses nest_asyncio to handle nested event loops if needed.
    """
    em_invoker: BaseEMInvoker
    def __init__(self, em_invoker: BaseEMInvoker, embed_batch_size: int = ..., **kwargs: Any) -> None:
        """Initialize the LlamaIndexEMInvokerAdapter.

        Args:
            em_invoker (BaseEMInvoker): The EM invoker to wrap.
            embed_batch_size (int, optional): The batch size for embedding operations.
                Defaults to DEFAULT_EMBED_BATCH_SIZE from LlamaIndex.
            **kwargs (Any): Additional keyword arguments passed to BaseEmbedding (e.g.,
                callback_manager).
        """
    @classmethod
    def class_name(cls) -> str:
        '''Get the class name (implements BaseEmbedding.class_name).

        This is used by LlamaIndex for serialization and debugging.

        Returns:
            str: The class name "LlamaIndexEMInvokerAdapter".
        '''
