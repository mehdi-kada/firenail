import logging
from uuid import UUID
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from sqlalchemy import select
from requests.exceptions import RequestException, HTTPError, Timeout
from app.services import transcripts, analysis, events, crawl
from app.services.transcripts import VideoUnavailableError, TranscriptUnavailableError, InvalidURLError
from app.services.image_generation import generate_thumbnail
from app.celery.celery_app import celery_app
from app.database.database import sessionLocal
from app.models.jobs import Job, JobStatus
from app.models.videos import Video
from app.models.images import Image
from app.models.profiles import Profile
from app.constants.prompts import analysis_prompt, thumbnail_generation_prompt
from app.constants.user_messages import ERROR_MESSAGES, SUCCESS_MESSAGES

logger = logging.getLogger(__name__)

# Configuration
MAX_KEYWORDS_FOR_IMAGE_SEARCH = 2
MAX_IMAGES_FOR_THUMBNAIL = 3
IMAGE_SEARCH_LIMIT_PER_KEYWORD = 1

def _get_user_friendly_error(exc: Exception) -> str:
    """Convert technical exceptions to user-friendly messages"""
    
    # Check for custom exceptions first
    if isinstance(exc, VideoUnavailableError):
        return ERROR_MESSAGES["video_unavailable"]
    elif isinstance(exc, TranscriptUnavailableError):
        return ERROR_MESSAGES["no_transcript"]
    elif isinstance(exc, InvalidURLError):
        return ERROR_MESSAGES["invalid_url"]
    
    error_str = str(exc).lower()[:1000]
    
    error_mappings = [
        ("transcript" in error_str and "disabled" in error_str, "transcript_disabled"),
        ("no transcript" in error_str or "captions" in error_str, "no_transcript"),
        ("age" in error_str and "restricted" in error_str, "age_restricted"),
        ("unavailable" in error_str or "private" in error_str, "video_unavailable"),
        ("not found" in error_str or "404" in error_str, "video_not_found"),
        ("invalid" in error_str and "url" in error_str, "invalid_url"),
        ("timeout" in error_str or "timed out" in error_str, "thumbnail_generation_timeout"),
        ("rate" in error_str and "limit" in error_str, "rate_limit"),
        ("api" in error_str or isinstance(exc, (RequestException, HTTPError)), "api_error"),
    ]

    for condition, message_key in error_mappings:
        if condition:
            return ERROR_MESSAGES[message_key]

    return ERROR_MESSAGES["unknown_error"]


