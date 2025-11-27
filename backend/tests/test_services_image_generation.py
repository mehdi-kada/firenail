
import pytest
from unittest.mock import patch, MagicMock
import requests
import base64
from app.services.image_generation import generate_thumbnail, regenerate_thumbnail, _download_image_to_base64

@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {"OPENROUTER_API_KEY": "test-key"}):
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
        # Mock OpenRouter response
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "http://openrouter.ai/generated.jpg"
                    }
                }
            ]
        }
        mock_post.return_value = mock_post_response

        # Mock downloading the generated image
        mock_image_response = MagicMock()
        mock_image_response.status_code = 200
        mock_image_response.content = b"generated-image-content"

        mock_get.return_value = mock_image_response

        result = generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

        assert result == "http://bucket/thumbnail.jpg"
        mock_download.assert_called()
        mock_post.assert_called()
        mock_get.assert_called_with("http://openrouter.ai/generated.jpg", timeout=30)
        mock_upload.assert_called_with("job-123", b"generated-image-content")

@patch("app.services.image_generation._download_image_to_base64")
def test_generate_thumbnail_api_error(mock_download, mock_env_vars):
    """Test handling of API errors."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="OpenRouter API returned 400"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

@patch("app.services.image_generation._download_image_to_base64")
def test_generate_thumbnail_no_image_url(mock_download, mock_env_vars):
    """Test handling of response with no image URL."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "I cannot generate an image."
                    }
                }
            ]
        }

        with pytest.raises(RuntimeError, match="No image data or URL found"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])


def test_generate_thumbnail_no_api_key():
    """Test error raised when API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
            generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])


def test_generate_thumbnail_no_reference_images(mock_env_vars):
    """Test error raised when no reference images provided."""
    with pytest.raises(ValueError, match="At least one reference image URL is required"):
        generate_thumbnail("job-123", "prompt", [])


@patch("app.services.image_generation._download_image_to_base64")
def test_generate_thumbnail_all_images_fail_download(mock_download, mock_env_vars):
    """Test error when all reference images fail to download."""
    mock_download.side_effect = ValueError("Failed to download")

    with pytest.raises(ValueError, match="No valid images could be downloaded"):
        generate_thumbnail("job-123", "prompt", ["http://ref1.jpg", "http://ref2.jpg"])


@patch("app.services.image_generation._download_image_to_base64")
@patch("app.services.image_generation.upload_thumbnail")
def test_generate_thumbnail_partial_image_download_success(mock_upload, mock_download, mock_env_vars):
    """Test that thumbnail generation succeeds even if some images fail to download."""
    # First image fails, second succeeds
    mock_download.side_effect = [ValueError("Failed"), "data:image/jpeg;base64,encoded"]
    mock_upload.return_value = "http://bucket/thumbnail.jpg"

    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "choices": [{"message": {"content": "http://openrouter.ai/generated.jpg"}}]
        }
        mock_post.return_value = mock_post_response

        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"generated-image-content"

        result = generate_thumbnail("job-123", "prompt", ["http://fail.jpg", "http://success.jpg"])

        assert result == "http://bucket/thumbnail.jpg"
        assert mock_download.call_count == 2


@patch("app.services.image_generation._download_image_to_base64")
@patch("app.services.image_generation.upload_thumbnail")
def test_generate_thumbnail_images_list_response(mock_upload, mock_download, mock_env_vars):
    """Test handling response with images list format."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"
    mock_upload.return_value = "http://bucket/thumbnail.jpg"

    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "choices": [{
                "message": {
                    "images": [{"image_url": {"url": "http://openrouter.ai/generated.jpg"}}]
                }
            }]
        }
        mock_post.return_value = mock_post_response

        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"generated-image-content"

        result = generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

        assert result == "http://bucket/thumbnail.jpg"


@patch("app.services.image_generation._download_image_to_base64")
@patch("app.services.image_generation.upload_thumbnail")
def test_generate_thumbnail_base64_data_uri_response(mock_upload, mock_download, mock_env_vars):
    """Test handling response with base64 data URI in content field."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"
    mock_upload.return_value = "http://bucket/thumbnail.jpg"

    # Create a small valid PNG image as base64
    image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    data_uri = f"data:image/png;base64,{base64_image}"

    with patch("requests.post") as mock_post:
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": data_uri
                }
            }]
        }
        mock_post.return_value = mock_post_response

        result = generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

        assert result == "http://bucket/thumbnail.jpg"
        mock_upload.assert_called_once_with("job-123", image_bytes)


@patch("app.services.image_generation._download_image_to_base64")
@patch("app.services.image_generation.upload_thumbnail")
def test_generate_thumbnail_raw_base64_response(mock_upload, mock_download, mock_env_vars):
    """Test handling response with raw base64 string in content field."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"
    mock_upload.return_value = "http://bucket/thumbnail.jpg"

    # Create a small valid PNG image as base64
    image_bytes = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N\x00\x00\x00\x00IEND\xaeB`\x82'
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    with patch("requests.post") as mock_post:
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": base64_image
                }
            }]
        }
        mock_post.return_value = mock_post_response

        result = generate_thumbnail("job-123", "prompt", ["http://ref1.jpg"])

        assert result == "http://bucket/thumbnail.jpg"
        mock_upload.assert_called_once_with("job-123", image_bytes)


# Tests for regenerate_thumbnail function
@patch("app.services.image_generation._download_image_to_base64")
@patch("app.services.image_generation.upload_thumbnail")
def test_regenerate_thumbnail_success(mock_upload, mock_download, mock_env_vars):
    """Test successful thumbnail regeneration."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"
    mock_upload.return_value = "http://bucket/regenerated.jpg"

    with patch("requests.post") as mock_post, patch("requests.get") as mock_get:
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "choices": [{"message": {"content": "http://openrouter.ai/regenerated.jpg"}}]
        }
        mock_post.return_value = mock_post_response

        mock_get.return_value.status_code = 200
        mock_get.return_value.content = b"regenerated-image-content"

        result = regenerate_thumbnail("job-123", "http://source.jpg", "Make it brighter")

        assert result == "http://bucket/regenerated.jpg"
        mock_download.assert_called_once_with("http://source.jpg")
        mock_upload.assert_called_with("job-123", b"regenerated-image-content")


def test_regenerate_thumbnail_no_api_key():
    """Test error raised when API key is missing for regeneration."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable not set"):
            regenerate_thumbnail("job-123", "http://source.jpg", "Make it brighter")


@patch("app.services.image_generation._download_image_to_base64")
def test_regenerate_thumbnail_source_image_download_fails(mock_download, mock_env_vars):
    """Test error when source image fails to download."""
    mock_download.side_effect = ValueError("Failed to download")

    with pytest.raises(ValueError, match="Failed to download source image"):
        regenerate_thumbnail("job-123", "http://source.jpg", "Make it brighter")


@patch("app.services.image_generation._download_image_to_base64")
def test_regenerate_thumbnail_api_error(mock_download, mock_env_vars):
    """Test handling of API errors during regeneration."""
    mock_download.return_value = "data:image/jpeg;base64,encoded"

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="OpenRouter API returned 500"):
            regenerate_thumbnail("job-123", "http://source.jpg", "Make it brighter")
