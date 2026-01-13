from adoc_link_checker.cli.types import CheckConfig
from adoc_link_checker.config import BLACKLIST


def build_check_config(
    *,
    timeout: int,
    max_workers: int,
    delay: float,
    blacklist: tuple[str, ...],
) -> CheckConfig:
    """
    Build the effective configuration for link checking.

    Rules:
    - config BLACKLIST provides defaults
    - CLI blacklist has priority
    - duplicates removed, order preserved
    """
    effective_blacklist = list(
        dict.fromkeys(BLACKLIST + list(blacklist))
    )

    return CheckConfig(
        timeout=timeout,
        max_workers=max_workers,
        delay=delay,
        blacklist=effective_blacklist,
    )
