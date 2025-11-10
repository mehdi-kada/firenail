import yt_dlp
import os


class VideoUnavailableError(Exception):
    pass

class TranscriptUnavailableError(Exception):
    pass

class InvalidURLError(Exception):
    pass




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
	"""Fetch video metadata using yt-dlp"""
	ydl_opts = _get_ydl_opts()

	try:
		with yt_dlp.YoutubeDL(ydl_opts) as ydl:
			info = ydl.extract_info(url, download=False)
			title = info.get('title')

			if not title:
				raise VideoUnavailableError(f"Could not fetch metadata for video")
			
			if info.get('availability') not in [None, 'public', 'unlisted']:
				raise VideoUnavailableError(f"Video is {info.get('availability')}")
			
			return title
	except yt_dlp.utils.DownloadError as e:
		error_msg = str(e).lower()
		if 'private' in error_msg or 'unavailable' in error_msg:
			raise VideoUnavailableError("This video is unavailable or private") from e
		elif 'not found' in error_msg or '404' in error_msg:
			raise VideoUnavailableError("Video not found") from e
		elif 'age' in error_msg and 'restricted' in error_msg:
			raise VideoUnavailableError("This video is age-restricted") from e
		else:
			raise VideoUnavailableError(f"Could not access video") from e
	except Exception as e:
		if 'invalid' in str(e).lower() and 'url' in str(e).lower():
			raise InvalidURLError("Invalid YouTube URL") from e
		raise
      

def fetch_transcript(url: str) -> str:
    """Fetch transcript using yt-dlp."""
    ydl_opts = _get_ydl_opts()
    ydl_opts.update({
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'skip_download': True,
    })
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Try manual subtitles first, then automatic
            subtitles = info.get('subtitles', {}).get('en') or info.get('automatic_captions', {}).get('en')
            
            if not subtitles:
                raise TranscriptUnavailableError("Transcript disabled for this video")
            
            # Find json3 format (contains text data)
            subtitle_url = None
            for sub in subtitles:
                if sub.get('ext') == 'json3':
                    subtitle_url = sub.get('url')
                    break
            
            if not subtitle_url:
                raise TranscriptUnavailableError("Could not find transcript data")
            
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
            
            transcript_text = " ".join(transcript_segments).strip()
            
            if not transcript_text or len(transcript_text) < 50:
                raise TranscriptUnavailableError("Transcript is too short or empty")
            
            return transcript_text
    except TranscriptUnavailableError:
        raise
    except yt_dlp.utils.DownloadError as e:
        error_msg = str(e).lower()
        if 'private' in error_msg or 'unavailable' in error_msg:
            raise VideoUnavailableError("This video is unavailable or private") from e
        elif 'age' in error_msg and 'restricted' in error_msg:
            raise VideoUnavailableError("This video is age-restricted") from e
        else:
            raise TranscriptUnavailableError("Could not fetch transcript") from e
    except Exception as e:
        raise TranscriptUnavailableError(f"Error fetching transcript: {str(e)}") from e