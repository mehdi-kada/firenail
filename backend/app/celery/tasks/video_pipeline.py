from multiprocessing import Value
from uuid import UUID
from celery import shared_task
from app.services import transcripts, analysis, storage, events, crawl
from app.celery import celery_app
from app.database.database import sessionLocal
from app.models.jobs import Job, JobStatus
from app.constants.prompts import analysis_prompt

@shared_task(bind=True, name="process_video_pipeline", max_retries=3, default_retry_delay=60)
def process_video_pipeline(self, job_id: str):
    job_uuid = UUID(job_id)

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
        keywords = analysis_result.get("image_keywords",[])
        step("analysis", {"summary": summary[:140],"keywords":keywords})



        



    except Exception as exc:
        events.record_event(job_id, step="error", status="failed", payload={"message": str(exc)})
        with sessionLocal() as session:
            job = session.get(Job, job_id)
            if job:
                job.status = JobStatus.failed
                job.error_message = str(exc)
                session.commit()
        
        raise