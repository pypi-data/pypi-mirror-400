from _typeshed import Incomplete
from typing import Any

logger: Incomplete

def generate_cache_key(input_: str, key_prefix: str = '') -> str:
    '''Generate a cache key from the input string.

    This function generates a cache key from the input string.
    If the input is a valid file, the function will hash the file.
    If the input is not a valid file, the function will hash the input string.

    Args:
        input_ (str): The input string to generate the cache key from.
        key_prefix (str, optional): The prefix of the cache key. Defaults to "".

    Returns:
        str: The generated cache key.

    Raises:
        Exception: If the input file path exists but cannot be read.
    '''
def generate_key_from_func(func_name: str, *args: Any, **kwargs: Any) -> str:
    """Generate a cache key based on function name and arguments.

    The key is created by hashing the function name, positional arguments, and keyword arguments.
    If the function name, positional arguments, or keyword arguments are modified, the cache key will change.

    Args:
        func_name (str): Name of the function being cached
        *args (Any): Positional arguments passed to the function
        **kwargs (Any): Keyword arguments passed to the function

    Returns:
        str: SHA-256 hash digest to be used as cache key
    """
