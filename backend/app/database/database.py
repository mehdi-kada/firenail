from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from sqlalchemy import create_engine
from uuid import uuid4
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", "sqlite:///./test.db")

# Async engine for FastAPI routes
async_engine = create_async_engine(
    DATABASE_URL,
    poolclass=AsyncAdaptedQueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    },
)

# Sync engine for Celery tasks and migrations
sync_engine = create_engine(SYNC_DATABASE_URL, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine)
sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

