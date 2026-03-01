from datetime import date
from zoneinfo import ZoneInfo

from openwrc.exceptions.session_exceptions import SessionInputValidationException
from openwrc.models.db.event import Entry, EventMetadata
from openwrc.models.db.itinerary import Stage
from openwrc.storage.database import WrcDatabase
from openwrc.storage.query_service import WrcQueryService
from openwrc.utils.datetime_utils import event_tz


class WrcSession:
    """
    Event-scoped entry point for querying WRC data from the local DB.

    Resolves event and rally identity once at creation time; all query methods
    use the resolved IDs so callers never have to pass them explicitly.

    Initialization options:
    - event_id: use the raw WRC event id directly
    - name + optional year: resolve event by name (e.g. name="monte carlo", year=2025)

    In both cases rally_id defaults to the main rally for the event.
    """

    def __init__(
        self,
        event_id: int,
        rally_id: int,
        query_service: WrcQueryService,
        event_start_date: date,
        event_finish_date: date,
        event_timezone: ZoneInfo,
    ):
        self.event_id = event_id
        self.rally_id = rally_id
        self.event_start_date = event_start_date
        self.event_finish_date = event_finish_date
        self.event_timezone = event_timezone
        self._qs = query_service

    @classmethod
    async def list_available_years(cls, db: WrcDatabase | None = None) -> list[int]:
        """Return distinct years for which events are stored in the local DB."""
        qs = WrcQueryService(db or WrcDatabase())
        return await qs.get_available_years()

    @classmethod
    async def list_events_for_year(
        cls, year: int, db: WrcDatabase | None = None
    ) -> list[EventMetadata]:
        """Return all events stored for a given year, ordered by start date."""
        qs = WrcQueryService(db or WrcDatabase())
        return await qs.get_events_for_year(year=year)

    @classmethod
    async def create(
        cls,
        *,
        event_id: int | None = None,
        name: str | None = None,
        year: int | None = None,
        rally_id: int | None = None,
        db: WrcDatabase | None = None,
    ) -> "WrcSession":
        qs = WrcQueryService(db or WrcDatabase())

        if event_id is None and name is None:
            raise SessionInputValidationException(
                message="Provide either event_id or name to start a session."
            )

        if event_id is None:
            event = await qs.get_event_by_name(name=name, year=year)
            if event is None:
                detail = f"year={year}" if year else "no year filter"
                raise SessionInputValidationException(
                    message=f"No event found matching name='{name}' ({detail})."
                )
        else:
            event = await qs.get_event_by_id(event_id=event_id)
            if event is None:
                raise SessionInputValidationException(
                    message=f"No event found with event_id={event_id}."
                )

        event_id = event.event_id
        event_start_date = event.start_date.date()
        event_finish_date = event.finish_date.date()
        event_timezone = event_tz(event.time_zone_id)

        resolved_rally_id: int
        if rally_id is not None:
            resolved_rally_id = rally_id
        else:
            rally = await qs.get_default_rally_for_event(event_id=event_id)
            if rally is None:
                raise SessionInputValidationException(
                    message=f"No rally found for event_id={event_id}."
                )
            resolved_rally_id = rally.rally_id

        return cls(
            event_id=event_id,
            rally_id=resolved_rally_id,
            query_service=qs,
            event_start_date=event_start_date,
            event_finish_date=event_finish_date,
            event_timezone=event_timezone,
        )

    async def entries(self) -> list[Entry]:
        """Return all entries for this rally."""
        return await self._qs.get_rally_entries(rally_id=self.rally_id)

    async def stages(self) -> list[Stage]:
        """Return all stages for this event, ordered by stage number."""
        return await self._qs.get_stages_for_event(event_id=self.event_id)

    async def split_times(
        self, stage_id: int | None = None, stage_number: int | None = None
    ):
        if stage_id is None:
            if stage_number is None:
                raise SessionInputValidationException(
                    message="Provide either stage_id or stage_number."
                )
            stage = await self._qs.get_stage_by_number(
                event_id=self.event_id, number=stage_number
            )
            if stage is None:
                raise SessionInputValidationException(
                    message=f"No stage found with number={stage_number} in event_id={self.event_id}."
                )
            stage_id = stage.stage_id
        return await self._qs.get_split_times(rally_id=self.rally_id, stage_id=stage_id)

    async def rally_standings(
        self,
        stage_id: int | None = None,
        stage_number: int | None = None,
    ):
        if stage_number is not None:
            stage = await self._qs.get_stage_by_number(
                event_id=self.event_id, number=stage_number
            )
            if stage is None:
                raise SessionInputValidationException(
                    message=f"No stage found with number={stage_number} in event_id={self.event_id}."
                )
            stage_id = stage.stage_id
        return await self._qs.get_rally_standings(
            rally_id=self.rally_id, stage_id=stage_id
        )
