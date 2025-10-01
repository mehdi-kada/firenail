from youtube_transcript_api import Transcript, TranscriptsDisabled, YouTubeTranscriptApi
import yt_dlp
from typing import NamedTuple


class VideoMeta(NamedTuple):
		video_id: str
		title: str

def fetch_metadata(url: str) -> VideoMeta:
		with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
				info = ydl.extract_info(url, download=False)
				return VideoMeta(video_id=info["id"], title=info.get("title", "Untitled"))

def fetch_transcript(video_id: str) -> str:
		try:
				youtube_t = YouTubeTranscriptApi()
				fetched_transcript = youtube_t.fetch(video_id, languages=["en"])
				transcript = fetched_transcript.to_raw_data()
		except TranscriptsDisabled:
				raise RuntimeError("Transcript disabled for this video")
		return " ".join(segment["text"] for segment in transcript)