from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel
from src.openwrc.models.external_api import (
    Itinerary,
    EventMetadata,
    RallyEntries,
    StageResults,
    RallyResults,
)

URL_BASE = "https://p-p.redbull.com/rb-wrccom-lintegration-yv-prod/api/events"
T = TypeVar("T", bound=BaseModel)


class WrcApiClient:
    def __init__(self, base_url: str = URL_BASE, timeout: float = 30.0) -> None:
        self.base_url = base_url
        self.client = httpx.Client(
            timeout=timeout, base_url=self.base_url, follow_redirects=True
        )

    def _get(
        self,
        external_path: str,
        params: Optional[dict[str, str]] = None,
        *,
        model: Optional[Type[T]] = None,
    ) -> T | dict:
        response = self.client.get(external_path, params=params)
        response.raise_for_status()
        data = response.json()
        return model.model_validate(data) if model else data

    def get_event_metadata(self, event_id: int) -> EventMetadata:
        """
        example: /635.json

        Args:
            event_id (int)

        Returns:
            EventMetadata object
        """
        return self._get(f"/{event_id}.json", model=EventMetadata)

    def get_event_itineraries(self, event_id: int, itinerary_id: int) -> Itinerary:
        """example: /635/itineraries/1321.json

        Args:
            event_id (int): identifier of the event (NOT rally)
            itinerary_id (int): you can find this id from the event metadata

        Returns:
            dict
        """
        return self._get(
            f"/{event_id}/itineraries/{itinerary_id}.json", model=Itinerary
        )

    def get_rally_entries(self, event_id: int, rally_id: int) -> RallyEntries:
        """example: /635/rallies/703/entries.json

        Args:
            event_id (int)
            rally_id (int)

        Returns:
            dict
        """
        return self._get(
            f"/{event_id}/rallies/{rally_id}/entries.json", model=RallyEntries
        )

    def get_rally_results(self, event_id: int, rally_id: int) -> RallyResults:
        """example: /555/rallies/603/results.json

        Args:
            event_id (int)
            rally_id (int)

        Returns:
            dict
        """
        return self._get(
            f"/{event_id}/rallies/{rally_id}/results.json", model=RallyResults
        )

    def get_event_stage_results(
        self, event_id: int, stage_id: int, rally_id: int
    ) -> StageResults:
        """example: 555/stages/10281/results.json?rallyId=603

        Args:
            event_id (int)
            stage_id (int)
            rally_id (int)

        Returns:
            dict
        """
        return self._get(
            f"/{event_id}/stages/{stage_id}/results.json",
            params={"rallyId": rally_id},
            model=StageResults,
        )
