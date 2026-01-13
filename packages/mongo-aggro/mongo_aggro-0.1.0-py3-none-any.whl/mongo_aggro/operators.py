"""Query and expression operators for MongoDB aggregation."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class QueryOperator(BaseModel):
    """Base class for query operators used in $match and other stages."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )


class And(QueryOperator):
    """
    Logical AND operator for combining multiple conditions.

    Example:
        >>> And(conditions=[
        ...     {"status": "active"},
        ...     {"age": {"$gt": 18}}
        ... ]).model_dump()
        {"$and": [{"status": "active"}, {"age": {"$gt": 18}}]}
    """

    conditions: list[dict[str, Any]] = Field(
        ..., description="List of conditions to AND together"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$and": self.conditions}


class Or(QueryOperator):
    """
    Logical OR operator for combining multiple conditions.

    Example:
        >>> Or(conditions=[
        ...     {"status": "active"},
        ...     {"status": "pending"}
        ... ]).model_dump()
        {"$or": [{"status": "active"}, {"status": "pending"}]}
    """

    conditions: list[dict[str, Any]] = Field(
        ..., description="List of conditions to OR together"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$or": self.conditions}


class Not(QueryOperator):
    """
    Logical NOT operator for negating a condition.

    Example:
        >>> Not(condition={"$regex": "^test"}).model_dump()
        {"$not": {"$regex": "^test"}}
    """

    condition: dict[str, Any] = Field(..., description="Condition to negate")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$not": self.condition}


class Nor(QueryOperator):
    """
    Logical NOR operator - matches documents that fail all conditions.

    Example:
        >>> Nor(conditions=[
        ...     {"price": {"$gt": 1000}},
        ...     {"rating": {"$lt": 3}}
        ... ]).model_dump()
        {"$nor": [{"price": {"$gt": 1000}}, {"rating": {"$lt": 3}}]}
    """

    conditions: list[dict[str, Any]] = Field(
        ..., description="List of conditions to NOR together"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$nor": self.conditions}


class Expr(QueryOperator):
    """
    $expr operator for using aggregation expressions in queries.

    Example:
        >>> Expr(expression={"$eq": ["$field1", "$field2"]}).model_dump()
        {"$expr": {"$eq": ["$field1", "$field2"]}}
    """

    expression: dict[str, Any] = Field(
        ..., description="Aggregation expression"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$expr": self.expression}


# Comparison operators
class Eq(QueryOperator):
    """$eq comparison operator."""

    value: Any = Field(..., description="Value to compare")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$eq": self.value}


class Ne(QueryOperator):
    """$ne (not equal) comparison operator."""

    value: Any = Field(..., description="Value to compare")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$ne": self.value}


class Gt(QueryOperator):
    """$gt (greater than) comparison operator."""

    value: Any = Field(..., description="Value to compare")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$gt": self.value}


class Gte(QueryOperator):
    """$gte (greater than or equal) comparison operator."""

    value: Any = Field(..., description="Value to compare")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$gte": self.value}


class Lt(QueryOperator):
    """$lt (less than) comparison operator."""

    value: Any = Field(..., description="Value to compare")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$lt": self.value}


class Lte(QueryOperator):
    """$lte (less than or equal) comparison operator."""

    value: Any = Field(..., description="Value to compare")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$lte": self.value}


class In(QueryOperator):
    """$in operator - matches any value in the array."""

    values: list[Any] = Field(..., description="List of values to match")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$in": self.values}


class Nin(QueryOperator):
    """$nin operator - matches none of the values in the array."""

    values: list[Any] = Field(..., description="List of values to exclude")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$nin": self.values}


class Regex(QueryOperator):
    """$regex operator for pattern matching."""

    pattern: str = Field(..., description="Regular expression pattern")
    options: str | None = Field(
        default=None, description="Regex options (i, m, x, s)"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        result: dict[str, Any] = {"$regex": self.pattern}
        if self.options:
            result["$options"] = self.options
        return result


class Exists(QueryOperator):
    """$exists operator - matches documents where field exists/doesn't."""

    exists: bool = Field(
        default=True, description="True if field should exist"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$exists": self.exists}


class Type(QueryOperator):
    """$type operator - matches documents where field is of specified type."""

    bson_type: str | int | list[str | int] = Field(
        ..., description="BSON type(s) to match"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$type": self.bson_type}


class ElemMatch(QueryOperator):
    """$elemMatch operator - matches array elements."""

    conditions: dict[str, Any] = Field(
        ..., description="Conditions for array elements"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$elemMatch": self.conditions}


class Size(QueryOperator):
    """$size operator - matches arrays with specific length."""

    size: int = Field(..., description="Array size to match")

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$size": self.size}


class All(QueryOperator):
    """$all operator - matches arrays containing all specified elements."""

    values: list[Any] = Field(
        ..., description="Values that must all be present"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, Any]:
        return {"$all": self.values}
