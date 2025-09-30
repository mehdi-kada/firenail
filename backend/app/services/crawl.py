import os
from dotenv import load_dotenv
from typing import List, Dict
import requests

load_dotenv()

FIRECRAWL_URL = "https://api.firecrawl.dev/v2/search"

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

    headers = {
        "Authorization": f"Bearer {os.getenv('FIRECRAWL_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(FIRECRAWL_URL, json=payload, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    return data.get("data", [])

