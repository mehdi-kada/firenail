
import pytest
from unittest.mock import MagicMock, AsyncMock
import uuid
from datetime import datetime, timezone
import os

# Set environment variables for tests
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_ANON_KEY"] = "test-anon-key"
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "test-service-role-key"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"
os.environ["SYNC_DATABASE_URL"] = "sqlite:///./test.db"
os.environ["GROQ_API_KEY"] = "test-groq-key"
os.environ["FIRECRAWL_KEY"] = "test-firecrawl-key"
os.environ["FREEPIK_API_KEY"] = "test-freepik-key"

# Mock objects that can be reused
@pytest.fixture
def mock_job_id():
    return uuid.uuid4()

@pytest.fixture
def mock_user_id():
    return uuid.uuid4()

@pytest.fixture
def mock_profile(mock_user_id):
    from app.models.profiles import Profile
    profile = MagicMock(spec=Profile)
    profile.id = mock_user_id
    profile.is_premium = True
    # Mock subscription relationship
    sub = MagicMock()
    sub.status = "active"
    sub.images_generated = 0
    profile.subscription = sub
    profile.images_generated = 0
    return profile

@pytest.fixture
def mock_job(mock_job_id, mock_user_id):
    from app.models.jobs import Job, JobStatus
    job = MagicMock(spec=Job)
    job.id = mock_job_id
    job.user_id = mock_user_id
    job.video_url = "https://youtube.com/watch?v=12345"
    job.status = JobStatus.queued
    job.created_at = datetime.now(timezone.utc)
    job.updated_at = datetime.now(timezone.utc)
    return job
