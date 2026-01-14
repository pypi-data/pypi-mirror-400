"""Name utility functions."""

import re


def convert_display_name_to_name(display_name: str) -> str:
    """Convert display_name to name following the conversion rules.

    Rules:
    1. Replace all whitespace (space, tab, etc.) with underscore (-)
    2. Convert to lowercase

    Args:
        display_name: The display name to convert

    Returns:
        Converted name
    """
    # Replace all whitespace with underscore
    name = re.sub(r"\s+", "-", display_name)

    # Convert to lowercase
    name = name.lower()

    return name
