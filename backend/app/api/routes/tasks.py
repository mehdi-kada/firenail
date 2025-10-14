import asyncio
import uuid
from datetime import UTC, datetime

from pydantic import UUID4, BaseModel, HttpUrl

from fastapi import APIRouter, Depends, status, HTTPException

from app.auth.validate import get_current_user_profile
from app.database.database import AsyncSessionLocal
from app.models.jobs import Job, JobStatus
from app.models.profiles import Profile
from app.services import events
from app.celery.tasks.video_pipeline import process_video_pipeline


def enqueue_video_pipeline(job_id: str):
    try:
        # Add producer-side retry logic for broker connection issues
        process_video_pipeline.apply_async(
            args=[job_id],
            ignore_result=True,
            retry=True,
            retry_policy={
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.5,
            }
        )
    except Exception as exc:
        # This will now catch errors only after retries have failed
        print(f"CRITICAL: Failed to enqueue job {job_id} after multiple retries: {exc}")

class CreateTaskRequest(BaseModel):
    url: HttpUrl

class TaskResponse(BaseModel):
    task_id: UUID4
    status: str


router = APIRouter()


async def _run_background(job_id: str, video_url: str):
    loop = asyncio.get_running_loop()

    def record():
        try:
            events.record_event(job_id, "job", "queued", {"video_url": video_url})
        except Exception as exc:
            print(f"Error recording queued event for job {job_id}: {exc}")

    def enqueue():
        try:
            enqueue_video_pipeline(job_id)
        except Exception as exc:
            print(f"Error enqueuing pipeline for job {job_id}: {exc}")

    try:
        await asyncio.gather(
            loop.run_in_executor(None, record),
            loop.run_in_executor(None, enqueue),
        )
    except Exception as exc:
        print(f"Unexpected error in background task for job {job_id}: {exc}")


@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    profile: Profile = Depends(get_current_user_profile),
):
    job_id = uuid.uuid4()
    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            user_id=profile.id,
            video_url=str(request.url),
            status=JobStatus.queued,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        session.add(job)

        try:
            await session.commit()
        except Exception as exc:
            await session.rollback()
            print(f"Error creating job {job_id}: {exc}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create job")

    job_id_str = str(job_id)
    
    # Create background task with proper exception handling
    task = asyncio.create_task(_run_background(job_id_str, str(request.url)))
    # Add done callback to log any unhandled exceptions
    task.add_done_callback(lambda t: t.exception() if not t.cancelled() else None)
    
    print(f"Queued job {job_id} for video URL {request.url}")

    return TaskResponse(task_id=job_id, status=JobStatus.queued.value)



@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: UUID4,
    profile: Profile = Depends(get_current_user_profile),
):
    async with AsyncSessionLocal() as session:
        job = await session.get(Job, task_id)
        if not job or job.user_id != profile.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return TaskResponse(task_id=job.id, status=job.status.value)

    