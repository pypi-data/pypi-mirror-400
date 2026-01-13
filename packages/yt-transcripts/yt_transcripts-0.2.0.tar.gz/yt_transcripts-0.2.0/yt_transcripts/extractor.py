"""Core transcript extraction functionality."""

import re
from typing import Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)

# Create a single instance to reuse
_api = YouTubeTranscriptApi()


def extract_video_id(url_or_id: str) -> str:
    """Extract video ID from a YouTube URL or return the ID if already provided."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract video ID from: {url_or_id}")


def get_transcript(
    video_id: str,
    languages: Optional[list[str]] = None,
) -> dict:
    """
    Get transcript for a single video.

    Args:
        video_id: YouTube video ID or URL
        languages: Preferred languages in order of preference (default: ['en'])

    Returns:
        Dictionary with video_id, transcript segments, and metadata
    """
    video_id = extract_video_id(video_id)
    languages = languages or ['en']

    try:
        transcript_list = _api.list(video_id)

        # Try to find transcript in preferred languages
        transcript = None
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except NoTranscriptFound:
                continue

        # If no preferred language found, try generated transcripts
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(languages)
            except NoTranscriptFound:
                # Fall back to any available transcript
                for t in transcript_list:
                    transcript = t
                    break

        if transcript is None:
            raise NoTranscriptFound(video_id, languages, transcript_list)

        fetched = transcript.fetch()
        # Convert to list of dicts for serialization
        segments = [{'text': s.text, 'start': s.start, 'duration': s.duration} for s in fetched]

        return {
            'video_id': video_id,
            'language': transcript.language_code,
            'is_generated': transcript.is_generated,
            'segments': segments,
        }

    except TranscriptsDisabled:
        return {
            'video_id': video_id,
            'error': 'Transcripts are disabled for this video',
        }
    except VideoUnavailable:
        return {
            'video_id': video_id,
            'error': 'Video is unavailable',
        }
    except NoTranscriptFound as e:
        return {
            'video_id': video_id,
            'error': f'No transcript found: {e}',
        }


def get_transcripts(
    video_ids: list[str],
    languages: Optional[list[str]] = None,
) -> list[dict]:
    """Get transcripts for multiple videos."""
    return [get_transcript(vid, languages) for vid in video_ids]
