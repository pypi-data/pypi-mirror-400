"""Accumulator operators for MongoDB $group stage."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Accumulator(BaseModel):
    """Base class for accumulator operators used in $group stage."""

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid",
    )

    name: str = Field(..., description="Output field name")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        raise NotImplementedError


class Sum(Accumulator):
    """
    $sum accumulator - sums numeric values.

    Example:
        >>> Sum(name="totalQuantity", field="quantity").model_dump()
        {"totalQuantity": {"$sum": "$quantity"}}

        >>> Sum(name="count", value=1).model_dump()
        {"count": {"$sum": 1}}
    """

    field: str | None = Field(
        default=None, description="Field path to sum (without $)"
    )
    value: int | float | None = Field(
        default=None, description="Literal value to sum (e.g., 1 for counting)"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        if self.field is not None:
            field_path = (
                f"${self.field}"
                if not self.field.startswith("$")
                else self.field
            )
            return {self.name: {"$sum": field_path}}
        return {self.name: {"$sum": self.value}}


class Avg(Accumulator):
    """
    $avg accumulator - calculates average of numeric values.

    Example:
        >>> Avg(name="avgPrice", field="price").model_dump()
        {"avgPrice": {"$avg": "$price"}}
    """

    field: str = Field(..., description="Field path to average (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$avg": field_path}}


class Min(Accumulator):
    """
    $min accumulator - returns minimum value.

    Example:
        >>> Min(name="minPrice", field="price").model_dump()
        {"minPrice": {"$min": "$price"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$min": field_path}}


class Max(Accumulator):
    """
    $max accumulator - returns maximum value.

    Example:
        >>> Max(name="maxPrice", field="price").model_dump()
        {"maxPrice": {"$max": "$price"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$max": field_path}}


class First(Accumulator):
    """
    $first accumulator - returns first value in group.

    Example:
        >>> First(name="firstItem", field="item").model_dump()
        {"firstItem": {"$first": "$item"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$first": field_path}}


class Last(Accumulator):
    """
    $last accumulator - returns last value in group.

    Example:
        >>> Last(name="lastItem", field="item").model_dump()
        {"lastItem": {"$last": "$item"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$last": field_path}}


class Push(Accumulator):
    """
    $push accumulator - creates array of values.

    Example:
        >>> Push(name="items", field="item").model_dump()
        {"items": {"$push": "$item"}}

        >>> Push(
            name="details",
            expression={"name": "$name", "qty": "$qty"}
        ).model_dump()
        {"details": {"$push": {"name": "$name", "qty": "$qty"}}}
    """

    field: str | None = Field(
        default=None, description="Field path to push (without $)"
    )
    expression: dict[str, Any] | None = Field(
        default=None, description="Expression to push"
    )

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        if self.expression is not None:
            return {self.name: {"$push": self.expression}}
        field_path = (
            f"${self.field}"
            if self.field and not self.field.startswith("$")
            else self.field
        )
        return {self.name: {"$push": field_path}}


class AddToSet(Accumulator):
    """
    $addToSet accumulator - creates array of unique values.

    Example:
        >>> AddToSet(name="uniqueTags", field="tag").model_dump()
        {"uniqueTags": {"$addToSet": "$tag"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$addToSet": field_path}}


class StdDevPop(Accumulator):
    """
    $stdDevPop accumulator - population standard deviation.

    Example:
        >>> StdDevPop(name="stdDev", field="score").model_dump()
        {"stdDev": {"$stdDevPop": "$score"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$stdDevPop": field_path}}


class StdDevSamp(Accumulator):
    """
    $stdDevSamp accumulator - sample standard deviation.

    Example:
        >>> StdDevSamp(name="stdDevSample", field="score").model_dump()
        {"stdDevSample": {"$stdDevSamp": "$score"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$stdDevSamp": field_path}}


class Count_(Accumulator):
    """
    $count accumulator - counts documents in group (MongoDB 5.0+).

    Example:
        >>> Count_(name="totalDocs").model_dump()
        {"totalDocs": {"$count": {}}}
    """

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {self.name: {"$count": {}}}


class MergeObjects(Accumulator):
    """
    $mergeObjects accumulator - merges documents into single document.

    Example:
        >>> MergeObjects(name="merged", field="details").model_dump()
        {"merged": {"$mergeObjects": "$details"}}
    """

    field: str = Field(..., description="Field path (without $)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        field_path = (
            f"${self.field}" if not self.field.startswith("$") else self.field
        )
        return {self.name: {"$mergeObjects": field_path}}


class Accumulate(Accumulator):
    """
    $accumulator - custom JavaScript accumulator (MongoDB 4.4+).

    Example:
        >>> Accumulate(  # noqa
        ...     name="custom",
        ...     init="function() { return { count: 0 } }",
        ...     accumulate="function(state, val) { state.count++; return state }",
        ...     merge="function(s1, s2) { return { count: s1.count + s2.count } }",
        ...     finalize="function(state) { return state.count }",
        ...     lang="js"
        ... ).model_dump()
    """

    init: str = Field(..., description="Init function")
    accumulate: str = Field(..., description="Accumulate function")
    merge: str = Field(..., description="Merge function")
    finalize: str | None = Field(default=None, description="Finalize function")
    init_args: list[Any] | None = Field(
        default=None,
        validation_alias="initArgs",
        serialization_alias="initArgs",
        description="Init function arguments",
    )
    accumulate_args: list[Any] | None = Field(
        default=None,
        validation_alias="accumulateArgs",
        serialization_alias="accumulateArgs",
        description="Accumulate function arguments",
    )
    lang: str = Field(default="js", description="Language (js)")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        result: dict[str, Any] = {
            "init": self.init,
            "accumulate": self.accumulate,
            "merge": self.merge,
            "lang": self.lang,
        }
        if self.finalize is not None:
            result["finalize"] = self.finalize
        if self.init_args is not None:
            result["initArgs"] = self.init_args
        if self.accumulate_args is not None:
            result["accumulateArgs"] = self.accumulate_args
        return {self.name: {"$accumulator": result}}


class TopN(Accumulator):
    """
    $topN accumulator - returns top N elements (MongoDB 5.2+).

    Example:
        >>> TopN(
        ...     name="top3",
        ...     n=3,
        ...     sort_by={"score": -1},
        ...     output="$item"
        ... ).model_dump()
        {
            "top3": {
                "$topN": {"n": 3, "sortBy": {"score": -1},
                "output": "$item"}
            }
        }
    """

    n: int = Field(..., gt=0, description="Number of results")
    sort_by: dict[str, int] = Field(
        ...,
        validation_alias="sortBy",
        serialization_alias="sortBy",
        description="Sort specification",
    )
    output: str | dict[str, Any] = Field(..., description="Output expression")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {
            self.name: {
                "$topN": {
                    "n": self.n,
                    "sortBy": self.sort_by,
                    "output": self.output,
                }
            }
        }


class BottomN(Accumulator):
    """
    $bottomN accumulator - returns bottom N elements (MongoDB 5.2+).

    Example:
        >>> BottomN(
        ...     name="bottom3",
        ...     n=3,
        ...     sort_by={"score": -1},
        ...     output="$item"
        ... ).model_dump()
        {
            "bottom3": {
                "$bottomN": {"n": 3, "sortBy": {"score": -1},
                "output": "$item"}
            }
        }
    """

    n: int = Field(..., gt=0, description="Number of results")
    sort_by: dict[str, int] = Field(
        ...,
        validation_alias="sortBy",
        serialization_alias="sortBy",
        description="Sort specification",
    )
    output: str | dict[str, Any] = Field(..., description="Output expression")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {
            self.name: {
                "$bottomN": {
                    "n": self.n,
                    "sortBy": self.sort_by,
                    "output": self.output,
                }
            }
        }


class FirstN(Accumulator):
    """
    $firstN accumulator - returns first N elements (MongoDB 5.2+).

    Example:
        >>> FirstN(name="first3", n=3, input="$item").model_dump()
        {"first3": {"$firstN": {"n": 3, "input": "$item"}}}
    """

    n: int = Field(..., gt=0, description="Number of results")
    input: str | dict[str, Any] = Field(..., description="Input expression")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {self.name: {"$firstN": {"n": self.n, "input": self.input}}}


class LastN(Accumulator):
    """
    $lastN accumulator - returns last N elements (MongoDB 5.2+).

    Example:
        >>> LastN(name="last3", n=3, input="$item").model_dump()
        {"last3": {"$lastN": {"n": 3, "input": "$item"}}}
    """

    n: int = Field(..., gt=0, description="Number of results")
    input: str | dict[str, Any] = Field(..., description="Input expression")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {self.name: {"$lastN": {"n": self.n, "input": self.input}}}


class MaxN(Accumulator):
    """
    $maxN accumulator - returns N maximum values (MongoDB 5.2+).

    Example:
        >>> MaxN(name="top3Scores", n=3, input="$score").model_dump()
        {"top3Scores": {"$maxN": {"n": 3, "input": "$score"}}}
    """

    n: int = Field(..., gt=0, description="Number of results")
    input: str | dict[str, Any] = Field(..., description="Input expression")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {self.name: {"$maxN": {"n": self.n, "input": self.input}}}


class MinN(Accumulator):
    """
    $minN accumulator - returns N minimum values (MongoDB 5.2+).

    Example:
        >>> MinN(name="lowest3", n=3, input="$score").model_dump()
        {"lowest3": {"$minN": {"n": 3, "input": "$score"}}}
    """

    n: int = Field(..., gt=0, description="Number of results")
    input: str | dict[str, Any] = Field(..., description="Input expression")

    def model_dump(self, **kwargs: Any) -> dict[str, dict[str, Any]]:
        return {self.name: {"$minN": {"n": self.n, "input": self.input}}}


def merge_accumulators(*accumulators: Accumulator) -> dict[str, Any]:
    """
    Merge multiple accumulators into a single dictionary for Group stage.

    Example:
        >>> merge_accumulators(
        ...     Sum(name="total", field="amount"),
        ...     Avg(name="average", field="amount"),
        ...     Count_(name="count")
        ... )
        {
            "total": {
                "$sum": "$amount"},
                "average": {"$avg": "$amount"},
                "count": {"$count": {}
            }
        }
    """
    result: dict[str, Any] = {}
    for acc in accumulators:
        result.update(acc.model_dump())
    return result
