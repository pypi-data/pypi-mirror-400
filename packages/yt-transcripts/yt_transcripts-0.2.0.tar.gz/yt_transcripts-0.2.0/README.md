# yt-transcripts 🎼

A Python CLI tool for extracting transcripts from YouTube videos, playlists, and channels.

## Installation

```bash
pip install -e .
```

Or install dependencies directly:

```bash
pip install youtube-transcript-api yt-dlp
```

### With AI Summarization

To enable AI-powered summarization:

```bash
pip install -e ".[summarize]"
```

## Usage

```bash
yt-transcripts [OPTIONS] SOURCE...
```

### Sources

The tool accepts multiple source types:

- **Video URL**: `https://www.youtube.com/watch?v=VIDEO_ID`
- **Video ID**: `dQw4w9WgXcQ`
- **Channel URL**: `https://www.youtube.com/@ChannelName`
- **Playlist URL**: `https://www.youtube.com/playlist?list=PLAYLIST_ID`

### Options

| Option | Description |
|--------|-------------|
| `-f, --format` | Output format: `text`, `json`, `srt`, `vtt` (default: `text`) |
| `-l, --language` | Preferred language code(s), can be specified multiple times (default: `en`) |
| `-o, --output` | Output file or directory (default: stdout) |
| `--max-videos` | Maximum number of videos to process from channel/playlist |
| `--list-only` | Only list videos without extracting transcripts |
| `-v, --verbose` | Verbose output |
| `-h, --help` | Show help message |
| `-s, --summarize` | Summarize transcripts using AI |
| `--model` | LiteLLM model string (default: `ollama/llama3.2`) |
| `--api-key` | API key for cloud providers |
| `--ollama-host` | Ollama server URL (default: `http://localhost:11434`) |

## Examples

### Single Video

```bash
# By URL
yt-transcripts "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# By video ID
yt-transcripts dQw4w9WgXcQ
```

### Multiple Videos

```bash
yt-transcripts VIDEO_ID1 VIDEO_ID2 VIDEO_ID3
```

### Output Formats

```bash
# Plain text (default)
yt-transcripts VIDEO_ID -f text

# JSON with timestamps and metadata
yt-transcripts VIDEO_ID -f json

# SRT subtitles
yt-transcripts VIDEO_ID -f srt

# WebVTT subtitles
yt-transcripts VIDEO_ID -f vtt
```

### Save to File

```bash
# Single file
yt-transcripts VIDEO_ID -o transcript.txt

# Multiple videos to separate files in a directory
yt-transcripts VIDEO_ID1 VIDEO_ID2 -o ./transcripts/
```

### Channels

```bash
# List all videos from a channel
yt-transcripts "https://www.youtube.com/@anthropic-ai" --list-only

# Extract transcripts from first 10 videos
yt-transcripts "https://www.youtube.com/@anthropic-ai" --max-videos 10

# Save channel transcripts to directory as JSON
yt-transcripts "https://www.youtube.com/@anthropic-ai" --max-videos 5 -f json -o ./transcripts/
```

### Playlists

```bash
# List videos in a playlist
yt-transcripts "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf" --list-only

# Extract all transcripts from playlist
yt-transcripts "https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf"
```

### Language Selection

```bash
# Prefer Spanish, fall back to English
yt-transcripts VIDEO_ID -l es -l en

# Prefer French
yt-transcripts VIDEO_ID -l fr
```

### AI Summarization

Summarize transcripts using LLMs. Supports Ollama (local), OpenAI, Anthropic, Gemini, and OpenRouter.

```bash
# Using local Ollama (default)
yt-transcripts -s VIDEO_ID

# Specify a model
yt-transcripts -s --model openai/gpt-4o-mini VIDEO_ID

# With API key
yt-transcripts -s --model anthropic/claude-sonnet-4-20250514 --api-key sk-ant-... VIDEO_ID

# Summarize multiple videos to a directory
yt-transcripts -s -o ./summaries/ VIDEO_ID1 VIDEO_ID2

# Summarize a playlist
yt-transcripts -s --max-videos 5 "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

#### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `YT_SUMMARIZE_MODEL` | Default LiteLLM model | `ollama/llama3.2` |
| `OLLAMA_HOST` | Ollama server URL | `http://localhost:11434` |
| `OPENAI_API_KEY` | OpenAI API key | - |
| `ANTHROPIC_API_KEY` | Anthropic API key | - |
| `GEMINI_API_KEY` | Google Gemini API key | - |
| `OPENROUTER_API_KEY` | OpenRouter API key | - |

You can also use a `.env` file in your project directory.

#### Supported Models

- **Ollama** (local): `ollama/llama3.2`, `ollama/mistral`, etc.
- **OpenAI**: `openai/gpt-4o`, `openai/gpt-4o-mini`
- **Anthropic**: `anthropic/claude-sonnet-4-20250514`, `anthropic/claude-haiku`
- **Gemini**: `gemini/gemini-1.5-flash`, `gemini/gemini-1.5-pro`
- **OpenRouter**: `openrouter/meta-llama/llama-3-8b-instruct`

## Output Formats

### Text

Plain text with all segments joined together:

```
We're no strangers to love You know the rules and so do I...
```

### JSON

Structured data with metadata and timestamps:

```json
{
  "video_id": "dQw4w9WgXcQ",
  "language": "en",
  "is_generated": false,
  "segments": [
    {
      "text": "We're no strangers to love",
      "start": 18.64,
      "duration": 3.24
    }
  ]
}
```

### SRT

Standard subtitle format:

```
1
00:00:18,640 --> 00:00:21,880
We're no strangers to love

2
00:00:22,640 --> 00:00:26,960
You know the rules and so do I
```

### VTT

WebVTT subtitle format:

```
WEBVTT

00:00:18.640 --> 00:00:21.880
We're no strangers to love

00:00:22.640 --> 00:00:26.960
You know the rules and so do I
```

## Error Handling

The tool gracefully handles common errors:

- **Transcripts disabled**: Reports when a video has transcripts turned off
- **Video unavailable**: Reports when a video is private or deleted
- **No transcript found**: Reports when no transcript exists in the requested language

Errors are included in the output rather than stopping execution, so batch processing continues even if some videos fail.

## Dependencies

**Core:**
- [youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) - Transcript extraction
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Channel and playlist video listing

**Summarization (optional):**
- [litellm](https://github.com/BerriAI/litellm) - Unified LLM interface
- [python-dotenv](https://github.com/theskumar/python-dotenv) - Environment file loading

## License

MIT
