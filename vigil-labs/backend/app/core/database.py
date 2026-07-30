"""
VIGIL LABS - Database Configuration
Async SQLAlchemy engine with connection pooling, migration support,
and production-ready session management.
"""
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from app.core.config import settings

logger = logging.getLogger("vigil_labs.database")

# Determine pool class based on database type
# SQLite doesn't support connection pooling
is_sqlite = "sqlite" in settings.DATABASE_URL

engine_kwargs = {
    "echo": settings.DEBUG,
    "future": True,
}

if is_sqlite:
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL/MySQL production settings
    engine_kwargs["poolclass"] = AsyncAdaptedQueuePool
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    engine_kwargs["pool_pre_ping"] = True  # Verify connections before use
    engine_kwargs["pool_recycle"] = 3600  # Recycle connections after 1 hour

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency for getting async database sessions.
    Properly handles commit/rollback on request lifecycle.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.
    In production, use Alembic migrations instead of create_all.
    """
    if settings.ENVIRONMENT == "production":
        logger.info("Production mode: skipping auto-create. Use 'alembic upgrade head' for migrations.")
        return
    
    logger.info(f"Initializing database: {settings.DATABASE_URL.split('://')[0]}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created/verified")


async def close_db():
    """Close database engine and release connections."""
    logger.info("Closing database connections")
    await engine.dispose()
