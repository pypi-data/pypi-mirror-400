import logging
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from adoc_link_checker.core.discovery import find_adoc_files
from adoc_link_checker.core.context import LinkCheckContext
from adoc_link_checker.reporting.json import write_report
from adoc_link_checker.core.processing import process_file
from adoc_link_checker.utils.exclusions import load_excluded_urls

logger = logging.getLogger(__name__)


def run_check(
    root_path: str,
    max_workers: int,
    delay: float,
    timeout: int,
    output_file: str,
    blacklist: list[str],
    exclude_from: str | None,
    fail_on_broken: bool = False,
) -> None:
    if not output_file:
        raise ValueError("output_file must be provided")

    files = find_adoc_files(root_path)
    logger.info(f"📄 Found {len(files)} .adoc file(s)")

    excluded_urls = load_excluded_urls(exclude_from)
    context = LinkCheckContext(timeout=timeout, blacklist=blacklist)

    broken_links: dict[str, list[tuple[str, str]]] = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(
                process_file,
                file,
                delay,
                context,
                excluded_urls,
            ): file
            for file in files
        }

        for future in as_completed(futures):
            file = futures[future]
            result = future.result()
            if result:
                broken_links[file] = result

    write_report(output_file, broken_links)

    if not broken_links:
        logger.info("✅ No broken links found.")

    if fail_on_broken and broken_links:
        logger.error("❌ Broken links detected.")
        sys.exit(1)
