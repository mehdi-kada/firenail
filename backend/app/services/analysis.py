import aiohttp
import os 
from dotenv import load_dotenv
from app.constants.prompts import analysis_prompt
import re
import json
import ast
from typing import Dict, List, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=8),
)
def analyze_transcript(prompt: str) -> Dict[str, Any]:
    api_key = os.environ.get('OPENROUTER_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY or OPENROUTER_KEY environment variable not set")
    
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "x-ai/grok-4-fast",
            "messages": [
                {"role": "user", "content": prompt},
            ],
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    
    try:
        raw = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        print(f"Error parsing OpenRouter response: {e}")
        print(f"Response data: {data}")
        raise ValueError(f"Invalid OpenRouter response structure: {e}") from e
    
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S | re.I)
    json_text = m.group(1) if m else raw.strip()

    try:
        parsed_data = json.loads(json_text)
        print("Parsed JSON data:", parsed_data)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("Raw text:", repr(json_text))
        try:
            if json_text.strip():
                parsed_data = ast.literal_eval(json_text)
            else:
                print("Empty json_text, cannot parse")
                return {"summary": "", "image_search_keywords": []}
        except (ValueError, SyntaxError) as e:
            print("Error with ast.literal_eval:", e)
            return {"summary": "", "image_search_keywords": []}

    summary = parsed_data.get('summary', '')
    image_search_keywords = parsed_data.get('image_search_keywords', [])

    return {"summary": summary, "image_search_keywords": image_search_keywords}