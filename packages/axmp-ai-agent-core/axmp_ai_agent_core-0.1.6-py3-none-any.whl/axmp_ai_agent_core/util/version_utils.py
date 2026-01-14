"""Generate profile version."""

from datetime import datetime
from typing import List


def generate_profile_version() -> str:
    """Generate a version timestamp string for MCP Server profiles (YYYY-MM-DD HH:MM:SS)."""
    current_version = datetime.now().replace(microsecond=0)
    version_str = current_version.strftime("%Y-%m-%d %H:%M:%S")

    return version_str


def _parse_version_number(version: str) -> int:
    """Parse version number from v1, v2, v3 format."""
    if not isinstance(version, str) or not version.startswith("v"):
        raise ValueError(f"Invalid version format: {version}")

    try:
        return int(version[1:])
    except ValueError:
        raise ValueError(f"Invalid version format: {version}")


def generate_sequential_profile_version(existing_versions: List[str]) -> str:
    """Generate next version in v1, v2, v3 format."""
    if not existing_versions:
        return "v1"

    version_numbers = []
    for version in existing_versions:
        try:
            version_numbers.append(_parse_version_number(version))
        except ValueError:
            # Skip invalid version formats
            continue

    next_number = max(version_numbers, default=0) + 1
    return f"v{next_number}"
