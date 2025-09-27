from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")  # Change to your actual database URL

engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool
)

AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# dependency for getting DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session