@celery_app.task(bind=True, name="process_video_pipeline", max_retries=2, default_retry_delay=60, time_limit=600, soft_time_limit=540)
def process_video_pipeline(self, job_id: str):
    """
    Process video pipeline with comprehensive error handling and user feedback
    Time limits: 600s hard limit, 540s soft limit for graceful shutdown
    """
    job_uuid = UUID(job_id)
    logger.info(f"Starting video pipeline for job {job_id}")

    with sessionLocal() as session:
        job = session.get(Job, job_uuid)
        if not job:
            logger.error(f"Job {job_id} not found")
            raise ValueError(f"Job {job_id} not found")
        job.status = JobStatus.processing
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to update job status to processing: {e}")
            raise
        video_url = job.video_url

    def emit(step_name: str, status: str, payload: dict | None = None, user_message: str | None = None):
        """Emit event with optional user-friendly message"""
        try:
            event_payload = payload or {}
            if user_message:
                event_payload["user_message"] = user_message
            events.record_event(job_uuid, step=step_name, status=status, payload=event_payload)
        except Exception as exc:
            logger.error(f"Failed to record event for job {job_uuid} ({step_name}:{status}): {exc}")

    emit("job", "processing", {"video_url": video_url}, SUCCESS_MESSAGES["queued"])

    try:
        emit("metadata", "started", user_message="Loading video information and captions...")
        try:
            video_data = transcripts.fetch_video_data(video_url)
            video_title = video_data.title
            transcript_text = video_data.transcript
            
            emit("metadata", "completed", {
                "title": video_title,
                "transcript_length": len(transcript_text)
            }, SUCCESS_MESSAGES["metadata_fetched"])
            
            if not transcript_text or len(transcript_text.strip()) < 50:
                user_error = ERROR_MESSAGES["no_transcript"]
                emit("metadata", "failed", {"error": "Transcript too short"}, user_error)
                raise ValueError(user_error)
                
        except Exception as exc:
            user_error = _get_user_friendly_error(exc)
            logger.error(f"Metadata fetch failed: {exc}")
            emit("metadata", "failed", {"error": str(exc)}, user_error)
            raise ValueError(user_error) from exc
        
        emit("analysis", "started", user_message="Analyzing video content...")
        try:
            prompt = analysis_prompt(transcript_text, video_title)
            analysis_result = analysis.analyze_transcript(prompt)
            summary = analysis_result.get("summary", "")
            keywords = analysis_result.get("image_search_keywords", [])
            
            if not keywords or len(keywords) == 0:
                user_error = ERROR_MESSAGES["no_keywords"]
                emit("analysis", "failed", {"error": "No keywords extracted"}, user_error)
                raise ValueError(user_error)
                
            emit("analysis", "completed", {
                "summary": summary[:170],
                "keywords": keywords
            }, SUCCESS_MESSAGES["analysis_completed"])
        except Exception as exc:
            user_error = _get_user_friendly_error(exc) if not isinstance(exc, ValueError) else str(exc)
            logger.error(f"Analysis failed: {exc}")
            emit("analysis", "failed", {"error": str(exc)}, user_error)
            raise ValueError(user_error) from exc

        emit("images", "started", user_message="Finding reference images...")
        image_urls = []
        failed_keywords = []
        
        search_keywords = keywords[:MAX_KEYWORDS_FOR_IMAGE_SEARCH]
        
        def search_image(keyword):
            try:
                images = crawl.crawl_images(keyword, limit=IMAGE_SEARCH_LIMIT_PER_KEYWORD)
                if images and len(images) > 0:
                    image_data = images[0]
                    image_url = image_data.get("imageUrl")
                    if image_url:
                        return {"keyword": keyword, "url": image_url}
                return None
            except Exception as exc:
                logger.error(f"Error searching images for '{keyword}': {exc}")
                return None

        # searching for images in parallel 
        with ThreadPoolExecutor(max_workers=len(search_keywords)) as executor:
            future_to_keyword = {executor.submit(search_image, kw): kw for kw in search_keywords}
            for future in as_completed(future_to_keyword):
                kw = future_to_keyword[future]
                try:
                    result = future.result()
                    if result:
                        image_urls.append(result)
                    else:
                        failed_keywords.append(kw)
                        logger.warning(f"No images found for keyword: {kw}")
                except Exception as exc:
                    failed_keywords.append(kw)
                    logger.error(f"Exception during image search for '{kw}': {exc}")

        if len(image_urls) == 0:
            user_error = ERROR_MESSAGES["image_search_failed"]
            emit("images", "failed", {
                "error": "No images found",
                "failed_keywords": failed_keywords
            }, user_error)
            raise ValueError(user_error)
        
        emit("images", "completed", {
            "count": len(image_urls),
            "found_for": [img["keyword"] for img in image_urls]
        }, SUCCESS_MESSAGES["images_found"])

        thumbnail_url = None
        image_id = None
        if len(image_urls) >= 1:
            thumbnail_prompt = thumbnail_generation_prompt(
                video_title=video_title,
                summary=summary,
                keywords=keywords,
            )
            try:
                emit("thumbnail", "started", user_message=SUCCESS_MESSAGES["thumbnail_started"])
                thumbnail_url = generate_thumbnail(
                    job_id=str(job_uuid),
                    prompt=thumbnail_prompt,
                    reference_image_urls=[p["url"] for p in image_urls[:MAX_IMAGES_FOR_THUMBNAIL]]
                )
                
                with sessionLocal() as session:
                    job = session.get(Job, job_uuid)
                    if job:
                        existing_video = session.execute(
                            select(Video).where(Video.job_id == job_uuid)
                        ).scalar_one_or_none()
                        if not existing_video:
                            video_record = Video(
                                job_id=job_uuid,
                                title=video_title,
                                summary=summary
                            )
                            session.add(video_record)
                        
                        generated_image = Image(
                            job_id=job_uuid,
                            profile_id=job.user_id,
                            video_title=video_title,
                            keywords=keywords or ["thumbnail"],
                            firecrawl_payload=None,
                            storage_public_url=thumbnail_url,
                        )
                        session.add(generated_image)
                        
                        profile = session.get(Profile, job.user_id)
                        if profile:
                            subscription = profile.subscription
                            if subscription and subscription.status in ["active", "cancelled"]:
                                if subscription.status == "cancelled" and subscription.current_period_end < datetime.now(timezone.utc):
                                    profile.images_generated += 1
                                else:
                                    subscription.images_generated += 1
                            else:
                                profile.images_generated += 1
                        
                        session.commit()
                        session.refresh(generated_image)
                        image_id = str(generated_image.id)

                emit("thumbnail", "completed", {"url": thumbnail_url, "image_id": image_id}, SUCCESS_MESSAGES["thumbnail_completed"])
            except ValueError as e:
                user_error = str(e) if "valid" in str(e).lower() else ERROR_MESSAGES["thumbnail_generation_failed"]
                # Truncate error log
                error_log = str(e)
                if len(error_log) > 500:
                    error_log = error_log[:500] + "... (truncated)"
                logger.error(f"Thumbnail generation validation error: {error_log}")
                emit("thumbnail", "failed", {"error": error_log}, user_error)
                raise ValueError(user_error) from e
            except Timeout as e:
                user_error = ERROR_MESSAGES["thumbnail_generation_timeout"]
                logger.error(f"Thumbnail generation timeout: {e}")
                emit("thumbnail", "failed", {"error": "Timeout"}, user_error)
                raise ValueError(user_error) from e
            except Exception as e:
                user_error = _get_user_friendly_error(e)
                error_log = str(e)
                if len(error_log) > 500:
                    error_log = error_log[:500] + "... (truncated)"
                logger.error(f"Thumbnail generation failed: {error_log}")
                emit("thumbnail", "failed", {"error": error_log}, user_error)
                raise ValueError(user_error) from e

        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                job.status = JobStatus.completed
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to commit job completion: {e}")
                    raise

        emit("done", "completed", {
            "images_count": len(image_urls),
            "thumbnail_url": thumbnail_url,
            "image_id": image_id
        }, SUCCESS_MESSAGES["completed"])
        return {"status": "success", "thumbnail_url": thumbnail_url, "image_id": image_id}

    except Exception as exc:
        user_error = _get_user_friendly_error(exc) if not isinstance(exc, ValueError) else str(exc)
        emit("error", "failed", {"error": str(exc)}, user_error)
        
        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                job.status = JobStatus.failed
                job.error_message = user_error  # Store user-friendly error
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to update job status to failed: {e}")
                    raise
        
        raise