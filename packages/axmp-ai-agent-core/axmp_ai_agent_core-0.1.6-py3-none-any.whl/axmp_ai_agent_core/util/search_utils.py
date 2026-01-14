"""This module contains the functions used for searching."""

import re


def get_escaped_regex_pattern(search_text: str | None) -> str:
    """Get pattern for search text.

    Escapes special characters and return pattern for mongodb search.
    """
    escaped_search_text = (
        re.sub(r"([.*+?^${}()|\[\]\\])", r"\\\1", search_text) if search_text else None
    )

    return f".*{escaped_search_text}.*" if escaped_search_text else ".*"
