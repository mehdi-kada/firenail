
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

def test_crawl_images_ssl_error(mock_env_vars):
    """Test handling of SSL errors."""
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = requests.exceptions.SSLError("SSL Error")

        images = crawl_images("test keyword")

        assert images == []

def test_crawl_images_read_timeout(mock_env_vars):
    """Test handling of read timeout errors."""
    with patch("requests.Session.post") as mock_post:
        mock_post.side_effect = requests.exceptions.ReadTimeout("Read Timeout")

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

def test_crawl_images_forbidden_error(mock_env_vars):
    """Test handling of 403 forbidden errors."""
    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
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

def test_crawl_images_rate_limited(mock_env_vars):
    """Test handling of rate limiting (429)."""
    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 429
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

def test_crawl_images_alternative_response_format(mock_env_vars):
    """Test handling of alternative response format with images at root."""
    mock_response_data = {
        "images": [
            {"url": "http://example.com/image1.jpg"}
        ]
    }

    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        images = crawl_images("test keyword")

        assert len(images) == 1
        assert images[0]["url"] == "http://example.com/image1.jpg"

def test_crawl_images_data_as_list_format(mock_env_vars):
    """Test handling of response format where data is a list."""
    mock_response_data = {
        "data": [
            {"url": "http://example.com/image1.jpg"}
        ]
    }

    with patch("requests.Session.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_response_data
        mock_post.return_value = mock_response

        images = crawl_images("test keyword")

        assert len(images) == 1

def test_crawl_images_custom_url(mock_env_vars):
    """Test using custom Firecrawl URL from environment."""
    mock_response_data = {
        "success": True,
        "data": {"images": []}
    }

    with patch.dict("os.environ", {"FIRECRAWL_URL": "https://custom.firecrawl.dev/v2/search"}):
        with patch("requests.Session.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_response_data
            mock_post.return_value = mock_response

            images = crawl_images("test keyword")

            # Verify the custom URL was used
            call_args = mock_post.call_args
            assert "https://custom.firecrawl.dev/v2/search" in str(call_args)
