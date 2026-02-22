"""
DB infrastructure: engine, session factory, schema init.
All other services take a WrcDatabase instance rather than managing their own engine.
"""

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from openwrc.models.db.base import Base


class WrcDatabase:

    def __init__(self, db_path: str = "wrc.db") -> None:
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{db_path}", echo=False)
        self._session_factory = async_sessionmaker(
            bind=self.engine, class_=AsyncSession, expire_on_commit=False
        )
        self._initialized = False

    async def _ensure_schema(self) -> None:
        if not self._initialized:
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all, checkfirst=True)
            self._initialized = True

    async def init(self) -> None:
        await self._ensure_schema()

    @asynccontextmanager
    async def session(self):
        await self._ensure_schema()
        async with self._session_factory() as s:
            yield s
