"""High-level formatter combining parsing and transformation."""

from whatsapp_formatter.parser import parse
from whatsapp_formatter.schemas import TransformResult
from whatsapp_formatter.transformer import transform


def format_for_whatsapp(text: str) -> TransformResult:
    """Parse raw LLM text and transform to WhatsApp JSON in one step.

    This is the main entry point for converting free-form LLM output
    into valid WhatsApp Business API message format.

    Environment variables:
    - LLM_API_KEY: API key (required)
    - LLM_BASE_URL: API endpoint (optional, defaults to OpenAI)
    - LLM_MODEL: Model name (optional, defaults to gpt-4o-mini)

    Args:
        text: Raw text from an LLM response (may contain options as
            numbered lists, bullets, inline choices, etc.).

    Returns:
        TransformResult containing:
        - whatsapp_json: Ready-to-send WhatsApp API payload
        - format_used: The selected format (plain_text, quick_reply, list)
        - fallback_used: Whether fallback was triggered
        - modifications: Any truncations/deduplications applied

    Example:
        ```python
        # Set env vars: LLM_API_KEY, LLM_BASE_URL (optional), LLM_MODEL (optional)
        from whatsapp_formatter import format_for_whatsapp

        raw = '''
        I can help with your account. What would you like?
        1. Check balance
        2. Transfer funds
        3. View transactions
        '''

        result = format_for_whatsapp(raw)
        print(result.whatsapp_json)
        ```
    """
    llm_output = parse(text)
    return transform(llm_output)
