from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.db.models import Base


def _get_engine() -> AsyncEngine:
    settings = get_settings()
    if settings.database_url.startswith("sqlite+aiosqlite:///"):
        db_file = settings.database_url.replace("sqlite+aiosqlite:///", "", 1)
        db_path = Path(db_file)
        if db_path.parent:
            db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_async_engine(settings.database_url, future=True)


engine = _get_engine()
SessionFactory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
