# extracts info from external wrc apis

import asyncio
from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.models.external_api import ApiEntry, ApiEventMetadata


def get_rally_ids(event_metadata: ApiEventMetadata) -> list[int]:
    return [rally.rally_id for rally in event_metadata.rallies]


def get_rally_id_to_itinerary_id(event_metadata: ApiEventMetadata) -> dict[int, int]:
    return {rally.rally_id: rally.itinerary_id for rally in event_metadata.rallies}


async def get_rally_id_to_api_entries(
    client: WrcApiClient, event_id: int, rally_ids: list[int]
) -> dict[int, list[ApiEntry]]:
    composite_entries = await asyncio.gather(
        *[client.get_rally_entries(event_id=event_id, rally_id=id) for id in rally_ids]
    )
    flattened_entries = []
    for entries in composite_entries:
        flattened_entries.extend(entries)
    return flattened_entries
