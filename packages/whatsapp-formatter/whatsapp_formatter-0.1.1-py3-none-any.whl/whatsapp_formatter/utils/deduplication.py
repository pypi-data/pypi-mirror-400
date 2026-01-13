"""Deduplication utilities for ensuring unique titles."""

from whatsapp_formatter.utils.truncation import truncate_with_suffix

DEDUP_SEPARATOR = "·"


def deduplicate_titles(titles: list[str], max_len: int) -> list[str]:
    """Ensure all titles are unique by appending suffixes to duplicates.

    Uses case-insensitive comparison for detecting duplicates.
    Duplicates are suffixed with ·2, ·3, etc.

    Args:
        titles: List of titles to deduplicate.
        max_len: Maximum allowed length for each title.

    Returns:
        List of unique titles with suffixes applied as needed.
    """
    if not titles:
        return titles

    result: list[str] = []
    # Track seen titles (lowercase) and their counts
    seen: dict[str, int] = {}

    for title in titles:
        title_lower = title.lower()

        if title_lower not in seen:
            # First occurrence
            seen[title_lower] = 1
            result.append(title)
        else:
            # Duplicate found
            seen[title_lower] += 1
            count = seen[title_lower]
            suffix = f"{DEDUP_SEPARATOR}{count}"

            # Truncate title to make room for suffix
            new_title = truncate_with_suffix(title, max_len, suffix)
            result.append(new_title)

    return result


def generate_unique_id(title: str, index: int, existing_ids: set[str]) -> str:
    """Generate a unique ID for a row/button.

    Args:
        title: The title to base the ID on.
        index: The index of this item.
        existing_ids: Set of already-used IDs.

    Returns:
        A unique ID string.
    """
    # Create a slug from the title
    slug = _slugify(title)

    # Try the simple ID first
    base_id = f"{slug}_{index}" if slug else f"opt_{index}"

    if base_id not in existing_ids:
        existing_ids.add(base_id)
        return base_id

    # Handle collision by appending a counter
    counter = 2
    while True:
        candidate = f"{base_id}_{counter}"
        if candidate not in existing_ids:
            existing_ids.add(candidate)
            return candidate
        counter += 1


def _slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Args:
        text: Text to slugify.

    Returns:
        Lowercase alphanumeric string with underscores.
    """
    # Convert to lowercase and replace spaces with underscores
    slug = text.lower().replace(" ", "_")

    # Keep only alphanumeric and underscores
    slug = "".join(c for c in slug if c.isalnum() or c == "_")

    # Remove consecutive underscores
    while "__" in slug:
        slug = slug.replace("__", "_")

    # Trim underscores from ends
    slug = slug.strip("_")

    # Limit length
    return slug[:50]
