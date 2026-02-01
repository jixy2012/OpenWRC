"""
CRUD utilities for storing WRC data models.
Stateless helper functions that transform API models to DB models and store them.
"""

import asyncio
from typing import TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession

from openwrc.models.db.base import Base
from openwrc.models.db.itinerary import StartList, StartListPublishStatus
from openwrc.models.external_api import (
    ApiEventMetadata,
    ApiItinerary,
    ApiItineraryLeg,
    ApiRallyEntries,
    ApiRallyResults,
    ApiShakedownTimeResults,
    ApiSplitTimeResults,
    ApiStageTimeResults,
    ApiStartList,
)
from openwrc.models.external_api.base_external_model import WrcExternalApiBaseModel
from openwrc.storage.mappers import (
    map_api_control_to_db_model,
    map_api_event_to_db_model,
    map_api_itinerary_leg_to_db_model,
    map_api_itinerary_section_to_db_model,
    map_api_itinerary_to_db_model,
    map_api_rally_to_db_model,
    map_api_stage_to_db_model,
)


T = TypeVar("T", bound=Base)
ApiT = TypeVar("ApiT", bound=WrcExternalApiBaseModel)


async def upsert_instance(session: AsyncSession, instance: T) -> T:
    """
    Generic upsert helper.
    Updates if exists, inserts if not.
    """
    return await session.merge(instance=instance)


async def upsert_from_api(
    session: AsyncSession,
    api_model: ApiT,
    db_model_class: Type[T],
    exclude: set[str] | None = None,
    **extra_fields,
) -> T:
    """
    Convenience wrapper that converts API model to DB model and upserts.

    Args:
        session: Database session
        api_model: API model instance
        db_model_class: DB model class to instantiate
        exclude: Set of field names to exclude from model_dump (e.g., nested objects)
        **extra_fields: Additional fields to add to the DB model (e.g., foreign keys)
    """
    data = api_model.model_dump(exclude=exclude)
    data.update(extra_fields)

    return await upsert_instance(session=session, instance=db_model_class(**data))


async def upsert_event_metadata(
    session: AsyncSession, api_response: ApiEventMetadata
) -> bool:
    event = map_api_event_to_db_model(api_event=api_response)
    # upsert event first for fk consistency
    await upsert_instance(session=session, instance=event)

    rallies_upsert_futures = [
        upsert_instance(session=session, instance=map_api_rally_to_db_model(rally))
        for rally in api_response.rallies
    ]
    await asyncio.gather(*rallies_upsert_futures)
    return True


async def upsert_start_list(session: AsyncSession, api_response: ApiStartList) -> bool:
    # TODO
    pass


async def upsert_event_itineraries(
    session: AsyncSession, api_response: ApiItinerary
) -> bool:
    itinerary = map_api_itinerary_to_db_model(api_itinerary=api_response)

    async def try_upsert_leg(leg: ApiItineraryLeg) -> bool:
        """_summary_

        Args:
            leg (ApiItineraryLeg): if the start list of the leg is not yet available, insert the start list with published status to '
        """
        start_list = await session.get(StartList, leg.start_list_id)
        if not start_list:
            # try inserting an unpublished start list
            await upsert_instance(
                session=session,
                instance=StartList(
                    start_list_id=leg.start_list_id,
                    event_id=api_response.event_id,
                    name="",
                    published_status=StartListPublishStatus.UNPUBLISHED,
                ),
            )
        await upsert_instance(
            session=session, instance=map_api_itinerary_leg_to_db_model(leg)
        )

    itinerary_legs_futures = [
        try_upsert_leg(leg=leg) for leg in api_response.itinerary_legs
    ]

    sections_futures = []
    controls_futures = []
    stages_futures = {}

    # unpack the complex objects
    for leg in api_response.itinerary_legs:
        for section in leg.itinerary_sections:
            sections_futures.append(
                upsert_instance(
                    session=session,
                    instance=map_api_itinerary_section_to_db_model(
                        api_itinerary_section=section
                    ),
                )
            )
            controls_futures.extend(
                [
                    upsert_instance(
                        session=session,
                        instance=map_api_control_to_db_model(
                            api_control=control,
                            itinerary_section_id=section.itinerary_section_id,
                        ),
                    )
                    for control in section.controls
                ]
            )
            stages_futures.extend(
                [
                    upsert_instance(
                        session=session,
                        instance=map_api_stage_to_db_model(
                            api_stage=stage,
                            itinerary_section_id=section.itinerary_section_id,
                        ),
                    )
                    for stage in section.stages
                ]
            )

    # start with parent itinerary object
    await upsert_instance(session=session, instance=itinerary)

    # then legs
    await asyncio.gather(*itinerary_legs_futures)
    # then the sections
    await asyncio.gather(*sections_futures)

    # lastly, the lowest layer controls and stages
    await asyncio.gather(*controls_futures, *stages_futures)
    return True


def upsert_rally_entries(session: AsyncSession, api_response: ApiRallyEntries) -> bool:
    pass


# results section TODO
def upsert_rally_results(session: AsyncSession, api_response: ApiRallyResults) -> bool:
    pass


def upsert_stage_time_results(
    session: AsyncSession, api_response: ApiStageTimeResults
) -> bool:
    pass


def upsert_split_time_results(
    session: AsyncSession, api_response: ApiSplitTimeResults
) -> bool:
    pass


def upsert_shakedown_results(
    session: AsyncSession, api_response: ApiShakedownTimeResults
) -> bool:
    pass
