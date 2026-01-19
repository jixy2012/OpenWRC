"""
Models for rally and stage results from WRC API
Important Note: this is for the entire rally up to the stage. single stage models will be under stage_models.py
"""

from pydantic import Field
from .base_external_model import WrcExternalApiBaseModel


class BaseEntry(WrcExternalApiBaseModel):
    entryId: int = Field(description="Entry ID for this driver/car combination")
    # Position and time differences
    position: int = Field(description="Current position in standings")
    diffFirstMs: int = Field(
        description="Overall time difference to leader in milliseconds"
    )
    diffPrevMs: int = Field(
        description="Overall time difference to previous position in milliseconds"
    )


class ResultEntry(BaseEntry):
    """A single result entry for a driver in a rally or stage"""

    # Time data in milliseconds (easier to work with)
    stageTimeMs: int = Field(description="Stage time in milliseconds")
    penaltyTimeMs: int = Field(description="Penalty time in milliseconds")
    totalTimeMs: int = Field(description="Total time (stage + penalty) in milliseconds")


class StageTimeEntry(WrcExternalApiBaseModel):
    """A single stage time entry for a driver's performance on a specific stage"""

    stageId: int = Field(description="Stage ID")
    elapsedDurationMs: int = Field(description="Elapsed duration in milliseconds")
    status: str = Field(
        description="Completion status (e.g., 'Completed')"
    )  # TODO: make enum
    source: str = Field(description="Data source (e.g., 'Default')")  # TODO: make enum


# Type aliases for clarity
RallyResults = list[ResultEntry]
StageResults = list[ResultEntry]
StageTimeResults = list[StageTimeEntry]
