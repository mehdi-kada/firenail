import os
import json
import base64
import re
from typing import List, Tuple, Optional
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


def _extract_image_from_response(result: dict) -> Tuple[Optional[bytes], Optional[str]]:
    """
    Helper function to extract image data or URL from OpenRouter/Gemini response.
    Returns (image_data_bytes, image_url_string).
    """
    if not ("choices" in result and len(result["choices"]) > 0):
         raise RuntimeError("Invalid response format from OpenRouter: No choices found")
    
    message = result["choices"][0]["message"]
    image_data = None
    image_url = None

    # 1. Check message.images (OpenAI style extension)
    if message.get("images") and len(message["images"]) > 0:
        image_url = message["images"][0]["image_url"]["url"]
        print(f"Found image URL in message.images: {image_url}")
        return image_data, image_url

    # 2. Check message.content
    content = message.get("content")
    if not content:
         # If no content and no images, raise error
         raise RuntimeError("No content or images in response message")

    if isinstance(content, list):
        # Multimodal list (e.g. [{"type": "text", ...}, {"type": "image_url", ...}])
        for part in content:
             if isinstance(part, dict):
                 # Check for inline_data format (Vertex AI style)
                 if "inline_data" in part and "data" in part["inline_data"]:
                      try:
                          image_data = base64.b64decode(part["inline_data"]["data"])
                          print(f"Decoded inline_data: {len(image_data)} bytes")
                          return image_data, image_url
                      except Exception as e:
                          print(f"Failed to decode inline_data: {e}")
                 
                 # Check for image_url format in content list
                 elif part.get("type") == "image_url" and "image_url" in part:
                      url = part["image_url"].get("url", "")
                      if url.startswith("http"):
                           image_url = url
                           print(f"Found image URL in content list: {image_url}")
                           return image_data, image_url
                      elif url.startswith("data:image/"):
                           try:
                               base64_data = url.split(",", 1)[1]
                               image_data = base64.b64decode(base64_data)
                               print(f"Decoded base64 from content list: {len(image_data)} bytes")
                               return image_data, image_url
                           except Exception as e:
                               print(f"Failed to decode base64 from content list: {e}")

    elif isinstance(content, str):
        content_preview = content[:200].replace("\n", " ")
        print(f"Processing string content (len={len(content)}): {content_preview}...")
        
        # A. Check for HTTP URL at start
        # Some models output just the URL
        if content.strip().startswith("http"):
             candidates = content.strip().split()
             if candidates:
                image_url = candidates[0]
                print(f"Found image URL in message.content: {image_url}")
                return image_data, image_url

        # B. Check for data URI using Regex (finds it anywhere in text)
        # Pattern: data:image/<type>;base64,<data>
        # We look for the pattern and capture the data.
        # Using a generous pattern for base64 chars.
        data_uri_pattern = r"data:image\/[a-zA-Z]+;base64,([a-zA-Z0-9+/=]+)"
        match = re.search(data_uri_pattern, content)
        if match:
             print("Found base64 data URI via regex")
             try:
                 base64_data = match.group(1)
                 # Validate padding if needed? standard b64decode usually handles it if valid.
                 image_data = base64.b64decode(base64_data)
                 print(f"Decoded base64 image data from regex: {len(image_data)} bytes")
                 return image_data, image_url
             except Exception as e:
                 print(f"Failed to decode regex-found base64: {e}")

        # C. Check for raw base64 (if content is mostly base64)
        # Clean up whitespace and markdown code blocks
        cleaned_content = content.replace("```base64", "").replace("```", "").strip()
        
        # Heuristic: starts with data:image but maybe regex missed it? 
        # Or just raw base64.
        # Check if it starts with { (JSON) -> skip
        # Lowered threshold to 50 to support smaller images in tests
        if len(cleaned_content) > 50 and not cleaned_content.startswith("{"):
             # Try to decode as raw base64
             # If it fails, it fails.
             if cleaned_content.startswith("data:image/"):
                 # Manual split if regex failed for some reason
                 try:
                    base64_data = cleaned_content.split(",", 1)[1]
                    image_data = base64.b64decode(base64_data)
                    print(f"Decoded data URI manually: {len(image_data)} bytes")
                    return image_data, image_url
                 except Exception:
                    pass
             
             print("Attempting to decode raw base64 content")
             try:
                 image_data = base64.b64decode(cleaned_content)
                 print(f"Decoded raw base64 image data: {len(image_data)} bytes")
                 return image_data, image_url
             except Exception as e:
                 print(f"Content is not valid raw base64: {e}")

    return image_data, image_url


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
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            error_detail = response.text[:1000] # Truncate error log
            print(f"OpenRouter API error ({response.status_code}): {error_detail}")
            raise RuntimeError(f"OpenRouter API returned {response.status_code}: {error_detail}")
        
        result = response.json()
        # Sanitize log: Don't print full result to avoid huge base64 dumps
        print(f"OpenRouter API response received. ID: {result.get('id', 'unknown')}, Model: {result.get('model', 'unknown')}")
        
        image_data, image_url = _extract_image_from_response(result)
        
        if image_data:
            thumbnail_url = upload_thumbnail(job_id, image_data)
            return thumbnail_url
        elif image_url:
            print(f"Downloading generated image from URL: {image_url}")
            image_response = requests.get(image_url, timeout=30)
            image_response.raise_for_status()
            thumbnail_url = upload_thumbnail(job_id, image_response.content)
            return thumbnail_url
        else:
            raise RuntimeError("No image data or URL found in OpenRouter response after parsing.")
            
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
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            error_detail = response.text[:1000] # Truncate
            print(f"OpenRouter API error ({response.status_code}): {error_detail}")
            raise RuntimeError(f"OpenRouter API returned {response.status_code}: {error_detail}")
        
        result = response.json()
        print(f"OpenRouter API response received. ID: {result.get('id', 'unknown')}")
        
        image_data, generated_image_url = _extract_image_from_response(result)
        
        if image_data:
            thumbnail_url = upload_thumbnail(job_id, image_data)
            return thumbnail_url
        elif generated_image_url:
            print(f"Downloading generated image from URL: {generated_image_url}")
            image_response = requests.get(generated_image_url, timeout=30)
            image_response.raise_for_status()
            thumbnail_url = upload_thumbnail(job_id, image_response.content)
            return thumbnail_url
        else:
            raise RuntimeError("No image data or URL found in OpenRouter response after parsing.")
            
    except Exception as e:
        print(f"Failed to process OpenRouter response: {e}")
        raise