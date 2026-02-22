from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, ForeignKey, Enum, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .event import EventMetadata, RallyMetadata, Entry
from .itinerary import Stage


class StageStatus(PyEnum):
    """Status of stage completion"""

    COMPLETED = "Completed"
    RETIRED = "Retired"
    DID_NOT_START = "DidNotStart"
    DISQUALIFIED = "Disqualified"
    EXCLUDED = "Excluded"


class DataSource(PyEnum):
    """Source of timing data"""

    DEFAULT = "Default"
    MANUAL = "Manual"
    CORRECTED = "Corrected"


class StageTime(Base):
    """Individual driver performance on a specific stage"""

    __tablename__ = "stage_times"

    # Composite PK: one record per (stage, driver)
    stage_id: Mapped[int] = mapped_column(ForeignKey(Stage.stage_id), primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id), primary_key=True)

    # Denormalized for query efficiency
    rally_id: Mapped[int] = mapped_column(ForeignKey(RallyMetadata.rally_id))

    # Performance data
    elapsed_duration_ms: Mapped[int | None]
    position: Mapped[int | None]
    diff_first_ms: Mapped[int | None]
    diff_prev_ms: Mapped[int | None]

    # Metadata
    status: Mapped[StageStatus] = mapped_column(Enum(StageStatus))
    source: Mapped[str] = mapped_column(String(50))

    # Indexes for common queries
    __table_args__ = (
        Index("ix_stage_time_rally_entry", "rally_id", "entry_id"),
        Index("ix_stage_time_stage", "stage_id"),
    )


class RallyStanding(Base):
    """Overall rally standings after each stage"""

    __tablename__ = "rally_standings"

    # Composite PK: standing after specific stage
    rally_id: Mapped[int] = mapped_column(
        ForeignKey(RallyMetadata.rally_id), primary_key=True
    )
    stage_id: Mapped[int] = mapped_column(ForeignKey(Stage.stage_id), primary_key=True)
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id), primary_key=True)

    # Cumulative data at this point in the rally
    position: Mapped[int | None]
    stage_time_ms: Mapped[int]
    penalty_time_ms: Mapped[int]
    total_time_ms: Mapped[int]
    diff_first_ms: Mapped[int | None]
    diff_prev_ms: Mapped[int | None]

    # Indexes for common queries
    __table_args__ = (
        Index("ix_rally_standing_rally_entry", "rally_id", "entry_id"),
        Index("ix_rally_standing_rally_stage", "rally_id", "stage_id"),
    )


class ShakedownTime(Base):
    """Pre-rally shakedown run times"""

    __tablename__ = "shakedown_times"

    # Primary key
    shakedown_time_id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    event_id: Mapped[int] = mapped_column(ForeignKey(EventMetadata.event_id))
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id))

    # Shakedown details
    run_number: Mapped[int]
    shakedown_number: Mapped[int]
    run_duration_ms: Mapped[int]

    # Indexes for common queries
    __table_args__ = (Index("ix_shakedown_event_entry", "event_id", "entry_id"),)


class SplitTime(Base):
    """Intermediate timing points within stages"""

    __tablename__ = "split_times"

    # Primary key
    split_point_time_id: Mapped[int] = mapped_column(primary_key=True)

    # Foreign keys
    split_point_id: Mapped[int]  # May need SplitPoint table later
    rally_id: Mapped[int] = mapped_column(ForeignKey(RallyMetadata.rally_id))
    stage_id: Mapped[int] = mapped_column(ForeignKey(Stage.stage_id))
    entry_id: Mapped[int] = mapped_column(ForeignKey(Entry.entry_id))

    # Timing data
    start_date_time: Mapped[datetime]
    split_date_time: Mapped[datetime]
    stage_time_duration_ms: Mapped[int | None]
    elapsed_duration_ms: Mapped[int]

    # Indexes for common queries
    __table_args__ = (Index("ix_split_time_stage_entry", "stage_id", "entry_id"),)
