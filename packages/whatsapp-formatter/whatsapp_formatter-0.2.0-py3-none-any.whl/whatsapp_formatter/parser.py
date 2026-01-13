"""LLM-powered parser to extract structured data from raw text."""

import json
import os

from openai import OpenAI

from whatsapp_formatter.schemas import LLMOutput

EXTRACTION_PROMPT = """Extract structured data from this text for a WhatsApp message.

Return a JSON object with:
- body (required): The main conversational message. Do NOT include options, headers, or footers.
- options (optional): Array of options if user needs to make a choice. Each option has:
  - title (required): MUST be 20 characters or less. Rephrase to preserve meaning.
  - description (optional): Additional detail about the option
- header (optional): Title/heading at the start (e.g., "Security Alert", "Account Selection")
- footer (optional): Disclaimer or note at the end (e.g., "Reply within 24 hours", "Terms apply")

CRITICAL - Option titles MUST be max 20 characters. Shorten intelligently:
- "Yes, it was me" → "Yes, it was me" (14 chars, OK)
- "No, secure my account" → "Secure Account" (14 chars)
- "View recent transactions" → "Recent Transactions" (19 chars)
- "Check your account balance" → "Check Balance" (13 chars)

Rules:
1. Detect options in ANY format: numbered lists, bullets, or inline choices
2. If no choices exist, omit "options" entirely
3. ALWAYS rephrase long option titles to fit 20 chars while keeping meaning
4. Extract header if there's a clear title/heading at the start
5. Extract footer if there's a disclaimer/note at the end (separate from body)
6. KEEP ALL OPTIONS even if they appear duplicate - do NOT remove duplicates

Example input:
"⚠️ Security Alert

We noticed a login from a new device. Was this you?

1. Yes, it was me
2. No, secure my account

Reply within 24 hours."

Example output:
{"header": "Security Alert", "body": "We noticed a login from a new device. Was this you?", "options": [{"title": "Yes, it was me"}, {"title": "Secure Account"}], "footer": "Reply within 24 hours."}

Return ONLY valid JSON, no other text."""

# Module-level client (lazy initialized)
_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Get or create the OpenAI client from environment variables.

    Environment variables:
    - LLM_API_KEY: API key (required)
    - LLM_BASE_URL: API endpoint (optional, defaults to OpenAI)

    Works with any OpenAI-compatible API:
    - OpenAI: No base URL needed
    - OpenRouter: https://openrouter.ai/api/v1
    - vLLM: http://localhost:8000/v1
    - Ollama: http://localhost:11434/v1
    - Any other OpenAI-compatible server
    """
    global _client
    if _client is None:
        api_key = os.environ.get("LLM_API_KEY")
        base_url = os.environ.get("LLM_BASE_URL")

        if not api_key:
            raise ValueError(
                "Missing API key. Set LLM_API_KEY environment variable."
            )

        _client = OpenAI(api_key=api_key, base_url=base_url)

    return _client


def _get_model() -> str:
    """Get model from environment or use default."""
    return os.environ.get("LLM_MODEL") or "gpt-4o-mini"


def parse(text: str) -> LLMOutput:
    """Parse raw LLM text into structured LLMOutput.

    Uses an LLM to extract body text, options, header, and footer from
    free-form text that may contain choices in various formats.

    Environment variables:
    - LLM_API_KEY: API key (required)
    - LLM_BASE_URL: API endpoint (optional, defaults to OpenAI)
    - LLM_MODEL: Model name (optional, defaults to gpt-4o-mini)

    Args:
        text: Raw text from an LLM response.

    Returns:
        Structured LLMOutput ready for transformation.

    Raises:
        ValueError: If API key is missing or LLM response is invalid.
    """
    client = _get_client()
    model = _get_model()

    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": EXTRACTION_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0,  # Deterministic extraction
    )

    content = response.choices[0].message.content
    if not content:
        raise ValueError("LLM returned empty response")

    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}") from e

    return LLMOutput(**data)
