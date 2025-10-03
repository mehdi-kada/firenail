from uuid import UUID

from app.models.job_events import JobEvent
from app.database.database import sessionLocal


def record_event(job_id: str | UUID, step: str, status: str, payload: dict | None = None):
    job_uuid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    with sessionLocal() as session:
        event = JobEvent(
            job_id=job_uuid,
            step=step,
            status=status,
            payload=payload or {},
        )
        session.add(event)
        session.commit()
        session.refresh(event)
        print(f"✅ Event recorded: job_id={job_uuid}, step={step}, status={status}, event_id={event.id}")
    return event

