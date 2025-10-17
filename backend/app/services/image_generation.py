import os
import time
from typing import List
from io import BytesIO
import requests
from dotenv import load_dotenv

from app.services.storage import upload_thumbnail

load_dotenv()


def _validate_image_url(url: str, timeout: int = 5) -> bool:
    """Check if image URL is accessible and returns valid image content"""
    try:
        if not url or not url.startswith(('http://', 'https://')):
            print(f"Invalid URL format: {url}")
            return False
        
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code != 200:
            print(f"URL returned status {response.status_code}: {url}")
            return False
        
        content_type = response.headers.get('content-type', '').lower()
        if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'jpg', 'webp']):
            print(f"URL is not an image (content-type: {content_type}): {url}")
            return False
        
        return True
    except Exception as e:
        print(f"Failed to validate URL {url}: {e}")
        return False


def generate_thumbnail(
    job_id: str,
    prompt: str,
    reference_image_urls: List[str],
) -> str:
    """
    Generate thumbnail using Freepik API
    """
    api_key = os.environ.get('FREEPIK_API_KEY')
    if not api_key:
        raise ValueError("FREEPIK_API_KEY environment variable not set")
    
    if not reference_image_urls:
        raise ValueError("At least one reference image URL is required")
    
    print(f"Validating {len(reference_image_urls)} image URLs...")
    valid_urls = [url for url in reference_image_urls[:3] if _validate_image_url(url)]
    
    if not valid_urls:
        raise ValueError("No valid image URLs found after validation")
    
    print(f"Using {len(valid_urls)} valid URLs out of {len(reference_image_urls[:3])}")
    
    base_url = "https://api.freepik.com/v1/ai/gemini-2-5-flash-image-preview"
    
    payload = {
        "reference_images": valid_urls,
        "prompt": prompt,
        "aspect_ratio": "widescreen_16_9",
    }
    
    headers = {
        "x-freepik-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to Freepik API with payload: {payload}")
    
    response = requests.post(base_url, json=payload, headers=headers, timeout=60)
    
    if response.status_code != 200:
        error_detail = response.text
        print(f"Freepik API error ({response.status_code}): {error_detail}")
        raise RuntimeError(f"Freepik API returned {response.status_code}: {error_detail}")
    
    result = response.json()
    print(f"Freepik API response: {result}")
    
    if not result.get("data") or not result["data"].get("task_id"):
        raise RuntimeError("No task_id returned from Freepik API")
    
    task_id = result["data"]["task_id"]
    
    max_attempts = 60
    poll_interval = 5
    
    for attempt in range(max_attempts):
        poll_url = f"{base_url}/{task_id}"
        poll_response = requests.get(poll_url, headers={"x-freepik-api-key": api_key}, timeout=30)
        poll_response.raise_for_status()
        
        poll_result = poll_response.json()
        status = poll_result.get("data", {}).get("status")
        
        print(f"Polling attempt {attempt + 1}/{max_attempts} - Status: {status}")
        
        if status == "COMPLETED":
            print(f"Full completed response: {poll_result}")
            generated = poll_result.get("data", {}).get("generated", [])
            error_field = poll_result.get("data", {}).get("error")
            
            if error_field:
                raise RuntimeError(f"Freepik API returned error in completed task: {error_field}")
            
            if generated and len(generated) > 0:
                image_url = generated[0] if isinstance(generated[0], str) else generated[0].get("url")
                if not image_url:
                    raise RuntimeError("No image URL in completed task")
                
                image_response = requests.get(image_url, timeout=30)
                image_response.raise_for_status()
                
                thumbnail_url = upload_thumbnail(job_id, image_response.content)
                return thumbnail_url
            else:
                raise RuntimeError(f"No generated images in completed task. Full response: {poll_result}")
        
        elif status == "FAILED":
            error_msg = poll_result.get("data", {}).get("error", "Unknown error")
            print(f"Full failed response: {poll_result}")
            raise RuntimeError(f"Freepik image generation failed: {error_msg}")
        
        time.sleep(poll_interval)
    
    raise RuntimeError(f"Freepik image generation timed out after {max_attempts * poll_interval} seconds")
