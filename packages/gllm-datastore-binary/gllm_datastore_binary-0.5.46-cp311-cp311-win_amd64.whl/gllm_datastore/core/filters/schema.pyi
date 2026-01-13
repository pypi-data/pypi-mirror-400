from enum import StrEnum
from pydantic import BaseModel
from typing import Any, Sequence

class FilterOperator(StrEnum):
    """Operators for comparing field values."""
    EQ: str
    NE: str
    GT: str
    LT: str
    GTE: str
    LTE: str
    IN: str
    NIN: str
    ANY: str
    ALL: str
    ARRAY_CONTAINS: str
    TEXT_CONTAINS: str

class FilterCondition(StrEnum):
    """Logical conditions for combining filters."""
    AND: str
    OR: str
    NOT: str

class FilterClause(BaseModel):
    '''Single filter criterion with operator support.

    Examples:
        ```python
        FilterClause(key="metadata.age", value=25, operator=FilterOperator.GT)
        FilterClause(key="metadata.status", value=["active", "pending"], operator=FilterOperator.IN)
        ```

    Attributes:
        key (str): The field path to filter on (supports dot notation for nested fields).
        value (int | float | str | bool | list[str] | list[float] | list[int] | list[bool] | None):
            The value to compare against.
        operator (FilterOperator): The comparison operator.
    '''
    key: str
    value: bool | int | float | str | list[str] | list[float] | list[int] | list[bool] | None
    operator: FilterOperator
    def to_query_filter(self) -> QueryFilter:
        '''Convert FilterClause to QueryFilter.

        This method enables automatic conversion of FilterClause to QueryFilter.

        Example:
            ```python
            clause = FilterClause(key="metadata.status", value="active", operator=FilterOperator.EQ)
            query_filter = clause.to_query_filter()
            # Results in: QueryFilter(filters=[clause], condition=FilterCondition.AND)
            ```

        Returns:
            QueryFilter: A QueryFilter wrapping this FilterClause with AND condition.
        '''

class QueryFilter(BaseModel):
    '''Composite filter supporting multiple conditions and logical operators.

    Attributes:
        filters (list[FilterClause | QueryFilter]): List of filters to combine.
            Can include nested QueryFilter for complex logic.
        condition (FilterCondition): Logical operator to combine filters. Defaults to AND.

    Examples:
        1. Simple AND: age > 25 AND status == "active"
            ```python
            QueryFilter(
                filters=[
                    FilterClause(key="metadata.age", value=25, operator=FilterOperator.GT),
                    FilterClause(key="metadata.status", value="active", operator=FilterOperator.EQ)
                ],
                condition=FilterCondition.AND
            )
            ```

        2. Complex OR: (status == "active" OR status == "pending") AND age >= 18
            ```python
            QueryFilter(
                filters=[
                    QueryFilter(
                        filters=[
                            FilterClause(key="metadata.status", value="active"),
                            FilterClause(key="metadata.status", value="pending")
                        ],
                        condition=FilterCondition.OR
                    ),
                    FilterClause(key="metadata.age", value=18, operator=FilterOperator.GTE)
                ],
                condition=FilterCondition.AND
            )
            ```

        3. NOT: NOT (status == "deleted")
            ```python
            QueryFilter(
                filters=[
                    FilterClause(key="metadata.status", value="deleted")
                ],
                condition=FilterCondition.NOT
            )
            ```
    '''
    filters: list[FilterClause | QueryFilter]
    condition: FilterCondition
    @classmethod
    def from_dicts(cls, filter_dicts: list[dict[str, Any]], condition: FilterCondition = ...) -> QueryFilter:
        '''Create QueryFilter from list of filter dictionaries.

        Example:
            ```python
            QueryFilter.from_dicts(
                [
                    {"key": "metadata.age", "value": 25, "operator": ">"},
                    {"key": "metadata.status", "value": "active"}
                ],
                condition=FilterCondition.AND
            )
            ```

        Args:
            filter_dicts (list[dict[str, Any]]): List of filter dictionaries. Contains the key, value, and operator.
            condition (FilterCondition, optional): Logical operator to combine filters. Defaults to AND.

        Returns:
            QueryFilter: Composite filter instance.
        '''

class QueryOptions(BaseModel):
    '''Model for query options.

    Attributes:
        include_fields (Sequence[str] | None): The fields to include in the query result. Defaults to None.
        order_by (str | None): The column to order the query result by. Defaults to None.
        order_desc (bool): Whether to order the query result in descending order. Defaults to False.
        limit (int | None): The maximum number of rows to return. Must be >= 0. Defaults to None.

    Example:
        ```python
        QueryOptions(include_fields=["field1", "field2"], order_by="column1", order_desc=True, limit=10)
        ```
    '''
    include_fields: Sequence[str] | None
    order_by: str | None
    order_desc: bool
    limit: int | None
