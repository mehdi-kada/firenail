import pytest
from unittest.mock import patch, MagicMock, call
import requests
import base64
from app.services.image_generation import (
    generate_thumbnail,
    regenerate_thumbnail,
    _download_image_to_base64,
)

@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {
        "FREEPIK_API_KEY": "test-freepik-key"
    }):
        yield

def test_download_image_to_base64_success():
    """Test successful image download and conversion to base64."""
    image_content = b"fake-image-content"
    encoded_content = base64.b64encode(image_content).decode('utf-8')
    expected_data_uri = f"data:image/jpeg;base64,{encoded_content}"

    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "image/jpeg"}
        mock_response.content = image_content
        mock_get.return_value = mock_response

        result = _download_image_to_base64("http://example.com/image.jpg")

        assert result == expected_data_uri

def test_download_image_to_base64_invalid_url():
    """Test validation of invalid URLs."""
    with pytest.raises(ValueError, match="Invalid URL format"):
        _download_image_to_base64("ftp://example.com/image.jpg")

def test_download_image_to_base64_not_image():
    """Test validation of non-image content types."""
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"content-type": "text/html"}
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="URL is not an image"):
            _download_image_to_base64("http://example.com/not-image")

def test_generate_thumbnail_success(mock_env_vars):
    """Test successful thumbnail generation flow with Freepik."""
    with patch("requests.post") as mock_post, \
         patch("requests.get") as mock_get, \
         patch("app.services.image_generation.upload_thumbnail") as mock_upload, \
         patch("app.services.image_generation._download_image_to_base64") as mock_download:
        
        mock_download.return_value = "data:image/jpeg;base64,encoded"
        
        # 1. POST to create task
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"data": {"task_id": "task-123"}}
        mock_post.return_value = mock_post_response
        
        # 2. GET to poll status (first running, then completed)
        mock_poll_running = MagicMock()
        mock_poll_running.status_code = 200
        mock_poll_running.json.return_value = {"data": {"status": "RUNNING"}}
        
        mock_poll_completed = MagicMock()
        mock_poll_completed.status_code = 200
        mock_poll_completed.json.return_value = {
            "data": {
                "status": "COMPLETED",
                "generated": ["http://freepik.com/image.jpg"]
            }
        }
        
        # 3. GET to download image
        mock_image_response = MagicMock()
        mock_image_response.status_code = 200
        mock_image_response.content = b"final-image-content"
        
        # Configure side effects for requests.get
        # The sequence of calls:
        # 1. Poll running
        # 2. Poll completed
        # 3. Download image
        mock_get.side_effect = [mock_poll_running, mock_poll_completed, mock_image_response]
        
        mock_upload.return_value = "http://bucket/thumbnail.jpg"
        
        result = generate_thumbnail("job-123", "prompt", ["http://ref.jpg"])
        
        assert result == "http://bucket/thumbnail.jpg"
        mock_post.assert_called_once()
        assert mock_get.call_count == 3
        mock_upload.assert_called_with("job-123", b"final-image-content")

def test_generate_thumbnail_api_error(mock_env_vars):
    """Test handling of Freepik API errors."""
    with patch("app.services.image_generation._download_image_to_base64") as mock_download, \
         patch("requests.post") as mock_post:
        
        mock_download.return_value = "data:image/jpeg;base64,encoded"
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Freepik API returned 400"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

def test_generate_thumbnail_polling_failure(mock_env_vars):
    """Test handling of Freepik polling failure."""
    with patch("requests.post") as mock_post, \
         patch("requests.get") as mock_get, \
         patch("app.services.image_generation._download_image_to_base64") as mock_download:
        
        mock_download.return_value = "data:image/jpeg;base64,encoded"
        
        # POST success
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": {"task_id": "task-123"}}
        
        # Poll returns FAILED
        mock_poll_failed = MagicMock()
        mock_poll_failed.status_code = 200
        mock_poll_failed.json.return_value = {
            "data": {
                "status": "FAILED",
                "error": "Generation failed"
            }
        }
        mock_get.return_value = mock_poll_failed
        
        with pytest.raises(RuntimeError, match="Freepik image generation failed"):
            generate_thumbnail("job-123", "prompt", ["http://ref.jpg"])

def test_generate_thumbnail_no_api_key():
    """Test error raised when Freepik API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="FREEPIK_API_KEY environment variable not set"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

def test_regenerate_thumbnail_success(mock_env_vars):
    """Test successful thumbnail regeneration using Freepik."""
    with patch("app.services.image_generation._download_image_to_base64") as mock_download, \
         patch("app.services.image_generation.upload_thumbnail") as mock_upload, \
         patch("requests.post") as mock_post, \
         patch("requests.get") as mock_get:
             
        mock_download.return_value = "data:image/jpeg;base64,encoded"
        mock_upload.return_value = "http://bucket/regenerated.jpg"
        
        # 1. POST to create task
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"data": {"task_id": "task-456"}}
        mock_post.return_value = mock_post_response
        
        # 2. GET to poll status (completed immediately for simplicity)
        mock_poll_completed = MagicMock()
        mock_poll_completed.status_code = 200
        mock_poll_completed.json.return_value = {
            "data": {
                "status": "COMPLETED",
                "generated": ["http://freepik.com/regenerated.jpg"]
            }
        }
        
        # 3. GET to download image
        mock_image_response = MagicMock()
        mock_image_response.status_code = 200
        mock_image_response.content = b"regenerated-image-content"
        
        mock_get.side_effect = [mock_poll_completed, mock_image_response]
        
        result = regenerate_thumbnail("job-123", "http://source.jpg", "Make it brighter")
        
        assert result == "http://bucket/regenerated.jpg"
        mock_download.assert_called_once_with("http://source.jpg")
        mock_upload.assert_called_with("job-123", b"regenerated-image-content")
        mock_post.assert_called_once()
