import time
import logging

from adoc_link_checker.core.extractor import extract_links
from adoc_link_checker.http.checker import create_session
from adoc_link_checker.core.context import LinkCheckContext
from adoc_link_checker.http.service import LinkChecker

logger = logging.getLogger(__name__)


def process_file(
    file_path: str,
    delay: float,
    context: LinkCheckContext,
    excluded_urls: set[str],
) -> list[tuple[str, str]]:
    """
    Process a single .adoc file and return its broken links.

    - One HTTP session per thread
    - Uses shared LinkCheckContext for caching
    """
    session = create_session()
    checker = LinkChecker(session, context)

    broken_links: list[tuple[str, str]] = []

    links = extract_links(file_path)
    links = [url for url in links if url not in excluded_urls]

    logger.debug(f"📂 Processing {file_path} ({len(links)} URLs)")

    for url in links:
        time.sleep(delay)

        if not checker.check(url):
            logger.warning(f"❌ Broken URL: {url}")
            broken_links.append((url, "URL not accessible"))
        else:
            logger.debug(f"✅ URL OK: {url}")

    return broken_links
