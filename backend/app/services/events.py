from app.models.job_events import JobEvent
from app.database.database import sessionLocal



def record_event(job_id: str, step: str, status: str, payload: dict | None = None):
    with sessionLocal() as session:
        event = JobEvent(
            job_id=job_id,
            step=step,
            status=status,
            payload=payload
        )
        session.add(event)
        session.commit()

