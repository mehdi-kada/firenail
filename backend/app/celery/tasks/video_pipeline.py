from uuid import UUID
from celery import shared_task
from app.services import transcripts, analysis, events, crawl
from app.services.image_generation import generate_thumbnail
from app.celery import celery_app
from app.database.database import sessionLocal
from app.models.jobs import Job, JobStatus
from app.models.videos import Video
from app.models.images import Image
from app.constants.prompts import analysis_prompt, thumbnail_generation_prompt

@shared_task(bind=True, name="process_video_pipeline", max_retries=3, default_retry_delay=60)
def process_video_pipeline(self, job_id: str):
    job_uuid = UUID(job_id)

    print(f"Starting video processing pipeline for job {job_id}")
    with sessionLocal() as session:
        job = session.get(Job, job_uuid)
        if not job : 
            raise ValueError(f"Job {job_id} not found")
        job.status = JobStatus.processing
        session.commit()
        video_url = job.video_url


    def step(name: str, payload: dict|None = None):
        events.record_event(job_id, step=name, status="processing", payload=payload)

    try:
        meta = transcripts.fetch_metadata(video_url)
        step("metadata", {"title": meta.title})

        transcript_text = transcripts.fetch_transcript(meta.video_id)
        step("transcript", {"chars": len(transcript_text)})
        
        prompt = analysis_prompt(transcript_text, meta.title)

        analysis_result = analysis.analyze_transcript(prompt)
        summary = analysis_result.get("summary","")
        keywords = analysis_result.get("image_search_keywords",[])
        step("analysis", {"summary": summary[:140],"keywords":keywords})

        image_urls = []
        image_records = []
        for keyword in keywords:
            images = crawl.crawl_images(keyword, limit=1)
            if images and len(images) > 0:
                image_data = images[0]
                image_url = image_data.get("imageUrl")
                if image_url:
                    image_urls.append({"keyword": keyword, "url": image_url})
                    
                    image_records.append({
                        "keyword": keyword,
                        "url": image_url,
                        "firecrawl_payload": image_data
                    })
            else:
                print(f"No images found for keyword: {keyword}")
        
        step("images", {"count": len(image_urls), "urls": [p["url"] for p in image_urls]})

        thumbnail_url = None
        if len(image_urls) >= 1:
            thumbnail_prompt = thumbnail_generation_prompt(
                video_title=meta.title,
                summary=summary,
                keywords=keywords
            )
            try:
                thumbnail_url = generate_thumbnail(
                    job_id=str(job_uuid),
                    prompt=thumbnail_prompt,
                    reference_image_urls=[p["url"] for p in image_urls[:3]]
                )
                step("thumbnail", {"url": thumbnail_url})
            except ValueError as e:
                print(f"Skipping thumbnail generation: {e}")
                step("thumbnail", {"status": "skipped", "reason": str(e)})
            except Exception as e:
                print(f"Thumbnail generation failed: {e}")
                step("thumbnail", {"status": "failed", "reason": str(e)})

        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                video_record = Video(
                    job_id=job_uuid,
                    youtube_id=meta.video_id,
                    title=meta.title,
                    transcript=transcript_text,
                    summary=summary
                )
                session.add(video_record)
                
                for img_data in image_records:
                    image_record = Image(
                        job_id=job_uuid,
                        profile_id=job.user_id,
                        keywords=[img_data["keyword"]],
                        firecrawl_payload=img_data["firecrawl_payload"],
                        storage_public_url=img_data["url"]
                    )
                    session.add(image_record)
                
                job.status = JobStatus.completed
                session.commit()

        events.record_event(job_id, step="done", status="completed", payload={"images_count": len(image_urls)})


    except Exception as exc:
        events.record_event(job_id, step="error", status="failed", payload={"message": str(exc)})
        with sessionLocal() as session:
            job = session.get(Job, job_uuid)
            if job:
                job.status = JobStatus.failed
                job.error_message = str(exc)
                session.commit()
        
        raise