import os
from pathlib import Path
from typing import List, Optional
from io import BytesIO
import re

from google import genai
from PIL import Image
from dotenv import load_dotenv

from app.services.storage import upload_thumbnail, delete_local_file

load_dotenv()


class GeminiQuotaError(Exception):
    def __init__(self, retry_after: Optional[int] = None, message: str = "Gemini API quota exceeded"):
        self.retry_after = retry_after
        super().__init__(message)


def _parse_retry_after(msg: str) -> Optional[int]:
    m = re.search(r"retryDelay['\"]:\s*'(\d+)s'", msg)
    if m:
        return int(m.group(1))
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", msg, re.IGNORECASE)
    if m:
        return int(float(m.group(1)))
    return None


def generate_thumbnail(
    job_id: str,
    prompt: str,
    reference_image_paths: List[str],
) -> str:
    """
    Generate thumbnail using nano banana
    """
    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable not set")
    
    if not reference_image_paths:
        raise ValueError("At least one reference image path is required")
    
    client = genai.Client(api_key=api_key)
    
    reference_images = []
    for img_path in reference_image_paths:
        if not Path(img_path).exists():
            raise ValueError(f"Reference image not found: {img_path}")
        reference_images.append(Image.open(img_path))
    
    contents = [prompt] + reference_images[:3]
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=contents,
        )
    except Exception as e:
        msg = str(e)
        if "429" in msg or "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower():
            retry_after = _parse_retry_after(msg)
            raise GeminiQuotaError(retry_after=retry_after)
        raise
    
    generated_image: Optional[Image.Image] = None
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            generated_image = Image.open(BytesIO(part.inline_data.data))
            break
    
    if generated_image is None:
        raise RuntimeError("No image generated in Gemini response")
    
    img_bytes = BytesIO()
    generated_image.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    thumbnail_url = upload_thumbnail(job_id, img_bytes.getvalue())
    
    for img_path in reference_image_paths:
        delete_local_file(img_path)
    
    return thumbnail_url
