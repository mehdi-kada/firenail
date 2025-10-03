import os
import uuid
from datetime import UTC, datetime

from pydantic import UUID4, BaseModel, HttpUrl

from fastapi import APIRouter, Depends, status, HTTPException

from app.auth.validate import get_current_user_profile
from app.database.database import AsyncSessionLocal
from app.models.jobs import Job, JobStatus
from app.models.profiles import Profile
from app.celery.celery_app import celery_app
from app.services import events
from app.supabase.supabase_client import supabase_admin
from app.celery.tasks.video_pipeline import process_video_pipeline

class CreateTaskRequest(BaseModel):
    url: HttpUrl

class TaskResponse(BaseModel):
    task_id: UUID4
    status: str


router = APIRouter()


@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    request: CreateTaskRequest,
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

    events.record_event(job_id, step="job", status="queued", payload={"video_url": str(request.url)})
    print(f"Enqueuing job {job_id} for video URL {request.url}")
    
    try:
        process_video_pipeline.delay(job_id=str(job_id))
    except Exception as exc:
        print(f"Error enqueuing task: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to enqueue task. Celery broker may be unavailable."
        )
    
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

    