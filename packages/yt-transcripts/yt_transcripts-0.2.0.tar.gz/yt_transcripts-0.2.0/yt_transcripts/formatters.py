"""Output formatters for transcripts."""

import json
from typing import TextIO


def format_as_text(transcript: dict) -> str:
    """Format transcript as plain text."""
    if 'error' in transcript:
        return f"Error for video {transcript['video_id']}: {transcript['error']}"

    lines = []
    for segment in transcript['segments']:
        lines.append(segment['text'])
    return ' '.join(lines)


def format_as_json(transcript: dict) -> str:
    """Format transcript as JSON."""
    return json.dumps(transcript, indent=2, ensure_ascii=False)


def format_as_srt(transcript: dict) -> str:
    """Format transcript as SRT subtitle format."""
    if 'error' in transcript:
        return f"Error for video {transcript['video_id']}: {transcript['error']}"

    def seconds_to_srt_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    lines = []
    for i, segment in enumerate(transcript['segments'], 1):
        start = seconds_to_srt_time(segment['start'])
        end = seconds_to_srt_time(segment['start'] + segment['duration'])
        lines.append(str(i))
        lines.append(f"{start} --> {end}")
        lines.append(segment['text'])
        lines.append('')

    return '\n'.join(lines)


def format_as_vtt(transcript: dict) -> str:
    """Format transcript as WebVTT subtitle format."""
    if 'error' in transcript:
        return f"Error for video {transcript['video_id']}: {transcript['error']}"

    def seconds_to_vtt_time(seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"

    lines = ['WEBVTT', '']
    for i, segment in enumerate(transcript['segments'], 1):
        start = seconds_to_vtt_time(segment['start'])
        end = seconds_to_vtt_time(segment['start'] + segment['duration'])
        lines.append(f"{start} --> {end}")
        lines.append(segment['text'])
        lines.append('')

    return '\n'.join(lines)


FORMATTERS = {
    'text': format_as_text,
    'json': format_as_json,
    'srt': format_as_srt,
    'vtt': format_as_vtt,
}


def get_formatter(format_name: str):
    """Get formatter function by name."""
    if format_name not in FORMATTERS:
        raise ValueError(f"Unknown format: {format_name}. Available: {list(FORMATTERS.keys())}")
    return FORMATTERS[format_name]
