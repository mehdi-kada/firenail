import uuid
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

import pytest_asyncio

from app.database.database import Base, get_db
from app.auth.validate import get_current_user_profile
from app.models.images import Image
from app.models.profiles import Profile
from app.models.jobs import Job
from app.main import main_app
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_engine():
    """ Create a test database engine """
    engine: AsyncEngine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False},
     poolclass=StaticPool)
    # create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine

    # Drop all tables after ending the test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_engine):
    """ creates an async database session for testing """
    async_session_maker = async_sessionmaker(test_engine)
    async with async_session_maker() as session:
        yield session  # Fresh session per test


@pytest_asyncio.fixture
async def test_profile(test_db):
    """ Creates a test user profile in the database """
    profile = Profile(id=uuid.uuid4(), username="testuser")
    test_db.add(profile)
    await test_db.commit()
    await test_db.refresh(profile)
    return profile


@pytest_asyncio.fixture
async def test_job(test_db, test_profile):
    """Create a test job."""
    job = Job(
        id=uuid.uuid4(),
        profile_id=test_profile.id,
        status="completed",
        video_url="https://youtube.com/watch?v=test"
    )
    test_db.add(job)
    await test_db.commit()
    await test_db.refresh(job)
    return job


@pytest_asyncio.fixture
async def test_images(test_db, test_job, test_profile):
    """ create test images """
    images = []
    for i in range(5):
        image = Image(
            id = uuid.uuid4(),
            job_id = test_job.id,
            profile_id= test_profile.id,
            keywords=[f"keyword {j}" for j in range(3)],
            storage_public_url=f"https://example.com/image{i}.jpg",
        )

        test_db.add(image)
        images.append(image)

    await test_db.commit()
    for image in images:
        await test_db.refresh(image)

    return images 


# time for overriding dependencies to use the one for tesing for the api endponit 
@pytest_asyncio.fixture
async def client(test_profile, test_db):

    async def override_get_db():
        yield test_db

    async def override_get_current_profile():
        return test_profile
    
    main_app.dependency_overrides[get_db] = override_get_db
    main_app.dependency_overrides[get_current_user_profile] = override_get_current_profile

    # create the test cline tnow pretty boy
    async with AsyncClient(
        transport=ASGITransport(app=main_app),
        base_url="http://test"
    ) as ac:
        yield ac

    main_app.dependency_overrides.clear()
