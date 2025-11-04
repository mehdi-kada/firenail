from youtube_transcript_api import TranscriptsDisabled, YouTubeTranscriptApi
from googleapiclient.discovery import build
from typing import NamedTuple
import yt_dlp
import os




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
	}

def fetch_metadata(url: str) -> str:
	"Fetch video metadata using yt-dlp"
	ydl_opts = _get_ydl_opts()

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		info = ydl.extract_info(url, download=False)
		title = info.get('title')

		if not title:
			raise ValueError(f"Couldnt fetch metadata for {url}")
		
		return title
	
def fetch_transcript(url: str) -> str:
    """Fetch transcript using yt-dlp."""
    ydl_opts = _get_ydl_opts()
    ydl_opts.update({
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
    })
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        # Try manual subtitles first, then automatic
        subtitles = info.get('subtitles', {}).get('en') or info.get('automatic_captions', {}).get('en')
        
        if not subtitles:
            raise RuntimeError("Transcript disabled for this video")
        
        # Find json3 format (contains text data)
        subtitle_url = None
        for sub in subtitles:
            if sub.get('ext') == 'json3':
                subtitle_url = sub.get('url')
                break
        
        if not subtitle_url:
            raise RuntimeError("Could not find transcript data")
        
        # Fetch and parse the subtitle data
        import urllib.request
        import json
        
        with urllib.request.urlopen(subtitle_url) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        # Extract text from json3 format
        transcript_segments = []
        for event in data.get('events', []):
            if 'segs' in event:
                for seg in event['segs']:
                    if 'utf8' in seg:
                        transcript_segments.append(seg['utf8'])
        
        return " ".join(transcript_segments).strip()