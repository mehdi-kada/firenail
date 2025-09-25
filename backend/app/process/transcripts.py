from youtube_transcript_api import YouTubeTranscriptApi

async def get_transcripts():

    ytt_api = YouTubeTranscriptApi()
    transcript = ytt_api.fetch("0PgdTddSpsA")

    transcript_text = " ".join([t.text for t in transcript])

    return transcript_text