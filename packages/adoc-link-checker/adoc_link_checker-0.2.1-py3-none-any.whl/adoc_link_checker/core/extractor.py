import re
import logging

from adoc_link_checker.config import LINK_PATTERNS
from adoc_link_checker.utils.url import (
    is_valid_url,
    normalize_url,
    youtube_id_to_url,
)

logger = logging.getLogger(__name__)


def extract_links(file_path: str) -> set[str]:
    """
    Extract all valid HTTP/HTTPS URLs from a .adoc file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        links: set[str] = set()

        for pattern in LINK_PATTERNS:
            for match in re.finditer(pattern, content):
                if pattern == LINK_PATTERNS[1]:
                    url = youtube_id_to_url(match.group(1))
                else:
                    url = normalize_url(match.group(0).replace("link:", ""))

                if is_valid_url(url):
                    links.add(url)

        return links

    except Exception as e:
        logger.debug(f"Error reading {file_path}: {e}")
        return set()
