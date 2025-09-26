import aiohttp
import os 
from dotenv import load_dotenv
from app.constants.prompts import analysis_prompt, transcript_prompt_test
import re
import json
import ast
from typing import Dict, List, Any

load_dotenv()

async def analyze_text(text: str) -> Dict[str, Any]:
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://openrouter.ai/api/alpha/responses',
            headers={
            'Authorization': 'Bearer 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',
            'Content-Type': 'application/json',
            },
            json={
            'model': 'deepseek/deepseek-chat-v3.1:free',
            'input': analysis_prompt(transcript_prompt_test),
            }
        ) as response:
            if response.status == 200:
                response_data = await response.json()
                print(response_data)
                
                # Extract the actual text content from the nested response structure
                try:
                    raw = response_data['output'][0]['content'][0]['text']
                except (KeyError, IndexError):
                    print("Error: Could not extract text from response structure")
                    return {"summary": "", "image_search_keywords": []}
                
                # Try to extract JSON from code blocks first
                m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, re.S | re.I)
                json_text = m.group(1) if m else raw.strip()

                try:
                    data = json.loads(json_text)
                    print("Parsed JSON data:", data)
                except json.JSONDecodeError as e:
                    print("Error decoding JSON:", e)
                    print("Raw text:", repr(json_text))
                    try:
                        # Try ast.literal_eval as fallback, but only if json_text is not empty
                        if json_text.strip():
                            data = ast.literal_eval(json_text)
                        else:
                            print("Empty json_text, cannot parse")
                            return {"summary": "", "image_search_keywords": []}
                    except (ValueError, SyntaxError) as e:
                        print("Error with ast.literal_eval:", e)
                        return {"summary": "", "image_search_keywords": []}

                summary = data.get('summary', '')
                image_search_keywords = data.get('image_search_keywords', [])


                return {"summary": summary, "image_search_keywords": image_search_keywords}
            else:
                print(f"API request failed with status {response.status}")
                return {"summary": "", "image_search_keywords": []}

                
if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_text("text"))