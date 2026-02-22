"""
Read-only query service for WRC data.
Exposes common query patterns against the local DB.
All methods take explicit IDs; see WrcSession for higher-level event-scoped access.
"""

from sqlalchemy import select

from openwrc.models.db.event import EventMetadata, RallyMetadata
from openwrc.models.db.itinerary import Stage
from openwrc.models.db.result import RallyStanding, SplitTime
from openwrc.storage.database import WrcDatabase


class WrcQueryService:

    def __init__(self, db: WrcDatabase) -> None:
        self._db = db

    async def get_event_by_name(
        self, name: str, year: int | None = None
    ) -> EventMetadata | None:
        """Find an event by its name, optionally filtered by year.

        For most cases a bare name match is sufficient. Pass year when the same
        event name appears across multiple seasons (e.g. "Rallye Monte Carlo").
        """
        stmt = select(EventMetadata).where(EventMetadata.name.ilike(f"%{name}%"))
        if year is not None:
            stmt = stmt.where(
                EventMetadata.start_date >= f"{year}-01-01",
                EventMetadata.start_date < f"{year + 1}-01-01",
            )
        async with self._db.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_default_rally_for_event(self, event_id: int) -> RallyMetadata | None:
        """Return the main rally for an event (is_main=True), falling back to the
        first rally by rally_id when no main rally is marked.
        """
        stmt = (
            select(RallyMetadata)
            .where(RallyMetadata.event_id == event_id)
            .order_by(RallyMetadata.is_main.desc(), RallyMetadata.rally_id)
        )
        async with self._db.session() as session:
            result = await session.execute(stmt)
            return result.scalars().first()

    async def get_stage_by_number(self, event_id: int, number: int) -> Stage | None:
        """Find a stage by its number within an event (e.g. number=5 → SS5)."""
        stmt = select(Stage).where(
            Stage.event_id == event_id,
            Stage.number == number,
        )
        async with self._db.session() as session:
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def get_split_times(self, rally_id: int, stage_id: int) -> list[SplitTime]:
        """Return all split times for a given stage within a rally."""
        stmt = select(SplitTime).where(
            SplitTime.rally_id == rally_id,
            SplitTime.stage_id == stage_id,
        )
        async with self._db.session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())

    async def get_rally_standings(
        self, rally_id: int, stage_id: int | None = None
    ) -> list[RallyStanding]:
        """Return rally standings for a given rally.

        When stage_id is provided, returns standings after that specific stage only.
        When omitted, returns all standings across all stages (full progression).
        """
        stmt = select(RallyStanding).where(RallyStanding.rally_id == rally_id)
        if stage_id is not None:
            stmt = stmt.where(RallyStanding.stage_id == stage_id)
        async with self._db.session() as session:
            result = await session.execute(stmt)
            return list(result.scalars().all())
