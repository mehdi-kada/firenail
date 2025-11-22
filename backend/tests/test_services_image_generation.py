
import pytest
from unittest.mock import patch, MagicMock
import requests
import base64
from app.services.image_generation import generate_thumbnail, _download_image_to_base64

@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {"FREEPIK_API_KEY": "test-key"}):
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

@patch("app.services.image_generation._download_image_to_base64")
@patch("app.services.image_generation.upload_thumbnail")
def test_generate_thumbnail_success(mock_upload, mock_download, mock_env_vars):
    """Test successful thumbnail generation flow."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"
    mock_upload.return_value = "http://bucket/thumbnail.jpg"

    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        # Mock initial task creation
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {"data": {"task_id": "task-123"}}
        mock_post.return_value = mock_post_response

        # Mock polling response (first poll is completed)
        mock_poll_response = MagicMock()
        mock_poll_response.status_code = 200
        mock_poll_response.json.return_value = {
            "data": {
                "status": "COMPLETED",
                "generated": [{"url": "http://freepik.com/generated.jpg"}]
            }
        }

        # Mock downloading the generated image
        mock_image_response = MagicMock()
        mock_image_response.status_code = 200
        mock_image_response.content = b"generated-image-content"

        mock_get.side_effect = [mock_poll_response, mock_image_response]

        result = generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

        assert result == "http://bucket/thumbnail.jpg"
        mock_download.assert_called()
        mock_post.assert_called()
        mock_get.assert_called()
        mock_upload.assert_called_with("job-123", b"generated-image-content")

@patch("app.services.image_generation._download_image_to_base64")
def test_generate_thumbnail_api_error(mock_download, mock_env_vars):
    """Test handling of API errors during task creation."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Freepik API returned 400"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

@patch("app.services.image_generation._download_image_to_base64")
def test_generate_thumbnail_failed_status(mock_download, mock_env_vars):
    """Test handling of FAILED status during polling."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"

    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"data": {"task_id": "task-123"}}

        mock_poll_response = MagicMock()
        mock_poll_response.status_code = 200
        mock_poll_response.json.return_value = {
            "data": {
                "status": "FAILED",
                "error": "Generation failed"
            }
        }
        mock_get.return_value = mock_poll_response

        with pytest.raises(RuntimeError, match="Freepik image generation failed"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])
