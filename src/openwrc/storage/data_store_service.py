"""
SQL storage service for WRC data.
Fetches from API and writes through to database.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.models.db.base import Base
from openwrc.models.external_api import ApiEventMetadata, ApiRallyEntries
from openwrc.storage.crud_utils import (
    upsert_codrivers,
    upsert_countries,
    upsert_drivers,
    upsert_entrants,
    upsert_entry_event_classes,
    upsert_event_classes,
    upsert_event_metadata,
    upsert_groups,
    upsert_manufacturers,
    upsert_rally_event_classes,
    upsert_rally_metadata,
)
from openwrc.storage.extract_utils import get_event_info
from openwrc.storage.transform_utils import (
    transform_api_entries,
    transform_api_event_metadata,
)


class WrcDataStore:

    def __init__(self, db_path: str = "wrc.db", api_client: WrcApiClient | None = None):
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
        self.SessionLocal = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self.api_client = api_client or WrcApiClient()

    async def init_db(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        return self.SessionLocal()

    # top level orchastrator
    async def etl_event_info(self, event_id: int) -> bool:
        event_metadata, itineraries, entries = await get_event_info(
            client=self.api_client, event_id=event_id
        )

    async def etl_event_metadata(self, event_metadata: ApiEventMetadata):
        rallies, event_classes, rally_to_class_ids = transform_api_event_metadata(
            api_response=event_metadata
        )
        async with self.SessionLocal() as session:
            await upsert_event_metadata(session=session, api_response=event_metadata)
            await upsert_rally_metadata(session=session, api_response=rallies)
            await upsert_event_classes(session=session, api_response=event_classes)
            for rally_id, class_ids in rally_to_class_ids.items():
                await upsert_rally_event_classes(
                    session=session, event_class_ids=class_ids, rally_id=rally_id
                )
            await session.commit()

    async def etl_event_entries(self, api_entries: ApiRallyEntries):
        (
            countries,
            manufacturers,
            entrants,
            groups,
            drivers,
            codrivers,
            event_classes,
            entry_id_to_event_class_ids,
        ) = transform_api_entries(api_response=api_entries)
        async with self.SessionLocal() as session:
            await upsert_countries(session=session, api_response=countries)
            await upsert_manufacturers(session=session, api_response=manufacturers)
            await upsert_entrants(session=session, api_response=entrants)
            await upsert_groups(session=session, api_response=groups)
            await upsert_drivers(session=session, api_response=drivers)
            await upsert_codrivers(session=session, api_response=codrivers)
            await upsert_event_classes(session=session, api_response=event_classes)
            for entry_id, class_ids in entry_id_to_event_class_ids.items():
                await upsert_entry_event_classes(
                    session=session, event_class_ids=class_ids, entry_id=entry_id
                )
            await session.commit()
