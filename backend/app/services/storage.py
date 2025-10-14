import uuid
import requests
from pathlib import Path
from typing import Optional

from app.supabase.supabase_client import supabase_admin


def upload_thumbnail(job_id: str, image_bytes: bytes):
    path = f"thumbnails/{job_id}/{uuid.uuid4()}.png"
    supabase_admin.storage.from_('thumbnails').upload(path, image_bytes, {'content-type': 'image/png'})
    url = supabase_admin.storage.from_('thumbnails').get_public_url(path)
    return url


