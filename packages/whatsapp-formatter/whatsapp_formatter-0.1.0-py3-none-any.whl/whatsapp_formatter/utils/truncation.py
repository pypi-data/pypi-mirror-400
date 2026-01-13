"""Smart text truncation utilities."""

ELLIPSIS = "…"


def truncate_smart(text: str, max_len: int) -> str:
    """Truncate text to max_len, preferring word boundaries.

    Args:
        text: The text to truncate.
        max_len: Maximum allowed length.

    Returns:
        Truncated text with ellipsis if needed.
    """
    if not text:
        return text

    # Strip whitespace first
    text = text.strip()

    # If already within limit, return as-is
    if len(text) <= max_len:
        return text

    # For very short limits (3 or less), just hard truncate without ellipsis
    if max_len <= 3:
        return text[:max_len]

    # Need to truncate - reserve space for ellipsis
    truncate_at = max_len - len(ELLIPSIS)

    # Get the text up to our truncation point
    truncated = text[:truncate_at]

    # Try to find a word boundary (space) to break at
    # Only use word boundary if we're not cutting off too much
    last_space = truncated.rfind(" ")

    if last_space > truncate_at // 2:
        # Found a reasonable word boundary - use it
        truncated = truncated[:last_space].rstrip()
    # else: no good space found, hard truncate mid-word

    return truncated + ELLIPSIS


def truncate_with_suffix(text: str, max_len: int, suffix: str) -> str:
    """Truncate text to fit both the text and a suffix within max_len.

    Args:
        text: The text to truncate.
        max_len: Maximum allowed length for text + suffix combined.
        suffix: The suffix to append (e.g., "·2").

    Returns:
        Truncated text with suffix appended.
    """
    available_for_text = max_len - len(suffix)

    if available_for_text <= 0:
        # Not enough room - just return suffix truncated
        return suffix[:max_len]

    truncated_text = truncate_smart(text, available_for_text)

    # If truncation added ellipsis but suffix is being added, we can remove ellipsis
    if truncated_text.endswith(ELLIPSIS):
        truncated_text = truncated_text[: -len(ELLIPSIS)]
        # Re-check if we need to truncate more
        if len(truncated_text) + len(suffix) > max_len:
            truncated_text = truncated_text[: max_len - len(suffix)]

    return truncated_text + suffix
