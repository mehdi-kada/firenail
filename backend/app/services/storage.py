import uuid
from app.supabase.supabase_client import supabase_admin
import io



def upload_thumbnail(job_id: str, image_bytes: bytes):
    path = f"thumbnails/{job_id}/{uuid.uuid4()}.png"
    supabase_admin.storage.from_('thumbnails').upload(path, io.BytesIO(image_bytes), {'content-type': 'image/png'})
    url = supabase_admin.storage.from_('thumbnails').get_public_url(path)
    return url