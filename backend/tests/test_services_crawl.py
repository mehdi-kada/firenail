
import pytest
from unittest.mock import patch, MagicMock
import requests
from app.services.crawl import crawl_images

@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {"FIRECRAWL_KEY": "test-key"}):
        yield

def test_crawl_images_success(mock_env_vars):
    """Test successful image crawling."""
    mock_response_data = {
        "success": True,
        "data": {
            "images": [
                {"url": "http://example.com/image1.jpg", "alt": "Image 1"},
                {"url": "http://example.com/image2.jpg", "alt": "Image 2"}
            ]
        }
    }

    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        images = crawl_images("test keyword", limit=2)

        assert len(images) == 2
        assert images[0]["url"] == "http://example.com/image1.jpg"
        assert images[1]["url"] == "http://example.com/image2.jpg"

def test_crawl_images_network_error(mock_env_vars):
    """Test handling of network errors."""
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ConnectTimeout("Timeout")

        images = crawl_images("test keyword")

        assert images == []

def test_crawl_images_auth_error(mock_env_vars):
    """Test handling of authentication errors."""
    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError, match="Firecrawl auth error"):
            crawl_images("test keyword")

def test_crawl_images_unavailable(mock_env_vars):
    """Test handling of service unavailability (5xx or 429)."""
    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_post.return_value = mock_response

        images = crawl_images("test keyword")

        assert images == []

def test_crawl_images_unexpected_response_format(mock_env_vars):
    """Test handling of unexpected response formats."""
    mock_response_data = {"unexpected": "structure"}

    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        images = crawl_images("test keyword")

        assert images == []
