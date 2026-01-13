"""Main transformer module - entry point for LLM output to WhatsApp JSON conversion."""

import logging
from typing import Any

from whatsapp_formatter.formatters.list_message import make_list
from whatsapp_formatter.formatters.plain_text import make_plain_text
from whatsapp_formatter.formatters.quick_reply import make_quick_reply
from whatsapp_formatter.schemas import (
    Constraints,
    FormatType,
    LLMOutput,
    TransformResult,
)

logger = logging.getLogger(__name__)


def transform(llm_output: LLMOutput) -> TransformResult:
    """Transform LLM output to WhatsApp Business API JSON.

    This is the main entry point. It selects the optimal format based on
    option count and generates valid WhatsApp JSON.

    Args:
        llm_output: Structured output from LLM.

    Returns:
        TransformResult with WhatsApp JSON and metadata.
    """
    modifications: list[str] = []
    fallback_used = False
    fallback_reason: str | None = None

    # Count total options
    option_count = count_total_options(llm_output)

    # Select format based on option count
    format_type = select_format(llm_output)

    # Check if we need to fallback due to too many options
    if option_count > Constraints.LIST_MAX_ROWS:
        fallback_used = True
        fallback_reason = f"too_many_options_{option_count}"
        format_type = FormatType.PLAIN_TEXT
        logger.warning(
            "Fallback triggered: %s options exceeds limit of %d",
            option_count,
            Constraints.LIST_MAX_ROWS,
        )

    # Check if we need to fallback due to too many sections
    if llm_output.sections and len(llm_output.sections) > Constraints.LIST_MAX_SECTIONS:
        fallback_used = True
        fallback_reason = f"too_many_sections_{len(llm_output.sections)}"
        format_type = FormatType.PLAIN_TEXT
        logger.warning(
            "Fallback triggered: %s sections exceeds limit of %d",
            len(llm_output.sections),
            Constraints.LIST_MAX_SECTIONS,
        )

    # Generate WhatsApp JSON based on selected format
    whatsapp_json = _generate_json(
        llm_output,
        format_type,
        fallback_used,
        modifications,
    )

    # Log the transformation
    logger.info(
        "Transform complete: format=%s, options=%d, fallback=%s, modifications=%d",
        format_type.value,
        option_count,
        fallback_used,
        len(modifications),
    )

    return TransformResult(
        success=True,
        whatsapp_json=whatsapp_json,
        format_used=format_type,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        modifications=modifications,
    )


def count_total_options(llm_output: LLMOutput) -> int:
    """Count total options including from sections.

    Args:
        llm_output: The LLM output.

    Returns:
        Total number of options.
    """
    if llm_output.options:
        return len(llm_output.options)

    if llm_output.sections:
        total = 0
        for section in llm_output.sections:
            total += len(section.options)
        return total

    return 0


def select_format(llm_output: LLMOutput) -> FormatType:
    """Select the optimal WhatsApp format based on option count.

    Decision tree:
    - 0 options → plain text
    - 1-3 options → quick reply buttons
    - 4-10 options → list message
    - >10 options → plain text fallback (handled in transform)

    Args:
        llm_output: The LLM output.

    Returns:
        The selected format type.
    """
    option_count = count_total_options(llm_output)

    if option_count == 0:
        return FormatType.PLAIN_TEXT

    if option_count <= Constraints.QUICK_REPLY_MAX_BUTTONS:
        return FormatType.QUICK_REPLY

    if option_count <= Constraints.LIST_MAX_ROWS:
        return FormatType.LIST

    # >10 options - will trigger fallback in transform()
    return FormatType.PLAIN_TEXT


def _generate_json(
    llm_output: LLMOutput,
    format_type: FormatType,
    is_fallback: bool,
    modifications: list[str],
) -> dict[str, Any]:
    """Generate WhatsApp JSON for the selected format.

    Args:
        llm_output: The LLM output.
        format_type: The selected format.
        is_fallback: Whether this is a fallback scenario.
        modifications: List to track modifications.

    Returns:
        WhatsApp message JSON.
    """
    if format_type == FormatType.PLAIN_TEXT:
        return make_plain_text(llm_output, is_fallback=is_fallback, modifications=modifications)

    if format_type == FormatType.QUICK_REPLY:
        return make_quick_reply(llm_output, modifications=modifications)

    if format_type == FormatType.LIST:
        return make_list(llm_output, modifications=modifications)

    # Should never reach here
    raise ValueError(f"Unknown format type: {format_type}")
