from _typeshed import Incomplete
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker
from llama_index.core.base.llms.types import ChatMessage, ChatResponse, CompletionResponse, LLMMetadata
from llama_index.core.llms import LLM
from typing import Any, AsyncGenerator, Sequence

ROLE_MAPPING: Incomplete

class LlamaIndexLMInvokerAdapter(LLM):
    """Minimal LMInvoker adapter for the LlamaIndex LLM interface.

    This adapter wraps a BaseLMInvoker instance to provide compatibility with
    LlamaIndex's LLM interface. It handles conversion between GLLM message formats
    and LlamaIndex ChatMessage formats.

    Only chat functionality is implemented. Completion and streaming methods raise
    NotImplementedError to keep the implementation minimal.

    Attributes:
        lm_invoker (BaseLMInvoker): The underlying LM invoker instance.

    Note:
        Message roles are converted using the ROLE_MAPPING constant, which maps
        all LlamaIndex message roles (SYSTEM, DEVELOPER, USER, ASSISTANT, TOOL,
        FUNCTION, CHATBOT, MODEL) to GLLM MessageRole values.
    """
    lm_invoker: BaseLMInvoker
    def __init__(self, lm_invoker: BaseLMInvoker, **kwargs: Any) -> None:
        """Initialize the LlamaIndexLMInvokerAdapter.

        Args:
            lm_invoker (BaseLMInvoker): The LM invoker to wrap.
            **kwargs (Any): Additional keyword arguments.
        """
    @property
    def metadata(self) -> LLMMetadata:
        """Get metadata about the language model.

        Returns:
            LLMMetadata: Metadata containing model information.
        """
    def chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        """Synchronous chat endpoint (implements LlamaIndex LLM.chat).

        This is a synchronous wrapper around the async achat() method.
        It handles both scenarios: when called from within an event loop and when
        called from synchronous code.

        Converts LlamaIndex ChatMessage objects to GLLM Message format, invokes
        the underlying LM invoker, and converts the response back to ChatResponse.

        Args:
            messages (Sequence[ChatMessage]): The chat messages in LlamaIndex format.
            **kwargs (Any): Additional keyword arguments. Supports:
                - hyperparameters (dict, optional): Model hyperparameters like
                  temperature, max_tokens, etc.

        Returns:
            ChatResponse: The chat response in LlamaIndex format with message content,
                role, and optional metadata (token usage, finish details).
        """
    def complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        """Synchronous completion endpoint.

        Args:
            prompt (str): The prompt string.
            formatted (bool, optional): Whether the prompt is already formatted. Defaults to False.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            CompletionResponse: The completion response.

        Raises:
            NotImplementedError: Always raises this exception.
        """
    def stream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> AsyncGenerator[ChatResponse, None]:
        """Streaming chat endpoint.

        Args:
            messages (Sequence[ChatMessage]): The chat messages.
            **kwargs (Any): Additional keyword arguments.

        Yields:
            ChatResponse: Streaming chat responses.

        Raises:
            NotImplementedError: Always raises this exception.
        """
    def stream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> AsyncGenerator[CompletionResponse, None]:
        """Streaming completion endpoint.

        Args:
            prompt (str): The prompt string.
            formatted (bool, optional): Whether the prompt is already formatted. Defaults to False.
            **kwargs (Any): Additional keyword arguments.

        Yields:
            CompletionResponse: Streaming completion responses.

        Raises:
            NotImplementedError: Always raises this exception.
        """
    async def achat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> ChatResponse:
        """Asynchronous chat endpoint (implements LlamaIndex LLM.achat).

        Converts LlamaIndex ChatMessage objects to GLLM Message format, invokes
        the underlying LM invoker asynchronously, and converts the response back
        to ChatResponse.

        Args:
            messages (Sequence[ChatMessage]): The chat messages in LlamaIndex format.
            **kwargs (Any): Additional keyword arguments. Supports:
                - hyperparameters (dict, optional): Model hyperparameters like
                  temperature, max_tokens, etc.

        Returns:
            ChatResponse: The chat response in LlamaIndex format with message content,
                role, and optional metadata (token usage, finish details).
        """
    async def acomplete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> CompletionResponse:
        """Asynchronous completion endpoint.

        Args:
            prompt (str): The prompt string.
            formatted (bool, optional): Whether the prompt is already formatted. Defaults to False.
            **kwargs (Any): Additional keyword arguments.

        Returns:
            CompletionResponse: The completion response.

        Raises:
            NotImplementedError: Always raises this exception.
        """
    def astream_chat(self, messages: Sequence[ChatMessage], **kwargs: Any) -> AsyncGenerator[ChatResponse, None]:
        """Asynchronous streaming chat endpoint.

        Args:
            messages (Sequence[ChatMessage]): The chat messages.
            **kwargs (Any): Additional keyword arguments.

        Yields:
            ChatResponse: Streaming chat responses.

        Raises:
            NotImplementedError: Always raises this exception.
        """
    def astream_complete(self, prompt: str, formatted: bool = False, **kwargs: Any) -> AsyncGenerator[CompletionResponse, None]:
        """Asynchronous streaming completion endpoint.

        Args:
            prompt (str): The prompt string.
            formatted (bool, optional): Whether the prompt is already formatted. Defaults to False.
            **kwargs (Any): Additional keyword arguments.

        Yields:
            CompletionResponse: Streaming completion responses.

        Raises:
            NotImplementedError: Always raises this exception.
        """
    @classmethod
    def class_name(cls) -> str:
        '''Get the class name (implements LLM.class_name).

        This is used by LlamaIndex for serialization and debugging.

        Returns:
            str: The class name "LlamaIndexLMInvokerAdapter".
        '''
