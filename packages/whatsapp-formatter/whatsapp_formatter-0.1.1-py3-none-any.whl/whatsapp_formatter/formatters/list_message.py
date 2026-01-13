"""List message formatter."""

from typing import Any

from whatsapp_formatter.schemas import Constraints, LLMOutput, Option, Section
from whatsapp_formatter.utils.deduplication import deduplicate_titles, generate_unique_id
from whatsapp_formatter.utils.truncation import truncate_smart


def make_list(
    llm_output: LLMOutput,
    modifications: list[str] | None = None,
) -> dict[str, Any]:
    """Generate list message WhatsApp JSON.

    Args:
        llm_output: The LLM output to transform.
        modifications: List to append modification notes to.

    Returns:
        WhatsApp interactive list message JSON.
    """
    if modifications is None:
        modifications = []

    # Determine if we have sections or flat options
    if llm_output.sections:
        sections = _build_sections_from_grouped(llm_output.sections, modifications)
    else:
        sections = _build_single_section(llm_output.options or [], modifications)

    # Build the interactive message
    interactive: dict[str, Any] = {
        "type": "list",
        "body": {
            "text": _truncate_body(llm_output.body, modifications)
        },
        "action": {
            "button": Constraints.DEFAULT_LIST_BUTTON_TEXT,
            "sections": sections
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


def _build_single_section(
    options: list[Option],
    modifications: list[str],
) -> list[dict[str, Any]]:
    """Build a single section (no title) from flat options.

    Args:
        options: List of options.
        modifications: List to append modification notes to.

    Returns:
        List containing single section dict.
    """
    rows = _build_rows(options, modifications)
    return [{"rows": rows}]


def _build_sections_from_grouped(
    sections: list[Section],
    modifications: list[str],
) -> list[dict[str, Any]]:
    """Build multiple sections from grouped options.

    Args:
        sections: List of sections with options.
        modifications: List to append modification notes to.

    Returns:
        List of section dicts with titles and rows.
    """
    # Collect all titles for deduplication across sections
    all_titles = []
    for section in sections:
        for option in section.options:
            all_titles.append(option.title)

    # Deduplicate all titles
    unique_titles = deduplicate_titles(all_titles, Constraints.LIST_ROW_TITLE_MAX)

    # Track which titles were deduplicated
    title_map: dict[int, str] = {}  # index -> unique title
    for i, (orig, unique) in enumerate(zip(all_titles, unique_titles)):
        title_map[i] = unique
        if orig != unique:
            modifications.append(f"deduplicated_row_title_{i}")

    # Build sections with unique titles
    result = []
    existing_ids: set[str] = set()
    title_idx = 0

    for section in sections:
        # Skip empty sections
        if not section.options:
            continue

        # Truncate section title if needed
        section_title = section.title
        if len(section_title) > Constraints.LIST_SECTION_TITLE_MAX:
            original_len = len(section_title)
            section_title = truncate_smart(section_title, Constraints.LIST_SECTION_TITLE_MAX)
            modifications.append(
                f"truncated_section_title_{original_len}_to_{len(section_title)}"
            )

        rows = []
        for option in section.options:
            row = _build_row(
                title_map[title_idx],
                option.description,
                title_idx,
                existing_ids,
                modifications,
            )
            rows.append(row)
            title_idx += 1

        result.append({
            "title": section_title,
            "rows": rows
        })

    return result


def _build_rows(
    options: list[Option],
    modifications: list[str],
) -> list[dict[str, Any]]:
    """Build row objects from options.

    Args:
        options: List of options.
        modifications: List to append modification notes to.

    Returns:
        List of row dicts.
    """
    # Collect and truncate titles
    titles = []
    for option in options:
        title = option.title
        if len(title) > Constraints.LIST_ROW_TITLE_MAX:
            title = truncate_smart(title, Constraints.LIST_ROW_TITLE_MAX)
        titles.append(title)

    # Track truncations
    for i, (orig, trunc) in enumerate(zip([o.title for o in options], titles)):
        if orig != trunc:
            modifications.append(f"truncated_row_title_{i}")

    # Deduplicate titles
    unique_titles = deduplicate_titles(titles, Constraints.LIST_ROW_TITLE_MAX)
    for i, (orig, unique) in enumerate(zip(titles, unique_titles)):
        if orig != unique:
            modifications.append(f"deduplicated_row_title_{i}")

    # Build rows
    existing_ids: set[str] = set()
    rows = []
    for i, (option, title) in enumerate(zip(options, unique_titles)):
        row = _build_row(title, option.description, i, existing_ids, modifications)
        rows.append(row)

    return rows


def _build_row(
    title: str,
    description: str | None,
    index: int,
    existing_ids: set[str],
    modifications: list[str],
) -> dict[str, Any]:
    """Build a single row object.

    Args:
        title: The row title (already truncated and deduplicated).
        description: Optional description.
        index: Row index for ID generation.
        existing_ids: Set of existing IDs for uniqueness.
        modifications: List to append modification notes to.

    Returns:
        Row dict with id, title, and optional description.
    """
    row_id = generate_unique_id(title, index, existing_ids)

    row: dict[str, Any] = {
        "id": row_id,
        "title": title
    }

    if description:
        desc = description
        if len(desc) > Constraints.LIST_ROW_DESCRIPTION_MAX:
            original_len = len(desc)
            desc = truncate_smart(desc, Constraints.LIST_ROW_DESCRIPTION_MAX)
            modifications.append(
                f"truncated_row_description_{index}_{original_len}_to_{len(desc)}"
            )
        row["description"] = desc

    return row


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
