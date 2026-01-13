# Public API re-exports (backward compatibility)

from adoc_link_checker.core.discovery import find_adoc_files
from adoc_link_checker.core.extractor import extract_links
from adoc_link_checker.core.context import LinkCheckContext
from adoc_link_checker.core.processing import process_file
from adoc_link_checker.core.runner import run_check

from adoc_link_checker.http.checker import check_url, create_session

from adoc_link_checker.utils.url import (
    normalize_url,
    is_valid_url,
    is_blacklisted,
)

from adoc_link_checker.utils.exclusions import load_excluded_urls

from adoc_link_checker.reporting.json import write_report
