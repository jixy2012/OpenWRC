from openwrc.models.external_api import RallyResults, StageResults, StageTimeResults
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

    def get_overall_stage_results_by_id(
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
        return self.external_api_client.get_event_stage_results(
            event_id=event_id, rally_id=rally_id, stage_id=stage_id
        )

    def get_single_stage_results_by_id(
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
        return self.external_api_client.get_event_stage_time_results(
            event_id=event_id, rally_id=rally_id, stage_id=stage_id
        )

    def get_single_stage_results_by_order(
        self, event_id: int, rally_id: int, order: int
    ) -> StageTimeResults:
        stage = self.event_service.get_rally_stage_by_order(
            event_id=event_id, rally_id=rally_id, order=order
        )
        return self.external_api_client.get_event_stage_time_results(
            event_id=event_id, stage_id=stage.stageId, rally_id=rally_id
        )
