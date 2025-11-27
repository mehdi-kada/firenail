
import pytest
from unittest.mock import patch, MagicMock
import json
from app.services.analysis import analyze_transcript
import tenacity

# Sample valid JSON response from the LLM
SAMPLE_LLM_RESPONSE = json.dumps({
    "summary": "This is a summary of the video.",
    "image_search_keywords": ["keyword1", "keyword2"]
})

# Sample LLM response wrapped in markdown code block
SAMPLE_MARKDOWN_RESPONSE = f"```json\n{SAMPLE_LLM_RESPONSE}\n```"

@pytest.fixture
def mock_env_vars():
    with patch.dict("os.environ", {"CEREBRAS_API_KEY": "test-key"}):
        yield

def test_analyze_transcript_success(mock_env_vars):
    """Test successful analysis of a transcript."""
    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": SAMPLE_LLM_RESPONSE}}
            ]
        }
        mock_post.return_value = mock_response

        result = analyze_transcript("Test prompt")

        assert result["summary"] == "This is a summary of the video."
        assert result["image_search_keywords"] == ["keyword1", "keyword2"]
        mock_post.assert_called_once()

def test_analyze_transcript_markdown_parsing(mock_env_vars):
    """Test parsing of JSON wrapped in markdown code blocks."""
    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": SAMPLE_MARKDOWN_RESPONSE}}
            ]
        }
        mock_post.return_value = mock_response

        result = analyze_transcript("Test prompt")

        assert result["summary"] == "This is a summary of the video."
        assert result["image_search_keywords"] == ["keyword1", "keyword2"]

def test_analyze_transcript_regex_fallback(mock_env_vars):
    """Test fallback to regex extraction when JSON parsing fails."""
    broken_json = '{"summary": "Broken JSON", "image_search_keywords": ["key1", "key2"]' # Missing closing brace

    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": broken_json}}
            ]
        }
        mock_post.return_value = mock_response

        result = analyze_transcript("Test prompt")

        assert result["summary"] == "Broken JSON"
        assert "key1" in result["image_search_keywords"]
        assert "key2" in result["image_search_keywords"]

def test_analyze_transcript_no_api_key():
    """Test error raised when API key is missing."""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(tenacity.RetryError):
             analyze_transcript("Test prompt")

def test_analyze_transcript_api_error(mock_env_vars):
    """Test handling of API errors."""
    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_post.return_value = mock_response

        # Tenacity will retry and raise RetryError
        with pytest.raises(tenacity.RetryError):
            analyze_transcript("Test prompt")


def test_analyze_transcript_empty_response(mock_env_vars):
    """Test handling of empty LLM response."""
    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": ""}}
            ]
        }
        mock_post.return_value = mock_response

        result = analyze_transcript("Test prompt")

        # Should return default empty values
        assert result["summary"] == ""
        assert result["image_search_keywords"] == []


def test_analyze_transcript_curly_quotes_handling(mock_env_vars):
    """Test handling of curly quotes in LLM response."""
    # Use unicode escapes for curly quotes to avoid syntax issues
    response_with_curly_quotes = '{"summary": "Video about \u201ctesting\u201d", "image_search_keywords": ["test\u2019s"]}'
    
    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {"message": {"content": response_with_curly_quotes}}
            ]
        }
        mock_post.return_value = mock_response

        # Should handle curly quotes and not crash
        result = analyze_transcript("Test prompt")
        assert "summary" in result
        assert "image_search_keywords" in result


def test_analyze_transcript_invalid_response_structure(mock_env_vars):
    """Test handling of invalid response structure from API."""
    with patch("httpx.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "structure"}
        mock_post.return_value = mock_response

        # Tenacity retries and wraps the ValueError in RetryError
        with pytest.raises(tenacity.RetryError):
            analyze_transcript("Test prompt")
