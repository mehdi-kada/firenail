import os
from dotenv import load_dotenv
from typing import List, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

load_dotenv()

FIRECRAWL_URL = "https://api.firecrawl.dev/v2/search"


def _session_with_retries() -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods={"GET", "POST"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=10)
    s = requests.Session()
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    s.headers.update({"Connection": "close"})
    return s

def crawl_images(keyword: str, limit: int = 1) -> List[Dict]:
    """Fetch images from Firecrawl API based on keyword"""
    payload = {
        "query": keyword,
        "sources": ["images"],
        "categories": ["research"],
        "limit": limit,
        "scrapeOptions": {
            "onlyMainContent": True,
            "maxAge": 172800000,
            "formats": []
        },
        "origin": "website"
    }

    url = os.getenv("FIRECRAWL_URL", FIRECRAWL_URL)
    api_key = os.getenv("FIRECRAWL_KEY")

    headers = {
        "Authorization": f"Bearer {api_key}" if api_key else "",
        "Content-Type": "application/json",
    }

    try:
        session = _session_with_retries()
        response = session.post(url, json=payload, headers=headers, timeout=(10, 30))
    except (requests.exceptions.SSLError, requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout) as e:
        print(f"Firecrawl network/SSL error for '{keyword}': {e}. Returning no images.")
        return []
    except requests.exceptions.RequestException:
        raise

    if response.status_code in {401, 403}:
        # Auth/permission issues should surface to caller for visibility
        raise requests.exceptions.HTTPError(
            f"Firecrawl auth error {response.status_code}: {response.text}",
            response=response,
        )
    if response.status_code == 429 or 500 <= response.status_code < 600:
        print(f"Firecrawl unavailable ({response.status_code}) for '{keyword}'. Returning no images.")
        return []

    response.raise_for_status()
    data = response.json()

    # Firecrawl v2 API returns: {"success": true, "data": {"images": [...]}}
    if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict):
        images = data["data"].get("images", [])
    elif isinstance(data, dict) and "images" in data:
        images = data.get("images", [])
    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        images = data["data"]
    else:
        images = []

    return images if isinstance(images, list) else []

