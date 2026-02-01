"""
SQL storage service for WRC data.
Fetches from API and writes through to database.
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from openwrc.clients.wrc_api_client import WrcApiClient
from openwrc.models.db.base import Base


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
