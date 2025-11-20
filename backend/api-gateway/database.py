"""
Database Connection and Session Management
==========================================

PostgreSQL database connection using SQLAlchemy 2.0 async engine.
Provides session factory and dependency injection for FastAPI.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from contextlib import asynccontextmanager
import logging

from config import settings

logger = logging.getLogger(__name__)

# Convert postgresql:// to postgresql+asyncpg:// for async support
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Determine if using SQLite or PostgreSQL
is_sqlite = DATABASE_URL.startswith("sqlite")

# Create async engine with database-specific configuration
engine_kwargs = {
    "echo": settings.LOG_LEVEL == "DEBUG",
    "future": True
}

# PostgreSQL-specific connection pooling (not supported by SQLite)
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_pre_ping": True,  # Verify connections before using
    })
else:
    # SQLite uses NullPool (no connection pooling)
    engine_kwargs["poolclass"] = NullPool

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Declarative base for models
Base = declarative_base()


async def init_db():
    """
    Initialize database (create tables if they don't exist)

    In production, use Alembic migrations instead.
    This is useful for development/testing.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    logger.info("Database connections closed")


@asynccontextmanager
async def get_db_context():
    """
    Context manager for database sessions

    Usage:
        async with get_db_context() as db:
            result = await db.execute(query)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db():
    """
    Dependency injection for FastAPI routes

    Usage:
        @app.get("/cameras")
        async def get_cameras(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Camera))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
