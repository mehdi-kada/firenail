from datetime import UTC, datetime
from uuid import UUID, uuid4

from typing import Any

from app.supabase.supabase_client import supabase_admin


def _to_serializable(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _to_serializable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_serializable(v) for v in value]
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


def record_event(job_id: str | UUID, step: str, status: str, payload: dict | None = None):
    job_uuid = job_id if isinstance(job_id, UUID) else UUID(str(job_id))
    event_payload = {
        "id": str(uuid4()),
        "job_id": str(job_uuid),
        "step": step,
        "status": status,
        "payload": _to_serializable(payload or {}),
        "created_at": datetime.now(UTC).isoformat(),
    }

    response = supabase_admin.table("job_events").insert(event_payload).execute()

    data = getattr(response, "data", None)
    if (not data) and getattr(response, "error", None) is None:
        with supabase_admin.client.postgrest.session as session:
            fetch_response = supabase_admin.table("job_events").select("id").eq("job_id", str(job_uuid)).eq("step", step).order("created_at", desc=True).limit(1).execute()
            data = getattr(fetch_response, "data", None)

    error = getattr(response, "error", None)
    if error:
        raise RuntimeError(f"Failed to record event: {error}")

    if data and isinstance(data, list) and data:
        return data[0]

    return event_payload

