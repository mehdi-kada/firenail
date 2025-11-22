
import pytest
from unittest.mock import MagicMock, patch, call, ANY
from uuid import uuid4
from app.services.transcripts import VideoData
from app.celery.tasks.video_pipeline import process_video_pipeline
from app.models.jobs import JobStatus
from app.models.profiles import Profile
from app.models.jobs import Job
from app.constants.user_messages import ERROR_MESSAGES

# Mock the sessionLocal and its context manager
@pytest.fixture
def mock_db_session(mock_job, mock_profile):
    mock_session = MagicMock()

    # Mock getting the job and profile
    def get_side_effect(model, id):
        if model == Job:
            return mock_job
        elif model == Profile:
            return mock_profile
        return None

    mock_session.get.side_effect = get_side_effect

    # Mock executing queries (for Video and Image checks)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None # Default to no existing video/image
    mock_session.execute.return_value = mock_result

    return mock_session

@pytest.fixture
def mock_session_local(mock_db_session):
    # SessionLocal returns a context manager that yields the session
    mock_factory = MagicMock()
    mock_factory.return_value.__enter__.return_value = mock_db_session
    return mock_factory

# Tests for process_video_pipeline

@patch("app.celery.tasks.video_pipeline.sessionLocal")
@patch("app.celery.tasks.video_pipeline.transcripts")
@patch("app.celery.tasks.video_pipeline.analysis")
@patch("app.celery.tasks.video_pipeline.crawl")
@patch("app.celery.tasks.video_pipeline.generate_thumbnail")
@patch("app.celery.tasks.video_pipeline.events")
def test_process_video_pipeline_success(
    mock_events,
    mock_generate_thumbnail,
    mock_crawl,
    mock_analysis,
    mock_transcripts,
    mock_session_factory,
    mock_job,
    mock_db_session,
    mock_job_id
):
    mock_session_factory.return_value.__enter__.return_value = mock_db_session

    # Setup successful responses
    mock_transcripts.fetch_video_data.return_value = VideoData(
        title="Test Video",
        transcript="This is a test transcript that is long enough to be processed by the system." * 5
    )

    mock_analysis.analyze_transcript.return_value = {
        "summary": "Test Summary",
        "image_search_keywords": ["keyword1", "keyword2"]
    }

    mock_crawl.crawl_images.return_value = [{"imageUrl": "http://example.com/image.jpg"}]

    mock_generate_thumbnail.return_value = "http://example.com/thumbnail.jpg"

    # Run the task
    result = process_video_pipeline(str(mock_job_id))

    # Verify success
    assert result == {"status": "success", "thumbnail_url": "http://example.com/thumbnail.jpg"}
    assert mock_job.status == JobStatus.completed

    # Verify events were recorded
    mock_events.record_event.assert_any_call(mock_job_id, step="job", status="processing", payload=ANY)
    mock_events.record_event.assert_any_call(mock_job_id, step="metadata", status="completed", payload=ANY)
    mock_events.record_event.assert_any_call(mock_job_id, step="analysis", status="completed", payload=ANY)
    mock_events.record_event.assert_any_call(mock_job_id, step="images", status="completed", payload=ANY)
    mock_events.record_event.assert_any_call(mock_job_id, step="thumbnail", status="completed", payload=ANY)
    mock_events.record_event.assert_any_call(mock_job_id, step="done", status="completed", payload=ANY)

@patch("app.celery.tasks.video_pipeline.sessionLocal")
@patch("app.celery.tasks.video_pipeline.transcripts")
@patch("app.celery.tasks.video_pipeline.events")
def test_process_video_pipeline_transcript_failed(
    mock_events,
    mock_transcripts,
    mock_session_factory,
    mock_job,
    mock_db_session,
    mock_job_id
):
    mock_session_factory.return_value.__enter__.return_value = mock_db_session

    # Setup failure
    mock_transcripts.fetch_video_data.side_effect = Exception("Video unavailable")

    # Run the task expecting exception
    with pytest.raises(ValueError) as excinfo:
        process_video_pipeline(str(mock_job_id))

    assert ERROR_MESSAGES["video_unavailable"] in str(excinfo.value)
    assert mock_job.status == JobStatus.failed

    # Verify failure event - using assert_any_call because finally block might emit generic error event too
    mock_events.record_event.assert_any_call(
        mock_job_id,
        step="metadata",
        status="failed",
        payload={"error": "Video unavailable", "user_message": ERROR_MESSAGES["video_unavailable"]}
    )

@patch("app.celery.tasks.video_pipeline.sessionLocal")
@patch("app.celery.tasks.video_pipeline.transcripts")
@patch("app.celery.tasks.video_pipeline.analysis")
@patch("app.celery.tasks.video_pipeline.events")
def test_process_video_pipeline_no_keywords(
    mock_events,
    mock_analysis,
    mock_transcripts,
    mock_session_factory,
    mock_job,
    mock_db_session,
    mock_job_id
):
    mock_session_factory.return_value.__enter__.return_value = mock_db_session

    mock_transcripts.fetch_video_data.return_value = VideoData(
        title="Test Video",
        transcript="Transcript content" * 5
    )

    # Return empty keywords
    mock_analysis.analyze_transcript.return_value = {
        "summary": "Test Summary",
        "image_search_keywords": []
    }

    with pytest.raises(ValueError) as excinfo:
        process_video_pipeline(str(mock_job_id))

    assert ERROR_MESSAGES["no_keywords"] in str(excinfo.value)

    mock_events.record_event.assert_any_call(
        mock_job_id,
        step="analysis",
        status="failed",
        payload={"error": "No keywords extracted", "user_message": ERROR_MESSAGES["no_keywords"]}
    )

@patch("app.celery.tasks.video_pipeline.sessionLocal")
@patch("app.celery.tasks.video_pipeline.transcripts")
@patch("app.celery.tasks.video_pipeline.analysis")
@patch("app.celery.tasks.video_pipeline.crawl")
@patch("app.celery.tasks.video_pipeline.events")
def test_process_video_pipeline_no_images(
    mock_events,
    mock_crawl,
    mock_analysis,
    mock_transcripts,
    mock_session_factory,
    mock_job,
    mock_db_session,
    mock_job_id
):
    mock_session_factory.return_value.__enter__.return_value = mock_db_session

    mock_transcripts.fetch_video_data.return_value = VideoData(
        title="Test Video",
        transcript="Transcript content" * 5
    )

    mock_analysis.analyze_transcript.return_value = {
        "summary": "Test Summary",
        "image_search_keywords": ["keyword1"]
    }

    # Return no images
    mock_crawl.crawl_images.return_value = []

    with pytest.raises(ValueError) as excinfo:
        process_video_pipeline(str(mock_job_id))

    assert ERROR_MESSAGES["image_search_failed"] in str(excinfo.value)

    # Check failure event
    mock_events.record_event.assert_any_call(
        mock_job_id,
        step="images",
        status="failed",
        payload={
            "error": "No images found",
            "failed_keywords": ["keyword1"],
            "user_message": ERROR_MESSAGES["image_search_failed"]
        }
    )
