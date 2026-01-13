from gllm_datastore.core.filters.schema import FilterClause as FilterClause, FilterCondition as FilterCondition, FilterOperator as FilterOperator, QueryFilter as QueryFilter
from typing import Any

def eq(key: str, value: Any) -> FilterClause:
    '''Create an equality filter.

    This operator checks if the field value is exactly equal to the specified value.
    Works with strings, numbers, booleans, and other scalar types.

    Example:
        Filter for documents where `metadata.status == active`.
        ```python
        from gllm_datastore.core.filters import eq

        filter = eq("metadata.status", "active")
        ```

    Args:
        key (str): Field path to filter on.
        value (Any): Value to compare. Matches field values exactly equal to this value.

    Returns:
        FilterClause: Equality filter.
    '''
def ne(key: str, value: Any) -> FilterClause:
    '''Create a not-equal filter.

    This operator checks if the field value is not equal to the specified value.
    Works with strings, numbers, booleans, and other scalar types.

    Example:
        Filter for documents where `metadata.status != active`.
        ```python
        from gllm_datastore.core.filters import ne

        filter = ne("metadata.status", "active")
        ```

    Args:
        key (str): Field path to filter on.
        value (Any): Value to exclude. Matches all values except this one.

    Returns:
        FilterClause: Not-equal filter.
    '''
def gt(key: str, value: int | float) -> FilterClause:
    '''Create a greater-than filter.

    This operator checks if the field value is strictly greater than the specified value.
    Only works with numeric fields (int or float).

    Example:
        Filter for documents where `metadata.price > 100`.
        ```python
        from gllm_datastore.core.filters import gt

        filter = gt("metadata.price", 100)
        ```

    Args:
        key (str): Field path to filter on (must be numeric).
        value (int | float): Threshold value. Matches field values greater than this.

    Returns:
        FilterClause: Greater-than filter.
    '''
def lt(key: str, value: int | float) -> FilterClause:
    '''Create a less-than filter.

    This operator checks if the field value is strictly less than the specified value.
    Only works with numeric fields (int or float).

    Example:
        Filter for documents where `metadata.price < 100`.
        ```python
        from gllm_datastore.core.filters import lt

        filter = lt("metadata.price", 100)
        ```

    Args:
        key (str): Field path to filter on (must be numeric).
        value (int | float): Threshold value. Matches field values less than this.

    Returns:
        FilterClause: Less-than filter.
    '''
def gte(key: str, value: int | float) -> FilterClause:
    '''Create a greater-than-or-equal filter.

    This operator checks if the field value is greater than or equal to the specified value.
    Only works with numeric fields (int or float).

    Example:
        Filter for documents where `metadata.price >= 100`.
        ```python
        from gllm_datastore.core.filters import gte

        filter = gte("metadata.price", 100)
        ```

    Args:
        key (str): Field path to filter on (must be numeric).
        value (int | float): Threshold value. Matches field values greater than or equal to this.

    Returns:
        FilterClause: Greater-than-or-equal filter.
    '''
def lte(key: str, value: int | float) -> FilterClause:
    '''Create a less-than-or-equal filter.

    This operator checks if the field value is less than or equal to the specified value.
    Only works with numeric fields (int or float).

    Example:
        Filter for documents where `metadata.price <= 100`.
        ```python
        from gllm_datastore.core.filters import lte

        filter = lte("metadata.price", 100)
        ```

    Args:
        key (str): Field path to filter on (must be numeric).
        value (int | float): Threshold value. Matches field values less than or equal to this.

    Returns:
        FilterClause: Less-than-or-equal filter.
    '''
def in_(key: str, values: list) -> FilterClause:
    '''Create an IN filter.

    This operator checks if the field value is one of the values in the provided list.
    Works with scalar fields (string, number, boolean). The field value must exactly
    match one of the values in the list.

    Example:
        Filter for documents where `metadata.status in ["active", "pending"]`.
        ```python
        from gllm_datastore.core.filters import in_

        filter = in_("metadata.status", ["active", "pending"])
        ```

    Args:
        key (str): Field path to filter on (must be a scalar field).
        values (list): List of possible values. Matches field values that match one of these exactly.

    Returns:
        FilterClause: IN filter.
    '''
def nin(key: str, values: list) -> FilterClause:
    '''Create a NOT IN filter.

    This operator checks if the field value is not in the provided list.
    Works with scalar fields (string, number, boolean). The field value must not
    match any of the values in the list.

    Example:
        Filter for documents where `metadata.status not in ["deleted", "archived"]`.
        ```python
        from gllm_datastore.core.filters import nin

        filter = nin("metadata.status", ["deleted", "archived"])
        ```

    Args:
        key (str): Field path to filter on (must be a scalar field).
        values (list): List of excluded values. Matches field values that do not match any of these.

    Returns:
        FilterClause: NOT IN filter.
    '''
