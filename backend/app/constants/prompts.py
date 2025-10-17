def analysis_prompt(transcript: str, video_title: str) -> str : 
    return f"""i am trying to get 3 image searches to feed an image language model alongside summary of youtube video transcript to create a thumbnail for the youtube video, i am gonna give you the transcript and i need a the summary of the transcript plus 2 image search keywords that i can use to get images from an image search api to feed the image model to get the best result ensure that the images relats best to the video transcripts and subjects and title 


Title: {video_title}

Transcript: {transcript}

Return ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{"summary": "summary here", "image_search_keywords": ["keyword1", "keyword2"]}}"""


def thumbnail_generation_prompt(video_title: str, summary: str, keywords: list[str]) -> str:

    return f"""You are an expert thumbnail designer. I will provide you with:
- Three reference images
- The title of a YouTube video
- The transcript of the video
- A summary of the video content

Your task:
1. Analyze the title, transcript, and summary to identify the video's main theme, emotional tone, and most visually striking ideas.

2. Create a single, eye-catching thumbnail by combining ONLY the three provided images. Do not generate or add any new elements beyond:
   - Adjusting the images (crop, resize, color correction, lighting, contrast enhancement)
   - Blending them together harmoniously
   - Adding a synthetic or abstract background if necessary for visual cohesion

3. Use the images meaningfully so they reflect the transcript, summary, and title — not just as a random collage, but as a semantic composition that tells the video's story at a glance.

4. Ensure the design is:
   - Eye-catching and vibrant
   - Clear and readable at small sizes (mobile thumbnails)
   - Has strong contrast and a clear focal point
   - Draws immediate attention with visual hierarchy

5. If text is included, use only short, bold words from or inspired by the title (maximum 4-5 words). Make text highly readable with strong contrast against the background.

6. The composition should evoke the emotional tone identified from the content and entice viewers to click.

7. **IMPORTANT:** The final image must be in a 16:9 aspect ratio (1920x1080 or equivalent proportions). This is critical for YouTube thumbnail formatting.

**Inputs:**

Video Title: {video_title}

Video Summary: {summary}


Reference Image Keywords: {", ".join(keywords)}

**Output:**
Create a single, polished YouTube thumbnail that uses only the provided images (plus optional background adjustments) to powerfully convey the theme and emotional essence of this video. Make it irresistible to click."""
