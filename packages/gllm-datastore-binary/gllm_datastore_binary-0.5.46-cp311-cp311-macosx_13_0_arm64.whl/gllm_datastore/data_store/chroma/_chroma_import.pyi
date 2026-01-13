import chromadb

def safe_import_chromadb() -> chromadb:
    """Import and return the `chromadb` module with SQLite fallback.

    This function centralizes the logic to import `chromadb`, applying the
    `pysqlite3` fallback for environments where the built-in sqlite3 causes
    issues. Other modules should use `safe_import_chromadb()` to
    avoid duplication.

    Returns:
        ModuleType: The imported `chromadb` module.
    """
