from youtube_transcript_api import YouTubeTranscriptApi
import yt_dlp

async def get_transcripts(url: str):

    ydl_opts = {
        'quiet': True,           # Suppress console output
        'skip_download': True,   # Do not download the video
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_id = info.get("id", None)
            video_title = info.get("title", "Unknown Title")
            if not video_id:
                raise ValueError("Could not extract video ID from URL")

        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_id)

        transcript_text = " ".join([t.text for t in transcript])
        print(f"Transcript: {transcript_text[:500]}...")  # Print first 500 characters of the transcript
        return transcript_text, video_title

    except Exception as e:
        print(f"Error: {e}")

    

if __name__ == "__main__":
    import asyncio
    asyncio.run(get_transcripts("https://youtu.be/Nx9Pf7AFkgM?si=X9xS5Ppgpfz8ctpN"))