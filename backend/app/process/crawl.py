from typing import Any, List, Dict
import requests

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
        "Authorization": "Bearer fc-92d2519e402241be8b2a5df8e601cb9a",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()

if __name__ == "__main__":
    import asyncio
    result = asyncio.run(crawl_images("Fortnite Travis Scott concert event"))
    images_url = (result.get("data").get("images")[0].get("imageUrl"))
    print(images_url)
