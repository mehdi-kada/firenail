import os
from dotenv import load_dotenv
from typing import Any, List, Dict
import requests

load_dotenv()

url = "https://api.firecrawl.dev/v2/search"

async def crawl_images(images: str):

    payload = {
    "query": "Fortnite Travis Scott concert event",
    "sources": [
        "images"
    ],
    "categories": [
        "research"
    ],
    "limit": 10,
    "scrapeOptions": {
        "onlyMainContent": True,
        "maxAge": 172800000,
        "parsers": [
        "pdf"
        ],
        "formats": []
    },
    "origin": "website"
    }

    headers = {
        "Authorization": f"Bearer {os.getenv('FIRECRAWL_KEY')}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()

