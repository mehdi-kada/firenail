import uuid 
import io
from pathlib import Path
from typing import Optional
from PIL import Image

from app.supabase.supabase_client import supabase_admin


# def optimize_image(image_bytes: bytes, max_width : int = 1280, quality: int = 85) -> bytes:
#     """ Optimizes the image from any format to a webp"""
#     image = Image.open(io.BytesIO(image_bytes))
#     if image.mode in ('RGBA', 'LA', 'P'):
#         background = Image.new('RGB', image.size, (255,255,255))
#         if image.mode == 'P':
#             image = image.convert('RGBA')
#         background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
#         image = background
#
#     if image.width > max_width:
#         ratio = max_width/image.width
#         new_height = int(image.height * ratio)
#         image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
#
#     output = io.BytesIO()
#     image.save(output, format='WebP',quality=quality, method=6)
#     output.seek(0)
#     return output.read()


def     upload_thumbnail(job_id: str, image_bytes: bytes):
    """Upload thumbnail image to storage"""

    # thumbnail_bytes = optimize_image(image_bytes)
    thumbnail_bytes = image_bytes
    
    file_id = str(uuid.uuid4())

    display_path = f"thumbnails/{job_id}/{file_id}.png"
    supabase_admin.storage.from_("thumbnails").upload(
        display_path,
        thumbnail_bytes,
        {
            "content-type": "image/webp",
            'cache-control': 'public, max-age=31536000'
        }
    )

    url = supabase_admin.storage.from_("thumbnails").get_public_url(display_path)

    return url