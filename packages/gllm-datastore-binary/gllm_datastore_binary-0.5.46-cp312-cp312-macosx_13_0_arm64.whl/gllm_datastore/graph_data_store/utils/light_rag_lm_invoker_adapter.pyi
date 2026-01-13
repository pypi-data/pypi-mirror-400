from gllm_datastore.graph_data_store.utils.constants import LightRAGConstants as LightRAGConstants, LightRAGKeys as LightRAGKeys
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker
from typing import Any

class LightRAGLMInvokerAdapter:
    """LMInvoker adapter for the LightRAG module.

    This adapter is used to adapt the LMInvoker interface to the LightRAG module.
    It handles the conversion between different prompt formats and manages
    asynchronous invocation in a way that's compatible with nested event loops.
    """
    def __init__(self, lm_invoker: BaseLMInvoker) -> None:
        """Initialize the LightRAGLMInvokerAdapter.

        Args:
            lm_invoker (BaseLMInvoker): The LM invoker to use.
        """
    def __deepcopy__(self, memo: dict) -> LightRAGLMInvokerAdapter:
        """Custom deepcopy implementation to handle non-serializable objects.

        This method is called when copy.deepcopy() is invoked on this object.
        We create a new instance without deep-copying the invoker object
        which may contain non-serializable components.

        Args:
            memo (dict): Memoization dictionary for deepcopy process

        Returns:
            LightRAGLMInvokerAdapter: A new instance with the same invoker reference
        """
    async def __call__(self, prompt: str, system_prompt: str | None = None, history_messages: list[dict[str, Any]] | None = None, **kwargs: Any) -> str:
        """Make the adapter callable for compatibility with LightRAG.

        Args:
            prompt (str): The prompt to invoke the LM invoker with.
            system_prompt (str | None, optional): The system prompt to format in string format. Defaults to None.
            history_messages (list[dict[str, Any]] | None, optional): The history messages to format in OpenAI format.
                Defaults to None.
            **kwargs (Any): Additional keyword arguments for the LM invoker.

        Returns:
            str: The response from the LM invoker.
        """
