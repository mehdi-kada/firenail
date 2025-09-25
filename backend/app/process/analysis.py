import aiohttp
import os 
from dotenv import load_dotenv
from app.constants.prompts import analysis_prompt, transcript_prompt_test

load_dotenv()

async def analyze_text(text: str) -> str:
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            'https://openrouter.ai/api/alpha/responses',
            headers={
                'Authorization': 'Bearer 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',
                'Content-Type': 'application/json',
            },
            json={
                'model': 'x-ai/grok-4-fast:free',  
                'input': analysis_prompt(transcript_prompt_test),
            }
        ) as response:
            if response.status == 200:
                data = await response.json()
                print(data)
                return f"Analyzed text: {data.get('output', 'No output found')}"
            else:
                return f"Error: {response.status}"
                
if __name__ == "__main__":
    import asyncio
    asyncio.run(analyze_text("text"))