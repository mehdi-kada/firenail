
import os 
import logging
from dotenv import load_dotenv
from app.constants.prompts import analysis_prompt
import re
import json
import ast
from typing import Dict, List, Any
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=2, min=1, max=8),
)
def analyze_transcript(prompt: str) -> Dict[str, Any]:
    api_key = os.environ.get('CEREBRAS_API_KEY')
    if not api_key:
        raise ValueError("CEREBRAS_API_KEY environment variable not set")
    
    response = httpx.post(
        "https://api.cerebras.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "qwen-3-235b-a22b-instruct-2507",
            "messages": [
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 20000,
            "temperature": 0.7,
            "top_p": 0.8,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    
    try:
        raw = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing OpenRouter response: {e}")
        logger.debug(f"Response data: {data}")
        raise ValueError(f"Invalid OpenRouter response structure: {e}") from e
    
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S | re.I)
    json_text = m.group(1) if m else raw.strip()
    
    # Clean up common JSON formatting issues from AI models
    json_text = re.sub(r'\]\s*\]\s*$', ']', json_text)
    json_text = re.sub(r'\}\s*\]\s*$', '}', json_text)  
    json_text = json_text.replace('"', '"').replace('"', '"')
    json_text = json_text.replace(''', "'").replace(''', "'")

    try:
        parsed_data = json.loads(json_text)
        logger.info("Successfully parsed JSON data")
    except json.JSONDecodeError as e:
        logger.warning(f"JSON decode error at position {e.pos}: {e.msg}")
        logger.debug(f"Raw text length: {len(json_text)}")
        logger.debug(f"Raw text preview (first 200 chars): {json_text[:200]}")
        logger.debug(f"Raw text preview (last 200 chars): {json_text[-200:]}")
        
        # Try to extract data using regex as fallback
        try:
            summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', json_text)
            keywords_match = re.search(r'"image_search_keywords"\s*:\s*\[(.*?)\]', json_text, re.S)
            
            if summary_match and keywords_match:
                summary = summary_match.group(1)
                keywords_str = keywords_match.group(1)
                keywords = re.findall(r'"([^"]+)"', keywords_str)
                
                logger.info(f"Extracted via regex - Summary length: {len(summary)}, Keywords count: {len(keywords)}")
                return {"summary": summary, "image_search_keywords": keywords}
        except Exception as regex_error:
            logger.error(f"Regex fallback failed: {regex_error}")
        
        try:
            if json_text.strip():
                parsed_data = ast.literal_eval(json_text)
                logger.info("Parsed with ast.literal_eval")
            else:
                logger.error("Empty json_text, cannot parse")
                return {"summary": "", "image_search_keywords": []}
        except (ValueError, SyntaxError) as ast_error:
            logger.error(f"ast.literal_eval failed: {ast_error}")
            return {"summary": "", "image_search_keywords": []}

    summary = parsed_data.get('summary', '')
    image_search_keywords = parsed_data.get('image_search_keywords', [])

    return {"summary": summary, "image_search_keywords": image_search_keywords}