
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import uuid
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from fastapi import status
from app.main import app
from app.auth.validate import get_current_user_profile
from app.auth.subscription_limits import check_image_generation_limit
from app.database.database import AsyncSessionLocal
from app.models.jobs import JobStatus
from app.services.subscription_services.limit_checker import LimitCheckResult

# Override dependencies
@pytest.fixture
def client(mock_profile):
    # Mock the profile dependency
    app.dependency_overrides[get_current_user_profile] = lambda: mock_profile

    # Mock the limit check dependency
    mock_limit_result = LimitCheckResult(
        images_used=0,
        limit=10,
        plan_name="free",
        reset_at=datetime.now(timezone.utc) + timedelta(days=30)
    )
    app.dependency_overrides[check_image_generation_limit] = lambda: mock_limit_result

    with TestClient(app) as c:
        yield c

    # Clean up overrides
    app.dependency_overrides = {}

@pytest.fixture
def mock_async_session():
    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.get = AsyncMock()
    return mock_session

@pytest.fixture
def mock_async_session_factory(mock_async_session):
    # Mock the context manager for AsyncSessionLocal
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__.return_value = mock_async_session
    mock_factory.return_value.__aexit__.return_value = None
    return mock_factory

@patch("app.api.routes.tasks.AsyncSessionLocal")
@patch("app.api.routes.tasks.process_video_pipeline")
@patch("app.api.routes.tasks.events")
def test_create_task_success(
    mock_events,
    mock_pipeline_task,
    mock_session_factory,
    client,
    mock_async_session
):
    mock_session_factory.return_value.__aenter__.return_value = mock_async_session

    # Valid request
    payload = {"url": "https://www.youtube.com/watch?v=validvideo"}

    response = client.post("/api/tasks/", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "task_id" in data
    assert data["status"] == JobStatus.queued.value

    # Verify DB interaction
    assert mock_async_session.add.called
    assert mock_async_session.commit.called

@patch("app.api.routes.tasks.AsyncSessionLocal")
def test_create_task_invalid_url(
    mock_session_factory,
    client
):
    # Invalid URL
    payload = {"url": "https://notyoutube.com/video"}

    response = client.post("/api/tasks/", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

@patch("app.api.routes.tasks.AsyncSessionLocal")
def test_get_task_status_success(
    mock_session_factory,
    client,
    mock_async_session,
    mock_job,
    mock_job_id
):
    mock_session_factory.return_value.__aenter__.return_value = mock_async_session
    mock_async_session.get.return_value = mock_job

    response = client.get(f"/api/tasks/{mock_job_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["task_id"] == str(mock_job_id)
    assert data["status"] == JobStatus.queued.value

@patch("app.api.routes.tasks.AsyncSessionLocal")
def test_get_task_status_not_found(
    mock_session_factory,
    client,
    mock_async_session
):
    mock_session_factory.return_value.__aenter__.return_value = mock_async_session
    mock_async_session.get.return_value = None

    random_id = uuid.uuid4()
    response = client.get(f"/api/tasks/{random_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND

@patch("app.api.routes.tasks.AsyncSessionLocal")
def test_get_task_status_forbidden(
    mock_session_factory,
    client,
    mock_async_session,
    mock_job
):
    mock_session_factory.return_value.__aenter__.return_value = mock_async_session

    # Job belongs to someone else
    mock_job.user_id = uuid.uuid4() # Different ID than mock_profile's
    mock_async_session.get.return_value = mock_job

    response = client.get(f"/api/tasks/{mock_job.id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND # Logic in route returns 404 for ownership check failure
