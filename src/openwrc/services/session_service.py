from datetime import datetime, timedelta, timezone
from functools import cached_property
from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.exceptions.session_exceptions import (
    SessionInputValidationException,
    SessionDateOutOfRangeException,
)
from openwrc.models.external_api import EventMetadata, ItineraryLeg
from openwrc.services.event_service import EventInfoService
from openwrc.services.result_service import RallyResultService
import httpx


class WrcSession:
    def __init__(self) -> None:
        """
        Start a persistent session to query a WRC event.

        Initializing the session:
        - session identification
            - you can use the raw event and rally id to start a session.
            - for usability, we also allow specifying a session by year and location name. for example, for Monte-Carlo 2026, try WrcSession(year=2026, location='monte-carlo')
        - rally event results
            - by stage
            - by split
            - deltas
        - rally event entries
            - entries by class
            - driver & co driver info
        """
        self.external_api_client = WrcApiClient()
        self._rally_itinerary_by_day: dict[int, ItineraryLeg] | None = None

    @classmethod
    async def create(
        cls,
        *,
        event_id: int | None = None,
        rally_id: int | None = None,
        year: int | None = None,
        location: str | None = None,
    ) -> "WrcSession":
        """Factory for creating a session

        Args:
            event_id (int): _description_
            rally_id (int): _description_
            year (int): _description_
            location (str): _description_

        """
        session = cls()
        await session._start_session(
            event_id=event_id, rally_id=rally_id, year=year, location=location
        )
        return session

    async def _start_session(
        self,
        *,
        event_id: int | None = None,
        rally_id: int | None = None,
        year: int | None = None,
        location: str | None = None,
    ) -> EventMetadata:
        # need both event id and rally id, or year and location
        if year and location:
            raise SessionInputValidationException(
                message="session via year and location is not yet supported"
            )
        elif event_id:
            try:
                self.event_metadata = await self.event_service.get_event_metadata(
                    event_id=event_id
                )
                self.event_id = event_id
            except httpx.HTTPStatusError:
                raise SessionInputValidationException(
                    message=f"event id {event_id} does not map to a valid wrc event."
                )
        else:
            raise SessionInputValidationException(
                message="Need either event id OR year and location"
            )
        if rally_id and rally_id not in [
            rally.rally_id for rally in self.event_metadata.rallies
        ]:
            raise SessionInputValidationException(
                message=f"Rally {rally_id} is not in event {event_id}"
            )
        self.rally_id = rally_id or self.event_metadata.rallies[0].rally_id

        # set up some properties
        self._rally_itinerary_by_day = (
            await self.event_service.get_rally_itinerary_by_day(
                event_id=self.event_id, rally_id=self.rally_id
            )
        )

    @property
    def rally_itinerary(self) -> dict[int, ItineraryLeg]:
        return self._rally_itinerary_by_day

    @cached_property
    def event_service(self) -> EventInfoService:
        return EventInfoService(self.external_api_client)

    @cached_property
    def result_service(self) -> RallyResultService:
        return RallyResultService(self.external_api_client)

    @property
    def current_itinerary_leg_number(self) -> int:
        cur_datetime = datetime.now(tz=timezone.utc)
        if (
            cur_datetime >= self.event_metadata.finish_date + timedelta(days=1)
            or cur_datetime < self.event_metadata.start_date
        ):
            raise SessionDateOutOfRangeException(
                cur_datetime,
                self.event_metadata.start_date,
                self.event_metadata.finish_date,
            )
        current_day = 1 + (
            (cur_datetime - self.event_metadata.start_date) // timedelta(days=1)
        )
        if current_day not in self.rally_itinerary:
            raise SessionDateOutOfRangeException(
                cur_datetime,
                self.event_metadata.start_date,
                self.event_metadata.finish_date,
            )
        return current_day

    @property
    def get_latest_stage_order(self) -> int:
        pass
