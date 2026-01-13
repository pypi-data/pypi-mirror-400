from _typeshed import Incomplete
from contextlib import contextmanager
from gllm_datastore.graph_data_store.light_rag_data_store import BaseLightRAGDataStore as BaseLightRAGDataStore
from gllm_datastore.graph_data_store.utils.constants import LightRAGPostgresStorageConstants as LightRAGPostgresStorageConstants
from gllm_datastore.graph_data_store.utils.light_rag_em_invoker_adapter import LightRAGEMInvokerAdapter as LightRAGEMInvokerAdapter
from gllm_datastore.graph_data_store.utils.light_rag_lm_invoker_adapter import LightRAGLMInvokerAdapter as LightRAGLMInvokerAdapter
from gllm_inference.em_invoker.em_invoker import BaseEMInvoker
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker
from lightrag import LightRAG
from pydantic import BaseModel
from typing import Any, Generator

class PostgresDBConfig(BaseModel):
    """Pydantic model containing PostgreSQL configuration parameters."""
    host: str
    port: int
    user: str
    password: str
    database: str
    workspace: str

@contextmanager
def postgres_config_context(config: PostgresDBConfig) -> Generator[None, None, None]:
    """Context manager to temporarily set postgres config.

    This context manager is used to temporarily set the environment variables
    for PostgreSQL configuration. It is used to set the environment variables
    for the duration of the context manager's block as it is required by LightRAG.

    Args:
        config (PostgresDBConfig): Pydantic model containing PostgreSQL configuration parameters.

    Returns:
        Generator[None, None, None]: Generator object that can be used in a context manager.
    """

class LightRAGPostgresDataStore(BaseLightRAGDataStore):
    '''Data store implementation for LightRAG-based graph RAG using PostgreSQL.

    This class extends the LightRAGDataStore to use PostgreSQL as the graph database,
    key-value store, and vector database.

    To use this data store, please ensure that you have a PostgreSQL with AGE and PGVector extensions installed.
    You can use the following docker run command to start a PostgreSQL container with AGE and PGVector extensions:

    ```bash
    docker run         -p 5455:5432         -d         --name postgres-LightRag         shangor/postgres-for-rag:v1.0         sh -c "service postgresql start && sleep infinity"
    ```

    Example:
        ```python
        from gllm_inference.em_invoker import OpenAIEMInvoker
        from gllm_inference.lm_invoker import OpenAILMInvoker
        from gllm_datastore.graph_data_store.light_rag_postgres_data_store import LightRAGPostgresDataStore

        # Create the indexer
        data_store = await LightRAGPostgresDataStore(
            lm_invoker=OpenAILMInvoker(model_name="gpt-4o-mini"),
            em_invoker=OpenAIEMInvoker(model_name="text-embedding-3-small"),
            postgres_db_user="rag",
            postgres_db_password="rag",
            postgres_db_name="rag",
            postgres_db_host="localhost",
            postgres_db_port=5455,
        )

        # Retrieve using LightRAG instance
        await data_store.query("What is AI?")
        ```

    Attributes:
        instance (LightRAG): The LightRAG instance used for indexing and querying.
        lm_invoker_adapter (LightRAGLMInvokerAdapter): The adapter for the LM invoker.
        em_invoker_adapter (LightRAGEMInvokerAdapter): The adapter for the EM invoker.
        postgres_config (PostgresDBConfig): Pydantic model containing PostgreSQL configuration parameters.
    '''
    lm_invoker_adapter: Incomplete
    em_invoker_adapter: Incomplete
    postgres_config: Incomplete
    def __init__(self, lm_invoker: BaseLMInvoker, em_invoker: BaseEMInvoker, postgres_db_host: str = 'localhost', postgres_db_port: int = 5432, postgres_db_user: str = 'postgres', postgres_db_password: str = 'password', postgres_db_name: str = 'postgres', postgres_db_workspace: str = 'default', use_cache: bool = False, lm_invoke_kwargs: dict[str, Any] | None = None, instance: LightRAG | None = None, **kwargs: Any) -> None:
        '''Initialize the LightRAGPostgresIndexer.

        Args:
            lm_invoker (BaseLMInvoker): The LM invoker to use.
            em_invoker (BaseEMInvoker): The EM invoker to use.
            postgres_db_host (str, optional): The host for the PostgreSQL database. Defaults to "localhost".
            postgres_db_port (int, optional): The port for the PostgreSQL database. Defaults to 5432.
            postgres_db_user (str, optional): The user for the PostgreSQL database. Defaults to "postgres".
            postgres_db_password (str, optional): The password for the PostgreSQL database. Defaults to "password".
            postgres_db_name (str, optional): The name for the PostgreSQL database. Defaults to "postgres".
            postgres_db_workspace (str, optional): The workspace for the PostgreSQL database. Defaults to "default".
            use_cache (bool, optional): Whether to enable caching for the LightRAG instance. Defaults to False.
            lm_invoke_kwargs (dict[str, Any] | None, optional): Keyword arguments for the LM invoker. Defaults to None.
            instance (LightRAG | None, optional): A configured LightRAG instance to use. Defaults to None.
            **kwargs (Any): Additional keyword arguments.
        '''
