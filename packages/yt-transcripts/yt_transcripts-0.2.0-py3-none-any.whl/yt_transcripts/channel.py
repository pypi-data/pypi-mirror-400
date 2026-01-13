"""Channel and playlist video listing functionality using yt-dlp."""

import re
from typing import Optional
import yt_dlp


def get_channel_videos(
    channel_url: str,
    max_videos: Optional[int] = None,
) -> list[dict]:
    """
    Get list of videos from a YouTube channel.

    Args:
        channel_url: YouTube channel URL (can be /channel/, /@username, or /c/ format)
        max_videos: Maximum number of videos to retrieve (None for all)

    Returns:
        List of dicts with video_id, title, and url
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
    }

    if max_videos:
        ydl_opts['playlistend'] = max_videos

    # Ensure we're getting the videos tab
    if not channel_url.endswith('/videos'):
        channel_url = channel_url.rstrip('/') + '/videos'

    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(channel_url, download=False)

        if result and 'entries' in result:
            for entry in result['entries']:
                if entry and entry.get('id'):
                    videos.append({
                        'video_id': entry['id'],
                        'title': entry.get('title', 'Unknown'),
                        'url': f"https://www.youtube.com/watch?v={entry['id']}",
                    })

    return videos


def get_playlist_videos(
    playlist_url: str,
    max_videos: Optional[int] = None,
) -> list[dict]:
    """
    Get list of videos from a YouTube playlist.

    Args:
        playlist_url: YouTube playlist URL
        max_videos: Maximum number of videos to retrieve (None for all)

    Returns:
        List of dicts with video_id, title, and url
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
    }

    if max_videos:
        ydl_opts['playlistend'] = max_videos

    videos = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(playlist_url, download=False)

        if result and 'entries' in result:
            for entry in result['entries']:
                if entry and entry.get('id'):
                    videos.append({
                        'video_id': entry['id'],
                        'title': entry.get('title', 'Unknown'),
                        'url': f"https://www.youtube.com/watch?v={entry['id']}",
                    })

    return videos


def is_channel_url(url: str) -> bool:
    """Check if URL is a YouTube channel URL."""
    patterns = [
        r'youtube\.com/channel/',
        r'youtube\.com/@',
        r'youtube\.com/c/',
        r'youtube\.com/user/',
    ]
    return any(re.search(p, url) for p in patterns)


def is_playlist_url(url: str) -> bool:
    """Check if URL is a YouTube playlist URL."""
    return 'youtube.com/playlist' in url or 'list=' in url
