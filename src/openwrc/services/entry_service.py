from openwrc.models.external_api import ApiRallyEntries
from openwrc.services.base_service import BaseService


class RallyEntryService(BaseService):

    async def get_rally_entries(self, event_id: int, rally_id: int) -> ApiRallyEntries:
        return await self.external_api_client.get_rally_entries(
            event_id=event_id, rally_id=rally_id
        )

    async def get_entry_id_to_driver_name(self, event_id: int, rally_id: int):
        entries = await self.get_rally_entries(event_id=event_id, rally_id=rally_id)
        return {entry.entry_id: entry.driver.abbv_name for entry in entries}
