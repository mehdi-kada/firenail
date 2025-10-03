import os
import uuid
from datetime import UTC, datetime

from pydantic import UUID4, BaseModel, HttpUrl

from fastapi import APIRouter, BackgroundTasks, Depends, status, HTTPException

from app.auth.validate import get_current_user_profile
from app.database.database import AsyncSessionLocal
from app.models.jobs import Job, JobStatus
from app.models.profiles import Profile
from app.celery.celery_app import celery_app
from app.services import events
from app.supabase.supabase_client import supabase_admin
from app.celery.tasks.video_pipeline import process_video_pipeline


def enqueue_video_pipeline(job_id: str):
    try:
        process_video_pipeline.apply_async(args=[job_id], ignore_result=True)
    except Exception as exc:
        print(f"Error enqueuing job {job_id}: {exc}")

class CreateTaskRequest(BaseModel):
    url: HttpUrl

class TaskResponse(BaseModel):
    task_id: UUID4
    status: str


router = APIRouter()


@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    profile: Profile = Depends(get_current_user_profile),
):
    job_id = uuid.uuid4()
    job_data = {
        "id": str(job_id),
        "user_id": str(profile.id),
        "video_url": str(request.url),
        "status": JobStatus.queued.value,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat(),
    }

    try:
        response = supabase_admin.table("jobs").insert(job_data).execute()
        if getattr(response, "error", None):
            raise RuntimeError(response.error)
        if not getattr(response, "data", None):
            raise RuntimeError("Empty response from Supabase when creating job")
    except Exception as exc:
        print(f"Error creating job {job_id}: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create job")

    job_id_str = str(job_id)
    background_tasks.add_task(events.record_event, job_id_str, "job", "queued", {"video_url": str(request.url)})
    background_tasks.add_task(enqueue_video_pipeline, job_id_str)
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

    