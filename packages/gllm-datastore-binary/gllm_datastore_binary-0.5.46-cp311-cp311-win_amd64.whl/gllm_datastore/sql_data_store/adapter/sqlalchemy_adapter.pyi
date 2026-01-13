from _typeshed import Incomplete
from sqlalchemy.engine import Engine
from typing import Any

class SQLAlchemyAdapter:
    """Initializes a database engine and session using SQLAlchemy.

    Provides a scoped session and a base query property for interacting with the database.

    Attributes:
        engine (Engine): The SQLAlchemy engine object.
        db (Session): The SQLAlchemy session object.
        base (DeclarativeMeta): The SQLAlchemy declarative base object.
    """
    engine: Incomplete
    db: Incomplete
    base: Incomplete
    @classmethod
    def initialize(cls, engine_or_url: Engine | str, pool_size: int = 10, max_overflow: int = 10, autocommit: bool = False, autoflush: bool = True, **kwargs: Any):
        """Creates a new database engine and session.

        Must provide either an engine or a database URL.
        If a database URL is provided, the engine will be created with the specified configurations:
            1. For SQLite, only the pool size can be specified, since the engine will use SingletonThreadPool which
                doesn't support max_overflow.
            2. For other databases, the pool size and max overflow can be specified.

        Args:
            engine_or_url (Engine | str): Sqlalchemy engine object or database URL.
            pool_size (int, optional): The size of the database connections to be maintained. Defaults to 10.
            max_overflow (int, optional): The maximum overflow size of the pool. Defaults to 10.
                If the engine_or_url is a SQLite URL, this parameter is ignored.
            autocommit (bool, optional): If True, all changes to the database are committed immediately.
                Defaults to False.
            autoflush (bool, optional): If True, all changes to the database are flushed immediately. Defaults to True.
            **kwargs (Any): Additional keyword arguments to be passed to the SQLAlchemy create_engine function.
                These are only used when engine_or_url is a string URL.
        """
