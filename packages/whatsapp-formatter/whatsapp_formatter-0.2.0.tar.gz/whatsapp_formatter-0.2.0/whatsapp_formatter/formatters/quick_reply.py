"""Quick reply button formatter."""

from typing import Any

from whatsapp_formatter.schemas import Constraints, LLMOutput, Option
from whatsapp_formatter.utils.deduplication import deduplicate_titles, generate_unique_id
from whatsapp_formatter.utils.truncation import truncate_smart


def make_quick_reply(
    llm_output: LLMOutput,
    modifications: list[str] | None = None,
) -> dict[str, Any]:
    """Generate quick reply button WhatsApp JSON.

    Args:
        llm_output: The LLM output to transform.
        modifications: List to append modification notes to.

    Returns:
        WhatsApp interactive button message JSON.
    """
    if modifications is None:
        modifications = []

    options = _get_options(llm_output)

    # Truncate titles
    titles = []
    for i, option in enumerate(options):
        title = option.title
        if len(title) > Constraints.QUICK_REPLY_BUTTON_TITLE_MAX:
            original = title
            title = truncate_smart(title, Constraints.QUICK_REPLY_BUTTON_TITLE_MAX)
            modifications.append(f"truncated_button_{i}_{len(original)}_to_{len(title)}")
        titles.append(title)

    # Deduplicate titles
    unique_titles = deduplicate_titles(titles, Constraints.QUICK_REPLY_BUTTON_TITLE_MAX)
    for i, (orig, deduped) in enumerate(zip(titles, unique_titles)):
        if orig != deduped:
            modifications.append(f"deduplicated_button_{i}")

    # Generate unique IDs
    existing_ids: set[str] = set()
    buttons = []
    for i, title in enumerate(unique_titles):
        button_id = generate_unique_id(title, i, existing_ids)
        buttons.append({
            "type": "reply",
            "reply": {
                "id": button_id,
                "title": title
            }
        })

    # Build the interactive message
    interactive: dict[str, Any] = {
        "type": "button",
        "body": {
            "text": _truncate_body(llm_output.body, modifications)
        },
        "action": {
            "buttons": buttons
        }
    }

    # Add optional header
    if llm_output.header:
        header_text = llm_output.header
        if len(header_text) > Constraints.HEADER_MAX:
            original_len = len(header_text)
            header_text = truncate_smart(header_text, Constraints.HEADER_MAX)
            modifications.append(f"truncated_header_{original_len}_to_{len(header_text)}")
        interactive["header"] = {
            "type": "text",
            "text": header_text
        }

    # Add optional footer
    if llm_output.footer:
        footer_text = llm_output.footer
        if len(footer_text) > Constraints.FOOTER_MAX:
            original_len = len(footer_text)
            footer_text = truncate_smart(footer_text, Constraints.FOOTER_MAX)
            modifications.append(f"truncated_footer_{original_len}_to_{len(footer_text)}")
        interactive["footer"] = {
            "text": footer_text
        }

    return {
        "type": "interactive",
        "interactive": interactive
    }


def _get_options(llm_output: LLMOutput) -> list[Option]:
    """Get options from either flat list or sections (flattened).

    Args:
        llm_output: The LLM output.

    Returns:
        Flat list of options.
    """
    if llm_output.options:
        return llm_output.options

    if llm_output.sections:
        all_options = []
        for section in llm_output.sections:
            all_options.extend(section.options)
        return all_options

    return []


def _truncate_body(body: str, modifications: list[str]) -> str:
    """Truncate body text if needed.

    Args:
        body: The body text.
        modifications: List to append modification notes to.

    Returns:
        Truncated body text.
    """
    if len(body) > Constraints.BODY_MAX:
        original_len = len(body)
        body = truncate_smart(body, Constraints.BODY_MAX)
        modifications.append(f"truncated_body_{original_len}_to_{len(body)}")
    return body
