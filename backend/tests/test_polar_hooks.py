
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from app.api.subscription.polar_hooks import router
from app.main import app  # Need the main app to mount the router
import json
from uuid import UUID

# We need to patch the dependencies in the router
@pytest.fixture
def client():
    app.include_router(router)
    return TestClient(app)

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_subscription_service():
    with patch("app.api.subscription.polar_hooks.SubscriptionService") as mock:
        mock.upsert_subscription = AsyncMock()
        mock.cancel_subscription = AsyncMock()
        mock.revoke_subscription = AsyncMock()
        yield mock

@pytest.fixture
def mock_validate_event():
    with patch("app.api.subscription.polar_hooks.validate_event") as mock:
        yield mock

def test_webhook_invalid_signature(client, mock_validate_event):
    """Test webhook rejection with invalid signature."""
    from polar_sdk.webhooks import WebhookVerificationError
    mock_validate_event.side_effect = WebhookVerificationError("Invalid signature")

    response = client.post(
        "/webhooks/polar",
        json={"some": "event"},
        headers={"webhook-signature": "invalid"}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid webhook signature"

@pytest.mark.asyncio
async def test_webhook_order_paid(mock_validate_event, mock_db, mock_subscription_service):
    """Test handling of order.paid event."""
    # Setup mock event
    mock_event = MagicMock()
    mock_event.TYPE = "order.paid"
    # Configure data as an object with attributes, not a dict
    mock_event.data.metadata = {"user_id": "00000000-0000-0000-0000-000000000001"}
    mock_event.data.subscription.id = "sub_123"
    mock_event.data.subscription.customer_id = "cust_123"
    mock_event.data.subscription.status = "active"
    mock_event.data.subscription.product.name = "Pro Plan"

    mock_validate_event.return_value = mock_event

    # Call the handler directly since TestClient is sync and we want to test async logic with mocks easier
    from app.api.subscription.polar_hooks import polar_webhook

    request = MagicMock()
    request.body = AsyncMock(return_value=b'{"some": "json"}')
    request.headers = {"webhook-signature": "valid"}

    await polar_webhook(request, db=mock_db, webhook_signature="valid")

    mock_subscription_service.upsert_subscription.assert_called_once()
    call_args = mock_subscription_service.upsert_subscription.call_args
    assert str(call_args[0][0].user_id) == "00000000-0000-0000-0000-000000000001"
    assert call_args[0][0].polar_subscription_id == "sub_123"

@pytest.mark.asyncio
async def test_webhook_subscription_updated(mock_validate_event, mock_db, mock_subscription_service):
    """Test handling of subscription.updated event."""
    mock_event = MagicMock()
    mock_event.TYPE = "subscription.updated"
    # Configure data as an object with attributes, not a dict
    mock_event.data.metadata = {"user_id": "00000000-0000-0000-0000-000000000001"}
    mock_event.data.id = "sub_123"
    mock_event.data.customer_id = "cust_123"
    mock_event.data.status = "active"
    mock_event.data.product.name = "Pro Plan"

    mock_validate_event.return_value = mock_event

    from app.api.subscription.polar_hooks import polar_webhook
    request = MagicMock()
    request.body = AsyncMock(return_value=b'{}')
    request.headers = {}

    await polar_webhook(request, db=mock_db, webhook_signature="valid")

    mock_subscription_service.upsert_subscription.assert_called_once()

@pytest.mark.asyncio
async def test_webhook_subscription_canceled(mock_validate_event, mock_db, mock_subscription_service):
    """Test handling of subscription.canceled event."""
    mock_event = MagicMock()
    mock_event.TYPE = "subscription.canceled"
    mock_event.data.id = "sub_123"

    mock_validate_event.return_value = mock_event

    from app.api.subscription.polar_hooks import polar_webhook
    request = MagicMock()
    request.body = AsyncMock(return_value=b'{}')
    request.headers = {}

    await polar_webhook(request, db=mock_db, webhook_signature="valid")

    mock_subscription_service.cancel_subscription.assert_called_once_with("sub_123", mock_db)

@pytest.mark.asyncio
async def test_webhook_subscription_revoked(mock_validate_event, mock_db, mock_subscription_service):
    """Test handling of subscription.revoked event."""
    mock_event = MagicMock()
    mock_event.TYPE = "subscription.revoked"
    mock_event.data.id = "sub_123"

    mock_validate_event.return_value = mock_event

    from app.api.subscription.polar_hooks import polar_webhook
    request = MagicMock()
    request.body = AsyncMock(return_value=b'{}')
    request.headers = {}

    await polar_webhook(request, db=mock_db, webhook_signature="valid")

    mock_subscription_service.revoke_subscription.assert_called_once_with("sub_123", mock_db)
