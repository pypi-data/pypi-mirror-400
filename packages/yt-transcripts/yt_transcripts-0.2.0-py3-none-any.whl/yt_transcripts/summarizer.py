"""AI-powered transcript summarization using LiteLLM."""

import os
from typing import Optional


def _get_litellm():
    """Lazy import litellm to keep summarization optional."""
    try:
        import litellm
        return litellm
    except ImportError:
        raise ImportError(
            "Summarization requires litellm. Install with: pip install yt-transcripts[summarize]"
        )


# Default models for each provider
DEFAULT_MODELS = {
    'ollama': 'ollama/llama3.2',
    'openai': 'openai/gpt-4o-mini',
    'anthropic': 'anthropic/claude-sonnet-4-20250514',
    'gemini': 'gemini/gemini-1.5-flash',
    'openrouter': 'openrouter/meta-llama/llama-3-8b-instruct',
}

# Environment variable names for API keys
API_KEY_ENV_VARS = {
    'openai': 'OPENAI_API_KEY',
    'anthropic': 'ANTHROPIC_API_KEY',
    'gemini': 'GEMINI_API_KEY',
    'openrouter': 'OPENROUTER_API_KEY',
}

DEFAULT_PROMPT = """Summarize the following video transcript concisely.
Focus on the main topics, key points, and conclusions.
Keep the summary informative but brief (2-4 paragraphs).

Transcript:
{transcript}

Summary:"""


def load_env_config():
    """Load configuration from .env file if present."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass  # python-dotenv not installed, skip


def get_config(
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    ollama_host: Optional[str] = None,
) -> dict:
    """
    Get summarization config, with CLI args taking precedence over env vars.

    Args:
        model: LiteLLM model string (e.g., "ollama/llama3.2", "openai/gpt-4o")
        api_key: API key for cloud providers
        ollama_host: Ollama server URL

    Returns:
        Dict with 'model', 'api_key', 'ollama_host' keys.
    """
    load_env_config()

    config = {
        'model': model or os.getenv('YT_SUMMARIZE_MODEL', DEFAULT_MODELS['ollama']),
        'api_key': api_key,
        'ollama_host': ollama_host or os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
    }

    # Determine provider from model string
    provider = config['model'].split('/')[0] if '/' in config['model'] else 'ollama'

    # Get API key from env if not provided via CLI
    if config['api_key'] is None and provider in API_KEY_ENV_VARS:
        config['api_key'] = os.getenv(API_KEY_ENV_VARS[provider])

    return config


def summarize_transcript(
    transcript_text: str,
    model: str,
    api_key: Optional[str] = None,
    ollama_host: Optional[str] = None,
    prompt_template: Optional[str] = None,
) -> str:
    """
    Summarize transcript text using LiteLLM.

    Args:
        transcript_text: Plain text transcript to summarize
        model: LiteLLM model string (e.g., "ollama/llama3.2", "openai/gpt-4o")
        api_key: API key for cloud providers (not needed for Ollama)
        ollama_host: Ollama server URL (default: http://localhost:11434)
        prompt_template: Custom prompt template with {transcript} placeholder

    Returns:
        Summary text
    """
    litellm = _get_litellm()

    prompt = (prompt_template or DEFAULT_PROMPT).format(transcript=transcript_text)

    # Configure based on provider
    provider = model.split('/')[0] if '/' in model else 'ollama'

    kwargs = {
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
    }

    if provider == 'ollama':
        kwargs['api_base'] = ollama_host or 'http://localhost:11434'
    elif api_key:
        kwargs['api_key'] = api_key

    response = litellm.completion(**kwargs)
    return response.choices[0].message.content


def summarize(transcript: dict, config: dict) -> str:
    """
    Summarize a transcript dict.

    Args:
        transcript: Transcript dict from get_transcript() with keys:
            - video_id: str
            - language: str
            - is_generated: bool
            - segments: list[dict] with 'text', 'start', 'duration'
            OR
            - video_id: str
            - error: str
        config: Config dict from get_config() with 'model', 'api_key', 'ollama_host'

    Returns:
        Summary string, or error message if transcript has error
    """
    if 'error' in transcript:
        return f"Cannot summarize: {transcript['error']}"

    # Convert segments to plain text
    text = ' '.join(segment['text'] for segment in transcript['segments'])

    return summarize_transcript(
        transcript_text=text,
        model=config['model'],
        api_key=config['api_key'],
        ollama_host=config['ollama_host'],
    )
