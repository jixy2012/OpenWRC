"""
Models for rally and stage results from WRC API
Important Note: this is for the entire rally up to the stage. single stage models will be under stage_models.py
"""

from typing import Optional
from pydantic import Field
from .base_external_model import WrcExternalApiBaseModel


class BaseEntry(WrcExternalApiBaseModel):
    entry_id: int = Field(description="Entry ID for this driver/car combination")
    # Position and time differences
    position: Optional[int] = Field(
        default=None, description="Current position in standings"
    )
    diff_first_ms: Optional[int] = Field(
        default=None, description="Overall time difference to leader in milliseconds"
    )
    diff_prev_ms: Optional[int] = Field(
        default=None,
        description="Overall time difference to previous position in milliseconds",
    )


class ResultEntry(BaseEntry):
    """A single result entry for a driver in a rally or stage"""

    # Time data in milliseconds (easier to work with)
    stage_time_ms: int = Field(description="Stage time in milliseconds")
    penalty_time_ms: int = Field(description="Penalty time in milliseconds")
    total_time_ms: int = Field(
        description="Total time (stage + penalty) in milliseconds"
    )


class StageTimeEntry(BaseEntry):
    """A single stage time entry for a driver's performance on a specific stage"""

    stage_id: int = Field(description="Stage ID")
    elapsed_duration_ms: Optional[int] = Field(
        default=None, description="Elapsed duration in milliseconds"
    )
    status: str = Field(
        description="Completion status (e.g., 'Completed')"
    )  # TODO: make enum
    source: str = Field(description="Data source (e.g., 'Default')")  # TODO: make enum


# Type aliases for clarity
RallyResults = list[ResultEntry]
StageResults = list[ResultEntry]
StageTimeResults = list[StageTimeEntry]
