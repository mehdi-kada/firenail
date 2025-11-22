
import pytest
from unittest.mock import patch, MagicMock
from fastapi import HTTPException
from app.auth.validate import get_current_user, get_current_user_profile
from app.models.profiles import Profile
import os

# Mock JWT token
MOCK_TOKEN = "mock.jwt.token"
MOCK_SECRET = "test-secret"

@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {"SUPABASE_JWT_SECRET": MOCK_SECRET}):
        # Also patch the module-level variable since it's loaded at import time
        with patch("app.auth.validate.SUPABASE_JWT_SECRET", MOCK_SECRET):
            yield

def test_get_current_user_success(mock_env_vars):
    """Test successful user extraction from JWT."""
    with patch("jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "user-123", "email": "test@example.com"}

        mock_bearer = MagicMock()
        mock_bearer.credentials = MOCK_TOKEN

        # We need to mock app.auth.validate.jwt.decode inside the module
        with patch("app.auth.validate.jwt.decode", mock_decode):
            user = get_current_user(mock_bearer)

            assert user == {"user_id": "user-123", "email": "test@example.com"}
            mock_decode.assert_called_with(
                MOCK_TOKEN,
                MOCK_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )

def test_get_current_user_missing_user_id(mock_env_vars):
    """Test error when JWT lacks user ID."""
    with patch("app.auth.validate.jwt.decode") as mock_decode:
        mock_decode.return_value = {"email": "test@example.com"}

        mock_bearer = MagicMock()
        mock_bearer.credentials = MOCK_TOKEN

        with pytest.raises(HTTPException) as exc:
            get_current_user(mock_bearer)

        assert exc.value.status_code == 401
        assert exc.value.detail == "User ID not in token"

def test_get_current_user_expired(mock_env_vars):
    """Test error when JWT is expired."""
    import jwt
    with patch("app.auth.validate.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError()

        mock_bearer = MagicMock()
        mock_bearer.credentials = MOCK_TOKEN

        with pytest.raises(HTTPException) as exc:
            get_current_user(mock_bearer)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token has expired"

def test_get_current_user_invalid(mock_env_vars):
    """Test error when JWT is invalid."""
    import jwt
    with patch("app.auth.validate.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.PyJWTError()

        mock_bearer = MagicMock()
        mock_bearer.credentials = MOCK_TOKEN

        with pytest.raises(HTTPException) as exc:
            get_current_user(mock_bearer)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_current_user_profile_existing():
    """Test retrieving an existing user profile."""
    mock_user = {"user_id": "00000000-0000-0000-0000-000000000001", "email": "test@example.com"}

    mock_db = MagicMock()
    mock_db.execute = MagicMock()
    mock_result = MagicMock()
    mock_profile = MagicMock(spec=Profile)
    mock_result.scalar_one_or_none.return_value = mock_profile
    mock_db.execute.return_value = mock_result # This needs to be awaitable

    # Since get_current_user_profile awaits db.execute, we need to mock it as an async function or return a future
    async def async_execute(*args, **kwargs):
        return mock_result

    mock_db.execute.side_effect = async_execute

    profile = await get_current_user_profile(mock_user, mock_db)

    assert profile == mock_profile
    mock_db.add.assert_not_called()

@pytest.mark.asyncio
async def test_get_current_user_profile_new():
    """Test creating a new user profile if one doesn't exist."""
    mock_user = {"user_id": "00000000-0000-0000-0000-000000000002", "email": "new@example.com"}

    mock_db = MagicMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None

    async def async_execute(*args, **kwargs):
        return mock_result

    async def async_commit():
        pass

    async def async_refresh(*args, **kwargs):
        pass

    mock_db.execute.side_effect = async_execute
    mock_db.commit.side_effect = async_commit
    mock_db.refresh.side_effect = async_refresh

    profile = await get_current_user_profile(mock_user, mock_db)

    assert str(profile.id) == mock_user["user_id"]
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
