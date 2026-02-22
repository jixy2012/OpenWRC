"""
Models for rally and stage results from WRC API
Important Note: this is for the entire rally up to the stage. single stage models will be under stage_models.py
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from .base_external_model import WrcExternalApiBaseModel


class ApiBaseEntry(WrcExternalApiBaseModel):
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


class ApiResultEntry(ApiBaseEntry):
    """A single result entry for a driver in a rally or stage"""

    # Time data in milliseconds (easier to work with)
    stage_time_ms: int = Field(description="Stage time in milliseconds")
    penalty_time_ms: int = Field(description="Penalty time in milliseconds")
    total_time_ms: int = Field(
        description="Total time (stage + penalty) in milliseconds"
    )


class ApiStageTimeEntry(ApiBaseEntry):
    """A single stage time entry for a driver's performance on a specific stage"""

    stage_id: int = Field(description="Stage ID")
    elapsed_duration_ms: Optional[int] = Field(
        default=None, description="Elapsed duration in milliseconds"
    )
    status: str = Field(
        description="Completion status (e.g., 'Completed')"
    )  # TODO: make enum
    source: str = Field(description="Data source (e.g., 'Default')")  # TODO: make enum


class ApiShakedownTimeEntry(WrcExternalApiBaseModel):
    """A single shakedown time entry for a driver's shakedown run"""

    shakedown_time_id: int = Field(
        description="Unique identifier for this shakedown time"
    )
    event_id: int = Field(description="Event ID")
    entry_id: int = Field(description="Entry ID for this driver/car combination")
    run_number: int = Field(description="Run number (e.g., 1st run, 2nd run)")
    shakedown_number: int = Field(description="Shakedown stage number")
    run_duration_ms: int = Field(description="Run duration in milliseconds")


class ApiSplitTimeEntry(WrcExternalApiBaseModel):
    """A single split time entry for an entry at a split point."""

    start_date_time: datetime = Field(description="Start time in UTC")
    stage_time_duration_ms: int | None = Field(
        default=None, description="Stage time duration in milliseconds"
    )
    split_point_time_id: int = Field(
        description="Unique identifier for this split point time"
    )
    split_point_id: int = Field(description="Split point ID")
    entry_id: int = Field(description="Entry ID for this driver/car combination")
    elapsed_duration_ms: int = Field(
        description="Elapsed duration in milliseconds at split point"
    )
    split_date_time: datetime = Field(description="Split time timestamp in UTC")


# Type aliases for clarity
ApiRallyResults = list[ApiResultEntry]
ApiStageResults = list[ApiResultEntry]
ApiStageTimeResults = list[ApiStageTimeEntry]
ApiShakedownTimeResults = list[ApiShakedownTimeEntry]
ApiSplitTimeResults = list[ApiSplitTimeEntry]
