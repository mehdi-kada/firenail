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


def download_and_save_image(image_url: str, job_id: str, keyword: str) -> str:
    """Download image from URL and save locally"""
    storage_dir = Path("storage/images") / str(job_id)
    storage_dir.mkdir(parents=True, exist_ok=True)
    
    response = requests.get(image_url, timeout=30)
    response.raise_for_status()
    
    ext = Path(image_url).suffix or ".jpg"
    filename = f"{keyword.replace(' ', '_')[:50]}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = storage_dir / filename
    
    with open(filepath, "wb") as f:
        f.write(response.content)
    
    return str(filepath)


def delete_local_file(path: str) -> bool:
    file_path = Path(path)
    if not file_path.exists():
        return False
    try:
        file_path.unlink()
        parent: Optional[Path] = file_path.parent
        if parent and parent.exists() and not any(parent.iterdir()):
            parent.rmdir()
        return True
    except Exception:
        return False