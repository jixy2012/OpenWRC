import asyncio
from openwrc.models.external_api import (
    RallyResults,
    ShakedownTimeResults,
    SplitTimeResults,
    StageResults,
    StageTimeResults,
)
from openwrc.models.services.result_models import (
    CumulativeRallyResultsByStage,
    CumulativeStageResults,
)
from openwrc.services.base_service import BaseService
from openwrc.services.event_service import EventInfoService


class RallyResultService(BaseService):
    @property
    def event_service(self):
        if not hasattr(self, "_event_service"):
            self._event_service = EventInfoService(self.external_api_client)
        return self._event_service

    def get_rally_results(self, event_id: int, rally_id: int) -> RallyResults:
        return self.external_api_client.get_rally_results(
            event_id=event_id, rally_id=rally_id
        )

    async def get_cumulative_stage_results_by_id(
        self, event_id: int, rally_id: int, stage_id: int
    ) -> StageResults:
        """overall results for the entire rally up until that stage

        Args:
            event_id (int): _description_
            rally_id (int): _description_
            stage_id (int): _description_

        Returns:
            StageResults: _description_
        """
        return await self.external_api_client.get_event_stage_results(
            event_id=event_id, rally_id=rally_id, stage_id=stage_id
        )

    async def get_single_stage_results_by_id(
        self, event_id: int, rally_id, stage_id: int
    ) -> StageTimeResults:
        """results for a single stage_summary_

        Args:
            event_id (int): _description_
            rally_id (_type_): _description_
            stage_id (int): _description_

        Returns:
            StageTimeResults
        """
        return await self.external_api_client.get_event_stage_time_results(
            event_id=event_id, rally_id=rally_id, stage_id=stage_id
        )

    async def get_single_stage_results_by_order(
        self, event_id: int, rally_id: int, order: int
    ) -> StageTimeResults:
        stage = await self.event_service.get_rally_stage_by_order(
            event_id=event_id, rally_id=rally_id, order=order
        )
        return await self.get_single_stage_results_by_id(
            event_id=event_id, stage_id=stage.stage_id, rally_id=rally_id
        )

    async def get_stage_split_time_results_by_id(
        self, event_id: int, rally_id, stage_id: int
    ) -> SplitTimeResults:
        return await self.external_api_client.get_rally_stage_split_time_results(
            event_id=event_id, rally_id=rally_id, stage_id=stage_id
        )

    async def get_stage_split_time_results_by_order(
        self, event_id: int, rally_id: int, order: int
    ) -> SplitTimeResults:
        stage = await self.event_service.get_rally_stage_by_order(
            event_id=event_id, rally_id=rally_id, order=order
        )
        return await self.get_stage_split_time_results_by_id(
            event_id=event_id, rally_id=rally_id, stage_id=stage.stage_id
        )

    async def get_cumulative_rally_results_by_stage(
        self, event_id: int, rally_id: int
    ) -> CumulativeRallyResultsByStage:
        stages = await self.event_service.get_rally_stages(
            event_id=event_id, rally_id=rally_id
        )

        async def getCumulativeStageResult(stage_id: int):
            return CumulativeStageResults(
                stage_id=stage_id,
                results=await self.get_cumulative_stage_results_by_id(
                    event_id=event_id, rally_id=rally_id, stage_id=stage_id
                ),
            )

        futures = [
            getCumulativeStageResult(stage_id=stage.stage_id) for stage in stages
        ]
        return CumulativeRallyResultsByStage(
            rally_id=rally_id,
            event_id=event_id,
            cumulative_stage_results=await asyncio.gather(*futures),
        )

    async def get_event_shakedown_results(
        self, event_id: int, shakedown_number: int = 1
    ) -> ShakedownTimeResults:
        return await self.external_api_client.get_event_shakedown_results(
            event_id=event_id, shakedown_number=shakedown_number
        )

    async def get_current_split_deltas(
        self, event_id: int, rally_id: int, stage_id: int
    ):
        pass
