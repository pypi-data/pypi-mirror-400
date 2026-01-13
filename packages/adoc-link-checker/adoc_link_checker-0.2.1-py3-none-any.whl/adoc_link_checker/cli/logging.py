import logging

from adoc_link_checker.config import LOGGING_CONFIG


def configure_logging(verbose: int, quiet: bool) -> None:
    """
    Configure global logging level.

    Priority:
    - --quiet
    - -vv
    - -v
    - default INFO
    """
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    if quiet:
        level = logging.ERROR
    elif verbose >= 2:
        level = logging.DEBUG
    elif verbose == 1:
        level = logging.INFO
    else:
        level = logging.INFO

    logging.basicConfig(
        level=level,
        format=LOGGING_CONFIG["format"],
        force=True,
    )
