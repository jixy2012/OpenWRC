from typing import Optional, Type, TypeVar
import httpx
from pydantic import BaseModel, TypeAdapter
from openwrc.models.external_api import (
    Itinerary,
    EventMetadata,
    RallyEntries,
    StageResults,
    RallyResults,
    StageTimeResults,
    ShakedownTimeResults,
    StartList,
)

URL_BASE = "https://p-p.redbull.com/rb-wrccom-lintegration-yv-prod/api/events"
T = TypeVar("T", bound=BaseModel)


class WrcApiClient:
    def __init__(self, base_url: str = URL_BASE, timeout: float = 30.0) -> None:
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=timeout, base_url=self.base_url, follow_redirects=True
        )

    async def aclose(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "WrcApiClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def _get(
        self,
        external_path: str,
        params: Optional[dict[str, str]] = None,
        *,
        model: Optional[Type[T]] = None,
    ) -> T | dict:
        response = await self.client.get(external_path, params=params)
        response.raise_for_status()
        data = response.json()

        return TypeAdapter[T](model).validate_python(data) if model else data

    async def get_event_metadata(self, event_id: int) -> EventMetadata:
        """
        example: /635.json

        Args:
            event_id (int)

        Returns:
            EventMetadata object
        """
        return await self._get(f"/{event_id}.json", model=EventMetadata)

    async def get_event_itineraries(
        self, event_id: int, itinerary_id: int
    ) -> Itinerary:
        """example: /635/itineraries/1321.json

        Args:
            event_id (int): identifier of the event (NOT rally)
            itinerary_id (int): you can find this id from the event metadata

        Returns:
            dict
        """
        return await self._get(
            f"/{event_id}/itineraries/{itinerary_id}.json", model=Itinerary
        )

    async def get_rally_entries(self, event_id: int, rally_id: int) -> RallyEntries:
        """example: /635/rallies/703/entries.json

        Args:
            event_id (int)
            rally_id (int)

        Returns:
            dict
        """
        return await self._get(
            f"/{event_id}/rallies/{rally_id}/entries.json", model=RallyEntries
        )

    async def get_rally_results(self, event_id: int, rally_id: int) -> RallyResults:
        """example: /555/rallies/603/results.json

        Args:
            event_id (int)
            rally_id (int)

        Returns:
            dict
        """
        return await self._get(
            f"/{event_id}/rallies/{rally_id}/results.json", model=RallyResults
        )

    async def get_event_stage_results(
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
        return await self._get(
            f"/{event_id}/stages/{stage_id}/results.json",
            params={"rallyId": rally_id},
            model=StageResults,
        )

    async def get_event_stage_time_results(
        self, event_id: int, stage_id: int, rally_id: int
    ) -> StageTimeResults:
        """example: 555/stages/10281/stagetimes.json?rallyId=603

        Args:
            event_id (int)
            stage_id (int)
            rally_id (int)

        Returns:
            StageTimeResults
        """
        return await self._get(
            f"/{event_id}/stages/{stage_id}/stagetimes.json",
            params={"rallyId": rally_id},
            model=StageTimeResults,
        )

    async def get_event_shakedown_results(
        self,
        event_id: int,
        shakedown_number: int = 1,
    ) -> ShakedownTimeResults:
        """example: /635/shakedowntimes.json?shakedownNumber=1

        Args:
            event_id (int): _description_
            shakedown_number (int, optional): _description_. Defaults to 1.

        Returns:
            ShakedownTimeResults: _description_
        """

        return await self._get(
            f"/{event_id}/shakedowntimes.json",
            params={"shakedownNumber": shakedown_number},
            model=ShakedownTimeResults,
        )

    async def get_event_start_list(
        self, event_id: int, start_list_id: int
    ) -> StartList:
        """example: /635/startLists/2158.json

        Args:
            event_id (int): _description_
            start_list_id (int): _description_

        Returns:
            StartList: _description_
        """
        return await self._get(
            f"/{event_id}/startLists/{start_list_id}.json",
            model=StartList,
        )
