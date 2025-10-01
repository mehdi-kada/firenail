import os
from pydantic import UUID4, BaseModel, HttpUrl
from app.auth.validate import get_current_user_profile


from fastapi import APIRouter, Depends, status

from app.database.database import AsyncSessionLocal
from app.models.jobs import Job, JobStatus
from app.models.profiles import Profile
from app.celery.celery_app import celery_app

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
    async with AsyncSessionLocal() as session:
        job = Job(video_url=str(request.url), status=JobStatus.queued, user_id=profile.id)
        session.add(job)
        await session.commit()
        await session.refresh(job)

    print(f"Enqueuing task for job {job.id}")
    celery_app.send_task('process_video_pipeline', args=[str(job.id)])
    print(f"Task enqueued for job {job.id}")
    return TaskResponse(task_id=job.id, status=job.status.value)



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

    