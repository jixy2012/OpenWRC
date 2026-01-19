from openwrc.exceptions.event_exceptions import (
    RallyNotFoundException,
    StageIndexOutOfRangeException,
    StageNotFoundException,
)
from openwrc.models.external_api import EventMetadata, Itinerary, Stage
from openwrc.models.external_api.event_models import RallyMetadata
from openwrc.models.services import Stages
from openwrc.services.base_service import BaseService


class EventInfoService(BaseService):
    """metadata and itinerary information tied to an event"""

    def list_events(self, year: int) -> list:
        raise NotImplementedError("cannot list all events yet!")

    def get_event_metadata(self, event_id: int) -> EventMetadata:
        return self.external_api_client.get_event_metadata(event_id=event_id)

    def get_event_rallies(self, event_id: int) -> list[RallyMetadata]:
        return self.get_event_metadata(event_id=event_id).rallies

    def get_event_rally(self, event_id: int, rally_id: int) -> RallyMetadata:
        rallies = self.get_event_rallies(event_id=event_id)
        target_rally = filter(lambda rally: rally.rallyId == rally_id, rallies)
        try:
            # assume rally id is unique
            return next(target_rally)
        except StopIteration:
            raise RallyNotFoundException(rally_id=rally_id, event_id=event_id)

    def get_rally_itinerary_id(self, event_id: int, rally_id: int) -> int:
        rally = self.get_event_rally(event_id=event_id, rally_id=rally_id)
        return rally.itineraryId

    def get_rally_itinerary(self, event_id: int, rally_id: int) -> Itinerary:
        id = self.get_rally_itinerary_id(event_id=event_id, rally_id=rally_id)
        return self.external_api_client.get_event_itineraries(
            event_id=event_id, itinerary_id=id
        )

    def get_rally_stages(self, event_id: int, rally_id: int) -> Stages:
        itinerary = self.get_rally_itinerary(event_id=event_id, rally_id=rally_id)
        stages = []
        for itinerary_leg in itinerary.itineraryLegs:
            for section in itinerary_leg.itinerarySections:
                stages.extend(section.stages)
        return stages

    def get_rally_stage_by_id(
        self, event_id: int, rally_id: int, stage_id: int
    ) -> Stage:
        stages = self.get_rally_stages(event_id=event_id, rally_id=rally_id)
        for stage in stages:
            if stage.stageId == stage_id:
                return stage
        raise StageNotFoundException(
            rally_id=rally_id, event_id=event_id, stage_id=stage_id
        )

    def get_rally_stage_by_order(
        self, event_id: int, rally_id: int, order: int
    ) -> Stage:
        stages = self.get_rally_stages(event_id=event_id, rally_id=rally_id)
        for stage in stages:
            if stage.number == order:
                return stage
        raise StageIndexOutOfRangeException(
            rally_id=rally_id, event_id=event_id, order=order
        )
