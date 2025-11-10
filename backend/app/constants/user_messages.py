"""User-friendly error messages and status updates"""

ERROR_MESSAGES = {
    "invalid_url": "The YouTube URL you provided is not valid. Please check the URL and try again.",
    "video_not_found": "We couldn't find that YouTube video. The video may be private, deleted, or the URL is incorrect.",
    "no_transcript": "This video doesn't have captions available. We need captions to generate thumbnails.",
    "transcript_disabled": "Captions are disabled for this video. Please try another video with captions enabled.",
    "age_restricted": "This video is age-restricted and cannot be processed. Please try a different video.",
    "video_unavailable": "This video is unavailable or cannot be accessed. It may be private or region-restricted.",
    "analysis_failed": "We couldn't analyze the video content. Please try again.",
    "no_keywords": "We couldn't extract meaningful keywords from the video. The content might be too short or unclear.",
    "image_search_failed": "We couldn't find suitable reference images for your video. Please try a different video.",
    "thumbnail_generation_timeout": "Thumbnail generation is taking longer than expected. Please try again.",
    "thumbnail_generation_failed": "We couldn't generate a thumbnail for this video. Please try again later.",
    "api_error": "An external service is temporarily unavailable. Please try again in a few moments.",
    "rate_limit": "You've made too many requests. Please wait a moment and try again.",
    "unknown_error": "Something went wrong. Please try again or contact support if the issue persists.",
}

SUCCESS_MESSAGES = {
    "queued": "Your request has been received and is being processed",
    "metadata_fetched": "Video information retrieved successfully",
    "transcript_fetched": "Video captions loaded",
    "analysis_completed": "Content analyzed successfully",
    "images_found": "Found reference images",
    "thumbnail_started": "Creating your thumbnail",
    "thumbnail_completed": "Thumbnail created successfully",
    "completed": "All done! Your thumbnail is ready",
}

STEP_DESCRIPTIONS = {
    "job": "Starting your request",
    "metadata": "Getting video information",
    "transcript": "Loading video captions",
    "analysis": "Analyzing video content",
    "images": "Finding reference images",
    "thumbnail": "Creating your thumbnail",
    "done": "Complete",
}
