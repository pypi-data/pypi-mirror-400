"""Base classes for MongoDB aggregation pipeline stages."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, Self

from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

# Sort direction constants for use with Sort stage and with_sort method
ASCENDING: int = 1
DESCENDING: int = -1

# Type alias for sort specification used in aggregation
# Uses int to be compatible with both Literal[-1, 1] and regular int values
SortSpec = dict[str, int]
# Type alias for aggregation input tuple (pipeline, sort)
AggregationInput = tuple[list[dict[str, Any]], SortSpec]


class BaseStage(ABC):
    """Abstract base class for all MongoDB aggregation pipeline stages."""

    @abstractmethod
    def model_dump(self) -> dict[str, Any]:
        """
        Convert the stage to its MongoDB dictionary representation.

        Returns:
            dict[str, Any]: MongoDB aggregation stage dictionary
        """
        pass


class Pipeline:
    """
    MongoDB aggregation pipeline builder.

    This class acts as a container for aggregation stages and can be
    directly passed to MongoDB's aggregate() method. It implements
    __iter__ to allow MongoDB drivers to iterate through the stages.

    Example:
        >>> pipeline = Pipeline()
        >>> pipeline.add_stage(Match(field="status", value="active"))
        >>> pipeline.add_stage(Group(id="$category", count={"$sum": 1}))
        >>> collection.aggregate(pipeline)

        >>> # Or with constructor
        >>> pipeline = Pipeline([
        ...     Match(field="status", value="active"),
        ...     Unwind(path="items")
        ... ])
    """

    def __init__(self, stages: list[BaseStage] | None = None) -> None:
        """
        Initialize the pipeline with optional initial stages.

        Args:
            stages: Optional list of initial pipeline stages
        """
        self._stages: list[BaseStage] = stages or []

    def add_stage(self, stage: BaseStage) -> Self:
        """
        Append a new stage to the pipeline.

        Args:
            stage: A pipeline stage instance

        Returns:
            Self: Self for method chaining
        """
        self._stages.append(stage)
        return self

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Iterate through pipeline stages as dictionaries.

        This allows the pipeline to be directly passed to MongoDB's
        aggregate() method without calling any additional methods.

        Yields:
            dict[str, Any]: Each stage's MongoDB dictionary representation
        """
        for stage in self._stages:
            yield stage.model_dump()

    def __len__(self) -> int:
        """Return the number of stages in the pipeline."""
        return len(self._stages)

    def __getitem__(self, index: int) -> BaseStage:
        """Get a stage by index."""
        return self._stages[index]

    def to_list(self) -> list[dict[str, Any]]:
        """
        Convert the entire pipeline to a list of dictionaries.

        Returns:
            list[dict[str, Any]]: List of MongoDB stage dictionaries
        """
        return list(self)

    def with_sort(self, sort: SortSpec) -> AggregationInput:
        """
        Return pipeline as aggregation input tuple with sort specification.

        This is useful for integrating with pagination utilities that
        expect a tuple of (pipeline, sort_spec). Common in Beanie ODM
        pagination patterns.

        Args:
            sort: Sort specification dict with field names as keys
                  and -1 (descending) or 1 (ascending) as values

        Returns:
            AggregationInput: Tuple of (pipeline_list, sort_spec)

        Example:
            >>> pipeline = Pipeline([
            ...     Match(query={"status": "active"}),
            ...     Group(id="$category", total={"$sum": "$amount"})
            ... ])
            >>> # Use with pagination utilities
            >>> aggregation_input = pipeline.with_sort({"total": -1})
            >>> await query.paginate_and_cast(
            ...     query=base_query,
            ...     projection_model=OutputModel,
            ...     aggregation_input=aggregation_input
            ... )
        """
        return (self.to_list(), sort)

    def extend(self, stages: list[BaseStage]) -> Self:
        """
        Extend the pipeline with multiple stages.

        Args:
            stages: List of pipeline stages to add

        Returns:
            Self: Self for method chaining
        """
        self._stages.extend(stages)
        return self

    def extend_raw(self, raw_stages: list[dict[str, Any]]) -> Self:
        """
        Extend the pipeline with raw dictionary stages.

        This is useful when combining typed stages with raw MongoDB
        pipeline stages that may not have a corresponding class.

        Args:
            raw_stages: List of raw MongoDB stage dictionaries

        Returns:
            Self: Self for method chaining

        Example:
            >>> pipeline = Pipeline([Match(query={"status": "active"})])
            >>> pipeline.extend_raw([
            ...     {"$addFields": {"computed": {"$multiply": ["$a", "$b"]}}},
            ...     {"$project": {"_id": 0, "result": "$computed"}}
            ... ])
        """
        for raw_stage in raw_stages:
            self._stages.append(_RawStage(raw_stage))
        return self

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        """
        Allow Pipeline to be used as a Pydantic field type.

        This enables using Pipeline in other Pydantic models,
        for example in Lookup's pipeline field.
        """
        return core_schema.is_instance_schema(cls)


class _RawStage(BaseStage):
    """Internal class for wrapping raw dictionary stages."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self._raw = raw

    def model_dump(self) -> dict[str, Any]:
        return self._raw
