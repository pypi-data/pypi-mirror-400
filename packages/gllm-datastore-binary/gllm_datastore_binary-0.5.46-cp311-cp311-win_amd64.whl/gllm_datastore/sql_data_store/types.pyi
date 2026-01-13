from pydantic import BaseModel
from typing import Any, Sequence

class QueryFilter(BaseModel):
    '''Model for query filters.

    Attributes:
        conditions (dict[str, Any]): The conditions for filtering the query.

    Example:
        QueryFilter(conditions={"column1": "value1", "column2": "value2"})
    '''
    conditions: dict[str, Any]

class QueryOptions(BaseModel):
    '''Model for query options.

    Attributes:
        columns (Sequence[str] | None): The columns to include in the query result. Defaults to None.
        fields (Sequence[str] | None): The fields to include in the query result. Defaults to None.
        order_by (str | None): The column to order the query result by. Defaults to None.
        order_desc (bool): Whether to order the query result in descending order. Defaults to False.
        limit (int | None): The maximum number of rows to return. Defaults to None.

    Example:
        QueryOptions(fields=["field1", "field2"], order_by="column1", order_desc=True, limit=10)
    '''
    columns: Sequence[str] | None
    order_by: str | None
    order_desc: bool
    limit: int | None
