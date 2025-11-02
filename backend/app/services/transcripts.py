from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi
from googleapiclient.discovery import build
from typing import NamedTuple
import os
import re


class VideoMeta(NamedTuple):
		video_id: str
		title: str

def extract_video_id(url: str) -> str:
		"""Extract video ID from YouTube URL."""
		patterns = [
				r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
				r'(?:embed\/)([0-9A-Za-z_-]{11})',
				r'^([0-9A-Za-z_-]{11})$'
		]
		for pattern in patterns:
				match = re.search(pattern, url)
				if match:
						return match.group(1)
		raise ValueError(f"Could not extract video ID from URL: {url}")

def fetch_metadata(url: str) -> VideoMeta:
		video_id = extract_video_id(url)
		api_key = os.getenv("YOUTUBE_API_KEY")
		if not api_key:
				raise ValueError("YOUTUBE_API_KEY environment variable not set")
		
		youtube = build("youtube", "v3", developerKey=api_key)
		response = youtube.videos().list(part="snippet", id=video_id).execute()
		
		if not response.get("items"):
				raise ValueError(f"Video not found: {video_id}")
		
		title = response["items"][0]["snippet"]["title"]
		return VideoMeta(video_id=video_id, title=title)

def fetch_transcript(video_id: str) -> str:
		try:
				youtube_t = YouTubeTranscriptApi()
				fetched_transcript = youtube_t.fetch(video_id, languages=["en"])
				transcript = fetched_transcript.to_raw_data()
		except TranscriptsDisabled:
				raise RuntimeError("Transcript disabled for this video")
		return " ".join(segment["text"] for segment in transcript)