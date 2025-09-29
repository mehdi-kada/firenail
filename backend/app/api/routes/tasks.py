from httpx import get
from pydantic import UUID4, BaseModel, HttpUrl
from app.auth.validate import get_current_user


from fastapi import APIRouter, Depends, status
from app.database.database import AsyncSessionLocal
from app.models.jobs import Job, JobStatus
from app.celery.celery_app import celery_app

class TaskResponse(BaseModel):
    task_id: UUID4
    status: str


router = APIRouter()

@router.post("/tasks/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(payload: HttpUrl, user_id: str = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        job = Job(video_url=payload, status=JobStatus.queued, user_id=user_id)
        session.add(job)
        await session.commit()
        await session.refresh(job)

    celery_app.send_task('process_video_pipeline', args=[str(job.id)])
    return TaskResponse(task_id=job.id, status=job.status.value)



@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: UUID4, user_id: str = Depends(get_current_user)):
    async with AsyncSessionLocal() as session:
        job = await session.get(Job, task_id)
        if not job or job.user_id != user_id:
            return {"detail": "Task not found"}

    return TaskResponse(task_id=job.id, status=job.status.value)

    