import logging
import os

from adoc_link_checker.cli.config import build_check_config
from adoc_link_checker.cli.logging import configure_logging
from adoc_link_checker.core.runner import run_check

logger = logging.getLogger(__name__)


def check_links_command(
    *,
    path: str,
    timeout: int,
    max_workers: int,
    delay: float,
    output: str,
    blacklist: tuple[str, ...],
    exclude_from: str | None,
    fail_on_broken: bool,
    verbose: int,
    quiet: bool,
) -> None:
    """
    Execute the check-links command.
    """
    configure_logging(verbose, quiet)

    abs_path = os.path.abspath(path)
    logger.info(f"🔍 Checking links in {abs_path}")

    config = build_check_config(
        timeout=timeout,
        max_workers=max_workers,
        delay=delay,
        blacklist=blacklist,
    )

    run_check(
        root_path=abs_path,
        max_workers=config.max_workers,
        delay=config.delay,
        timeout=config.timeout,
        output_file=output,
        blacklist=config.blacklist,
        exclude_from=exclude_from,
        fail_on_broken=fail_on_broken,
    )
