from pydantic import BaseModel

from openwrc.models.external_api.result_models import StageResults


class CumulativeStageResults(BaseModel):
    stage_id: int
    results: StageResults


class CumulativeRallyResultsByStage(BaseModel):
    event_id: int
    rally_id: int
    cumulative_stage_results: list[CumulativeStageResults]
