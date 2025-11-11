from uuid import UUID
from datetime import datetime, timezone
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

def _get_user_friendly_error(exc: Exception) -> str:
    """Convert technical exceptions to user-friendly messages"""
    
    # Check for custom exceptions first
    if isinstance(exc, VideoUnavailableError):
        return ERROR_MESSAGES["video_unavailable"]
    elif isinstance(exc, TranscriptUnavailableError):
        return ERROR_MESSAGES["no_transcript"]
    elif isinstance(exc, InvalidURLError):
        return ERROR_MESSAGES["invalid_url"]
    
    # Check error string patterns
    error_str = str(exc).lower()
    
    if "transcript" in error_str and "disabled" in error_str:
        return ERROR_MESSAGES["transcript_disabled"]
    elif "no transcript" in error_str or "captions" in error_str:
        return ERROR_MESSAGES["no_transcript"]
    elif "age" in error_str and "restricted" in error_str:
        return ERROR_MESSAGES["age_restricted"]
    elif "unavailable" in error_str or "private" in error_str:
        return ERROR_MESSAGES["video_unavailable"]
    elif "not found" in error_str or "404" in error_str:
        return ERROR_MESSAGES["video_not_found"]
    elif "invalid" in error_str and "url" in error_str:
        return ERROR_MESSAGES["invalid_url"]
    elif "timeout" in error_str or "timed out" in error_str:
        return ERROR_MESSAGES["thumbnail_generation_timeout"]
    elif "rate" in error_str and "limit" in error_str:
        return ERROR_MESSAGES["rate_limit"]
    elif "api" in error_str or isinstance(exc, (RequestException, HTTPError)):
        return ERROR_MESSAGES["api_error"]
    else:
        return ERROR_MESSAGES["unknown_error"]


@celery_app.task(bind=True, name="process_video_pipeline", max_retries=2, default_retry_delay=60, time_limit=600, soft_time_limit=540)
def process_video_pipeline(self, job_id: str):
    """
    Process video pipeline with comprehensive error handling and user feedback
    Time limits: 600s hard limit, 540s soft limit for graceful shutdown
    """
    job_uuid = UUID(job_id)

    with sessionLocal() as session:
        job = session.get(Job, job_uuid)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        job.status = JobStatus.processing
        try:
            session.commit()
        except Exception:
            session.rollback()
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
            print(f"Failed to record event for job {job_uuid} ({step_name}:{status}): {exc}")

    emit("job", "processing", {"video_url": video_url}, SUCCESS_MESSAGES["queued"])

    try:
        # Step 1: Fetch video data (metadata + transcript in one request)
        emit("metadata", "started", user_message="Loading video information and captions...")
        try:
            video_data = transcripts.fetch_video_data(video_url)
            video_title = video_data.title
            transcript_text = video_data.transcript
            
            emit("metadata", "completed", {
                "title": video_title,
                "transcript_length": len(transcript_text)
            }, SUCCESS_MESSAGES["metadata_fetched"])
            
            # Validate transcript length
            if not transcript_text or len(transcript_text.strip()) < 50:
                user_error = ERROR_MESSAGES["no_transcript"]
                emit("metadata", "failed", {"error": "Transcript too short"}, user_error)
                raise ValueError(user_error)
                
        except Exception as exc:
            user_error = _get_user_friendly_error(exc)
            emit("metadata", "failed", {"error": str(exc)}, user_error)
            raise ValueError(user_error) from exc
        
        # Step 2: Analyze content
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
            emit("analysis", "failed", {"error": str(exc)}, user_error)
            raise ValueError(user_error) from exc

        # Step 3: Search for reference images
        emit("images", "started", user_message="Finding reference images...")
        image_urls = []
        failed_keywords = []
        
        for keyword in keywords[:2]:  # Limit to 2-3 keywords to avoid AI not following instructions
            try:
                images = crawl.crawl_images(keyword, limit=1)
                if images and len(images) > 0:
                    image_data = images[0]
                    image_url = image_data.get("imageUrl")
                    if image_url:
                        image_urls.append({"keyword": keyword, "url": image_url})
                else:
                    failed_keywords.append(keyword)
                    print(f"No images found for keyword: {keyword}")
            except Exception as exc:
                failed_keywords.append(keyword)
                print(f"Error searching images for '{keyword}': {exc}")
        
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

        # Step 4: Generate thumbnail
        thumbnail_url = None
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
                    reference_image_urls=[p["url"] for p in image_urls[:3]]
                )
                emit("thumbnail", "completed", {"url": thumbnail_url}, SUCCESS_MESSAGES["thumbnail_completed"])
            except ValueError as e:
                user_error = str(e) if "valid" in str(e).lower() else ERROR_MESSAGES["thumbnail_generation_failed"]
                print(f"Thumbnail generation validation error: {e}")
                emit("thumbnail", "failed", {"error": str(e)}, user_error)
                raise ValueError(user_error) from e
            except Timeout as e:
                user_error = ERROR_MESSAGES["thumbnail_generation_timeout"]
                print(f"Thumbnail generation timeout: {e}")
                emit("thumbnail", "failed", {"error": "Timeout"}, user_error)
                raise ValueError(user_error) from e
            except Exception as e:
                user_error = _get_user_friendly_error(e)
                print(f"Thumbnail generation failed: {e}")
                emit("thumbnail", "failed", {"error": str(e)}, user_error)
                raise ValueError(user_error) from e

        # Step 5: Save to database
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
                

                if thumbnail_url:
                    existing_generated = session.execute(
                        select(Image).where(
                            Image.job_id == job_uuid,
                            Image.storage_public_url == thumbnail_url
                        )
                    ).scalar_one_or_none()
                    if not existing_generated:
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
                
                job.status = JobStatus.completed
                try:
                    session.commit()
                except Exception:
                    session.rollback()
                    raise

        emit("done", "completed", {
            "images_count": len(image_urls),
            "thumbnail_url": thumbnail_url
        }, SUCCESS_MESSAGES["completed"])
        return {"status": "success", "thumbnail_url": thumbnail_url}

    except Exception as exc:
        # Emit user-friendly error
        user_error = _get_user_friendly_error(exc) if not isinstance(exc, ValueError) else str(exc)
        emit("error", "failed", {"error": str(exc)}, user_error)
        
        # Update job status
        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                job.status = JobStatus.failed
                job.error_message = user_error  # Store user-friendly error
                try:
                    session.commit()
                except Exception:
                    session.rollback()
                    raise
        
        raise