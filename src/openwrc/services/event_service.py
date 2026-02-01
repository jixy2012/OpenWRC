from openwrc.exceptions.event_exceptions import (
    RallyNotFoundException,
    StageIndexOutOfRangeException,
    StageNotFoundException,
    StartListNotFoundException,
    StartListNotAvailableYetException,
)
from openwrc.models.external_api import (
    ApiEventMetadata,
    ApiItinerary,
    ApiItineraryLeg,
    ApiStage,
    ApiStartList,
)
from openwrc.models.external_api import ApiRallyMetadata
from openwrc.models.services import Stages
from openwrc.services.base_service import BaseService


class EventInfoService(BaseService):
    """metadata and itinerary information tied to an event"""

    def list_events(self, year: int) -> list:
        raise NotImplementedError("cannot list all events yet!")

    async def get_event_metadata(self, event_id: int) -> ApiEventMetadata:
        return await self.external_api_client.get_event_metadata(event_id=event_id)

    async def get_event_rallies(self, event_id: int) -> list[ApiRallyMetadata]:
        return (await self.get_event_metadata(event_id=event_id)).rallies

    async def get_event_rally(self, event_id: int, rally_id: int) -> ApiRallyMetadata:
        rallies = await self.get_event_rallies(event_id=event_id)
        target_rally = filter(lambda rally: rally.rally_id == rally_id, rallies)
        try:
            # assume rally id is unique
            return next(target_rally)
        except StopIteration:
            raise RallyNotFoundException(rally_id=rally_id, event_id=event_id)

    async def get_rally_itinerary_id(self, event_id: int, rally_id: int) -> int:
        rally = await self.get_event_rally(event_id=event_id, rally_id=rally_id)
        return rally.itinerary_id

    async def get_rally_itinerary(self, event_id: int, rally_id: int) -> ApiItinerary:
        id = await self.get_rally_itinerary_id(event_id=event_id, rally_id=rally_id)
        return await self.external_api_client.get_event_itineraries(
            event_id=event_id, itinerary_id=id
        )

    async def get_rally_itinerary_by_day(
        self, event_id: int, rally_id: int
    ) -> dict[int, ApiItineraryLeg]:
        itinerary = await self.get_rally_itinerary(event_id=event_id, rally_id=rally_id)
        return {
            itinerary_leg.order: itinerary_leg
            for itinerary_leg in itinerary.itinerary_legs
        }

    async def get_rally_stages(self, event_id: int, rally_id: int) -> Stages:
        itinerary = await self.get_rally_itinerary(event_id=event_id, rally_id=rally_id)
        stages = []
        for itinerary_leg in itinerary.itinerary_legs:
            for section in itinerary_leg.itinerary_sections:
                stages.extend(section.stages)
        return stages

    async def get_rally_stage_by_id(
        self, event_id: int, rally_id: int, stage_id: int
    ) -> ApiStage:
        stages = await self.get_rally_stages(event_id=event_id, rally_id=rally_id)
        for stage in stages:
            if stage.stage_id == stage_id:
                return stage
        raise StageNotFoundException(
            rally_id=rally_id, event_id=event_id, stage_id=stage_id
        )

    async def get_rally_stage_by_order(
        self, event_id: int, rally_id: int, order: int
    ) -> ApiStage:
        stages = await self.get_rally_stages(event_id=event_id, rally_id=rally_id)
        for stage in stages:
            if stage.number == order:
                return stage
        raise StageIndexOutOfRangeException(
            rally_id=rally_id, event_id=event_id, order=order
        )

    async def get_rally_start_list_ids(
        self,
        event_id: int,
        rally_id: int,
    ) -> list[int | None]:
        itinerary = await self.get_rally_itinerary(event_id=event_id, rally_id=rally_id)
        return [leg.start_list_id for leg in itinerary.itinerary_legs]

    async def get_rally_start_list_by_id(
        self,
        event_id: int,
        start_list_id: int,
    ) -> ApiStartList:
        return await self.external_api_client.get_event_start_list(
            event_id=event_id, start_list_id=start_list_id
        )

    async def get_rally_start_list_by_order(
        self, event_id: int, rally_id: int, order: int
    ) -> ApiStartList:
        start_list_ids = await self.get_rally_start_list_ids(
            event_id=event_id, rally_id=rally_id
        )
        try:
            target_start_list_id = start_list_ids[order]
            if target_start_list_id is None:
                raise StartListNotAvailableYetException(
                    rally_id=rally_id, event_id=event_id, order=order
                )
            return await self.get_rally_start_list_by_id(
                event_id=event_id, start_list_id=target_start_list_id
            )
        except IndexError:
            raise StartListNotFoundException(
                rally_id=rally_id, event_id=event_id, order=order
            )
