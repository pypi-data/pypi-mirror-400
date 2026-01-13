from typing import Any

def flatten_dict(nested_dict: dict[str, Any], parent_key: str = '', sep: str = '.') -> dict[str, Any]:
    '''Flatten a nested dictionary into a single level dictionary.

    Args:
        nested_dict (dict[str, Any]): The nested dictionary to flatten.
        parent_key (str, optional): The parent key to prepend to the keys in the flattened dictionary.
            Defaults to empty string.
        sep (str, optional): The separator to use between the parent key and the child key. Defaults to ".".

    Returns:
        dict[str, Any]: The flattened dictionary.

    Examples:
        ```python
        nested = {"a": {"b": 1, "c": 2}, "d": 3}
        flattened = flatten_dict(nested)
        # Result: {"a.b": 1, "a.c": 2, "d": 3}
        ```
    '''