def array_contains(key: str, value: Any) -> FilterClause:
    '''Create an ARRAY_CONTAINS filter (array field contains value).

    This operator checks if an array field contains the specified value as an element.
    The field must be an array/list, and the value must be present in that array.
    Use this for checking array membership.

    Example:
        Filter for documents where the tags array contains "python".
        This will match documents where "python" is an element in metadata.tags.
        For example, if metadata.tags = ["python", "javascript"], this will match.
        ```python
        from gllm_datastore.core.filters import array_contains

        filter = array_contains("metadata.tags", "python")
        ```

    Args:
        key (str): Field path to filter on (must be an array field).
        value (Any): Value to check if it exists as an element in the array.

    Returns:
        FilterClause: ARRAY_CONTAINS filter.
    '''
def text_contains(key: str, value: str) -> FilterClause:
    '''Create a TEXT_CONTAINS filter (text field contains substring).

    This operator checks if a text/string field contains the specified substring.
    The field must be a string, and the value must appear as a substring within that string.
    Use this for substring matching in text content.

    Example:
        Filter for documents where the content field contains "machine learning".
        This will match documents where "machine learning" appears anywhere in the content.
        For example, if content = "This is about machine learning algorithms", this will match.
        ```python
        from gllm_datastore.core.filters import text_contains

        filter = text_contains("content", "machine learning")
        ```

    Args:
        key (str): Field path to filter on (must be a string/text field).
        value (str): Substring to search for in the text.

    Returns:
        FilterClause: TEXT_CONTAINS filter.
    '''
def any_(key: str, values: list) -> FilterClause:
    '''Create an ANY filter (array field contains any of the values).

    This operator checks if an array field contains at least one of the values in the provided list.
    The field must be an array/list, and at least one element from the values list must be
    present in the array. This is similar to checking if the arrays have any intersection.

    Example:
        Filter for documents where the tags array contains at least one of "python" or "javascript".
        This will match if metadata.tags contains "python", "javascript", or both.
        For example, if metadata.tags = ["python", "rust"], this will match (because of "python").
        ```python
        from gllm_datastore.core.filters import any_

        filter = any_("metadata.tags", ["python", "javascript"])
        ```

    Args:
        key (str): Field path to filter on (must be an array field).
        values (list): List of values. At least one must be present in the array.

    Returns:
        FilterClause: ANY filter.
    '''
def all_(key: str, values: list) -> FilterClause:
    '''Create an ALL filter (array field contains all of the values).

    This operator checks if an array field contains all of the values in the provided list.
    The field must be an array/list, and every value in the values list must be present
    as an element in the array. The array may contain additional elements.

    Example:
        Filter for documents where the tags array contains both "python" and "javascript".
        This will match only if metadata.tags contains both values.
        For example, if metadata.tags = ["python", "javascript", "rust"], this will match.
        If metadata.tags = ["python", "rust"], this will not match (missing "javascript").
        ```python
        from gllm_datastore.core.filters import all_

        filter = all_("metadata.tags", ["python", "javascript"])
        ```

    Args:
        key (str): Field path to filter on (must be an array field).
        values (list): List of values. All must be present in the array.

    Returns:
        FilterClause: ALL filter.
    '''
def and_(*filters: FilterClause | QueryFilter) -> QueryFilter:
    '''Combine filters with AND condition.

    This logical operator combines multiple filters such that all conditions must be satisfied.
    A document matches only if it satisfies every filter in the list.

    Example:
        Filter for documents where status is "active" AND age is at least 18.
        This will match documents that satisfy both conditions simultaneously.
        ```python
        from gllm_datastore.core.filters import and_, eq, gte

        filter = and_(eq("metadata.status", "active"), gte("metadata.age", 18))
        ```

    Args:
        *filters (FilterClause | QueryFilter): Variable number of filters to combine.
            All filters must match for a document to be included.

    Returns:
        QueryFilter: Combined filter with AND condition.
    '''
def or_(*filters: FilterClause | QueryFilter) -> QueryFilter:
    '''Combine filters with OR condition.

    This logical operator combines multiple filters such that at least one condition must be satisfied.
    A document matches if it satisfies any of the filters in the list.

    Example:
        Filter for documents where status is "active" OR status is "pending".
        This will match documents that satisfy either condition (or both).
        ```python
        from gllm_datastore.core.filters import or_, eq

        filter = or_(eq("metadata.status", "active"), eq("metadata.status", "pending"))
        ```

    Args:
        *filters (FilterClause | QueryFilter): Variable number of filters to combine.
            At least one filter must match for a document to be included.

    Returns:
        QueryFilter: Combined filter with OR condition.
    '''
def not_(filter: FilterClause | QueryFilter) -> QueryFilter:
    '''Negate a filter.

    This logical operator inverts the result of a filter. A document matches if it does
    not satisfy the specified filter condition. Useful for exclusion criteria.

    This operator only supports NOT with a single filter. Multiple filters in NOT condition are not supported.

    Example:
        Filter for documents where status is NOT "deleted".
        This will match all documents except those with status == "deleted".
        Can also be used with other operators, e.g., not_(text_contains("content", "spam"))
        to exclude documents containing a specific substring.
        ```python
        from gllm_datastore.core.filters import not_, eq

        filter = not_(eq("metadata.status", "deleted"))
        ```

    Args:
        filter (FilterClause | QueryFilter): Filter to negate. Documents matching this
            filter will be excluded from results.

    Returns:
        QueryFilter: Negated filter.
    '''
