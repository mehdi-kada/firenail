import os
import json
import base64
from typing import List
import requests
from dotenv import load_dotenv

from app.services.storage import upload_thumbnail

load_dotenv()


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
            raise ValueError(f"URL is not an image (content-type: {content_type}): {url}")
        
        image_bytes = response.content
        base64_encoded = base64.b64encode(image_bytes).decode('utf-8')
        
        data_uri = f"data:{content_type};base64,{base64_encoded}"
        
        print(f"Successfully converted image to base64 (size: {len(image_bytes)} bytes)")
        return data_uri
        
    except Exception as e:
        print(f"Failed to download and convert image from {url}: {e}")
        raise


def generate_thumbnail(
    job_id: str,
    prompt: str,
    reference_image_urls: List[str],
) -> str:
    """
    Generate thumbnail using OpenRouter API with gemini-2.5-flash-image-preview
    """
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    if not reference_image_urls:
        raise ValueError("At least one reference image URL is required")
    
    print(f"Downloading and converting {len(reference_image_urls)} images to base64...")
    
    # Download and convert images to base64 (limit to first 3)
    base64_images = []
    for url in reference_image_urls[:3]:
        try:
            base64_image = _download_image_to_base64(url)
            base64_images.append(base64_image)
        except Exception as e:
            print(f"Failed to process image {url}: {e}")
            continue
    
    if not base64_images:
        raise ValueError("No valid images could be downloaded and converted")
    
    print(f"Successfully converted {len(base64_images)} images to base64 out of {len(reference_image_urls[:3])}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://thumbnailai.com", 
        "X-Title": "ThumbnailAI"
    }
    
    content = [
        {
            "type": "text",
            "text": prompt
        }
    ]
    
    for base64_image in base64_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": base64_image
            }
        })

    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    
    payload = {
        "model": "google/gemini-2.5-flash-image-preview",
        "messages": messages,
        "modalities": ["image", "text"],
        "image_config": {
            "aspect_ratio": "16:9"
        }
    }
    
    print(f"Sending request to OpenRouter API with {len(base64_images)} base64 images")
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        error_detail = response.text
        print(f"OpenRouter API error ({response.status_code}): {error_detail}")
        raise RuntimeError(f"OpenRouter API returned {response.status_code}: {error_detail}")
    
    result = response.json()
    print(f"OpenRouter API response: {result}")
    
    try:
        image_url = None
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]
            
            # Check for images list 
            if message.get("images") and len(message["images"]) > 0:
                image_url = message["images"][0]["image_url"]["url"]
                print(f"Found image URL in message.images: {image_url}")
            
            # Fallback to content string if no images list
            elif isinstance(message.get("content"), str) and message["content"].startswith("http"):
                image_url = message["content"].strip()
                print(f"Found image URL in message.content: {image_url}")
                
            if image_url:
                image_response = requests.get(image_url, timeout=30)
                image_response.raise_for_status()
                
                thumbnail_url = upload_thumbnail(job_id, image_response.content)
                return thumbnail_url
            else:
                print(f"Response content: {message.get('content')[:100]}...")
                raise RuntimeError("No image URL found in OpenRouter response")
        else:
            raise RuntimeError("Invalid response format from OpenRouter")
            
    except Exception as e:
        print(f"Failed to process OpenRouter response: {e}")
        raise


def regenerate_thumbnail(
    job_id: str,
    image_url: str,
    prompt: str,
) -> str:
    """
    Regenerate thumbnail based on an existing image and a prompt 
    """
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")
    
    print(f"Downloading source image from {image_url}...")
    try:
        base64_image = _download_image_to_base64(image_url)
    except Exception as e:
        raise ValueError(f"Failed to download source image: {e}")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://thumbnailai.com", 
        "X-Title": "ThumbnailAI"
    }
    
    # Construct the prompt for editing
    full_prompt = f"Edit this YouTube thumbnail based on the following instruction: {prompt}. Ensure the result is a high-quality, eye-catching YouTube thumbnail."

    content = [
        {
            "type": "text",
            "text": full_prompt
        },
        {
            "type": "image_url",
            "image_url": {
                "url": base64_image
            }
        }
    ]

    messages = [
        {
            "role": "user",
            "content": content
        }
    ]
    
    payload = {
        "model": "google/gemini-2.5-flash-image-preview",
        "messages": messages,
        "modalities": ["image", "text"],
        "image_config": {
            "aspect_ratio": "16:9"
        }
    }
    
    print(f"Sending regeneration request to OpenRouter API")
    
    response = requests.post(url, headers=headers, json=payload, timeout=60)
    
    if response.status_code != 200:
        error_detail = response.text
        print(f"OpenRouter API error ({response.status_code}): {error_detail}")
        raise RuntimeError(f"OpenRouter API returned {response.status_code}: {error_detail}")
    
    result = response.json()
    print(f"OpenRouter API response: {result}")
    
    try:
        image_url = None
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0]["message"]
            
            # Check for images list 
            if message.get("images") and len(message["images"]) > 0:
                image_url = message["images"][0]["image_url"]["url"]
                print(f"Found image URL in message.images: {image_url}")
            
            # Fallback to content string if no images list
            elif isinstance(message.get("content"), str) and message["content"].startswith("http"):
                image_url = message["content"].strip()
                print(f"Found image URL in message.content: {image_url}")
                
            if image_url:
                image_response = requests.get(image_url, timeout=30)
                image_response.raise_for_status()
                
                thumbnail_url = upload_thumbnail(job_id, image_response.content)
                return thumbnail_url
            else:
                print(f"Response content: {message.get('content')[:100]}...")
                raise RuntimeError("No image URL found in OpenRouter response")
        else:
            raise RuntimeError("Invalid response format from OpenRouter")
            
    except Exception as e:
        print(f"Failed to process OpenRouter response: {e}")
        raise