import os
import time
import base64
import logging
from typing import List
import requests
from dotenv import load_dotenv
from openai import OpenAI

from app.services.storage import upload_thumbnail

load_dotenv()

logger = logging.getLogger(__name__)

def _download_image_to_base64(url: str, timeout: int = 20) -> str:
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
    Internal helper to call AI Gateway API and return the generated image.
    Returns the image bytes of the generated image.
    """
    api_key = os.getenv("AI_GATEWAY_API_KEY") or os.getenv("VERCEL_OIDC_TOKEN")
    base_url = (
        os.getenv("AI_GATEWAY_BASE_OPENAI_COMPAT_URL")
        or "https://ai-gateway.vercel.sh/v1"
    )

    if not api_key:
        raise ValueError("AI_GATEWAY_API_KEY environment variable is required")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    # Build message content with images and prompt
    content = []
    for image in reference_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": image
            }
        })
    content.append({
        "type": "text",
        "text": prompt
    })

    print(f"Sending request to AI Gateway with {len(reference_images)} reference images")

    response = client.chat.completions.create(
    model="google/gemini-2.5-flash-image",
    messages=[{"role": "user", "content": content}],
    extra_body={
        "providerOptions": {
            "google": {
                "responseModalities": ["TEXT", "IMAGE"],
                "imageConfig": {"aspectRatio": "16:9"},
            }
        }
    },
    )

    message = response.choices[0].message

    # Check if images are in the response
    if not hasattr(message, 'images') or not message.images:
        raise RuntimeError(f"No image data received from API. Response: {message.content}")

    # Extract the image data from the response
    image_data = message.images[0]
    image_url = image_data["image_url"]["url"]

    if image_url.startswith("data:"):
        # Extract base64 part after the comma
        base64_data = image_url.split(",", 1)[1]
        image_bytes = base64.b64decode(base64_data)
    else:
        raise RuntimeError("Unexpected image format in response")

    print(f"Generated image size: {len(image_bytes)} bytes")
    if message.content:
        print(f"Model response: {message.content}")

    return image_bytes


def generate_thumbnail(
    job_id: str,
    prompt: str,
    reference_image_urls: List[str],
) -> str:
    """
    Generate thumbnail using Freepik API
    """
    api_key = os.getenv("AI_GATEWAY_API_KEY") or os.getenv("VERCEL_OIDC_TOKEN")
    if not api_key:
        raise ValueError("AI_GATEWAY_API_KEY environment variable not set")

    if not reference_image_urls:
        raise ValueError("At least one reference image URL is required")
    
    print(f"Processing {len(reference_image_urls)} images...")
    
    # Process images
    processed_images = []
    for url in reference_image_urls[:3]:
        try:
            print(f"Downloading and converting image: {url}")
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
    api_key = os.getenv("AI_GATEWAY_API_KEY") or os.getenv("VERCEL_OIDC_TOKEN")
    if not api_key:
        raise ValueError("AI_GATEWAY_API_KEY environment variable not set")

    print(f"Preparing source image from {image_url}...")
    try:
        print(f"Downloading and converting source image: {image_url}")
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