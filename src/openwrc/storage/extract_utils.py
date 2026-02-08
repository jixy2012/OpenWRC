# extracts info from external wrc apis

import asyncio
from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.models.external_api import ApiEntry, ApiEventMetadata, ApiItinerary


async def get_event_info(
    client: WrcApiClient, event_id: int
) -> tuple[ApiEventMetadata, list[ApiItinerary], list[ApiEntry]]:
    """
    get event info, including metadata, itineraries, and entries
    these objects have almost infinite ttl, rarely requires update

    Args:
        client (WrcApiClient): _description_
        event_id (int): _description_

    Returns:
        tuple[ApiEventMetadata, list[ApiItinerary], list[ApiEntry]]: _description_
    """
    event_metadata = await client.get_event_metadata(event_id=event_id)
    rally_ids = [rally.rally_id for rally in event_metadata.rallies]
    itinerary_ids = [rally.itinerary_id for rally in event_metadata.rallies]
    itineraries = await asyncio.gather(
        *[
            client.get_event_itineraries(event_id=event_id, itinerary_id=id)
            for id in itinerary_ids
        ]
    )
    entries = await asyncio.gather(
        *[client.get_rally_entries(event_id=event_id, rally_id=id) for id in rally_ids]
    )
    return event_metadata, itineraries, entries
