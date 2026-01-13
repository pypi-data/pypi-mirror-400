from _typeshed import Incomplete
from gllm_datastore.graph_data_store.utils.constants import LightRAGConstants as LightRAGConstants
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from lightrag.base import EmbeddingFunc

class LightRAGEMInvokerAdapter(EmbeddingFunc):
    """Adapter for embedding model invokers to work with LightRAG.

    This adapter wraps BaseEMInvoker instances to make them compatible
    with LightRAG's expected interface.

    Attributes:
        _em_invoker (BaseEMInvoker): The EM invoker to use.
        func (callable): The embedding function.
        embedding_dim (int): The embedding dimension. Defaults to 0.
    """
    func: Incomplete
    embedding_dim: int
    def __init__(self, em_invoker: BaseEMInvoker) -> None:
        """Initialize the LightRAGEMInvokerAdapter.

        Args:
            em_invoker (BaseEMInvoker): The EM invoker to use.
        """
    async def ensure_initialized(self) -> None:
        """Ensure that the adapter is initialized.

        This asynchronous method ensures that the embedding dimension is determined.
        If the embedding dimension is 0, it will determine the dimension by calling
        the embedding invoker with a test input. Raises an error if initialization fails.

        Raises:
            RuntimeError: If embedding dimension cannot be determined after initialization.
        """
    def __deepcopy__(self, memo: dict) -> LightRAGEMInvokerAdapter:
        """Custom deepcopy implementation to handle non-serializable objects.

        This method is called when copy.deepcopy() is invoked on this object.
        We create a new instance without deep-copying the invoker object
        which may contain non-serializable components.

        Args:
            memo (dict): Memoization dictionary for deepcopy process

        Returns:
            LightRAGEMInvokerAdapter: A new instance with the same invoker reference
        """
    async def __call__(self, input: str | list[str]) -> list[list[float]]:
        """Make the adapter callable for compatibility with LightRAG.

        Args:
            input (str | list[str]): The input text or list of texts to embed.

        Returns:
            list[list[float]]: The embeddings for the input texts.
        """
