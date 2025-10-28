def analysis_prompt(transcript: str, video_title: str) -> str:
    return f"""You are a senior thumbnail art director. From the transcript and title, produce:
- A concise summary of the video’s core message.
- One to three strong image search keywords/phrases (choose 1, 2, or 3 based on the concept’s needs).
- A compact style direction that states how many images to use and exactly how to combine them.


Guidelines:
1) Infer mood, pacing, and genre from the transcript.
2) Identify a single dominant focal subject visible at a glance.
3) Select visually distinct keywords that map to foreground/mid/background or split roles.
4) Style direction:
   Include: layering/composition plan (e.g., Foreground/Mid/Background or split/diagonal), mood & energy, color palette and contrast plan, lighting/atmosphere, background treatment, typography guidance with a overlay suggestion (no double quotes), and Do/Don’t constraints (avoid clutter, tiny text).

Title: {video_title}

Transcript: {transcript}

Return ONLY a valid JSON object in this exact format (no markdown, no extra text):
{{"summary": "string", "image_search_keywords": ["keywords (min 1 max 3)"], "style_direction": "string"}}"""



def thumbnail_generation_prompt(
    video_title: str,
    summary: str,
    keywords: list[str],
    style_direction: str = ""
) -> str:
    return f"""You are an expert thumbnail designer and art director. You will receive:
- Three reference images
- The title of a YouTube video
- A summary of the video content

Primary objective:
Create a single 16:9 thumbnail that communicates the video's main idea and emotional tone using ONLY the three provided images, with allowed adjustments.

Style Direction:
- If provided, strictly follow this style brief: "{style_direction}"
- If empty, infer the style from the title and summary. Determine and apply:
  - Mood and energy (e.g., calm, urgent, epic, playful)
  - Color palette and contrast strategy
  - Lighting and atmosphere (e.g., cinematic, high-key, moody)
  - Typography weight and placement (if text used)
  - Composition style (e.g., centered hero, rule-of-thirds, split-screen, diagonal flow)

Design policy:
- Do not add new objects, people, logos, or elements.
- Allowed: crop, resize, color correction, lighting/contrast enhancements, blending, subtle overlays, and a synthetic/abstract background only for cohesion.
- If text is included, use short, bold words from or inspired by the title (max 4–5 words), with strong contrast and high readability.

Your task:
1. Analyze the title and summary to identify the main theme, emotional tone, and the most visually striking ideas.
2. Compose a single, eye-catching thumbnail that uses ONLY the three images meaningfully to reflect the content (not a random collage).
3. Ensure the design is:
   - Eye-catching and vibrant
   - Clear and readable at small sizes
   - High contrast with a clear focal point
   - Visually hierarchical to draw immediate attention
4. Make the composition evoke the identified emotional tone and entice viewers to click.
5. Respect the style direction if provided. If conflicts arise, keep semantic faithfulness to the content while prioritizing the specified style.

Technical specs:
- Aspect ratio: 16:9 (1920x1080 or proportional)
- Safe text sizing and placement for mobile visibility
- Crisp edges and clean blending without halos or muddy midtones

Inputs:
- Video Title: {video_title}
- Video Summary: {summary}
- Reference Image Keywords: {", ".join(keywords)}

Output:
Create a single, polished YouTube thumbnail that uses only the provided images (plus optional background adjustments) and aligns with the style direction (or inferred vibe) to powerfully convey the theme and emotional essence of this video. Make it irresistible to click."""
