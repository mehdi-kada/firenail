import os
import time
import base64
import logging
from typing import List
import requests
from dotenv import load_dotenv

from app.services.storage import upload_thumbnail

load_dotenv()

logger = logging.getLogger(__name__)

def _download_image_to_base64(url: str, timeout: int = 10) -> str:
    """
    Download an image from a URL and convert it to base64 string.
    Returns base64 encoded string with data URI prefix (data:image/...;base64,...)
    """
    try:
        if not url or not url.startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL format: {url}")
        
        print(f"Downloading image from: {url}")
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        
        if response.status_code != 200:
            raise ValueError(f"URL returned status {response.status_code}: {url}")
        
        content_type = response.headers.get('content-type', '').lower()
        if not any(img_type in content_type for img_type in ['image/', 'jpeg', 'png', 'jpg', 'webp']):
            if url.lower().endswith('.png'):
                content_type = 'image/png'
            elif url.lower().endswith('.webp'):
                content_type = 'image/webp'
            elif url.lower().endswith(('.jpg', '.jpeg')):
                content_type = 'image/jpeg'
            else:
                 raise ValueError(f"URL is not an image (content-type: {content_type}): {url}")
        
        image_bytes = response.content
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
        data_uri = f"data:{content_type};base64,{base64_encoded}"
        
        print(f"Successfully converted image to base64 (size: {len(image_bytes)} bytes)")
        return data_uri
        
    except Exception as e:
        print(f"Failed to download and convert image from {url}: {e}")
        raise


def _is_url_public(url: str, timeout: int = 5) -> bool:
    """Check if a URL is publicly accessible."""
    try:
        response = requests.head(url, timeout=timeout, allow_redirects=True)
        if response.status_code == 200:
            return True
        # Fallback to GET for servers that block HEAD
        response = requests.get(url, timeout=timeout, stream=True, allow_redirects=True)
        response.close()
        return response.status_code == 200
    except Exception:
        return False


def _generate_with_freepik(prompt: str, reference_images: List[str]) -> bytes:
    """
    Internal helper to call Freepik API, poll for completion, and download the result.
    Returns the image bytes of the generated image.
    """
    api_key = os.environ.get('FREEPIK_API_KEY')
    if not api_key:
        raise ValueError("FREEPIK_API_KEY environment variable not set")

    base_url = "https://api.freepik.com/v1/ai/text-to-image/seedream-v4-edit"
    
    payload = {
        "reference_images": reference_images,
        "prompt": prompt,
        "aspect_ratio": "widescreen_16_9",
    }
    
    headers = {
        "x-freepik-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    print(f"Sending request to Freepik API with {len(reference_images)} reference images")
    
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
                
                print(f"Downloading generated image from: {image_url}")
                image_response = requests.get(image_url, timeout=30)
                image_response.raise_for_status()
                return image_response.content
            else:
                raise RuntimeError(f"No generated images in completed task. Full response: {poll_result}")
        
        elif status == "FAILED":
            error_msg = poll_result.get("data", {}).get("error", "Unknown error")
            print(f"Full failed response: {poll_result}")
            raise RuntimeError(f"Freepik image generation failed: {error_msg}")
        
        time.sleep(poll_interval)
    
    raise RuntimeError(f"Freepik image generation timed out after {max_attempts * poll_interval} seconds")


def generate_thumbnail(
    job_id: str,
    prompt: str,
    reference_image_urls: List[str],
) -> str:
    """
    Generate thumbnail using Freepik API
    """
    if not os.environ.get('FREEPIK_API_KEY'):
        raise ValueError("FREEPIK_API_KEY environment variable not set")

    if not reference_image_urls:
        raise ValueError("At least one reference image URL is required")
    
    print(f"Processing {len(reference_image_urls)} images...")
    
    # Process images
    processed_images = []
    for url in reference_image_urls[:3]:
        try:
            if _is_url_public(url):
                print(f"URL is public, using directly: {url}")
                processed_images.append(url)
            else:
                print(f"URL not public, downloading and converting: {url}")
                base64_image = _download_image_to_base64(url)
                processed_images.append(base64_image)
        except Exception as e:
            print(f"Failed to process image {url}: {e}")
            continue
    
    if not processed_images:
        raise ValueError("No valid images could be processed")
    
    print(f"Successfully processed {len(processed_images)} images out of {len(reference_image_urls[:3])}")
    
    try:
        image_content = _generate_with_freepik(prompt, processed_images)
        thumbnail_url = upload_thumbnail(job_id, image_content)
        return thumbnail_url
    except Exception as e:
        print(f"Failed to generate thumbnail: {e}")
        raise


def regenerate_thumbnail(
    job_id: str,
    image_url: str,
    prompt: str,
) -> str:
    """
    Regenerate thumbnail based on an existing image and a prompt using Freepik API
    """
    if not os.environ.get('FREEPIK_API_KEY'):
        raise ValueError("FREEPIK_API_KEY environment variable not set")

    print(f"Preparing source image from {image_url}...")
    try:
        if _is_url_public(image_url):
            print(f"URL is public, using directly: {image_url}")
            processed_image = image_url
        else:
            print(f"URL not public, downloading and converting: {image_url}")
            processed_image = _download_image_to_base64(image_url)
    except Exception as e:
        raise ValueError(f"Failed to process source image: {e}")
    
    # Construct the prompt for editing
    full_prompt = f"Edit this YouTube thumbnail based on the following instruction: {prompt}. Ensure the result is a high-quality, eye-catching YouTube thumbnail."

    try:
        image_content = _generate_with_freepik(full_prompt, [processed_image])
        thumbnail_url = upload_thumbnail(job_id, image_content)
        return thumbnail_url
    except Exception as e:
        print(f"Failed to regenerate thumbnail: {e}")
        raise