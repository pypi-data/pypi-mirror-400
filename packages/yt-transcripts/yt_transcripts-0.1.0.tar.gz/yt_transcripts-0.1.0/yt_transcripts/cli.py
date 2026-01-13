"""Command-line interface for YouTube transcript extraction."""

import argparse
import io
import sys
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .extractor import get_transcript, extract_video_id
from .channel import get_channel_videos, get_playlist_videos, is_channel_url, is_playlist_url
from .formatters import get_formatter, FORMATTERS


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='yt-transcripts',
        description='Extract transcripts from YouTube videos, playlists, or channels.',
    )

    parser.add_argument(
        'source',
        nargs='*',
        help='YouTube video URL(s), video ID(s), channel URL, or playlist URL',
    )

    parser.add_argument(
        '-f', '--format',
        choices=list(FORMATTERS.keys()),
        default='text',
        help='Output format (default: text)',
    )

    parser.add_argument(
        '-l', '--language',
        action='append',
        dest='languages',
        help='Preferred language code(s) in order of preference (default: en)',
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file or directory (default: stdout)',
    )

    parser.add_argument(
        '--max-videos',
        type=int,
        help='Maximum number of videos to process from channel/playlist',
    )

    parser.add_argument(
        '--list-only',
        action='store_true',
        help='Only list videos without extracting transcripts (for channels/playlists)',
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output',
    )

    return parser


def process_video(video_id: str, languages: list[str], format_name: str, verbose: bool) -> tuple[str, str]:
    """Process a single video and return (video_id, formatted_transcript)."""
    if verbose:
        print(f"Processing video: {video_id}", file=sys.stderr)

    transcript = get_transcript(video_id, languages)
    formatter = get_formatter(format_name)
    return video_id, formatter(transcript)


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.source:
        parser.print_help()
        return 1

    languages = args.languages or ['en']
    videos_to_process = []

    # Gather all video IDs to process
    for source in args.source:
        if is_channel_url(source):
            if args.verbose:
                print(f"Fetching videos from channel: {source}", file=sys.stderr)
            videos = get_channel_videos(source, args.max_videos)
            if args.list_only:
                for v in videos:
                    print(f"{v['video_id']}\t{v['title']}")
                continue
            videos_to_process.extend([v['video_id'] for v in videos])

        elif is_playlist_url(source):
            if args.verbose:
                print(f"Fetching videos from playlist: {source}", file=sys.stderr)
            videos = get_playlist_videos(source, args.max_videos)
            if args.list_only:
                for v in videos:
                    print(f"{v['video_id']}\t{v['title']}")
                continue
            videos_to_process.extend([v['video_id'] for v in videos])

        else:
            # Single video URL or ID
            try:
                video_id = extract_video_id(source)
                videos_to_process.append(video_id)
            except ValueError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1

    if args.list_only:
        return 0

    if not videos_to_process:
        print("No videos to process.", file=sys.stderr)
        return 1

    # Process videos
    output_dir = None
    if args.output and len(videos_to_process) > 1:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for video_id in videos_to_process:
        vid, content = process_video(video_id, languages, args.format, args.verbose)
        results.append((vid, content))

    # Output results
    if output_dir:
        # Multiple files
        ext = args.format if args.format != 'text' else 'txt'
        for vid, content in results:
            output_file = output_dir / f"{vid}.{ext}"
            output_file.write_text(content, encoding='utf-8')
            if args.verbose:
                print(f"Written: {output_file}", file=sys.stderr)
    elif args.output:
        # Single file
        with open(args.output, 'w', encoding='utf-8') as f:
            for vid, content in results:
                if len(results) > 1:
                    f.write(f"=== {vid} ===\n")
                f.write(content)
                f.write('\n\n')
        if args.verbose:
            print(f"Written: {args.output}", file=sys.stderr)
    else:
        # stdout
        for vid, content in results:
            if len(results) > 1:
                print(f"=== {vid} ===")
            print(content)
            if len(results) > 1:
                print()

    return 0


if __name__ == '__main__':
    sys.exit(main())
