import os
import uuid
from datetime import datetime, UTC
from pydantic import UUID4, BaseModel, HttpUrl
from app.auth.validate import get_current_user_profile


from fastapi import APIRouter, Depends, status, HTTPException

from app.database.database import AsyncSessionLocal
from app.models.jobs import Job, JobStatus
from app.models.profiles import Profile
from app.celery.celery_app import celery_app
from app.supabase.supabase_client import supabase_admin

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
    if not os.getenv("CELERY_BROKER_URL"):
        return {"detail": "Task queue is not configured."}
    
    print(f"Creating job for URL: {request.url}")
    
    # Create job directly via Supabase API
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
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create job")
    except Exception as e:
        print(f"Error creating job: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

    print(f"Enqueuing task for job {job_id}")
    celery_app.send_task('process_video_pipeline', args=[str(job_id)])
    print(f"Task enqueued for job {job_id}")
    return TaskResponse(task_id=job_id, status=JobStatus.queued.value)



@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: UUID4,
    profile: Profile = Depends(get_current_user_profile),
):
    async with AsyncSessionLocal() as session:
        job = await session.get(Job, task_id)
        if not job or job.user_id != profile.id:
            return {"detail": "Task not found"}

    return TaskResponse(task_id=job.id, status=job.status.value)

    