
from uuid import UUID
from sqlalchemy import select
from app.services import transcripts, analysis, events, crawl
from app.services.image_generation import generate_thumbnail
from app.celery.celery_app import celery_app
from app.database.database import sessionLocal
from app.models.jobs import Job, JobStatus
from app.models.videos import Video
from app.models.images import Image
from app.models.profiles import Profile
from app.constants.prompts import analysis_prompt, thumbnail_generation_prompt

@celery_app.task(bind=True, name="process_video_pipeline", max_retries=3, default_retry_delay=60)
def process_video_pipeline(self, job_id: str):
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

    def emit(step_name: str, status: str, payload: dict | None = None):
        try:
            events.record_event(job_uuid, step=step_name, status=status, payload=payload)
        except Exception as exc:
            print(f"Failed to record event for job {job_uuid} ({step_name}:{status}): {exc}")

    emit("job", "processing", {"video_url": video_url})

    try:
        meta = transcripts.fetch_metadata(video_url)
        emit("metadata", "completed", {"title": meta.title})

        transcript_text = transcripts.fetch_transcript(meta.video_id)
        
        prompt = analysis_prompt(transcript_text, meta.title)

        analysis_result = analysis.analyze_transcript(prompt)
        summary = analysis_result.get("summary","")
        keywords = analysis_result.get("image_search_keywords",[])
        style_direction = analysis_result.get("style_direction","")
        emit("analysis", "completed", {"summary": summary[:170],"keywords":keywords})

        image_urls = []
        for keyword in keywords:
            images = crawl.crawl_images(keyword, limit=1)
            if images and len(images) > 0:
                image_data = images[0]
                image_url = image_data.get("imageUrl")
                if image_url:
                    image_urls.append({"keyword": keyword, "url": image_url})
            else:
                print(f"No images found for keyword: {keyword}")

        thumbnail_url = None
        if len(image_urls) >= 1:
            thumbnail_prompt = thumbnail_generation_prompt(
                video_title=meta.title,
                summary=summary,
                keywords=keywords,
                style_direction=style_direction
            )
            try:
                emit("thumbnail", "started")
                thumbnail_url = generate_thumbnail(
                    job_id=str(job_uuid),
                    prompt=thumbnail_prompt,
                    reference_image_urls=[p["url"] for p in image_urls[:3]]
                )
                emit("thumbnail", "completed", {"url": thumbnail_url})
            except ValueError as e:
                print(f"Skipping thumbnail generation: {e}")
                emit("thumbnail", "skipped", {"reason": str(e)})
            except Exception as e:
                print(f"Thumbnail generation failed: {e}")
                emit("thumbnail", "failed", {"reason": str(e)})

        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                existing_video = session.execute(
                    select(Video).where(Video.job_id == job_uuid)
                ).scalar_one_or_none()
                if not existing_video:
                    video_record = Video(
                        job_id=job_uuid,
                        youtube_id=meta.video_id,
                        title=meta.title,
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
                            video_title=meta.title,
                            keywords=keywords or ["thumbnail"],
                            firecrawl_payload=None,
                            storage_public_url=thumbnail_url,
                        )
                        session.add(generated_image)
                        
                        profile = session.get(Profile, job.user_id)
                        if profile:
                            subscription = profile.subscription
                            if subscription and subscription.status in ["active", "cancelled"]:
                                from datetime import datetime
                                if subscription.status == "cancelled" and subscription.current_period_end < datetime.utcnow():
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

        emit("done", "completed", {"images_count": len(image_urls), "thumbnail_url": thumbnail_url})
        return {"status": "success"}

    except Exception as exc:
        emit("error", "failed", {"message": str(exc)})
        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                job.status = JobStatus.failed
                job.error_message = str(exc)
                try:
                    session.commit()
                except Exception:
                    session.rollback()
                    raise
        
        raise