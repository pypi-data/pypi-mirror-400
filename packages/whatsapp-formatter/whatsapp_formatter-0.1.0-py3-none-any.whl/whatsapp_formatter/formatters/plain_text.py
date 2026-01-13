"""Plain text message formatter."""

from typing import Any

from whatsapp_formatter.schemas import Constraints, LLMOutput
from whatsapp_formatter.utils.truncation import truncate_smart


def make_plain_text(
    llm_output: LLMOutput,
    is_fallback: bool = False,
    modifications: list[str] | None = None,
) -> dict[str, Any]:
    """Generate plain text WhatsApp JSON.

    Args:
        llm_output: The LLM output to transform.
        is_fallback: Whether this is a fallback from another format.
        modifications: List to append modification notes to.

    Returns:
        WhatsApp plain text message JSON.
    """
    if modifications is None:
        modifications = []

    body = llm_output.body

    # If fallback with options, append numbered list
    if is_fallback:
        options_text = _format_options_as_list(llm_output)
        if options_text:
            body = f"{body}\n\nReply with a number:\n{options_text}"

    # Truncate body if needed
    if len(body) > Constraints.PLAIN_TEXT_BODY_MAX:
        original_len = len(body)
        body = truncate_smart(body, Constraints.PLAIN_TEXT_BODY_MAX - 15)
        body += "\n(continued...)"
        modifications.append(
            f"truncated_body_from_{original_len}_to_{len(body)}"
        )

    return {
        "type": "text",
        "text": {
            "body": body
        }
    }


def _format_options_as_list(llm_output: LLMOutput) -> str:
    """Format options as a numbered list for plain text fallback.

    Args:
        llm_output: The LLM output containing options.

    Returns:
        Formatted numbered list string.
    """
    options = _get_all_options(llm_output)
    if not options:
        return ""

    lines = []
    for i, option in enumerate(options, 1):
        line = f"{i}. {option.title}"
        if option.description:
            line += f" - {option.description}"
        lines.append(line)

    return "\n".join(lines)


def _get_all_options(llm_output: LLMOutput) -> list:
    """Get all options from either flat list or sections.

    Args:
        llm_output: The LLM output.

    Returns:
        Flat list of all options.
    """
    if llm_output.options:
        return llm_output.options

    if llm_output.sections:
        all_options = []
        for section in llm_output.sections:
            all_options.extend(section.options)
        return all_options

    return []
