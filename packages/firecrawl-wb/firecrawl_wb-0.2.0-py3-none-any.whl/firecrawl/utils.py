"""Utility functions for Firecrawl client."""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["load_api_key"]

_KEY_PATHS = (
    Path("~/.secrets/firecrawl.key"),
    Path("~/.secrets"),
)


def load_api_key(key_file: str | Path | None = None) -> str:
    """Load API key from environment or file.

    Priority:
        1. FIRECRAWL_API_KEY environment variable
        2. Specified key_file path
        3. ~/.secrets/firecrawl.key
        4. ~/.secrets (first line starting with 'fc-')

    Args:
        key_file: Optional path to API key file.

    Returns:
        API key string.

    Raises:
        ValueError: If no API key found.
    """
    if key := os.getenv("FIRECRAWL_API_KEY"):
        return key.strip()

    if key_file:
        return Path(key_file).expanduser().read_text().strip()

    for path in _KEY_PATHS:
        p = path.expanduser()
        if p.exists():
            content = p.read_text().strip()
            for line in content.splitlines():
                if line.strip().startswith("fc-"):
                    return line.strip()
            if content.startswith("fc-"):
                return content

    raise ValueError(
        "No API key found. Set FIRECRAWL_API_KEY or create ~/.secrets/firecrawl.key"
    )
