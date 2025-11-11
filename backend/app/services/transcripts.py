import yt_dlp
import os
from typing import NamedTuple


class VideoUnavailableError(Exception):
    pass

class TranscriptUnavailableError(Exception):
    pass

class InvalidURLError(Exception):
    pass


class VideoData(NamedTuple):
    title: str
    transcript: str


def _get_ydl_opts():
	"""Returns yt-dlp options with cookies authentication"""
	cookie_path = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')
	if not os.path.exists(cookie_path):
		raise FileNotFoundError(f"Cookie file not found at : {cookie_path}")
	
	return {
		'cookiefile': cookie_path,
		'http_headers': {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
		},
		'quiet': True,
		'no_warnings': True,
		'skip_download': True,
		'format': 'worst',
		'writesubtitles': True,
		'writeautomaticsub': True,
		'subtitleslangs': ['en'],
	}


def fetch_video_data(url: str) -> VideoData:
	"""Fetch video metadata and transcript in one call"""
	
	try:
		with yt_dlp.YoutubeDL(_get_ydl_opts()) as ydl:
			info = ydl.extract_info(url, download=False)
			
			# Get title
			title = info.get('title')
			if not title:
				raise VideoUnavailableError("Could not fetch video title")
			
			# Get transcript
			subtitles = info.get('subtitles', {}).get('en') or info.get('automatic_captions', {}).get('en')
			if not subtitles:
				raise TranscriptUnavailableError("No captions available for this video")
			
			subtitle_url = next((sub.get('url') for sub in subtitles if sub.get('ext') == 'json3'), None)
			if not subtitle_url:
				raise TranscriptUnavailableError("Could not find transcript data")
			
			import urllib.request
			import json
			
			with urllib.request.urlopen(subtitle_url, timeout=30) as response:
				data = json.loads(response.read().decode('utf-8'))
			
			transcript_segments = [
				seg['utf8'] 
				for event in data.get('events', []) 
				if 'segs' in event 
				for seg in event['segs'] 
				if 'utf8' in seg
			]
			
			transcript_text = " ".join(transcript_segments).strip()
			if len(transcript_text) < 50:
				raise TranscriptUnavailableError("Transcript too short")
			
			return VideoData(title=title, transcript=transcript_text)
			
	except (TranscriptUnavailableError, VideoUnavailableError):
		raise
	except yt_dlp.utils.DownloadError as e:
		if 'private' in str(e).lower() or 'unavailable' in str(e).lower():
			raise VideoUnavailableError("Video unavailable or private") from e
		raise VideoUnavailableError("Could not access video") from e
	except Exception as e:
		raise VideoUnavailableError(f"Error: {str(e)}") from e
