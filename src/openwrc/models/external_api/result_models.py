"""
Models for rally and stage results from WRC API
Important Note: this is for the entire rally up to the stage. single stage models will be under stage_models.py
"""

from pydantic import Field, ConfigDict
from .base_external_model import WrcExternalApiBaseModel


class ResultEntry(WrcExternalApiBaseModel):
    """A single result entry for a driver in a rally or stage"""

    model_config = ConfigDict(extra="ignore")

    entryId: int = Field(description="Entry ID for this driver/car combination")

    # Time data in milliseconds (easier to work with)
    stageTimeMs: int = Field(description="Stage time in milliseconds")
    penaltyTimeMs: int = Field(description="Penalty time in milliseconds")
    totalTimeMs: int = Field(description="Total time (stage + penalty) in milliseconds")

    # Position and time differences
    position: int = Field(description="Current position in standings")
    diffFirstMs: int = Field(
        description="Overall time difference to leader in milliseconds"
    )
    diffPrevMs: int = Field(
        description="Overall time difference to previous position in milliseconds"
    )


# Type aliases for clarity
RallyResults = list[ResultEntry]
StageResults = list[ResultEntry]
